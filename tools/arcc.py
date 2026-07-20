"""ARCC / ARC archive codec for Monster Hunter Stories (2024 PC port).

The game packs its resources in Capcom MT Framework .arc archives. The 2024 PC
release encrypts them (magic 'ARCC'); some are stored plain (magic 'ARC\\0').

Encryption format (recovered by analysis, compatible with MHS2 community tooling):
  - Blowfish-ECB, key b"QZHaM;-5:)dV#"
  - A 4-byte-chunk endianness reversal is applied BOTH before and after the
    Blowfish pass (a quirk of how the engine feeds the cipher).
  - Each entry's payload is individually zlib-compressed.
  - File extensions are stored as a jamcrc hash, not text.

Entry table (after the 8-byte header), one 144-byte record per file:
  - 128 bytes: null-padded path (backslash-separated, no extension)
  - u32 extension hash, u32 compressed size, u32 (uncompressed size & flags),
    u32 offset (absolute in the original file; subtract 8 for the header)

Usage:
  python arcc.py list  <archive.arc> [substring]
  python arcc.py find  <glob>        [substring]   # sweep many archives
  python arcc.py extract <archive.arc> <substring> <out_dir>

Requires: pycryptodome  (pip install pycryptodome)
"""
import glob
import os
import struct
import sys
import zlib

from Crypto.Cipher import Blowfish

KEY = b"QZHaM;-5:)dV#"
_cipher = Blowfish.new(KEY, Blowfish.MODE_ECB)


def _endian_swap(data: bytes) -> bytes:
    """Reverse each aligned 4-byte chunk. Applied before and after Blowfish."""
    return b"".join(data[i:i + 4][::-1] for i in range(0, len(data), 4))


def _decrypt_body(raw: bytes) -> bytes:
    return _endian_swap(_cipher.decrypt(_endian_swap(raw)))


def read_entries(path):
    """Return list of (name, ext_hash, comp_size, uncomp_size, offset)."""
    with open(path, "rb") as f:
        magic = f.read(4)
        _version, file_count = struct.unpack("<HH", f.read(4))
        rest = f.read()
    if magic == b"ARCC":
        dec = _decrypt_body(rest)
    elif magic == b"ARC\x00":
        dec = rest
    else:
        raise ValueError(f"not an arc archive: {magic!r}")

    entries = []
    off = 0
    for _ in range(file_count):
        name = bytes(b for b in dec[off:off + 128] if b).decode("utf-8", "replace")
        off += 128
        ext_hash, comp, uncomp, eoff = struct.unpack_from("<IIII", dec, off)
        off += 16
        entries.append((name, ext_hash, comp, uncomp & 0xFFFFFF, eoff))
    return entries, dec


def list_archive(path, needle=None):
    entries, _ = read_entries(path)
    names = [e[0] for e in entries]
    if needle is None:
        return names
    return [n for n in names if needle.lower() in n.lower()]


def extract(path, needle, out_dir):
    entries, dec = read_entries(path)
    extracted = []
    for name, _ext, comp, _uncomp, eoff in entries:
        if needle.lower() not in name.lower():
            continue
        blob = dec[eoff - 8: eoff - 8 + comp]  # offsets are relative to the raw file
        try:
            data = zlib.decompress(blob)
        except zlib.error:
            data = blob  # some small entries are stored uncompressed
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, name.replace("\\", "_") + ".bin")
        with open(out_path, "wb") as g:
            g.write(data)
        extracted.append((name, len(data), out_path))
    return extracted


def _cli(argv):
    if len(argv) < 2:
        print(__doc__)
        return
    cmd = argv[1]
    if cmd == "list":
        needle = argv[3] if len(argv) > 3 else None
        for n in list_archive(argv[2], needle):
            print(n)
    elif cmd == "find":
        needle = argv[3] if len(argv) > 3 else None
        total = 0
        for p in sorted(glob.glob(argv[2], recursive=True)):
            try:
                hits = list_archive(p, needle)
            except Exception:
                continue
            if needle is not None and not hits:
                continue
            total += 1
            print(f"\n=== {p} ===")
            for n in hits:
                print(f"  {n}")
        print(f"\n=== {total} archive(s) matched ===")
    elif cmd == "extract":
        for name, size, out in extract(argv[2], argv[3], argv[4]):
            print(f"extracted: {name} ({size} bytes) -> {out}")
    else:
        print(__doc__)


if __name__ == "__main__":
    _cli(sys.argv)
