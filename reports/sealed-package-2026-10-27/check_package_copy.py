"""Verify a sealed package and check its packaged runtime on disposable copies.

This parent uses ordinary byte reads only. Native libraries run in the child,
against copied data and service code, and must exit before preservation checks.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.evaluate_research_copy import is_preserved


def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Package cannot contain symlinks')
        if path.is_file():
            with path.open('rb') as handle:
                result[str(path.relative_to(root))] = hashlib.file_digest(handle, 'sha256').hexdigest()
    return result


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--seal-sha256', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    package, output = args.package.resolve(), args.output_dir.resolve()
    if output.is_relative_to(package) or is_preserved(output):
        parser.error('Write reports outside preserved packages and snapshots')
    before = inventory(package)
    assert before['seal.json'] == args.seal_sha256
    seal = json.loads((package/'seal.json').read_text())
    expected = {entry['path']: entry['sha256'] for entry in seal['files']}
    expected['seal.json'] = args.seal_sha256
    assert before == expected, 'Seal does not cover the actual package bytes'
    directories_before = sorted(str(p.relative_to(package)) for p in package.rglob('*') if p.is_dir())
    assert directories_before == seal['directories']
    for entry in seal['files']:
        assert (package/entry['path']).stat().st_size == entry['bytes']
    output.mkdir(parents=True, exist_ok=True)
    report = {'package': str(package), 'seal_sha256': args.seal_sha256,
              'package_files': len(before), 'before_sha256': fingerprint(before),
              'provider_calls': 0, 'source_opened_in_native_library': False}
    result = None
    try:
        with tempfile.TemporaryDirectory(prefix='actforgoa-package-check-') as temporary:
            scratch = Path(temporary)
            for name in ('data', 'service'):
                subprocess.run(['cp', '-cR', str(package/name), str(scratch/name)], check=True)
            payload = {k: v for k, v in before.items() if k.startswith(('data/', 'service/'))}
            assert inventory(scratch) == payload
            environment = {k: v for k, v in os.environ.items()
                           if not k.startswith(('RESEARCH_', 'OPENAI_', 'OPENROUTER_', 'DASHSCOPE_'))}
            environment['PYTHONDONTWRITEBYTECODE'] = '1'
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('runtime_check.py')),
                                     '--data-root', str(scratch/'data'), '--service-root', str(scratch/'service'),
                                     '--output', str(output/'packaged-runtime.json')], env=environment, check=False)
            changed = inventory(scratch)
            report['child_exit_code'] = result.returncode
            report['working_copy_changed_files'] = sorted(k for k in payload.keys() | changed.keys()
                                                        if payload.get(k) != changed.get(k))
        report['owned_temporary_copy_removed'] = True
    finally:
        after = inventory(package)
        report['after_sha256'] = fingerprint(after)
        directories_after = sorted(str(p.relative_to(package)) for p in package.rglob('*') if p.is_dir())
        report['package_unchanged_after_child_exit'] = before == after and directories_before == directories_after
        (output/'packaged-runtime-preservation.json').write_text(json.dumps(report, indent=2)+'\n')
        if not report['package_unchanged_after_child_exit']:
            raise RuntimeError('Sealed package changed; stop and inspect preservation evidence')
    print(json.dumps(report))
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
