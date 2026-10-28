"""Pinning tests and optional consumed-source replay; no network requests."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import source_context_probe as probe


class InputPinningTests(unittest.TestCase):
    def test_tampered_or_symlink_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = b'{"pages": []}'
            manifest = root / 'pins.json'
            manifest.write_text(json.dumps({'files': {'capture.json': hashlib.sha256(raw).hexdigest()}}))
            capture = root / 'capture.json'
            capture.write_bytes(raw)
            with patch.object(probe, 'MANIFEST', manifest):
                self.assertEqual(probe.load_inputs(root)[1]['capture.json'], {'pages': []})
                capture.write_bytes(raw + b' ')
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    probe.load_inputs(root)
                capture.unlink()
                target = root / 'target.json'
                target.write_bytes(raw)
                capture.symlink_to(target)
                with self.assertRaisesRegex(ValueError, 'symlink'):
                    probe.load_inputs(root)

    @unittest.skipUnless(os.getenv('AFG_SOURCE_CONTEXT_INPUTS'), 'explicit consumed-source packet not supplied')
    def test_consumed_sources_remain_counterexamples(self):
        result = probe.run(Path(os.environ['AFG_SOURCE_CONTEXT_INPUTS']))
        cases = {c['id']: c for c in result['cases']}
        self.assertEqual(len(cases), 7)
        for identifier, case in cases.items():
            self.assertEqual(case['checks']['semantic'], 'not_assessed')
            self.assertEqual(case['checks']['release'], 'hold')
            self.assertEqual(case['checks']['mechanical'], 'rejected' if identifier == 'lake-orphan' else 'valid')
            for span in case['pack']['spans']:
                original = case['pack']['passages'][span['passage']]
                self.assertTrue(original[span['start']:span['end']])
        self.assertEqual(cases['lake-orphan']['candidate']['supports'], ['lake-functions'])
        self.assertIn('104', cases['bio-distorted']['candidate']['text'])
        self.assertIn('105 Oriolidae', cases['bio-preserving']['pack']['passages']['66'])


if __name__ == '__main__':
    unittest.main()
