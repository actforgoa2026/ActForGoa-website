"""Explicit local input, stdout or exclusive atomic output; no directory scanning."""

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

from .adapter import error, link, rejected


def publish(destination, raw):
    """Only publish a complete file, without replacing any existing path."""
    destination = Path(destination)
    fd, temporary = tempfile.mkstemp(prefix='.capture-review-', dir=destination.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, destination, follow_symlinks=False)
    finally:
        os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output is not None and os.path.lexists(args.output):
            raise FileExistsError()
        try:
            raw = args.input.read_bytes()
        except (OSError, ValueError):
            result, code = rejected([error('IO_FAILURE', ['input'])]), 2
        else:
            result, code = link(raw)
        serialized = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
        if code == 2:
            sys.stderr.buffer.write(serialized)
        elif args.output is None:
            sys.stdout.buffer.write(serialized)
        else:
            publish(args.output, serialized)
        return code
    except FileExistsError:
        result = rejected([error('OUTPUT_EXISTS', ['output'])])
    except (OSError, ValueError):
        result = rejected([error('IO_FAILURE', ['output'])])
    sys.stderr.write(json.dumps(result, ensure_ascii=False) + '\n')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
