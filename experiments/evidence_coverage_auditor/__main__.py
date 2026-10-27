"""Read one explicitly named JSON file (or stdin); never follow its locators."""

import argparse
import json
from pathlib import Path
import sys

from .auditor import audit_bytes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit supplied synthetic evidence mechanics only.")
    parser.add_argument("input", help="Envelope JSON path, or - for stdin")
    parser.add_argument("--output", help="New report file; existing paths are never overwritten")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.buffer.read() if args.input == "-" else Path(args.input).read_bytes()
        report = audit_bytes(raw)
        text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            # Exclusive creation also refuses symlinks, including dangling ones.
            with Path(args.output).open("x", encoding="utf-8") as output:
                output.write(text)
        else:
            sys.stdout.buffer.write(text.encode("utf-8"))
    except FileExistsError:
        print("Report path exists; no overwrite performed.", file=sys.stderr)
        return 2
    except OSError:
        print("Cannot read input or write report.", file=sys.stderr)
        return 2
    except RecursionError:
        print("Input exceeds this interpreter's nesting capacity; no audit completed.", file=sys.stderr)
        return 2
    return 0 if report["status"] == "mechanically_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
