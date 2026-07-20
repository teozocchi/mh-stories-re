# The Monstie Scale Mod: The Whole Ugly Journey

*A complete technical post-mortem of roughly twelve sessions of reverse engineering
Monster Hunter Stories (2024 PC port) to make hatched Monsties big. Written for the
one person who lived through it.*

---

## The premise

The ask sounded simple: hatched Monsties render at a shrunken "chibi" scale compared
to wild monsters of the same species, in both overworld and battle. Make them bigger.
Preferably as a drop-in file mod.

What made it non-simple: eight years of community consensus said this was impossible.
No size mod existed for any game in the series — not the 3DS original, not MHS2, not
the remaster. The prevailing theory called it a "discarded growth mechanic," size
permanently baked somewhere nobody had found. That should have been a warning. It was
instead a dare.

## Act I — Value hunting in the dark

The project opened the way every naive memory hack opens: Cheat Engine-style value
scanning. HP differential scans to find entity structs. String-anchor pointer scans
that landed in generic string pools. Heuristic vtable+offset scans that "found" scale
fields at offsets like +0x70 — offsets so common across unrelated classes that every
hit was noise. This era produced exactly one deliverable: a confidently-announced
"wild scale field" that later had to be retracted. Lesson zero, learned early and
relearned often: this engine does not store displayed values plainly, and a value
scan without a falsification protocol is a random-number generator with good PR.

## Act II — Ghidra draws first blood

The static-analysis pivot changed everything. The binary's RTTI/reflection metadata
coughed up two field names that would haunt the entire project: `mFamilyChildScaleRate`
(species definition struct, +0xC0) and `mBattleScale` (battle instance, +0x70). Neither
could be located live at the time. **Remember `mBattleScale`. It comes back at the end,
and the way it comes back is genuinely funny.**

The real win came from searching for code *shape* instead of data: a distinctive
DIVSS→MULSS×3 instruction pattern turned up `FUN_1412230d0` — the growth-ratio writer.
It computes a ratio and stores it to `[entity+0x80/0x84/0x88]` against a baseline at
`[entity+0x1FD0]`. The write instruction at `0x14122323F` (`MOVSS [RBX+0x80], XMM7`)
became the single most-used breakpoint of the project — our reliable window into which
monster model was being (re)synced, complete with readable path strings on the stack
(`mod\mo\mo###\fi###` for monsties, `em###` for wilds).

## Act III — The growth field lives... and dies

Proof of relevance came fast and it was spectacular: patch a wild Tigrex's growth
field to 2.0 or 4.0 at battle entry and you get camera-inside-the-mouth kaiju. Genuine
cause-and-effect, screenshot-proven. The mechanism existed. Surely monsties used it too.

They did not, and proving that consumed entire sessions. Patched the 4 known copies →
nothing. Event-discovered every copy via breakpoint and patched them all → nothing.
Finally, the nuclear option: a whole-process signature scan (`VirtualQueryEx` + numpy
over a 5.8 GB address space) found **98–122 copies of the growth structure. Every single
one was set to 2.0. All of them survived a genuine fresh zone spawn and re-bake. Zero
visual change.** For completeness, a suspicious byte flag at `[entity+0x1F9]` got the
same treatment — 60 instances forced in combination with the growth edit. Nothing.

That whole-process scan was the most decisive falsification tool we ever built.
Event-breakpoint discovery is never exhaustive; memory-wide signature sweeps are. The
growth field was pronounced dead for monsties with actual confidence, which is worth
more than a win — it killed the "you probably missed a copy" ghost that would otherwise
have haunted every later hypothesis.

## Act IV — The render-path detour

If the data field wasn't consumed, find the code that consumes whatever *is*. We found
`0x141263BF3`, a matrix-build function with a beautiful property: wild entities
provably never enter it (0 hits across an entire wild battle), monsties always do.
A monstie-exclusive code path. Surely the shrink lived here.

We built a working code-cave injection to find out — stack-swapping far trampoline,
multiplying the function's output row by 4, every frame. It fired correctly, never
crashed, and changed *absolutely nothing on screen*. The other register triplet it
computed was never even stored. Downstream, a 26KB "skeletal buffer" class allocator
(`FUN_140f2d880`) looked like the model-construction site — until a whole-process scan
found **zero live instances**, and a boot ambush (attaching at the literal first
instruction via x64dbg's system breakpoint, riding through TLS callbacks, from process
birth through gameplay) recorded **zero calls, ever**. Both functions also turned out
to be statically unreachable — no callers in Ghidra beyond a PE unwind-table data ref;
pure indirect dispatch. Dead end, sealed from both sides.

The conclusion that mattered: monstie shrink is decided *upstream*, at skeleton or
instance construction, in a moment we had never observed. Per-frame math was innocent.

## Act V — The asset pivot, and the artifact we found then threw away

External research reframed everything: nobody had ever shipped a size mod for this
series. So we went where runtime hunting couldn't: the files.

First, the encryption. The game's `.arc` archives are ARCC: Blowfish-ECB with the key
`QZHaM;-5:)dV#`, with a cursed 4-byte-chunk endianness reversal applied both before
and after decryption, per-file zlib, and jamcrc extension hashes. MHS2 community
tooling worked nearly unmodified. One afternoon of format work bought ground truth
that weeks of debugger sessions couldn't: extracting `fi338.arc` proved **wild and
monstie share the literal identical mesh file**. No `em338.mod` exists anywhere in
the install (verified exhaustively, twice). The size difference was never baked
geometry. It had to be data.

And then we found the data. `nativeDX11x64\mod\scale\mo\###_body.lmt` — 130 loose
LMT files (MT Framework motion format: 16-byte header, uint64 offset table,
96-byte AnimationBlocks, 48-byte BonePath records where `usage=2` means a static
per-bone scale living directly in the `reference_frame` floats). And the values were
*art-directed*: Lagiacrus head ≈0.5, limbs ≈0.3, torso ≈0.55. Non-uniform,
per-species, chibi-shaped. This was obviously, screamingly the mechanism.

We edited it ×2. Then ×6. Full restarts. **Zero effect.** And so the single most
important file family in the entire project was labeled "vestigial" and shelved.
That conclusion was correct about the test and catastrophically wrong about the
system — for reasons that took another week to understand (a wrong species-ID map,
mostly, plus a reload-behavior misread). The correct answer was in our hands and
we put it down.

## Act VI — Loader tracing, and assorted debugger warfare

The last engine-side push tried to catch model loading in the act. Highlights and
lowlights, in no order:

- The binary contains **no literal resource path strings at all** — only `sprintf`
  templates (`archive\mod\mo\mo%03d\fi%03d`). String-searching for "fi338" returns
  nothing forever. (Also: Ghidra's string search defaults to "Loaded Blocks" and
  silently misses everything; it must be "All Blocks." We hit that trap more than once.)
- Found the path-builder `FUN_14113e4a0` and its one dynamic caller `FUN_140f2da40`,
  which reads a genuine per-entity wild/monstie flag at `[ctx+0x6134]` to choose
  fi vs em. Real discovery, useless outcome: the builder is a rare specialized path,
  fires a handful of times per boot, and never fired for our species. The bulk loader
  builds paths some other way we never found.
- A live UI-hover capture logged the game building **species 012's** path while the
  user hovered Tigrex in a menu. At the time this was filed as an unexplained
  absurdity. *File this one away too. It was not an absurdity. It was the answer,
  three sessions early, and we didn't believe it.*
- x64dbg field notes: conditional breakpoints (`cx==152`) to tame noisy hits; reading
  a function's string *output* by noting the RDX buffer at entry, Ctrl+F9 to return,
  then a Watch deref and an ASCII dump view; the command-bar focus bug that once
  turned `bp 14113e4a0` into a byte-pattern search for `B14113E4A0` (0 hits, much
  confusion); stale one-shot TLS-callback breakpoints firing in gdi32full/shlwapi/
  inputhost, twice each, long after the setting was unchecked.
- An external AI chatbot confidently described a "dual-archive nv_m/nv_e system"
  under `nativePC`, with citations. Our own extraction ground truth contradicted
  every specific. It was a hallucination blending a real fact about Monster Hunter
  *World* with fiction. (The `nv` folder is Navirou's costumes.) Grounding claims
  against data you personally extracted is not optional.

## Act VII — Your theory, and the day it broke open

The pivotal insight was not mine. The user came back with a field observation: chibi-ness
is *differential*. Brute Tigrex's monstie head is nearly 1:1 with the wild model;
Stygian Zinogre's is comically oversized. Manual head/body ratio measurements backed
it up. That is exactly the signature of the per-bone scale data we had shelved as
vestigial — art-directed, per-species, non-uniform. We had given up on scale too fast.

So: bulk-edit ALL 130 scale LMTs ×2 (with byte-verified backups), and test. The user
happened to already be in-game, idly browsing monster showcase screens, when the
messages arrived in all caps: models blowing past the UI frame entirely, no restart,
no hatch. Then the overworld screenshot: a ridden Ivory Lagiacrus the size of a
building. After ~12 sessions of dead ends, the mechanism was alive, live-reloading,
and dramatic.

(We spent the next two days believing the reload was triggered by "opening the
Kinship/Monsties menu," because that's where the user happened to be standing.
Post-hoc attribution from a sample size of one. It was eventually debunked in the
funniest possible way — the user: "no idea what this Kinship menu is you're talking
about lol. it just worked on boot. and live." The reload was never gated at all.)

## Act VIII — The confusion arc

Then everything stopped making sense, because success revealed our map was wrong.

The bulk ×2 test had also doubled **every wild monster in the game** — Aptonoth,
Velociprey, Rathalos. Fine: the files are per-species, not per-role; scope the edit
to the party. Our long-held ID map said Brute Tigrex = `mo338`, Ivory Lagiacrus =
`mo060`. And then, in sequence:

1. Only mo338+mo060 at ×1.5 → nothing. Even after a full restart.
2. All 130 rewritten, 128 as identity ×1.0 no-ops, those 2 real → nothing.
3. Blanket real ×1.1 on 128 + real ×1.5 on those 2 → **everything grew ×1.1**,
   including the two targets, including a freshly-added *unedited* regular Lagiacrus.
   The on-disk ×1.5 was byte-verified intact, fresh timestamps.
4. A live zone-transition capture at `0x14122323F` fired for **mo052** — an ID in
   nobody's notes — with growth 0.8, across the familiar 4-duplicate-RBX,
   double-fire resync pattern, while the lead was supposedly Brute Tigrex or Ivory
   Lagiacrus.

We invented a "must touch all 130 files with real diffs to trigger reload" cache
theory to hold this together. It was wrong, and the data to kill it was already in
point 3.

## Act IX — The 1:30 AM synthesis (no debugger, no exe, off the dome)

The user called a halt: no x64dbg, no exe, just think. Laid side by side, all four
anomalies dissolved under a single hypothesis: **the species↔file map is wrong.**
Tests 1–2 edited files no on-screen monster used. Test 3's targets displayed the
blanket value because their *real* files were inside the blanket. Test 4 was the
smoking gun, not an anomaly. And the cache theory died cleanly: in test 3 the targets
showed the *fresh* 1.1, not the *stale* 2.25 left over from a prior compounded run —
a cache would have shown 2.25. Targeting problem, not caching problem. Corollary:
the ground-clip Y-offset "fix" we'd tested had never actually been tested — it had
been applied to irrelevant files both times.

## Act X — table.arc, or: the answer was a spreadsheet all along

The verification plan was supposed to be a slow in-game bisection. Instead, the
read-only archive census (all 5,586 `.arc` files, decrypting only entry tables —
Blowfish-ECB decrypts fine in fragments if you respect 8-byte blocks) turned up two
things: the resource ID space is sparse and self-consistent (every `mo###` folder
contains only same-numbered `fi/em` variants — 137 folders total), and
`archive\battle\` contains `otm###scd.arc` sound banks for **exactly the 83 rideable
species**. And then, sitting at the archive root, ignored for the entire project:
**`table.arc`**. 2.6 MB. The game's brain.

Inside, serialized in MT Framework's XFS format, which we reverse-engineered on the
spot (0x40 header with class count and def size; 48-byte property defs — u64 name
offset, u8 type, u8 flags, u16 size; 16-byte class headers; then array elements
chained as `u32 tag, u32 size` with `next = tag_pos + 4 + size`; every property
count-prefixed with `01 00 00 00`; strings inline, null-terminated, Shift-JIS —
record zero literally named ダミー, "dummy"):

- **`monster_book_data`** — the Monsterpedia table. 116 records:
  `mNo` (the pedia number printed on the user's old Kinship screenshots!),
  `mFieldEmSetNo`, `mBattleEmNo`, `mBuddyId`, `mSize`, inline Japanese name.
  Critical trap discovered here: `mBattleEmNo` and `mFieldEmSetNo` are *dense
  internal enums*, not resource IDs — Ivory Lagiacrus's battleEm=120 has no mo120
  folder. Three-plus ID spaces, all superficially similar 1–3 digit numbers.
  This project drowned in off-by-one-namespace errors for weeks because of exactly this.
- **`buddyPath`** — 100 records indexed by buddyId, 77 properties each, including
  `mArchivePath` (a literal `archive\battle\otm###` string — **the real resource
  number**) and... **`mBattleScale`**. The reflection field from Act II. The
  "discarded growth mechanic." Sitting in a moddable data table the whole time,
  holding the exact per-monstie shrink ratios: Tigrex family 0.231, Lagiacrus family
  0.22, Rathalos family 0.28, Nerscylla 0.21 — and Kirin **1.15**, because the Kirin
  monstie is actually scaled *up*. Months of memory scanning for values that were
  loaded from a spreadsheet.

Join the two tables and the map falls out, cross-validated by the user's own
screenshots (pedia #086 = Ivory Lagiacrus, #103 = Seregios — exact match):

| Monstie | Real file | Old wrong guess |
|---|---|---|
| Brute Tigrex | **mo012** | mo338 |
| Lagiacrus | **mo346** | — |
| Ivory Lagiacrus | **mo347** | mo060 |
| Oroshi Kirin | **mo035** | — |
| Seregios | **mo088** | — |
| Ratha | *(see Act XI)* | mo303 |

Every ghost died at once. The `mo052` live capture? Aptonoth — a wild one spawning
at the zone edge, never the lead monstie. The "species 012 menu hover" absurdity from
Act VI? **Correct data, disbelieved for three sessions.** Brute Tigrex was mo012 all
along; the anomaly was our map, never the capture.

Six correct files at ×1.5, 124 verified pristine, one screenshot: mounted Lagiacrus
dwarfing the rider, wild Aptonoth at factory size in the same frame. Confirmed in
battle. Confirmed across restart. No reload ritual needed. Done — the actual original
request, achieved.

## Act XI — Mop-up: three failures and a poogie

**Ground clipping.** Scaled monsties sink into terrain. The obvious lever — bone 0's
`usage=1` position track Y — was tested honestly this time (on the *correct* files):
+0.5, then a placebo-proof +5.0. Zero effect either time; every position
reference_frame in these files is (0,0,0) and apparently inert. Whatever anchors
model-to-ground lives elsewhere. Abandoned by explicit decision: "not worth going
down a crazy rabbit hole."

**Head proportions.** The pristine data showed a gorgeous candidate: bone 250,
scaled 4.545× perfectly isotropically on Lagiacrus/Ivory, 3.571× on Seregios, and
*absent on Brute Tigrex* — matching the user's own chibi-head measurements
species-for-species. Cranked it to ×20 for an unmistakable test. Nothing. Another
art-pipeline channel the runtime ignores, exactly like the growth field, exactly
like the `141263BF3` output row. This engine is a museum of plausible-looking dead
inputs. Also abandoned.

**Battle camera.** Found the real per-species battle camera table
(`enemy_camera_param_data`, keyed by `mFieldEmSetNo`, with `mDistanceDefault/Min/Max`)
— fixable, but it requires writing an ARCC *repacker* (recompress, re-chain every
subsequent entry offset, re-encrypt). Real engineering for a cosmetic gain. User
verdict: "I honestly dgaf 🤣". Shelved.

**Ratha.** The story companion. Not in the 112-monster pedia at all. Our label
"mo303 = Ratha?" — question mark included — dated from the first buddyPath decode
and had never been verified; the authoritative species list revealed pedia #109 /
mo303 is **Great Poogie**. A pig. We had shipped a size buff to a pig. The
Rathalos-recolor hypothesis (mo002) tested negative. A blanket ×3 on all 130 proved
Ratha *is* in the mo-file system. Then a textbook 4-way bucket bisection
(×2/×4/×8/×16, interleaved groups) went one round well — the round where an
"it's 16x" eyeball read was *checked* with a differential test and corrected to the
8x group — and one round badly, where a second "definitely 16x" eyeball read was
*not* differential-checked, and we narrowed into seven files Ratha had never been in.
Files byte-verified, full restart, everything 1x, much confusion. The lesson, learned
twice in one night: between adjacent multiplier buckets, a single-glance size read is
worthless; only shrink-one-group-and-recheck counts. Meanwhile the user just loaded
all 16 unnamed "Unknown" special-companion slots at once and undid them one at a
time. **Ratha = mo302.** Brute force beat clever, and honestly, fair.

## Epilogue — What shipped

- Six species (mo012, mo346, mo347, mo035, mo088, mo302) at ×1.5, live-reloading,
  battle-proof, restart-proof, drop-in.
- A tkinter trainer (`scale_trainer_gui.py` + `species_data.py`): full searchable
  species list (78 English-named via the pedia join + hand-translation session, plus
  Ratha and 15 remaining unnamed specials), per-species multipliers,
  restore-pristine-then-patch apply logic, first-run path autodetection.
- `BiggerMonsties_v1.0.zip`: mod + vanilla revert + trainer + README + mod-page copy.
  To our knowledge, the first released size mod for any game in this series.

## The meta-lessons, compressed

1. **Exhaustive falsification is the only falsification.** The whole-process
   signature scan is what let dead hypotheses actually die.
2. **Code shapes beat data values; data archaeology beats both.** The DIVSS→MULSS
   scan out-performed every value scan — and one decoded parameter table
   out-performed the entire runtime campaign.
3. **An unverified label is a time bomb.** "mo338 = Tigrex," "mo060 = Ivory,"
   "mo303 = Ratha?" — every one came from an early, reasonable, unchecked inference,
   and every one detonated weeks later.
4. **When anomalies pile up, suspect the assumption you're most sure of.** Four
   contradictory results shared one parent: the thing we'd stopped questioning.
5. **Post-hoc trigger attribution from n=1 is how you invent Kinship-menu folklore.**
6. **Differential A/B or it didn't happen.** Screenshots false-positived 0-for-3
   early on; eyeballed 8x-vs-16x sent the bisection down a wrong branch late.
7. **This engine ships data it never reads.** Growth fields on monsties, bone 250,
   position tracks, an entire matrix row — plausible-looking inert channels
   everywhere. "It's the right shape" is not evidence of consumption.
8. **The user's game knowledge was a first-class instrument.** The Deviljho
   overworld precedent, the chibi-head differential theory, the "I don't have a
   regular Tigrex, only Brute" remark, the brute-force Unknowns sweep — the technical
   work got redirected by domain knowledge more often than by any tool.

Twelve sessions. One impossible mod. One enormous Lagiacrus.

*— Claudius Maximus, 2026-07-20, 1:30 AM sharp*
