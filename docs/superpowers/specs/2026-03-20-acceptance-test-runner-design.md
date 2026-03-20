# Capcat Acceptance Test Runner — Design Spec

## Goal

A human-in-the-loop acceptance test runner that executes every capcat CLI
command and TUI flow as real subprocesses, streams live output to the terminal,
presents a structured result block, waits for the user to accept or flag the
result, writes a report entry, then loads the next test. No automation of
verdicts — the human is the judge.

## Architecture

```
tests/acceptance/
├── run_acceptance.py          # The runner — entry point
├── catalog.py                 # Full ordered test catalog (74 tests)
├── reporter.py                # Writes per-test report entries + session summary
├── fixtures/
│   ├── mock_feed.xml          # Minimal valid RSS 2.0 feed for add-source tests
│   └── batch_ids.txt          # Source ID list for remove-source --batch tests
└── results/                   # Created by run_acceptance.py on startup if absent
    └── YYYY-MM-DD_HH-MM.md    # One file per session, opened by reporter.py
```

`results/` is created by `run_acceptance.py` at startup using
`Path("tests/acceptance/results").mkdir(parents=True, exist_ok=True)` before
`reporter.py` opens the session file. `reporter.py` may assume the directory exists.

No third-party dependencies beyond the standard library and capcat itself.
The runner calls `capcat` as a subprocess — requires `capcat` to be on PATH
(installed via `pipx install capcat` or `pip install -e .`).

---

## The Core Loop

For each test in the catalog the runner:

1. Prints a header block with test number, group, and the exact command
2. Runs the command as a subprocess, streaming stdout+stderr live to the terminal
   (using `subprocess.Popen` with `stdout=sys.stdout`, `stderr=sys.stderr` so
   output is printed in real time — no capture, no buffering)
3. On completion, prints a **RESULT** block:
   - Exit code (✓ or ✗ based on expected)
   - Duration in seconds
   - Any `file://` links to output directories or files created (clickable in WezTerm)
   - A concise auto-analysis note (anomalies, missing expected strings, unexpected errors)
4. Waits for a single keypress (no Enter required) using `tty.setraw` on
   macOS/Linux or `msvcrt.getch` on Windows, wrapped in a helper function
   `_getch()` in `run_acceptance.py` that selects the platform-appropriate
   implementation at import time:
   - `Enter` (0x0D / 0x0A) → PASS (recorded as PASS in report and summary count)
   - `f` → FAIL (recorded as FAIL in report and summary count)
   - `n` → terminal returns to normal mode; `input("Note: ")` is called; after
     the user types a note and presses Enter, recorded as PASS with note text
   - `s` → SKIP (no report entry written; counted as skipped in summary)
   - `q` → quit session (summary written with tests-run-so-far counts, runner exits)
5. Appends one report entry to the active session file
6. Prints `\033[2J\033[H` (ANSI clear screen + cursor home) to clear the terminal,
   then loads the next test

Step 5 is skipped for `s` (skip) keypresses — no report entry is written.
Step 6 (screen clear) runs after every keypress including `s` — the terminal
is always cleared before the next test regardless of verdict.

For `q` (quit): the screen clear does NOT run. Instead the runner immediately
writes the session summary (prepend), prints a short "Session ended" message to
the terminal, and exits. The terminal is left as-is after quit.

Note: `n` (Note) counts as PASS in all summary tables and PASS/FAIL/SKIP totals.
The note text appears in the report entry but does not change the status to anything
other than PASS.

Each CLI test runs in its own isolated temporary directory created with
`tempfile.mkdtemp()`. The directory is not deleted after the test — the `file://`
link in the RESULT block points into it so the user can inspect files.

---

## Project Initialization per Test

Tests in groups `single`, `fetch`, `bundle`, `list`, `add-source`,
`remove-source`, `generate-config`, and `tui` need a capcat project to exist
before they run. For these, the runner:

1. Creates a fresh tmp dir
2. Runs `capcat init` silently in that dir (stdout/stderr suppressed,
   exit code checked; abort if init fails unexpectedly)
3. Then runs the test command in that same dir

Tests in group `global` (tests 1–7) do not need init — they test flags that
work without a project.

Tests in group `init` (tests 8–10) are special:

- **Test 8** (fresh init): runs `capcat init` in a new empty tmp dir.
  `needs_init` is False — init IS the test command.
- **Test 9** (already init'd → exit 1): runner creates a tmp dir, runs
  `capcat init` silently first (pre-setup), then runs `capcat init` again
  as the test command. `needs_init` is effectively True (silent pre-init),
  then the test command is also `capcat init`.
- **Test 10** (--reinit on existing): same pre-setup as test 9, then test
  command is `capcat init --reinit`. Expected exit 0.

The catalog schema uses two mutually exclusive init fields:
- `needs_init: True, pre_init: False` — runner silently inits the tmp dir before
  running the test command. The test command is something other than `capcat init`.
- `needs_init: False, pre_init: True` — runner silently inits the tmp dir before
  running the test command, AND the test command itself is `capcat init` or a
  variant. A row must never have both `needs_init: True` and `pre_init: True`.
- `needs_init: False, pre_init: False` — no silent init; the test command runs in
  a fresh empty tmp dir.

Tests 9 and 10 set `needs_init: False, pre_init: True`.
Tests 1–7 (group global, except test 5) set `needs_init: False, pre_init: False`.
Test 5 (group global, `-L` + `fetch`) sets `needs_init: True, pre_init: False`
because `fetch` requires an initialized project even though the test is in the
global group. The "global group does not need init" rule applies to tests 1–4, 6–7
only — test 5 is the exception and its `needs_init` field overrides the group default.

---

## UX — Exact Screen Layout

### CLI test

```
══════════════════════════════════════════════════════════════
TEST 12/74  [fetch]   capcat fetch hn --count 3
══════════════════════════════════════════════════════════════

Running...  (timeout: 30s)

━━━━━━━━━━━━━━━━━━━━ LIVE OUTPUT ━━━━━━━━━━━━━━━━━━━━━━━━━━━
Initialized capcat in ./
Fetching hn (3 articles)...
Saved to: /tmp/cap_t12/News_20-03-2026/Hacker-News_20-03-2026/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESULT
  Exit code : 0  ✓  (expected 0)
  Duration  : 4.2s
  Output    : file:///tmp/cap_t12/News_20-03-2026/   ← open in browser
  Files     : 3 article directories created  ✓
  Analysis  : Exit match ✓ | No error strings ✓ | 3 article dirs found

[Enter] Pass   [f] Fail   [n] Note+Pass   [s] Skip   [q] Quit
```

### TUI test and passthrough test RESULT block

For `is_tui: True` and `passthrough: True` tests, no output was captured.
The "LIVE OUTPUT" section is omitted entirely from the RESULT block.
The RESULT block for these tests shows only exit code, duration, and analysis:

```
RESULT
  Exit code : 0  ✓  (expected 0)
  Duration  : 18.3s
  Analysis  : Exit match ✓  (output passed through — no capture)

[Enter] Pass   [f] Fail   [n] Note+Pass   [s] Skip   [q] Quit
```

For TUI tests: before launch, the runner prints the header and step list,
then waits for Enter. After the process exits it prints the RESULT block above.

TUI subprocess: `subprocess.Popen(["capcat", "catch"], cwd=tmp_dir)` with no
stdout/stderr redirection (`stdout=None, stderr=None`).

Passthrough subprocess: `subprocess.Popen(cmd, cwd=tmp_dir)` with no
stdout/stderr redirection — same as TUI.

```
══════════════════════════════════════════════════════════════
TEST 48/74  [tui]   Main Menu → bundle → techpro → No HTML
══════════════════════════════════════════════════════════════

MANUAL TEST — you drive this one.

Steps to follow:
  1. Select "Catch articles from a bundle of sources"
  2. Select "techpro"
  3. Choose "No" for HTML
  4. In completion screen choose "Back to Main Menu"
  5. Choose "Exit"

Press [Enter] to launch TUI, interact, then return here.
```

After TUI process exits:

```
RESULT
  Exit code : 0  ✓  (expected 0)
  Duration  : 18.3s
  Analysis  : Exit match ✓  (no output to analyze — TUI ran in terminal)

[Enter] Pass   [f] Fail   [n] Note+Pass   [s] Skip   [q] Quit
```

---

## Test Catalog — 74 Tests

Tests are grouped and run in order. Each entry in `catalog.py` is a dict with:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Sequential 1-based test number |
| `group` | str | One of the 10 group names (see below) |
| `label` | str | Short human-readable description |
| `cmd` | list[str] | Full argv list starting with `"capcat"` |
| `expected_exit` | int or None | 0, 1, or None (None = do not check exit code in auto-analysis) |
| `expected_in_output` | list[str] | Strings checked case-sensitively in combined stdout+stderr (empty list = no check) |
| `creates_files` | bool | If True, runner counts non-hidden items in tmp dir after run |
| `needs_init` | bool | True = silent init before test; mutually exclusive with `pre_init` |
| `pre_init` | bool | True = silent init before test AND test cmd is an `init` variant; mutually exclusive with `needs_init` |
| `is_tui` | bool | If True, uses manual TUI launch flow (no output capture, no string/file auto-checks) |
| `passthrough` | bool | If True, subprocess stdout/stderr passed through to terminal (no capture); auto-analysis limited to exit code check only (no string checks, no file count check). Must always pair with `expected_in_output: []` and `creates_files: False`. Used for interactive non-TUI commands (remove-source, generate-config). |
| `timeout` | int | Seconds; default 30, TUI tests use 120 |
| `fixture` | str or None | Filename from `fixtures/` to copy into tmp dir before running |

Valid `--group` names for the runner CLI: `global`, `init`, `single`, `fetch`,
`bundle`, `list`, `add-source`, `remove-source`, `generate-config`, `tui`.
Hyphens are preserved exactly as shown. `--group add-source` is valid.

---

### global (7 tests)

| # | Label | Command | expected_exit | needs_init |
|---|-------|---------|---------------|------------|
| 1 | No args prints help | `capcat` | 0 | False |
| 2 | --help flag | `capcat --help` | 0 | False |
| 3 | -h flag | `capcat -h` | 0 | False |
| 4 | --version prints version | `capcat --version` | 0 | False |
| 5 | -L logs to file | `capcat -L <tmp>/capcat.log fetch hn --count 1` | 0 | True |
| 6 | -L missing filename | `capcat -L` | 1 | False |
| 7 | Unknown command | `capcat unknowncmd_xyz` | 1 | False |

Test 5: the log file path is `<tmp>/capcat.log` where `<tmp>` is the test's
own tmp dir. After the command completes the runner checks that this file
exists and is non-empty and reports it in the RESULT block.

---

### init (3 tests)

| # | Label | Command | expected_exit | needs_init | pre_init |
|---|-------|---------|---------------|------------|----------|
| 8 | Fresh init | `capcat init` | 0 | False | False |
| 9 | Already init'd exits 1 | `capcat init` | 1 | False | True |
| 10 | --reinit on existing | `capcat init --reinit` | 0 | False | True |

Tests 9 and 10: `pre_init: True` means the runner runs `capcat init` silently
in the tmp dir before executing the test command.

---

### single (9 tests)

All single tests use `needs_init: True`. The URL `https://example.com` is a
real URL — the test may succeed or fail depending on whether example.com is
reachable and what content is returned. The user judges the result.

| # | Label | Command | expected_exit |
|---|-------|---------|---------------|
| 11 | No URL prints usage | `capcat single` | None |
| 12 | --help | `capcat single --help` | 0 |
| 13 | Basic single URL | `capcat single https://example.com` | 0 |
| 14 | single + --html | `capcat single https://example.com --html` | 0 |
| 15 | single + --media | `capcat single https://example.com --media` | 0 |
| 16 | single + --update | `capcat single https://example.com --update` | 0 |
| 17 | single + --output | `capcat single https://example.com --output <tmp>/out` | 0 |
| 18 | single + -V verbose | `capcat single https://example.com -V` | 0 |
| 19 | single + -q quiet | `capcat single https://example.com -q` | 0 |

Test 17: `--output` value is `<tmp>/out` — a subdirectory of the test's tmp dir.

---

### fetch (13 tests)

All fetch tests use `needs_init: True`, `creates_files: True`.

| # | Label | Command | expected_exit |
|---|-------|---------|---------------|
| 20 | No source prints usage | `capcat fetch` | None |
| 21 | --help | `capcat fetch --help` | 0 |
| 22 | Single source: hn | `capcat fetch hn --count 3` | 0 |
| 23 | Single source: bbc | `capcat fetch bbc --count 3` | 0 |
| 24 | Single source: lb | `capcat fetch lb --count 3` | 0 |
| 25 | Multi source: hn,bbc | `capcat fetch hn,bbc --count 3` | 0 |
| 26 | Three sources | `capcat fetch hn,bbc,lb --count 3` | 0 |
| 27 | fetch + --html | `capcat fetch hn --count 3 --html` | 0 |
| 28 | fetch + --media | `capcat fetch hn --count 3 --media` | 0 |
| 29 | fetch + --update | `capcat fetch hn --count 3 --update` | 0 |
| 30 | fetch + --output | `capcat fetch hn --count 3 --output <tmp>/out` | 0 |
| 31 | fetch + -V | `capcat fetch hn --count 3 -V` | 0 |
| 32 | fetch + -q | `capcat fetch hn --count 3 -q` | 0 |

Tests 20–21: `creates_files: False` (no fetch happens).

---

### bundle (14 tests)

All bundle tests use `needs_init: True`. Tests 35–45 use `creates_files: True`.

| # | Label | Command | expected_exit |
|---|-------|---------|---------------|
| 33 | No name prints usage | `capcat bundle` | None |
| 34 | --help | `capcat bundle --help` | 0 |
| 35 | Bundle: tech | `capcat bundle tech --count 3` | 0 |
| 36 | Bundle: techpro | `capcat bundle techpro --count 3` | 0 |
| 37 | Bundle: news | `capcat bundle news --count 3` | 0 |
| 38 | Bundle: science | `capcat bundle science --count 3` | 0 |
| 39 | Bundle: ai | `capcat bundle ai --count 3` | 0 |
| 40 | Bundle: sports | `capcat bundle sports --count 3` | 0 |
| 41 | Bundle: all keyword | `capcat bundle all --count 2` | 0 |
| 42 | Bundle: --all flag | `capcat bundle --all --count 2` | 0 |
| 43 | bundle + --html | `capcat bundle tech --count 3 --html` | 0 |
| 44 | bundle + --output | `capcat bundle tech --count 3 --output <tmp>/out` | 0 |
| 45 | bundle + -V | `capcat bundle tech --count 3 -V` | 0 |
| 46 | Unknown bundle exits 1 | `capcat bundle unknown_bundle_xyz` | 1 |

---

### list (5 tests)

All list tests use `needs_init: True`, `creates_files: False`.

| # | Label | Command | expected_exit | expected_in_output |
|---|-------|---------|---------------|--------------------|
| 47 | list (no subcommand) | `capcat list` | 0 | `["Available sources", "Available bundles"]` |
| 48 | list sources | `capcat list sources` | 0 | `["Available sources"]` |
| 49 | list bundles | `capcat list bundles` | 0 | `["Available bundles"]` |
| 50 | list all | `capcat list all` | 0 | `["Available sources", "Available bundles"]` |
| 51 | list --help | `capcat list --help` | 0 | `["Usage"]` |

---

### add-source (4 tests)

All add-source tests use `needs_init: True`.

| # | Label | Command | expected_exit | fixture | notes |
|---|-------|---------|---------------|---------|-------|
| 52 | No --url exits 1 | `capcat add-source` | 1 | — | — |
| 53 | --help | `capcat add-source --help` | 0 | — | — |
| 54 | Valid feed (fixture) | `capcat add-source --url file://<fixture_path>` | 0 | `mock_feed.xml` | see below |
| 55 | Invalid URL | `capcat add-source --url http://localhost:19999/no-such-feed` | 1 | — | — |

**Test 54 fixture setup:**
The runner copies `fixtures/mock_feed.xml` into the test's tmp dir before
running. The `file://` URL is constructed at runtime as
`"file://" + str(Path(tmp_dir) / "mock_feed.xml")` resolved to an absolute path.
Example: `file:///tmp/cap_t54/mock_feed.xml`.

In `catalog.py`, the `cmd` list stores the sentinel string `"__FIXTURE_URL__"`
as the value argument: `["capcat", "add-source", "--url", "__FIXTURE_URL__"]`.
In `run_acceptance.py`, before executing any test whose `fixture` field is set,
the runner builds the resolved URL and replaces every occurrence of
`"__FIXTURE_URL__"` in the `cmd` list with the actual URL string. The sentinel
is not a Python format string — it is a plain equality comparison and list
replacement.

---

### remove-source (8 tests)

All remove-source tests use `needs_init: True`. The flags match the actual
CLI as defined in `capcat/cli.py` `_cmd_remove_source`.

A fresh `capcat init` project has no user-added sources to remove — only
mirrored builtin sources. The behavior of `capcat remove-source` against such
a project (e.g. whether it exits 0 or 1 when nothing is selected) is unknown
at spec-write time. Therefore `expected_exit` for tests 57–63 is set to `None`
(do not check in auto-analysis). The user observes the result and judges.
Test 56 (`--help`) has `expected_exit: 0` because help flags always exit 0.

| # | Label | Command | expected_exit |
|---|-------|---------|---------------|
| 56 | --help | `capcat remove-source --help` | 0 |
| 57 | Interactive (manual) | `capcat remove-source` | None |
| 58 | --dry-run | `capcat remove-source --dry-run` | None |
| 59 | --force | `capcat remove-source --force` | None |
| 60 | --no-backup | `capcat remove-source --no-backup` | None |
| 61 | --no-analytics | `capcat remove-source --no-analytics` | None |
| 62 | --batch (fixture) | `capcat remove-source --batch <tmp>/batch_ids.txt` | None |
| 63 | --undo latest | `capcat remove-source --undo` | None |

**Test 62 fixture setup:**
The runner copies `fixtures/batch_ids.txt` into the test's tmp dir.
`batch_ids.txt` contains one source ID per line — initially just `hn`.
Format: plain text, one source ID per line, no headers.

```
hn
```

Tests 57–63 are interactive (questionary-driven). They use `passthrough: True` —
subprocess is launched with stdout/stderr passed through to terminal (not captured).
Auto-analysis is limited to exit code check only (no string checks, no file count).
User interacts if needed, then gives verdict.

---

### generate-config (3 tests)

All generate-config tests use `needs_init: True`, `passthrough: True`,
`creates_files: False`, `expected_in_output: []`.

| # | Label | Command | expected_exit |
|---|-------|---------|---------------|
| 64 | --help | `capcat generate-config --help` | 0 |
| 65 | Interactive | `capcat generate-config` | None |
| 66 | --output file | `capcat generate-config --output <tmp>/myconfig.yaml` | None |

Tests 64–66 are interactive (questionary-driven). Subprocess passes through to
terminal. Auto-analysis limited to exit code check. User interacts and judges verdict.

---

### tui (8 tests — manual)

All TUI tests: `is_tui: True`, `needs_init: True`, `timeout: 120`,
`creates_files: False`.

Subprocess launch: `subprocess.Popen(["capcat", "catch"], cwd=tmp_dir)` with no
stdout/stderr redirection. Runner waits for the process to exit, then records
exit code and duration. No output capture — the TUI rendered live in the terminal.

For test 74, the user must type the fixture RSS URL manually into the TUI's
text prompt. The runner prints the exact URL to type before launching:

```
URL to enter when prompted: file:///tmp/cap_t74/mock_feed.xml
```

The runner constructs this URL at runtime as
`"file://" + str(Path(tmp_dir) / "mock_feed.xml")` and prints it before
launching the TUI. The fixture file is copied to the tmp dir before launch.
The `__FIXTURE_URL__` sentinel is not used for TUI test 74 (since the URL is
displayed to the user rather than injected into the subprocess argv). The
`fixture` field is `"mock_feed.xml"` — the runner copies it and prints the URL.

| # | Label | Steps | fixture |
|---|-------|-------|---------|
| 67 | Main Menu → Exit | Select "Exit" | — |
| 68 | bundle → techpro → No HTML → Back → Exit | Follow steps | — |
| 69 | bundle → tech → Yes HTML → Exit | Follow steps | — |
| 70 | fetch multi-select hn+bbc → No HTML → Back → Exit | Space-select two sources | — |
| 71 | single source → hn → No HTML → Back → Exit | Follow steps | — |
| 72 | single URL → type URL → No HTML → Back → Exit | Type `https://example.com` | — |
| 73 | Manage Sources → List → browse → back → Exit | Follow steps | — |
| 74 | Manage Sources → Add RSS → type URL → back → Exit | Type fixture URL shown before launch | `mock_feed.xml` |

---

## Auto-Analysis Rules

Performed automatically and printed in RESULT block. All checks are
informational — the user decides the verdict.

| Check | Trigger | Pass condition |
|-------|---------|----------------|
| Exit code match | when `expected_exit` is not None | `actual_exit == expected_exit` (case: None → skip check, print "exit check skipped") |
| Expected strings | if `expected_in_output` non-empty | all strings found in combined stdout+stderr, **case-sensitive** exact substring match |
| Error string scan | when `expected_exit == 0` | none of `Traceback`, `Error:`, `CRITICAL` appear in output |
| Output file count | if `creates_files: True` | count of top-level entries in tmp dir that are not named `.capcat` or `Config`. If neither of those dirs exists, count all top-level entries. |
| Log file exists | if `-L <path>` in cmd | file at that path exists and `os.path.getsize() > 0` |
| Timeout flag | always | process completed within `timeout` seconds |

For TUI tests (`is_tui: True`) only the exit code check and timeout check apply —
no string or file checks (no captured output).

For `expected_exit: None` tests, the exit code is still printed in the RESULT
block (so the user can see it), but the ✓/✗ indicator is replaced with `?`
and the auto-analysis line reads "exit check skipped — user judges".

---

## Report Format

### Per-test entry (appended immediately after user keypress)

```markdown
## TEST 12 — fetch: capcat fetch hn --count 3
- **Status**: PASS
- **Exit**: 0 (expected 0)  ✓
- **Duration**: 4.2s
- **Output**: file:///tmp/cap_t12/News_20-03-2026/
- **Files created**: 3
- **Auto-analysis**: Exit ✓ | No error strings ✓ | 3 article dirs found ✓
- **Note**: —
```

Status is one of: `PASS`, `FAIL`. A noted test (`n` keypress) is `PASS` with
note text filled in. A skipped test (`s` keypress) has no entry written at all.

### Session summary (written at the TOP of the session file on `q` or completion)

The session file is written in two phases:
1. Per-test entries are appended to the file after each verdict throughout the session.
2. When the session ends, `reporter.py` prepends the summary block to the file by
   reading the full file content, writing the summary header, then rewriting the
   full content after it. The summary always appears at the top; test entries follow.

```markdown
# Capcat Acceptance Test Run — 2026-03-20 14:30

**Passed**: 61  **Failed**: 3  **Skipped**: 10  **Total run**: 64

| Group           | Pass | Fail | Skip |
|-----------------|------|------|------|
| global          | 7    | 0    | 0    |
| init            | 3    | 0    | 0    |
| single          | 8    | 1    | 0    |
| fetch           | 10   | 2    | 1    |
| bundle          | 14   | 0    | 0    |
| list            | 5    | 0    | 0    |
| add-source      | 3    | 0    | 1    |
| remove-source   | 5    | 0    | 3    |
| generate-config | 3    | 0    | 0    |
| tui             | 3    | 0    | 5    |

### Failed Tests
- TEST 18: single -V — [user note]
- TEST 25: fetch hn,bbc — Traceback in output
- TEST 30: fetch --output — Output dir not created
```

When `--from`, `--only`, or `--group` filters are active:
- Tests not run due to the filter are excluded from the summary table entirely
- The summary header shows `Total run: N` (not 74) so it is clear a subset was run
- Skipped tests (user pressed `s`) appear in the Skip column normally

---

## CLI Flags for the Runner

```
python tests/acceptance/run_acceptance.py                   # run all 74
python tests/acceptance/run_acceptance.py --group fetch     # one group
python tests/acceptance/run_acceptance.py --group add-source  # hyphens ok
python tests/acceptance/run_acceptance.py --from 22         # resume from #22
python tests/acceptance/run_acceptance.py --only 25,30,46   # specific tests
python tests/acceptance/run_acceptance.py --timeout 60      # override timeout
```

`--from`, `--only`, and `--group` are mutually exclusive. If more than one is
passed, the runner prints an error and exits. They cannot be combined.

`--timeout N` overrides the `timeout` field of every test in the active run,
including TUI tests. It replaces the per-test value entirely.

---

## Fixtures

### fixtures/mock_feed.xml

Minimal RSS 2.0 document, 2 items. Used for `add-source` tests (54, 74).
Referenced via `file://` URL constructed at runtime from the test tmp dir path.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Mock Test Feed</title>
    <link>https://example.com</link>
    <description>Fixture feed for acceptance tests</description>
    <item>
      <title>Test Article One</title>
      <link>https://example.com/article-1</link>
      <description>First test article.</description>
      <pubDate>Fri, 20 Mar 2026 10:00:00 +0000</pubDate>
    </item>
    <item>
      <title>Test Article Two</title>
      <link>https://example.com/article-2</link>
      <description>Second test article.</description>
      <pubDate>Fri, 20 Mar 2026 11:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>
```

### fixtures/batch_ids.txt

Source ID list for `remove-source --batch` (test 62). Plain text, one ID per line.

```
hn
```

---

## Constraints and Non-Goals

- **No mocking** — all tests run real capcat commands against real or fixture data
- **No auto-verdict** — the human decides pass/fail for every test
- **No network requirement for fixtures** — tests that need a feed use `file://` URLs;
  tests using `https://example.com` are best-effort and the user judges
- **Not a regression guard** — this is a manual acceptance session, not a CI gate;
  the automated unit tests in `tests/unit/` serve that role
- **TUI tests are observation-only** — the runner cannot automate questionary/keyboard
  input; the user interacts manually and the subprocess runs unmodified in the terminal
