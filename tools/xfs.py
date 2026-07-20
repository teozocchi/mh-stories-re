"""Minimal MT-Framework XFS table parser for MHST 2024 (table.arc contents).

Layout learned empirically from table\\monster_book_data:
- 0x00 header: magic 'XFS\\0', u16 ver, u16 type, u32 entryHint, u32 pad,
  u32 classCount, u32 defSize (data begins at 0x18+defSize), ...
- 0x40: root class prop defs (3 x 48B: mVersion, mpArray, mQuality),
  then per extra class: 16B header (hash u32, pad u32, propCount u32, pad u32)
  followed by propCount x 48B prop defs.
- prop def: u64 nameOff (add 0x18 for file offset), u8 type, u8 flags, u16 size.
- prop types seen: 3=bool(1B) 4=u8 5=u16 6=u32 0xc=u32 0xe=cstring 2=f32? etc.
  Non-string values read as size-byte little-endian ints (or floats if type==2/0xf?).
- data stream: root prelude, then array elements: u32 tag, u32 size
  (next element at tagPos+4+size), u32 unk, then per prop: u32 count(==1),
  value (strings null-terminated inline).
"""
import struct

STRING_TYPES = {14}
FLOAT_TYPES = {2, 12}


def parse_defs(data):
    """Return (classes, strings_start). classes = list of prop lists [(name,type,size)]."""
    def cstr(off):
        end = data.index(b'\0', off)
        return data[off:end].decode('ascii', 'replace')

    class_count = struct.unpack_from('<I', data, 0x10)[0]
    def_size = struct.unpack_from('<I', data, 0x14)[0]
    data_start = 0x18 + def_size

    def read_prop(off):
        name_off = struct.unpack_from('<Q', data, off)[0]
        t, fl = data[off + 8], data[off + 9]
        sz = struct.unpack_from('<H', data, off + 10)[0]
        return (cstr(name_off + 0x18), t, fl, sz)

    classes = []
    off = 0x40
    # root class: 3 props, no header
    root = [read_prop(off + i * 0x30) for i in range(3)]
    classes.append(root)
    off += 3 * 0x30
    for _ in range(class_count - 1):
        prop_count = struct.unpack_from('<I', data, off + 8)[0]
        off += 0x10
        props = [read_prop(off + i * 0x30) for i in range(prop_count)]
        classes.append(props)
        off += prop_count * 0x30
    return classes, data_start


def parse_element(data, pos, props):
    """Parse one array element at pos; returns (record dict, next_pos)."""
    size = struct.unpack_from('<I', data, pos + 4)[0]
    p = pos + 12
    rec = {}
    for name, t, fl, sz in props:
        cnt = struct.unpack_from('<I', data, p)[0]
        p += 4
        if cnt != 1:
            raise ValueError(f'count!=1 for {name} at {hex(p)}: {cnt}')
        if t in STRING_TYPES:
            e = data.index(b'\0', p)
            rec[name] = data[p:e]
            p = e + 1
        elif t in FLOAT_TYPES and sz == 4:
            rec[name] = struct.unpack_from('<f', data, p)[0]
            p += 4
        else:
            rec[name] = int.from_bytes(data[p:p + sz], 'little')
            p += sz
    return rec, pos + 4 + size


def parse_table(data, record_class=-1, scan_window=0x200):
    """Parse all elements of the record class (largest/last by default).
    Finds the first element by scanning after data_start for a position where
    a full chain of successful parses reaches near EOF."""
    classes, data_start = parse_defs(data)
    props = classes[record_class]
    best = []
    for start in range(data_start, min(len(data), data_start + scan_window)):
        recs = []
        pos = start
        try:
            while pos + 16 < len(data):
                rec, pos = parse_element(data, pos, props)
                recs.append(rec)
        except Exception:
            pass
        if len(recs) > len(best) and len(data) - pos < 0x40:
            best = recs
            break
    return best, classes
