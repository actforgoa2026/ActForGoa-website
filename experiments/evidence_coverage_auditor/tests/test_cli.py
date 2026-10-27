from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from experiments.evidence_coverage_auditor.profile import canonical

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = json.loads((Path(__file__).parent / "fixtures" / "examples.json").read_text(encoding="utf-8"))["examples"][0]


class CliTests(unittest.TestCase):
    def cli(self, *args, raw=None):
        # -S disables site packages: this command must work with the standard library alone.
        return subprocess.run([sys.executable, "-S", "-m", "experiments.evidence_coverage_auditor", *args],
                              cwd=ROOT, input=raw, capture_output=True, check=False, timeout=10)

    def test_stdin_stdout_and_report_only_output(self):
        r = self.cli("-", raw=canonical(EXAMPLE["envelope"]))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr, b"")
        self.assertEqual(json.loads(r.stdout), EXAMPLE["author_expected_report"])

    def test_parse_and_component_failures_exit_one(self):
        r = self.cli("-", raw=b'{"duplicate":1,"duplicate":2}')
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["global_scope"], "parse")
        e = deepcopy(EXAMPLE["envelope"])
        e["candidate"]["claims"][0]["supports"][0]["unit_id"] = "unit:absent"
        r = self.cli("-", raw=canonical(e))
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["status"], "component_issues")

    def test_file_output_and_overwrite_refusal(self):
        with TemporaryDirectory() as temp:
            source, target = Path(temp) / "input.json", Path(temp) / "report.json"
            source.write_bytes(canonical(EXAMPLE["envelope"]))
            r = self.cli(str(source), "--output", str(target))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout, b"")
            saved = target.read_bytes()
            self.assertEqual(json.loads(saved), EXAMPLE["author_expected_report"])
            r = self.cli(str(source), "--output", str(target))
            self.assertEqual(r.returncode, 2)
            self.assertIn(b"no overwrite", r.stderr)
            self.assertEqual(target.read_bytes(), saved)
            r = self.cli(str(source), "--output", str(source))
            self.assertEqual(r.returncode, 2)
            self.assertEqual(source.read_bytes(), canonical(EXAMPLE["envelope"]))

    def test_output_symlinks_are_not_followed_or_created(self):
        with TemporaryDirectory() as temp:
            target, link = Path(temp) / "target", Path(temp) / "link"
            link.symlink_to(target)
            r = self.cli("-", "--output", str(link), raw=canonical(EXAMPLE["envelope"]))
            self.assertEqual(r.returncode, 2)
            self.assertFalse(target.exists())
            target.write_bytes(b"synthetic prior artifact")
            r = self.cli("-", "--output", str(link), raw=canonical(EXAMPLE["envelope"]))
            self.assertEqual(r.returncode, 2)
            self.assertEqual(target.read_bytes(), b"synthetic prior artifact")

    def test_io_error_does_not_emit_invented_audit(self):
        with TemporaryDirectory() as temp:
            r = self.cli(str(Path(temp) / "absent"))
            self.assertEqual(r.returncode, 2)
            self.assertEqual(r.stdout, b"")
            self.assertNotIn(temp.encode(), r.stderr)


if __name__ == "__main__":
    unittest.main()
