import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ..__main__ import publish
from ..adapter import error, rejected

ROOT = Path(__file__).resolve().parents[3]


def invoke(source, output=None):
    args = [sys.executable, '-m', 'experiments.capture_review_adapter', str(source)]
    if output is not None:
        args.extend(['--output', str(output)])
    return subprocess.run(args, cwd=ROOT, capture_output=True, timeout=30)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = self.directory / 'input.json'
        self.source.write_bytes(b'{"a":1,"a":2}')
        self.output = self.directory / 'output.json'

    def test_complete_rejection_stdout(self):
        run = invoke(self.source)
        self.assertEqual(1, run.returncode)
        self.assertEqual(b'', run.stderr)
        self.assertEqual(rejected([error('INPUT_SHAPE', [])]), json.loads(run.stdout))

    def test_complete_rejection_file(self):
        run = invoke(self.source, self.output)
        self.assertEqual(1, run.returncode)
        self.assertEqual((b'', b''), (run.stdout, run.stderr))
        self.assertEqual(rejected([error('INPUT_SHAPE', [])]), json.loads(self.output.read_bytes()))
        self.assertEqual(0o600, self.output.stat().st_mode & 0o777)

    def test_existing_and_dangling_symlink_are_untouched(self):
        for dangling in [False, True]:
            with self.subTest(dangling=dangling):
                if dangling:
                    self.output.symlink_to(self.directory / 'missing-target')
                else:
                    self.output.write_bytes(b'original')
                run = invoke(self.directory / 'missing-input', self.output)
                self.assertEqual(2, run.returncode)
                self.assertEqual(b'', run.stdout)
                self.assertEqual(rejected([error('OUTPUT_EXISTS', ['output'])]), json.loads(run.stderr))
                if dangling:
                    self.assertTrue(self.output.is_symlink())
                    self.assertFalse((self.directory / 'missing-target').exists())
                else:
                    self.assertEqual(b'original', self.output.read_bytes())
                self.output.unlink()

    def test_input_output_same_path_is_untouched(self):
        before = self.source.read_bytes()
        run = invoke(self.source, self.source)
        self.assertEqual(2, run.returncode)
        self.assertEqual(before, self.source.read_bytes())

    def test_missing_input_operational_failure(self):
        run = invoke(self.directory / 'missing', self.output)
        self.assertEqual(2, run.returncode)
        self.assertEqual(b'', run.stdout)
        self.assertEqual(rejected([error('IO_FAILURE', ['input'])]), json.loads(run.stderr))
        self.assertFalse(self.output.exists())

    def test_missing_output_parent_operational_failure(self):
        run = invoke(self.source, self.directory / 'absent' / 'output.json')
        self.assertEqual(2, run.returncode)
        self.assertEqual(b'', run.stdout)
        self.assertEqual(rejected([error('IO_FAILURE', ['output'])]), json.loads(run.stderr))

    def test_no_replace_under_race(self):
        original_link = os.link
        def race(source, destination, **kwargs):
            Path(destination).write_bytes(b'competing completed result')
            return original_link(source, destination, **kwargs)
        with patch('experiments.capture_review_adapter.__main__.os.link', side_effect=race):
            with self.assertRaises(FileExistsError):
                publish(self.output, b'our completed result')
        self.assertEqual(b'competing completed result', self.output.read_bytes())
        self.assertEqual([], list(self.directory.glob('.capture-review-*')))

    def test_fsync_failure_publishes_nothing(self):
        with patch('experiments.capture_review_adapter.__main__.os.fsync', side_effect=OSError('synthetic failure')):
            with self.assertRaises(OSError):
                publish(self.output, b'complete result')
        self.assertFalse(self.output.exists())
        self.assertEqual([], list(self.directory.glob('.capture-review-*')))

    def test_result_complete_before_publication(self):
        original_link = os.link
        payload = b'{"complete":true}\n'
        def inspect(source, destination, **kwargs):
            self.assertFalse(Path(destination).exists())
            self.assertEqual(payload, Path(source).read_bytes())
            return original_link(source, destination, **kwargs)
        with patch('experiments.capture_review_adapter.__main__.os.link', side_effect=inspect):
            publish(self.output, payload)
        self.assertEqual(payload, self.output.read_bytes())
        self.assertEqual([], list(self.directory.glob('.capture-review-*')))
