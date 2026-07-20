# Monster Hunter Stories — Monstie Scale (Reverse Engineering)

Reverse-engineering the 2024 PC port of *Monster Hunter Stories* to do something
the community had considered impossible for eight years: make your hatched
Monsties render at their full, un-shrunk size — in the overworld **and** in battle.

The result is the first known working size modification for any game in the
series. This repo contains the **tooling and the full technical writeup**; it
deliberately ships **no game assets** (see [Legal](#legal)). Everything is
reproducible from your own copy of the game.

> 📖 **The full story — every dead end, every wrong turn, and how it was finally
> cracked — is in [THE_JOURNEY.md](THE_JOURNEY.md).** It's the interesting part.

---

## The problem

Hatched Monsties are rendered at a shrunken, "chibi" scale versus wild monsters
of the same species. Eight years of community consensus held this was baked-in
and immutable — a "discarded growth mechanic." It is not. It's data.

## The result

- Six party species scaled to 1.5× (Brute Tigrex, Lagiacrus, Ivory Lagiacrus,
  Oroshi Kirin, Seregios, and the story companion Ratha), applied live with no
  restart, persisting through battle and across sessions.
- A GUI trainer that lets anyone pick any species and set a per-species
  multiplier, backed by a reconstructed species → resource-ID map.

## What made it hard (the transferable part)

This project is really a case study in **binary reverse engineering under
uncertainty**. The techniques that actually moved it forward:

- **Static analysis (Ghidra):** recovered field names from RTTI/reflection
  metadata; located the growth-ratio writer by searching for an *instruction
  pattern* (DIVSS → MULSS×3) rather than a value.
- **Live debugging (x64dbg):** conditional and hardware breakpoints, reading a
  function's string output via its buffer register, and boot-time process
  ambush through TLS callbacks to catch load-time-only events.
- **Exhaustive falsification:** whole-process signature scanning
  (`VirtualQueryEx` over a multi-GB address space) to *prove a hypothesis dead*
  rather than assume it — the single most decisive tool in the project.
- **Format reverse engineering (the crown jewel):** decoding two undocumented
  Capcom MT Framework binary formats from scratch —
  - **ARCC** archives: Blowfish-ECB (with a pre/post 4-byte endianness-swap
    quirk) + per-entry zlib + hashed extensions → [`tools/arcc.py`](tools/arcc.py)
  - **XFS** parameter tables: a reflective, class-defined serialization format
    whose decode is what finally produced the correct species map →
    [`tools/xfs.py`](tools/xfs.py)
- **Data archaeology beat the entire runtime campaign:** the answer turned out
  to live in a 2.6 MB parameter table (`table.arc`) that had been sitting in
  plain sight the whole time. One decoded spreadsheet outperformed weeks of
  memory hunting.

## Repo layout

```
tools/
  arcc.py               ARCC/ARC archive codec (list / find / extract)
  xfs.py                MT Framework XFS parameter-table parser
  lmt.py                LMT bone-scale parser + patcher (rank / scale)
  census.py             sweep every archive -> monster resource-ID map
  species_data.py       reconstructed species database
  scale_trainer_gui.py  tkinter trainer: pick a team, set multipliers, apply
data/
  species_map.md        derived species -> scale-folder / battleScale table
THE_JOURNEY.md          full technical post-mortem (~12 sessions)
```

## Quickstart

```bash
pip install pycryptodome            # for the ARCC codec

# inspect what's inside an archive
python tools/arcc.py list  "<game>/nativeDX11x64/archive/table.arc" buddyPath

# rank species by how aggressively they're shrunk
python tools/lmt.py rank   "<game>/nativeDX11x64/mod/scale/mo"

# scale one species' model x1.5 (edit is picked up live by the game)
python tools/lmt.py scale  "<game>/.../mod/scale/mo/mo346/mo346_body.lmt" 1.5

# or just run the GUI (snapshots your vanilla files on first use)
python tools/scale_trainer_gui.py
```

## How the mod works, in one paragraph

Each Monstie species has a loose `mod\scale\mo\mo###\mo###_body.lmt` file holding
a static **per-bone scale** channel (the source of the chibi proportions).
Multiplying that channel uniformly enlarges the rendered model everywhere, and
the running game hot-reloads the file. The only genuinely hard part was
identifying *which* `mo###` file corresponds to *which* on-screen species — the
IDs are not the Monsterpedia numbers, subspecies have their own IDs, and there
are several overlapping ID namespaces. That map was recovered by decoding
`table.arc` (see [`data/species_map.md`](data/species_map.md)).

## Legal

This repository contains only original tools and documentation. It ships **no
game files, assets, or extracted data** — the tools operate on your own legally
obtained copy of the game. *Monster Hunter Stories* is © Capcom; this is an
unaffiliated, non-commercial research and modding project. Use at your own risk;
back up your files.

## License

Code and documentation are released under the [MIT License](LICENSE).
