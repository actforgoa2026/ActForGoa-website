"""Run the offline evidence gate on a disposable copy, then verify its source.

Zvec 0.8.0 may rewrite HNSW timestamps on close even with read_only=True.
The parent process must never open Zvec. It checks source bytes after the child
has exited, including native destructors. No providers or usage ledgers are used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PARTS = ('.research-index', 'corpus/raw')
PRESERVATION_MARKERS = ('snapshot-files.json', 'seal.json')


def is_preserved(path):
    path = Path(path).resolve()
    return any((parent/marker).is_file() for parent in (path, *path.parents)
               for marker in PRESERVATION_MARKERS)


def inventory(root):
    files = {}
    for name in PARTS:
        directory = root/name
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError('Expected an ordinary research data directory: '+name)
        for path in sorted(directory.rglob('*')):
            if path.is_symlink():
                raise ValueError('Research data cannot contain symlinks')
            if path.is_file():
                with path.open('rb') as handle:
                    files[str(path.relative_to(root))] = hashlib.file_digest(handle, 'sha256').hexdigest()
    return files


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source, output = args.data_root.resolve(), args.output.resolve()
    if output.is_relative_to(source) or is_preserved(output):
        parser.error('Write evaluation reports outside the preserved data directory')
    before = inventory(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path = output.with_suffix('.preservation.json')
    report = {'source': str(source), 'source_files': len(before), 'source_before_sha256': fingerprint(before),
              'provider_calls': 0, 'usage_database_created': False,
              'method': 'Copy index and originals only; run offline evidence gate in a subprocess; hash source after child exit. Do not open the preservation source through Library/Zvec.'}
    child = None
    try:
        with tempfile.TemporaryDirectory(prefix='actforgoa-retrieval-') as temporary:
            scratch = Path(temporary)/'data'
            for name in PARTS:
                target = scratch/name
                target.parent.mkdir(parents=True, exist_ok=True)
                if sys.platform == 'darwin':
                    subprocess.run(['cp', '-cR', str(source/name), str(target)], check=True)
                else:
                    shutil.copytree(source/name, target)
            assert inventory(scratch) == before, 'Working copy differs before evaluation'
            # Credentials are unnecessary for this offline entry point.
            environment = {k: v for k, v in os.environ.items()
                           if not k.startswith(('OPENAI_', 'OPENROUTER_', 'DASHSCOPE_', 'RESEARCH_'))}
            child = subprocess.run([sys.executable, str(ROOT/'scripts/evaluate_retrieval_evidence.py'),
                                    '--data-root', str(scratch), '--cases', str(args.cases.resolve()),
                                    '--output', str(output)], env=environment, check=False)
            after_child = inventory(scratch)
            report['child_exit_code'] = child.returncode
            report['working_copy_changed_files'] = sorted(k for k in before.keys() | after_child.keys()
                                                        if before.get(k) != after_child.get(k))
            assert not (scratch/'.research-usage').exists()
    finally:
        after = inventory(source)
        report['source_after_sha256'] = fingerprint(after)
        report['source_unchanged_after_child_exit'] = before == after
        report['source_changed_files'] = sorted(k for k in before.keys() | after.keys()
                                               if before.get(k) != after.get(k))
        report_path.write_text(json.dumps(report, indent=2)+'\n')
        if before != after:
            raise RuntimeError('Preservation source changed; stop and inspect '+str(report_path))
    print(json.dumps({'source_unchanged': True, 'source_files': len(before),
                      'working_copy_changed_files': report['working_copy_changed_files']}))
    return child.returncode


if __name__ == '__main__':
    sys.exit(main())
