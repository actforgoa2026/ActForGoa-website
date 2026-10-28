"""Recover this one recorded index file to a NEW path, guarded by whole-file hashes.

Incident-specific forensic reconstruction, not a general index repair tool.
Never overwrite the accepted snapshot or its manifests. Never open the result
through Zvec; verify it with ordinary byte reads and use disposable copies.
"""
import argparse
import hashlib
from pathlib import Path
import struct

CHANGED = '4a39df4854b045f73cd9bc78bcbbf03ad52f3ca671ee18f2b4f19286ae017a56'
ACCEPTED = '4c8c86b4cf9768ef21d237201218e6b05369d2f91b92729ce7553a6c7c973185'


def crc32c(data):
    crc = 0  # Ailego uses raw CRC32C with seed zero and no final complement.
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x82F63B78 if crc & 1 else 0)
    return crc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or any((p/'snapshot-files.json').exists() for p in output.parents):
        parser.error('Use a new file outside all preservation snapshots')
    blob = bytearray(args.input.read_bytes())
    assert hashlib.sha256(blob).hexdigest() == CHANGED, 'Unrecognized input: do not patch'
    footer = 1064832
    old_crc = struct.unpack_from('<I', blob, footer)[0]
    struct.pack_into('<I', blob, footer, 0)
    assert crc32c(blob[footer:footer+128]) == old_crc
    # The accepted whole-file checksum verifies the recovered timestamp; it is
    # not an approximate date repair. No graph, vector or document bytes change.
    for offset in [1064880, 1081440]:
        struct.pack_into('<Q', blob, offset, 1793084588)  # 2026-10-27T07:03:08Z
    struct.pack_into('<I', blob, footer, crc32c(blob[footer:footer+128]))
    assert hashlib.sha256(blob).hexdigest() == ACCEPTED, 'Exact historical checksum not recovered'
    with output.open('xb') as handle:
        handle.write(blob)
    print(ACCEPTED)


if __name__ == '__main__':
    main()
