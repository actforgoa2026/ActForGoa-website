"""Run this bounded offline experiment only on a disposable APFS copy."""
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
from scripts.evaluate_research_copy import inventory, fingerprint, is_preserved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--task', choices=['capture_sources', 'capture_assessment_sources', 'evaluate', 'evaluate_development'], required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if output.is_relative_to(source) or is_preserved(output) or output.is_relative_to(Path.home()/'Documents/ActForGoa Recovery'):
        parser.error('Reports must remain outside preservation roots')
    if output.exists() or output.with_suffix('.preservation.json').exists():
        parser.error('Reports are immutable; use a fresh output path')
    before = inventory(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {'source': str(source), 'source_files': len(before), 'before_sha256': fingerprint(before),
              'native_source_opens': 0, 'provider_calls': 0, 'task': args.task}
    result = None
    try:
        with tempfile.TemporaryDirectory(prefix='actforgoa-passage-selection-') as temporary:
            scratch = Path(temporary)/'data'
            for name in ('.research-index', 'corpus/raw'):
                target = scratch/name
                target.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(['cp', '-cR', str(source/name), str(target)], check=True)
            assert inventory(scratch) == before
            environment = {k: v for k, v in os.environ.items()
                           if not k.startswith(('RESEARCH_', 'OPENAI_', 'OPENROUTER_', 'DASHSCOPE_', 'ANTHROPIC_'))}
            environment['PYTHONDONTWRITEBYTECODE'] = '1'
            result = subprocess.run([sys.executable, str(Path(__file__).with_name(args.task+'.py')),
                                     '--data-root', str(scratch), '--output', str(output)],
                                    env=environment, check=False)
            report['child_exit_code'] = result.returncode
            after_child = inventory(scratch)
            report['scratch_changes'] = sorted(k for k in before.keys() | after_child.keys()
                                               if before.get(k) != after_child.get(k))
            assert not (scratch/'.research-usage').exists()
        report['owned_copy_removed'] = True
    finally:
        after = inventory(source)
        report['after_sha256'] = fingerprint(after)
        report['source_unchanged_after_child_exit'] = before == after
        output.with_suffix('.preservation.json').write_text(json.dumps(report, indent=2)+'\n')
        if before != after:
            raise RuntimeError('Preservation source changed')
    print(json.dumps(report))
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
