"""Recover exact Git bytes for offline review; never run recovered application code.

Requires an explicit cloud clone and a NEW output directory. Does not search a
workstation, use credentials, call a provider, inspect a ledger or change Git refs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PINS = Path(__file__).with_name('recovered_native_inputs.json')


def recover(repository, output):
    pins = json.loads(PINS.read_text())
    rows = []
    count = 0
    for item in pins['files']:
        raw = subprocess.check_output(['git', '-C', str(repository), 'show',
                                       pins['source_commit'] + ':' + item['path']])
        if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('recovery bytes differ from pinned input')
        if 'cases' in item:
            value = json.loads(raw)
            cases = value if isinstance(value, list) else value['cases']
            if len(cases) != item['cases']:
                raise ValueError('recovered case count differs')
            count += len(cases)
        rows.append((item['path'], raw))
    if count != 67 or pins['required_semantic_cases'] != 71:
        raise ValueError('acceptance accounting changed')
    # Validate all objects first. Never overwrite an earlier recovery or source.
    output.mkdir(mode=0o700)
    for name, raw in rows:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (output / 'recovery-manifest.json').write_text(json.dumps(pins, indent=2) + '\n')
    return {'recovered_cases': count, 'required_cases': 71,
            'missing_boundary_cases': 4, 'provider_calls': 0, 'acceptance': 'not_run'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output-directory', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(recover(args.repository, args.output_directory)))


if __name__ == '__main__':
    main()
