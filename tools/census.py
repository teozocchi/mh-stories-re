"""Archive census: map the game's monster resource-ID space.

Sweeps every .arc under a directory, reads each entry table (via arcc.py, no
payload decompression), and records which mo### folders reference which fi/em
variants -- exposing the sparse, self-consistent ID space and any subspecies
that live under a different folder number than their variant.

Usage:
  python census.py <path-to>/nativeDX11x64/archive
"""
import collections
import glob
import re
import sys

import arcc

# ...mo\mo346\fi346... or em346 etc. -- captures (folder_num, prefix, variant_num)
PATH_RE = re.compile(r"mo[\\/]mo(\d{3})[\\/]([a-z]{2,4})(\d{3})", re.IGNORECASE)


def run(archive_root):
    folder_variants = collections.defaultdict(set)
    mismatches = collections.defaultdict(set)
    n_arcs = n_err = 0

    for path in glob.iglob(archive_root + "/**/*.arc", recursive=True):
        try:
            names = arcc.list_archive(path)
        except Exception:
            n_err += 1
            continue
        n_arcs += 1
        for name in names:
            for m in PATH_RE.finditer(name):
                folder, prefix, num = m.group(1), m.group(2).lower(), m.group(3)
                folder_variants[folder].add((prefix, num))
                if folder != num:
                    mismatches[(folder, prefix, num)].add(path)

    print(f"archives scanned: {n_arcs}  (errors: {n_err})")
    print(f"distinct mo folders referenced: {len(folder_variants)}\n")
    print("=== folder -> variants ===")
    for folder in sorted(folder_variants):
        vs = " ".join(f"{p}{n}" for p, n in sorted(folder_variants[folder]))
        flag = "   <-- cross-numbered" if any(n != folder for _p, n in folder_variants[folder]) else ""
        print(f"mo{folder}: {vs}{flag}")
    print("\n=== cross-numbered variants (folder != variant) ===")
    if not mismatches:
        print("(none -- every variant number matches its folder number)")
    for (folder, prefix, num) in sorted(mismatches):
        print(f"mo{folder} contains {prefix}{num}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    else:
        run(sys.argv[1])
