# TD-040: the fixtures carry the release they belong to

**Status:** In review 2026-11-04 (the designer). Class: **wide**, because it changes a published, vendored artefact: the conformance set any implementation runs, and what a consumer's copy proves about itself (cap 6 rounds, cadence.md §4.8 *Design review rounds*). The review record is `docs/reviews/TD-040.md`.

**Entry:** [TD-040](../ledger/TD-040.md), split off TD-035 on Paul's answer of 2026-11-04.

## The problem

Target design §7.4's last bullet: "Fixtures carry the release they apply to, so a consumer can run the set for its own pin (CommonMark publishes its tests per spec version)." Today nothing in `fixtures/` names a release. The package does: each `ledgerboard/*.py` starts `# ledgerboard v<x.y> sha256:<hex>`, stamped by `release.sh` and checked by `fixtures/run.py --check-header`, so a vendored copy proves which release it is. A copy of the fixtures proves nothing. A consumer or another-language reader holding a set cannot tell which release's outputs it expects, or whether it was edited after that release, and a consumer that upgrades its package but not its fixtures (or the reverse) runs one release's module against another's expectations without being told.

## Options weighed

**(a) A release key on each case** (`"release": "<x.y>"` in each `cases.json` case and each directory case's `cmd.json`, plus a sidecar for the `ledger/`, `board/` and `archive/` cases, which have no JSON input to carry it), and `run.py --release <x.y>` running the cases at or below the pin. Rejected, on three counts.
- *Which release it names cannot be kept true.* Most expected files bundle several functions' outputs: a `board/<case>.json` holds `item_record()`, `item_key()`, `closed_items()`, `needs_you()` (v2.3) and `board_people()` (v2.3). A case's expectation changes whenever any function it covers changes, and `run.py --write` rewrites every expected file at once. A tag naming the release that *added* the case then lies (every `board/` case now expects `needs_you` and `people`, v2.3's outputs, so a case added before v2.3 and tagged with its own release fails against that release's module). A tag naming the release that *last changed* its expected output is true only if every `--write` bumps it, which nothing in a file can check without history.
- *An older pin gets little coverage.* Under "last changed", nearly every case moves to the newest release each time a function it touches gains an output, so `--release 2.2` would run few cases.
- *It stores what git already has.* The cases at their release's tag are exactly the set for that release.

**(b) A directory per release** (`fixtures/v2.3/`, `fixtures/v2.4/`, …). Rejected: it copies about 1,800 files each release to keep what the tags already keep, and the copies drift unless every old one is frozen.

**(c) The set carries its release, as the package does (chosen).** One file, `fixtures/MANIFEST`, names the release and lists the sha256 of every other file in the set. `release.sh` stamps it when it stamps the headers, and `run.py --check-header` checks it beside them: intact, and the same release as the package. This is CommonMark's model, a test set per spec version, not a version per test. A consumer runs the set its pin ships, and its vendor check proves the set and the package are one release. An older release's set is its tag's.

The four questions in TD-040's Fix, answered:
1. *How a case names its release:* it does not. The set does, in `fixtures/MANIFEST`.
2. *Added, or last changed:* neither. The set's release is the one whose module wrote every expected output in it.
3. *How `run.py` runs the set for a pin:* by running the set that pin ships (a vendored copy, or the tag's `fixtures/`); `--check-header` proves the set and the package it runs against are one release. There is no `--release` option and no subset.
4. *The existing cases:* nothing is tagged per case. The first stamp is v2.4's. A set from before v2.4 carries no manifest; its release is its tag's.

**On §7.4's cross-version bullet.** "a v2.4 reader (whose fixtures stay in the suite) …" does not need a newer set run against an older module. A reader's behaviour on text from a newer minor is tested in the reader's own set with invented words that no release defines (TD-039's planned `fixtures/ledger/unknownstatus`, word `Xyzzy`, in PR #108), so each release's set stays self-contained.

## The rules

1. **The file.** `fixtures/MANIFEST`, UTF-8, every line ending in LF, the last included.
   - Its first line is `# ledgerboard v<x.y> fixtures`, where `<x.y>` is `<major>.<minor>`, each a run of ASCII digits.
   - Each later line is `<sha256>  <path>`: 64 lower-case hex digits, two spaces, then the path, as `sha256sum` writes them. There is one line per file in the set, and no other line.
   - **The set** is every regular file under `fixtures/`, at any depth, except `fixtures/MANIFEST` itself and any file under a directory named `__pycache__`. `run.py` is in the set. A symbolic link is not a regular file and is refused (rule 3).
   - `<path>` is the file's path relative to `fixtures/`, its parts joined by `/`. No path in the set holds a newline, a carriage return or a backslash (rule 3 refuses one), so no escaping is needed.
   - The lines are sorted by `<path>`'s UTF-8 bytes, so `a-b` sorts before `a/b` (`-` is 0x2D, `/` is 0x2F) and `B` before `a`.
   - `<sha256>` is of the file's bytes as stored, untranslated (`.gitattributes` already keeps `fixtures/**` byte for byte, `-text`), so a CRLF fixture hashes its CRs.
2. **Writing it.** `run.py --stamp <x.y>` writes `fixtures/MANIFEST` for the set beside it (`HERE`) and prints `stamped fixtures v<x.y> (<n> files)`. A `<x.y>` that is not two dot-separated runs of digits exits 2, `usage: --stamp <major.minor>`, and writes nothing; so does a set rule 3 refuses, with that rule's text. `release.sh <x.y>` runs it after stamping the headers and before its checks, then adds and commits it with the package: `git add fixtures/MANIFEST` and `git commit -qm "Release v$v" -- ledgerboard fixtures/MANIFEST` (the add is needed: the first release's manifest is untracked, and a commit pathspec naming an untracked file fails). Between releases the manifest is left as it is, as the headers are; a PR that changes a fixture does not restamp it.
3. **Checking it.** `run.py --check-header` checks the package's headers, as today, and then the manifest of the set beside it. It prints the header line as today (`header: ok (v<x.y>)` or `header: <why>`), then either `fixtures: ok (v<x.y>, <n> files)` or one line per problem, in this order, each starting `fixtures: `:
   - `no MANIFEST — this set names no release (a set from before v2.4 is its tag's)`; nothing more is checked.
   - `MANIFEST's first line is not a release line: '<line>'` (the line as Python's `repr` of the decoded text gives it); nothing more is checked.
   - `MANIFEST line <n> is not '<sha256>  <path>': '<line>'`, for each malformed later line (`<n>` counts from 1, the release line being 1); `MANIFEST lists <path> twice` for each later line whose path equals an earlier well-formed line's; and `MANIFEST line <n> is out of order` for each other well-formed line whose path sorts before the previous well-formed line's. A path listed twice gives only the first of those two. These are reported line by line, in line order; the checks below then run over the well-formed lines, the first of each path counting.
   - `<path>: a symbolic link, not a file` and `<path>: a path holding a newline, a carriage return or a backslash` for each such entry of the set on disk.
   - `<path>: in MANIFEST but missing`, `<path>: not in MANIFEST — added after its release`, and `<path>: its sha256 does not match MANIFEST — edited after its release`, the three kinds merged into one list in path order.
   - When the package's headers are intact and name one release, and the manifest has no problem above: `MANIFEST names v<a>, the package v<b>` if they differ.

   It exits 1 when the header or the manifest has any problem, else 0. A manifest is checked only by `--check-header` (run by `release.sh` before both its commit and its tag, and by a consumer's vendor check); a plain run (`python3 fixtures/run.py`) reads no manifest, so the repo's precheck, which runs between releases, is unchanged.
4. **One definition.** The manifest's text and its problems are two functions of `run.py`, `manifest_text(root: Path, release: str) -> str` and `manifest_problems(root: Path) -> list[str]` (the problem texts above, without the `fixtures: ` prefix), which `--stamp`, `--check-header` and the tests share. `release.sh` writes no manifest of its own. Nothing goes into the package: `ledgerboard/` neither reads nor writes `fixtures/`.

## What changes where

- **`fixtures/run.py`:** `manifest_text()`, `manifest_problems()` and `--stamp`; `--check-header` gains the manifest check (rule 3), and its help text says it checks both; the docstring's usage block and its `--check-header` paragraph say so (text below).
- **`release.sh`:** the stamp and the wider commit (rule 2); its header comment gains the manifest (text below). `--tag` needs no change: it already runs `--check-header`, which now refuses a manifest edited after the stamp.
- **`fixtures/MANIFEST`:** written once, by v2.4's `release.sh` run, never by the build's PR. The build commits no manifest, so main between the build and the release has none, and `--check-header` on main says so (`no MANIFEST …`); only `release.sh` and a consumer's check run it, and `release.sh` stamps before it checks.
- **`README.md`:** the `fixtures/` bullet gains one sentence (text below).
- **`SPEC.md`:** two passages (below).
- **`docs/plans/target-design.md`:** §7.4's last bullet gains a dated pointer (below).
- **`tests/test_release.py`:** the cases below.

## The SPEC text

**In the opening paragraph**, after (it wraps over lines 4–5) "Where this text and the module disagree, the fixtures decide, and the disagreement is a bug here." insert:

> From v2.4 the set names the release it belongs to (*Versions*).

**In *Versions*, a new paragraph after "**v2.4 changes what `split()` writes** … `split_notes()` is new.":**

> **v2.4 stamps the fixtures with their release:** `fixtures/MANIFEST` names the release and lists the sha256 of every other file in the set, so a copy of the set proves which release it is, as each package file's first line does, and an implementation of release `x.y` runs the set stamped `x.y`. Its first line is `# ledgerboard v<x.y> fixtures`. Each later line is `<sha256>  <path>` (64 lower-case hex digits and two spaces, as `sha256sum` writes), one per regular file under `fixtures/` but the manifest itself and any file under a `__pycache__` directory, the path relative to `fixtures/` with `/` between its parts, the lines sorted by the paths' UTF-8 bytes, every line ending in LF. The hash is of the file's bytes as stored. A case names no release of its own: the set's release is the one whose module wrote every expected output in it. A release stamps the manifest when it stamps the package; between releases it is left as it is, and only a release's is checked (`fixtures/run.py --check-header`). A set from before v2.4 carries no manifest; its release is its tag's. Nothing a reader reads changes.

## The other text

**`fixtures/run.py`'s docstring.** The usage block becomes:

```
    python3 fixtures/run.py [--module PATH] [--write]
    python3 fixtures/run.py --check-header [--module PATH]
    python3 fixtures/run.py --stamp <x.y>
```

and the sentence beginning "``--check-header`` checks only the first line of every ``*.py`` file in the package" gains, after its parenthesis: "It then checks this set's ``MANIFEST`` (v2.4): the release it names and the sha256 of every other file here, which must match, with no file missing or added, and the same release as the package (exit 1 on any difference). ``--stamp <x.y>`` writes that ``MANIFEST`` for this set; ``release.sh`` runs it."

**`release.sh`'s header comment**, after "stamp the first line of every file in the package (ledgerboard/*.py) with the release and that file's hash,": "write fixtures/MANIFEST (the release and every fixture file's sha256, fixtures/run.py --stamp),", and the closing paragraph gains: "The fixtures carry the same release in fixtures/MANIFEST, checked by the same --check-header."

**`README.md`'s `fixtures/` bullet** gains: "Each release stamps the set with its release in `fixtures/MANIFEST` (v2.4), so a copy of the set, like a copy of the package, proves which release it is."

**`docs/plans/target-design.md` §7.4's last bullet** gains: "*Designed 2026-11-04 (TD-040, `docs/plans/TD-040-fixture-release.md`):* the set, not each case, carries its release: `fixtures/MANIFEST`, stamped by `release.sh` and checked by `run.py --check-header`."

## The cases

The manifest is the runner's, not the module's, so its cases are unit tests in `tests/test_release.py`, each over a set built in a temporary directory (a copy of `run.py` and a few invented files), with `manifest_text()` and `manifest_problems()` imported from that copy:

1. Stamp then check: no problem; `--check-header` against an intact package of the same release prints `fixtures: ok (v<x.y>, <n> files)` and exits 0.
2. The text, pinned byte for byte, of `manifest_text()` over a set of four files (no `run.py`: the function takes its root): `a/b.json`, `a-b.md`, `B.md` and `crlf.md`, whose bytes are `x\r\n`. It is the release line, then the lines in the order `B.md`, `a-b.md`, `a/b.json`, `crlf.md`, the last hashing `x\r\n` with its CR.
3. A file under `__pycache__/` is neither listed nor reported as added.
4. Each problem of rule 3, one test each, with its exact text: no manifest; a bad first line; a malformed line; an out-of-order line; a path listed twice (the one `lists … twice` line, no out-of-order line); a malformed line beside an edited file (both reported); a missing file; an added file; an edited file; a symbolic link; a path holding a backslash (skipped where the file system refuses one); and the release mismatch (a package stamped v2.3, a manifest v2.4).
5. The mismatch is not reported while either side has another problem.
6. `--stamp 2` and `--stamp v2.4` exit 2 with the usage line and write nothing.
7. **The tag.** The existing `ReleaseTag` tests seed a throwaway repo with `release.sh`, `ledgerboard/__init__.py` and `fixtures/run.py`, stamp the header as a release would, and run `release.sh --tag`. Once `--check-header` checks the manifest, that seed has none and every one of them would be refused, so `setUp` also runs the seed's `fixtures/run.py --stamp <version>` before its commit. A new test then edits `fixtures/run.py` in a later commit (pushed, so HEAD is still origin/main) and checks that `release.sh --tag` exits non-zero with `fixtures: run.py: its sha256 does not match MANIFEST — edited after its release` in its output, and creates no tag.
8. **The stamp step.** `release.sh <x.y>` runs the whole suite and the fixtures, which a throwaway seed cannot hold, so its stamp step is pinned by text: a test reads `release.sh` and checks that it runs `python3 fixtures/run.py --stamp "$v"` before its first `python3 fixtures/run.py --check-header` after the branch is cut, that a `git add fixtures/MANIFEST` comes before its commit, and that its commit line names `fixtures/MANIFEST`. The step itself first runs for real at v2.4's release, whose `--check-header` (in `release.sh`, before the commit) checks what it wrote.

## The build

One build, **part of TD-040**, in **v2.4** (TD-036's `Blocked by` gains it when it is filed). Its Fix is this plan's *The rules*, *What changes where* and *The other text*; its Done when: every case above passes; the precheck is green; and the two SPEC passages quoted above land in `SPEC.md` with the code, in the same PR.
