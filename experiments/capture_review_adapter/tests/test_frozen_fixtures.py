"""Opt-in tests of the approved local packet; raw captures stay outside Git."""

import json
import os
from pathlib import Path
import tempfile
import unittest

from ..adapter import PACKET_SHA
from ..profile import sha
from .test_cli import invoke

PACKET = os.environ.get('AFG_CAPTURE_REVIEW_PACKET')


@unittest.skipUnless(PACKET, 'Set AFG_CAPTURE_REVIEW_PACKET to the frozen approved local packet')
class FrozenFixtureTests(unittest.TestCase):
    def test_all_nineteen_exact_outputs_and_input_integrity(self):
        packet = Path(PACKET)
        manifest_path = packet / 'manifest.json'
        self.assertEqual(PACKET_SHA, sha(manifest_path.read_bytes()))
        manifest = json.loads(manifest_path.read_bytes())
        # The pinned manifest, not an editable environment catalog, bounds reads.
        audited = {manifest_path: PACKET_SHA}
        for item in manifest['outputs']:
            path = packet / item['path']
            self.assertEqual(item['sha256'], sha(path.read_bytes()))
            audited[path] = item['sha256']
        for item in manifest['inputs']:
            path = Path(item['path'])
            self.assertEqual(item['file_sha256'], sha(path.read_bytes()))
            audited[path] = item['file_sha256']
        cases = json.loads((packet / 'fixtures.json').read_bytes())['cases']
        self.assertEqual(19, len(cases))
        for case in cases:
            with self.subTest(fixture=case['id']), tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)
                source = folder / 'input.json'
                source.write_text(json.dumps(case['input'], ensure_ascii=False), encoding='utf-8')
                expected = case.get('expected_result')
                if expected is None:
                    expected = json.loads((packet / case['expected_result_file']).read_bytes())
                operation = case.get('operation')
                if operation:
                    output = folder / operation['output_path']
                    output.write_bytes(operation['preexisting_bytes_utf8'].encode())
                    run = invoke(source, output)
                    self.assertEqual(operation['expected_stdout_utf8'].encode(), run.stdout)
                    self.assertEqual(operation['expected_destination_bytes_utf8'].encode(), output.read_bytes())
                    self.assertEqual(expected, json.loads(run.stderr))
                else:
                    run = invoke(source)
                    self.assertEqual(b'', run.stderr)
                    self.assertEqual(expected, json.loads(run.stdout))
                self.assertEqual(case['expected_exit'], run.returncode)
        for path, digest in audited.items():
            self.assertEqual(digest, sha(path.read_bytes()), str(path))
