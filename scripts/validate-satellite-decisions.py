"""One paid Decisions request using verified, previously captured CDSE rasters.

No CDSE retrieval, retries, alternate providers or research generation. Reports
contain only reviewed metadata and validated choices; never keys or raw bodies.
The CLI uses a persistent one-attempt-per-UTC-day validation ledger, including
failures. Run only after reviewing an earlier failed attempt, never as a retry.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx
from dotenv import load_dotenv
from satellite.domain import Area, DomainError, Intent
from satellite.evidence import classification_image, compare_pixels, read_observation
from satellite.providers import DecisionsClassifier
from satellite.store import Store
from satellite.summary import canopy_presence, summarize_comparison

ENDPOINT = 'https://api.openai.com/v1/decisions'
LEDGER = ROOT/'.reports/satellite-decisions-validation/usage.sqlite'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def limited_bytes(path, maximum):
    with path.open('rb') as stream:
        data = stream.read(maximum+1)
    if len(data) > maximum:
        raise DomainError('oversized_input', 'Recorded validation input exceeds the allowed size.')
    return data


def load_recorded_pair(recorded_run):
    """Recheck source hashes and grid/provenance before any reservation or call."""
    raw = limited_bytes(recorded_run/'validation.json', 1_000_000)
    source = json.loads(raw)
    if source['state'] != 'passed' or len(source['observations']) != 2:
        raise DomainError('unverified_recording', 'Use a passed two-observation CDSE validation run.')
    area = Area.model_validate(source['request']['area'])
    grid = area.grid()
    observations, provenance, inputs = [], [], []
    for index, label in enumerate(('before', 'after')):
        saved = source['observations'][index]
        original = saved['provenance']
        instant = original['catalog_acquired_at']
        scene = original['catalog_scene_id']
        if (saved['label'] != label or source['selected_scene_ids'][index] != scene or
                original['acquired_at'] != [instant] or original['collection'] != 'sentinel-2-l2a' or
                not isinstance(scene, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,200}', scene)):
            raise DomainError('invalid_provenance', 'The recording does not identify one matching acquisition per observation.')
        timestamp = datetime.fromisoformat(instant.replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            raise DomainError('invalid_provenance', 'Acquisition times must include a timezone.')
        data = limited_bytes(recorded_run/(label+'.tif'), 16_000_000)
        actual_hash = digest(data)
        if actual_hash != saved['spectral_sha256']:
            raise DomainError('recording_hash_mismatch', 'A recorded raster no longer matches its verified source hash.')
        observation = read_observation(data, grid)
        observations.append(observation)
        # Reconstruct an allowlist; never forward raw saved/provider text.
        provenance.append({'catalog_scene_id': scene, 'acquired_at': [timestamp.isoformat()],
                           'collection': 'sentinel-2-l2a', 'display_resolution_m': 10,
                           'swir_and_scene_classification_native_resolution_m': 20})
        inputs.append({'label': label, 'spectral_sha256': actual_hash,
                       'catalog_scene_id': scene, 'acquired_at': timestamp.isoformat(),
                       'quality': observation['quality']})
    if datetime.fromisoformat(inputs[0]['acquired_at']) >= datetime.fromisoformat(inputs[1]['acquired_at']):
        raise DomainError('invalid_order', 'Recorded observations must be in chronological order.')
    return observations, provenance, inputs, grid, digest(raw)


class SingleRequestClient:
    """Restrict the existing adapter to one bounded request and safe telemetry."""
    def __init__(self, client, report, save):
        self.client, self.report, self.save = client, report, save

    def post(self, url, **kwargs):
        if url != ENDPOINT or self.report['requests_attempted']:
            raise DomainError('request_boundary', 'Only one request to the Decisions endpoint is allowed.')
        self.report['requests_attempted'] = 1
        self.save()
        with self.client.stream('POST', url, **kwargs, follow_redirects=False) as response:
            request_id = response.headers.get('x-request-id', '')
            self.report['provider_response'] = {'status': response.status_code,
                'request_id': request_id if re.fullmatch(r'req_[A-Za-z0-9_-]{1,128}', request_id) else None}
            self.save()
            chunks, size = [], 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > 1_000_000:
                    raise DomainError('oversized_response', 'The Decisions response exceeded the allowed size.')
                chunks.append(chunk)
            body = b''.join(chunks)
            # Retain reported tokens even when the answer fails schema validation.
            try:
                usage = json.loads(body).get('usage', {})
                self.report['provider_usage'] = {key: value for key, value in usage.items()
                    if key in {'input_tokens', 'output_tokens'} and type(value) is int and value >= 0}
            except (ValueError, AttributeError, TypeError):
                pass
            self.save()
            return httpx.Response(response.status_code, content=body)


def run_validation(recorded_run, output, *, intent='canopy_loss', client=None, ledger_path=LEDGER):
    """Caller-supplied client/ledger are for offline tests; CLI fixes the ledger."""
    os.umask(0o077)
    output.mkdir(parents=True, exist_ok=False)
    report = {'started_at': datetime.now(timezone.utc).isoformat(), 'state': 'running',
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_sha256': {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in
            [Path(__file__).resolve(), *sorted((ROOT/'satellite').glob('*.py'))]},
        'mode': 'One live OpenAI Decisions request on previously captured real CDSE rasters; no new imagery retrieval.',
        'intent': Intent(intent).value, 'requests_attempted': 0, 'reservation': 'not_made',
        'provider_usage': {}, 'validation': 'Contract smoke only; not Goa field accuracy or individual-tree detection.'}

    def save():
        temporary = output/'validation.json.tmp'
        temporary.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
        temporary.replace(output/'validation.json')

    save()
    store, owned_client = None, None
    try:
        observations, sources, inputs, grid, recording_hash = load_recorded_pair(recorded_run)
        report.update(inputs=inputs, recorded_validation_sha256=recording_hash,
                      grid={'crs': grid['crs'], 'width': grid['width'], 'height': grid['height'], 'resolution_m': 10})
        evidence = compare_pixels(*observations, grid)
        report['numeric_evidence'] = evidence
        interval = {'before': inputs[0]['acquired_at'], 'after': inputs[1]['acquired_at'],
                    'exact_event_date': None, 'cause': 'not_established'}
        report['observation_interval'] = interval
        if evidence['state'] != 'observable':
            raise DomainError('insufficient_coverage', 'Common usable coverage is insufficient; no model request was made.')
        if not os.getenv('OPENAI_API_KEY'):
            raise DomainError('missing_credentials', 'OpenAI Decisions is not configured; no request was made.')
        common = observations[0]['clear'] & observations[1]['clear']
        images = [classification_image(observation, common) for observation in observations]
        for item, image in zip(report['inputs'], images):
            item['common_masked_png_sha256'] = digest(image)
        save()
        store = Store(ledger_path)
        store.reserve('classifications', 1)
        report['reservation'] = 'persisted_before_request'
        report['ledger'] = str(ledger_path)
        save()
        if client is None:
            owned_client = httpx.Client(timeout=60, follow_redirects=False)
            client = owned_client
        classification = DecisionsClassifier(SingleRequestClient(client, report, save)).classify(*images, {
            'before': sources[0], 'after': sources[1], 'spectral_metrics': evidence['metrics'],
            'common_usable_fraction': evidence['common_usable_fraction'], 'area_m2': grid['area_m2'],
            'intent': intent, 'water_change': evidence['water_change'],
            'numeric_vegetation_loss_candidates': len(evidence['candidates']['features'])})
        if classification['state'] != 'complete':
            raise DomainError('incomplete_assessment', 'No complete image assessment was returned.')
        report.update(classification=classification, canopy_presence=canopy_presence(evidence, classification),
            summary=summarize_comparison(intent, evidence, classification, interval), state='passed')
    except DomainError as error:
        report.update(state='failed', error={'code': error.code, 'message': error.message})
    except Exception as error:
        # Never include exception text, request objects, provider errors or headers.
        report.update(state='failed', error={'code': type(error).__name__,
            'message': 'Validation stopped safely. No result was inferred and no retry was attempted.'})
    finally:
        if owned_client is not None: owned_client.close()
        if store is not None: store.close()
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        report['usage_note'] = 'Reported tokens only; not a currency charge or field-accuracy measure. Reservations remain consumed on failures.'
        save()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recorded-run', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--intent', choices=[intent.value for intent in Intent], default='canopy_loss')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if not output.is_relative_to(ROOT/'.reports'):
        parser.error('Use a new output directory under ignored .reports/. Review safe report fields before publishing.')
    if output.exists():
        parser.error('Choose a new output directory; existing evidence is never overwritten.')
    load_dotenv(ROOT/'.env.local', override=False)
    report = run_validation(Path(args.recorded_run).resolve(), output, intent=args.intent)
    print(json.dumps({'state': report['state'], 'report': str(output/'validation.json'),
        'requests_attempted': report['requests_attempted'], 'reservation': report['reservation'],
        'provider_response': report.get('provider_response'), 'usage': report['provider_usage'],
        'error': report.get('error')}))
    return 0 if report['state'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
