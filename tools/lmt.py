"""LMT scale parser + patcher for Monster Hunter Stories (2024 PC port).

The per-monstie "chibi" retarget data lives in loose files at
    nativeDX11x64\\mod\\scale\\mo\\mo###\\mo###_body.lmt
in Capcom's MT Framework LMT (motion/bone-track) format. These files hold a
static per-bone SCALE channel; multiplying it uniformly makes the rendered
Monstie bigger (or smaller) in both overworld and battle. Edits are picked up
live by the running game.

LMT layout (the subset we need):
  header: 'LMT\\0' (4s) + version (H) + entry_count (H) + unkn (8s)   = 16 bytes
  then entry_count x uint64 absolute offsets to 96-byte AnimationBlocks
  AnimationBlock: bone_paths_offset (Q), bone_path_count (i), frame_count (i),
                  loop_frame (i), ...
  BonePath (48 bytes): buffer_type/usage/joint_type/unkn (4B), bone_id (i),
                  weight (f), buffer_size (i), buffer_offset (q),
                  reference_frame (4f), bounds_offset (q)
  usage: 0/3 = rotation, 1/4 = position, 2 = SCALE
         (for static scale: frame_count == 1, buffer_size == 0, and the value
          lives directly in reference_frame X/Y/Z)

Some offset-table slots point at overlapping / garbage data, so we dedupe by
bone_paths_offset and sanity-bound the counts.

Usage:
  python lmt.py rank  <dir with *_body.lmt>      # rank species by retarget strength
  python lmt.py scale <file.lmt> <factor>        # multiply every SCALE bone
"""
import glob
import os
import struct
import sys

MAGIC = b"LMT\x00"


def _iter_scale_bones(data):
    """Yield (record_offset, bone_id, (sx, sy, sz)) for every static SCALE bone."""
    if data[:4] != MAGIC:
        return
    _version, entry_count = struct.unpack_from("<HH", data, 4)
    offsets = struct.unpack_from(f"<{entry_count}Q", data, 16)
    seen = set()
    for off in offsets:
        if off == 0 or off + 96 > len(data):
            continue
        bp_off, bp_count = struct.unpack_from("<Qi", data, off)
        if bp_off == 0 or bp_off in seen or not (0 < bp_count <= 512):
            continue
        if bp_off + bp_count * 48 > len(data):
            continue
        seen.add(bp_off)
        for i in range(bp_count):
            rec = bp_off + i * 48
            usage = data[rec + 1]
            if usage != 2:
                continue
            bone_id = struct.unpack_from("<i", data, rec + 4)[0]
            sx, sy, sz, _sw = struct.unpack_from("<4f", data, rec + 24)
            yield rec, bone_id, (sx, sy, sz)


def parse_scale_bones(path):
    """bone_id -> (sx, sy, sz), first-seen value per bone."""
    with open(path, "rb") as f:
        data = f.read()
    bones = {}
    for _rec, bone_id, val in _iter_scale_bones(data):
        bones.setdefault(bone_id, val)
    return bones


def summarize(bones):
    vals = [sum(v) / 3.0 for v in bones.values() if all(0.01 < c < 100 for c in v)]
    if not vals:
        return None
    return {
        "n_bones": len(vals),
        "mean": sum(vals) / len(vals),
        "min": min(vals),
        "max": max(vals),
        "spread": max(vals) / min(vals) if min(vals) > 0 else float("inf"),
    }


def patch_scale(path, factor, overrides=None):
    """Multiply every SCALE bone's reference_frame by `factor` in place.
    `overrides` maps bone_id -> its own multiplier (applied instead of factor).
    Only plausible values (0.001 < v < 100) are touched. Returns count patched.
    """
    overrides = overrides or {}
    with open(path, "rb") as f:
        data = bytearray(f.read())
    n = 0
    for rec, bone_id, (sx, sy, sz) in _iter_scale_bones(bytes(data)):
        if not all(0.001 < c < 100 for c in (sx, sy, sz)):
            continue
        m = overrides.get(bone_id, factor)
        struct.pack_into("<3f", data, rec + 24, sx * m, sy * m, sz * m)
        n += 1
    with open(path, "wb") as f:
        f.write(data)
    return n


def _cli(argv):
    if len(argv) < 2:
        print(__doc__)
        return
    if argv[1] == "rank":
        rows = []
        for path in sorted(glob.glob(os.path.join(argv[2], "*", "*_body.lmt"))):
            name = os.path.basename(path).replace("_body.lmt", "")
            rows.append((name, summarize(parse_scale_bones(path))))
        rows.sort(key=lambda r: (r[1]["spread"] if r[1] else 0), reverse=True)
        print(f"{'species':10} {'bones':>5} {'mean':>6} {'min':>6} {'max':>6} {'spread':>7}")
        for name, s in rows:
            if s is None:
                print(f"{name:10} (no scale tracks)")
            else:
                print(f"{name:10} {s['n_bones']:>5} {s['mean']:>6.3f} "
                      f"{s['min']:>6.3f} {s['max']:>6.3f} {s['spread']:>7.2f}")
    elif argv[1] == "scale":
        path, factor = argv[2], float(argv[3])
        print(f"{path}: patched {patch_scale(path, factor)} scale bones x{factor}")
    else:
        print(__doc__)


if __name__ == "__main__":
    _cli(sys.argv)
