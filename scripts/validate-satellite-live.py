"""One bounded CDSE validation run; explicit pair, no retries or model calls.

Save raw imagery under an ignored private output directory. Only reviewed,
credential-free report fields should be copied into committed evidence.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx
import numpy as np
from rasterio.io import MemoryFile
from satellite.domain import Area, CatalogRequest, DomainError
from satellite.eve_cdse import CDSE, PROCESS_URL
from satellite.evidence import compare_pixels, read_observation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bbox', required=True, type=float, nargs=4, metavar=('WEST', 'SOUTH', 'EAST', 'NORTH'))
    parser.add_argument('--start-date', required=True)
    parser.add_argument('--end-date', required=True)
    parser.add_argument('--before-id')
    parser.add_argument('--after-id')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if bool(args.before_id) != bool(args.after_id):
        parser.error('Provide both scene IDs or neither (catalog only).')
    request = CatalogRequest(area=Area(bbox=args.bbox), start_date=args.start_date, end_date=args.end_date)
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {
        'started_at': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted((ROOT/'satellite').glob('*.py'))},
        'request': request.model_dump(mode='json'),
        'selected_scene_ids': [args.before_id, args.after_id] if args.before_id else [],
        'requests': [], 'bundles': [], 'observations': [], 'state': 'running',
        'classification': 'not_requested',
    }

    def save():
        (output/'validation.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')

    def record(response):
        # Never serialize request headers, OAuth bodies, tokens or provider errors.
        report['requests'].append({
            'url': str(response.request.url), 'status': response.status_code,
            'content_type': response.headers.get('content-type'),
            'processing_units': response.headers.get('x-processingunits-spent'),
        })
        save()

    class CaptureCDSE(CDSE):
        def post(self, url, payload, limit=16_000_000):
            data = super().post(url, payload, limit)
            if url == PROCESS_URL:
                name = f'process-{len(report["bundles"])+1}.bin'
                (output/name).write_bytes(data)
                bundle = {'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                try:
                    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                        bundle['members'] = [{'name': m.name, 'bytes': m.size} for m in archive.getmembers()]
                except tarfile.TarError:
                    bundle['format'] = 'not_tar'
                report['bundles'].append(bundle)
                save()
            return data

    save()
    try:
        with httpx.Client(timeout=60, follow_redirects=False, event_hooks={'response': [record]}) as client:
            cdse = CaptureCDSE(client)
            catalog = cdse.catalog(request)
            (output/'catalog.json').write_text(json.dumps(catalog, indent=2)+'\n')
            report['catalog'] = {'state': catalog['state'], 'count': len(catalog['scenes']), 'truncated': catalog['truncated']}
            if args.before_id:
                scenes = {s['id']: s for s in catalog['scenes']}
                if args.before_id not in scenes or args.after_id not in scenes:
                    raise DomainError('scene_unavailable', 'Selected scene IDs were not returned by this catalog.')
                selected = [scenes[args.before_id], scenes[args.after_id]]
                if datetime.fromisoformat(selected[0]['acquired_at']) >= datetime.fromisoformat(selected[1]['acquired_at']):
                    raise DomainError('invalid_order', 'Select two different observations in chronological order.')
                grid = request.area.grid()
                report['grid'] = grid
                observations = []
                for label, scene in zip(('before', 'after'), selected):
                    data, provenance = cdse.observation(scene, grid)
                    (output/f'{label}.tif').write_bytes(data)
                    observation = read_observation(data, grid)
                    observations.append(observation)
                    (output/f'{label}.png').write_bytes(observation['png'])
                    with MemoryFile(data) as memory, memory.open() as dataset:
                        raster = {'shape': [dataset.count, dataset.height, dataset.width],
                                  'crs': str(dataset.crs), 'transform': list(dataset.transform),
                                  'dtypes': dataset.dtypes,
                                  'evalscript_band_order': ['B04', 'B03', 'B02', 'B08', 'B11', 'B12', 'SCL', 'dataMask'],
                                  'scl_values': np.unique(observation['bands'][6]).tolist(),
                                  'data_mask_values': np.unique(observation['bands'][7]).tolist()}
                    if not set(raster['scl_values']) <= set(range(12)) or not set(raster['data_mask_values']) <= {0, 1}:
                        raise DomainError('invalid_quality_bands', 'Unexpected scene-classification or data-mask values.')
                    report['observations'].append({'label': label, 'provenance': provenance,
                        'quality': observation['quality'], 'raster': raster,
                        'spectral_sha256': hashlib.sha256(data).hexdigest(),
                        'png_sha256': hashlib.sha256(observation['png']).hexdigest()})
                    save()
                report['comparison'] = compare_pixels(*observations, grid)
            report['state'] = 'passed'
    except DomainError as error:
        report.update(state='failed', error={'code': error.code, 'message': error.message})
    except Exception as error:
        report.update(state='failed', error={'code': type(error).__name__, 'message': 'Validation stopped. No finding inferred.'})
    finally:
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        report['processing_units_reported'] = sum(float(r['processing_units']) for r in report['requests'] if r['processing_units'] is not None)
        report['processing_units_note'] = 'Provider-reported usage for recorded responses only; not a currency charge or account balance.'
        save()
    print(json.dumps({'state': report['state'], 'report': str(output/'validation.json'),
                      'catalog': report.get('catalog'), 'error': report.get('error'),
                      'processing_units_reported': report['processing_units_reported']}))
    return 0 if report['state'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
