"""Offline construction through pinned native PR #88 code. No dispatch or ledger.

The full-page examples are recovered development inputs, not historical retrieval
profiles. Fixed model/effort only; no inference or configuration comparison.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from source_context_probe import load_inputs, probes

REFERENCE = '0c234e6f53dce24632875cc1f58f0c4dd302078a'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-checkout', type=Path, required=True)
    parser.add_argument('--input-directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    head = subprocess.check_output(['git', '-C', str(args.reference_checkout), 'rev-parse', 'HEAD'], text=True).strip()
    # Refuse edits to runtime modules. Extra ignored source artifacts are irrelevant.
    clean = subprocess.run(['git', '-C', str(args.reference_checkout), 'diff', '--quiet', 'HEAD', '--', 'backend'], check=False)
    if head != REFERENCE or clean.returncode:
        raise ValueError('native reference differs from pinned source')
    sys.path.insert(0, str(args.reference_checkout.resolve()))
    from backend.chat import ChatRequest, prepare_answer
    from backend.phase_effort import local_plan_adapter
    from backend.providers import ChatConfig
    from backend.reconstruction import prepare_reconstruction, reconstruction_message_request
    from backend.source_spans import encoded
    config = ChatConfig(provider='anthropic', model='claude-haiku-5-5', label='offline only',
                        key_name='UNUSED_NO_CLIENT', base_url='https://api.anthropic.com',
                        max_output_tokens=12000, effort='medium', pipeline='single_final_v2')
    manifest, inputs = load_inputs(args.input_directory)
    result = {'reference_commit': REFERENCE, 'provider_calls': 0, 'ledger_access': False,
              'kind': 'new_consumed_source_builder_profiles', 'semantic': 'not_assessed',
              'release': 'hold', 'profiles': []}
    seen = set()
    for identifier, pack, _, _ in probes(manifest, inputs):
        if pack['question'] in seen:
            continue
        seen.add(pack['question'])
        evidence = [{'id': 'page-' + page, 'text': text, 'page': int(page),
                     'start': 0, 'end': len(text), **pack['provenance']}
                    for page, text in pack['passages'].items()]
        for style in ('standard', 'brief'):
            row = {'id': identifier + '-' + style, 'input_page_ids': [e['id'] for e in evidence]}
            request = ChatRequest(question=pack['question'], answer_style=style)
            try:
                original = prepare_answer(request, evidence, provider='anthropic')
                row.update(original_message_bytes=len(encoded(original.messages)),
                           selected_page_ids=[e['id'] for e in original.evidence],
                           all_original_pages_retained=original.evidence == evidence)
                # Do not proceed with a reduced set and call it full-source success.
                if original.evidence != evidence:
                    raise ValueError('original preparation dropped full-page evidence')
                final = prepare_reconstruction(request, original, local_plan_adapter())
                body = reconstruction_message_request(config, final)
                row.update(final_message_bytes=len(encoded(final.messages)),
                           schema_bytes=len(encoded(final.schema)),
                           body_sha256=hashlib.sha256(encoded(body)).hexdigest(),
                           max_output_tokens=body['max_tokens'], status='constructed')
            except ValueError as error:
                row.update(status='refused', reason=str(error))
            result['profiles'].append(row)
    import os
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
