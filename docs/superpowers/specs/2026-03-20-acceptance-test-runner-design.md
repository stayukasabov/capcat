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

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Field</th>
      <th>Type</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>id</code></td>
      <td>int</td>
      <td>Sequential 1-based test number</td>
    </tr>
    <tr>
      <td><code>group</code></td>
      <td>str</td>
      <td>One of the 10 group names (see below)</td>
    </tr>
    <tr>
      <td><code>label</code></td>
      <td>str</td>
      <td>Short human-readable description</td>
    </tr>
    <tr>
      <td><code>cmd</code></td>
      <td>list[str]</td>
      <td>Full argv list starting with <code>"capcat"</code></td>
    </tr>
    <tr>
      <td><code>expected_exit</code></td>
      <td>int or None</td>
      <td>0, 1, or None (None = do not check exit code in auto-analysis)</td>
    </tr>
    <tr>
      <td><code>expected_in_output</code></td>
      <td>list[str]</td>
      <td>Strings checked case-sensitively in combined stdout+stderr (empty list = no check)</td>
    </tr>
    <tr>
      <td><code>creates_files</code></td>
      <td>bool</td>
      <td>If True, runner counts non-hidden items in tmp dir after run</td>
    </tr>
    <tr>
      <td><code>needs_init</code></td>
      <td>bool</td>
      <td>True = silent init before test; mutually exclusive with <code>pre_init</code></td>
    </tr>
    <tr>
      <td><code>pre_init</code></td>
      <td>bool</td>
      <td>True = silent init before test AND test cmd is an <code>init</code> variant; mutually exclusive with <code>needs_init</code></td>
    </tr>
    <tr>
      <td><code>is_tui</code></td>
      <td>bool</td>
      <td>If True, uses manual TUI launch flow (no output capture, no string/file auto-checks)</td>
    </tr>
    <tr>
      <td><code>passthrough</code></td>
      <td>bool</td>
      <td>If True, subprocess stdout/stderr passed through to terminal (no capture); auto-analysis limited to exit code check only (no string checks, no file count check). Must always pair with <code>expected_in_output: []</code> and <code>creates_files: False</code>. Used for interactive non-TUI commands (remove-source, generate-config).</td>
    </tr>
    <tr>
      <td><code>timeout</code></td>
      <td>int</td>
      <td>Seconds; default 30, TUI tests use 120</td>
    </tr>
    <tr>
      <td><code>fixture</code></td>
      <td>str or None</td>
      <td>Filename from <code>fixtures/</code> to copy into tmp dir before running</td>
    </tr>
  </tbody>
</table>
</div>

Valid `--group` names for the runner CLI: `global`, `init`, `single`, `fetch`,
`bundle`, `list`, `add-source`, `remove-source`, `generate-config`, `tui`.
Hyphens are preserved exactly as shown. `--group add-source` is valid.

---

### global (7 tests)

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
      <th>needs_init</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>No args prints help</td>
      <td><code>capcat</code></td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <td>2</td>
      <td>--help flag</td>
      <td><code>capcat --help</code></td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <td>3</td>
      <td>-h flag</td>
      <td><code>capcat -h</code></td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <td>4</td>
      <td>--version prints version</td>
      <td><code>capcat --version</code></td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <td>5</td>
      <td>-L logs to file</td>
      <td><code>capcat -L <tmp>/capcat.log fetch hn --count 1</code></td>
      <td>0</td>
      <td>True</td>
    </tr>
    <tr>
      <td>6</td>
      <td>-L missing filename</td>
      <td><code>capcat -L</code></td>
      <td>1</td>
      <td>False</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Unknown command</td>
      <td><code>capcat unknowncmd_xyz</code></td>
      <td>1</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>

Test 5: the log file path is `<tmp>/capcat.log` where `<tmp>` is the test's
own tmp dir. After the command completes the runner checks that this file
exists and is non-empty and reports it in the RESULT block.

---

### init (3 tests)

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
      <th>needs_init</th>
      <th>pre_init</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>8</td>
      <td>Fresh init</td>
      <td><code>capcat init</code></td>
      <td>0</td>
      <td>False</td>
      <td>False</td>
    </tr>
    <tr>
      <td>9</td>
      <td>Already init'd exits 1</td>
      <td><code>capcat init</code></td>
      <td>1</td>
      <td>False</td>
      <td>True</td>
    </tr>
    <tr>
      <td>10</td>
      <td>--reinit on existing</td>
      <td><code>capcat init --reinit</code></td>
      <td>0</td>
      <td>False</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>

Tests 9 and 10: `pre_init: True` means the runner runs `capcat init` silently
in the tmp dir before executing the test command.

---

### single (9 tests)

All single tests use `needs_init: True`. The URL `https://example.com` is a
real URL — the test may succeed or fail depending on whether example.com is
reachable and what content is returned. The user judges the result.

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>11</td>
      <td>No URL prints usage</td>
      <td><code>capcat single</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>12</td>
      <td>--help</td>
      <td><code>capcat single --help</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>13</td>
      <td>Basic single URL</td>
      <td><code>capcat single https://example.com</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>14</td>
      <td>single + --html</td>
      <td><code>capcat single https://example.com --html</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>15</td>
      <td>single + --media</td>
      <td><code>capcat single https://example.com --media</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>16</td>
      <td>single + --update</td>
      <td><code>capcat single https://example.com --update</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>17</td>
      <td>single + --output</td>
      <td><code>capcat single https://example.com --output <tmp>/out</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>18</td>
      <td>single + -V verbose</td>
      <td><code>capcat single https://example.com -V</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>19</td>
      <td>single + -q quiet</td>
      <td><code>capcat single https://example.com -q</code></td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>

Test 17: `--output` value is `<tmp>/out` — a subdirectory of the test's tmp dir.

---

### fetch (13 tests)

All fetch tests use `needs_init: True`, `creates_files: True`.

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>20</td>
      <td>No source prints usage</td>
      <td><code>capcat fetch</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>21</td>
      <td>--help</td>
      <td><code>capcat fetch --help</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>22</td>
      <td>Single source: hn</td>
      <td><code>capcat fetch hn --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>23</td>
      <td>Single source: bbc</td>
      <td><code>capcat fetch bbc --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>24</td>
      <td>Single source: lb</td>
      <td><code>capcat fetch lb --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>25</td>
      <td>Multi source: hn,bbc</td>
      <td><code>capcat fetch hn,bbc --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>26</td>
      <td>Three sources</td>
      <td><code>capcat fetch hn,bbc,lb --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>27</td>
      <td>fetch + --html</td>
      <td><code>capcat fetch hn --count 3 --html</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>28</td>
      <td>fetch + --media</td>
      <td><code>capcat fetch hn --count 3 --media</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>29</td>
      <td>fetch + --update</td>
      <td><code>capcat fetch hn --count 3 --update</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>30</td>
      <td>fetch + --output</td>
      <td><code>capcat fetch hn --count 3 --output <tmp>/out</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>31</td>
      <td>fetch + -V</td>
      <td><code>capcat fetch hn --count 3 -V</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>32</td>
      <td>fetch + -q</td>
      <td><code>capcat fetch hn --count 3 -q</code></td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>

Tests 20–21: `creates_files: False` (no fetch happens).

---

### bundle (14 tests)

All bundle tests use `needs_init: True`. Tests 35–45 use `creates_files: True`.

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>33</td>
      <td>No name prints usage</td>
      <td><code>capcat bundle</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>34</td>
      <td>--help</td>
      <td><code>capcat bundle --help</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>35</td>
      <td>Bundle: tech</td>
      <td><code>capcat bundle tech --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>36</td>
      <td>Bundle: techpro</td>
      <td><code>capcat bundle techpro --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>37</td>
      <td>Bundle: news</td>
      <td><code>capcat bundle news --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>38</td>
      <td>Bundle: science</td>
      <td><code>capcat bundle science --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>39</td>
      <td>Bundle: ai</td>
      <td><code>capcat bundle ai --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>40</td>
      <td>Bundle: sports</td>
      <td><code>capcat bundle sports --count 3</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>41</td>
      <td>Bundle: all keyword</td>
      <td><code>capcat bundle all --count 2</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>42</td>
      <td>Bundle: --all flag</td>
      <td><code>capcat bundle --all --count 2</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>43</td>
      <td>bundle + --html</td>
      <td><code>capcat bundle tech --count 3 --html</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>44</td>
      <td>bundle + --output</td>
      <td><code>capcat bundle tech --count 3 --output <tmp>/out</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>45</td>
      <td>bundle + -V</td>
      <td><code>capcat bundle tech --count 3 -V</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>46</td>
      <td>Unknown bundle exits 1</td>
      <td><code>capcat bundle unknown_bundle_xyz</code></td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>

---

### list (5 tests)

All list tests use `needs_init: True`, `creates_files: False`.

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
      <th>expected_in_output</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>47</td>
      <td>list (no subcommand)</td>
      <td><code>capcat list</code></td>
      <td>0</td>
      <td><code>["Available sources", "Available bundles"]</code></td>
    </tr>
    <tr>
      <td>48</td>
      <td>list sources</td>
      <td><code>capcat list sources</code></td>
      <td>0</td>
      <td><code>["Available sources"]</code></td>
    </tr>
    <tr>
      <td>49</td>
      <td>list bundles</td>
      <td><code>capcat list bundles</code></td>
      <td>0</td>
      <td><code>["Available bundles"]</code></td>
    </tr>
    <tr>
      <td>50</td>
      <td>list all</td>
      <td><code>capcat list all</code></td>
      <td>0</td>
      <td><code>["Available sources", "Available bundles"]</code></td>
    </tr>
    <tr>
      <td>51</td>
      <td>list --help</td>
      <td><code>capcat list --help</code></td>
      <td>0</td>
      <td><code>["Usage"]</code></td>
    </tr>
  </tbody>
</table>
</div>

---

### add-source (4 tests)

All add-source tests use `needs_init: True`.

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
      <th>fixture</th>
      <th>notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>52</td>
      <td>No --url exits 1</td>
      <td><code>capcat add-source</code></td>
      <td>1</td>
      <td>—</td>
      <td>—</td>
    </tr>
    <tr>
      <td>53</td>
      <td>--help</td>
      <td><code>capcat add-source --help</code></td>
      <td>0</td>
      <td>—</td>
      <td>—</td>
    </tr>
    <tr>
      <td>54</td>
      <td>Valid feed (fixture)</td>
      <td><code>capcat add-source --url file://<fixture_path></code></td>
      <td>0</td>
      <td><code>mock_feed.xml</code></td>
      <td>see below</td>
    </tr>
    <tr>
      <td>55</td>
      <td>Invalid URL</td>
      <td><code>capcat add-source --url http://localhost:19999/no-such-feed</code></td>
      <td>1</td>
      <td>—</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

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

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>56</td>
      <td>--help</td>
      <td><code>capcat remove-source --help</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>57</td>
      <td>Interactive (manual)</td>
      <td><code>capcat remove-source</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>58</td>
      <td>--dry-run</td>
      <td><code>capcat remove-source --dry-run</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>59</td>
      <td>--force</td>
      <td><code>capcat remove-source --force</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>60</td>
      <td>--no-backup</td>
      <td><code>capcat remove-source --no-backup</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>61</td>
      <td>--no-analytics</td>
      <td><code>capcat remove-source --no-analytics</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>62</td>
      <td>--batch (fixture)</td>
      <td><code>capcat remove-source --batch <tmp>/batch_ids.txt</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>63</td>
      <td>--undo latest</td>
      <td><code>capcat remove-source --undo</code></td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>

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

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Command</th>
      <th>expected_exit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>64</td>
      <td>--help</td>
      <td><code>capcat generate-config --help</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>65</td>
      <td>Interactive</td>
      <td><code>capcat generate-config</code></td>
      <td>None</td>
    </tr>
    <tr>
      <td>66</td>
      <td>--output file</td>
      <td><code>capcat generate-config --output <tmp>/myconfig.yaml</code></td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>

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

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Label</th>
      <th>Steps</th>
      <th>fixture</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>67</td>
      <td>Main Menu → Exit</td>
      <td>Select "Exit"</td>
      <td>—</td>
    </tr>
    <tr>
      <td>68</td>
      <td>bundle → techpro → No HTML → Back → Exit</td>
      <td>Follow steps</td>
      <td>—</td>
    </tr>
    <tr>
      <td>69</td>
      <td>bundle → tech → Yes HTML → Exit</td>
      <td>Follow steps</td>
      <td>—</td>
    </tr>
    <tr>
      <td>70</td>
      <td>fetch multi-select hn+bbc → No HTML → Back → Exit</td>
      <td>Space-select two sources</td>
      <td>—</td>
    </tr>
    <tr>
      <td>71</td>
      <td>single source → hn → No HTML → Back → Exit</td>
      <td>Follow steps</td>
      <td>—</td>
    </tr>
    <tr>
      <td>72</td>
      <td>single URL → type URL → No HTML → Back → Exit</td>
      <td>Type <code>https://example.com</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td>73</td>
      <td>Manage Sources → List → browse → back → Exit</td>
      <td>Follow steps</td>
      <td>—</td>
    </tr>
    <tr>
      <td>74</td>
      <td>Manage Sources → Add RSS → type URL → back → Exit</td>
      <td>Type fixture URL shown before launch</td>
      <td><code>mock_feed.xml</code></td>
    </tr>
  </tbody>
</table>
</div>

---

## Auto-Analysis Rules

Performed automatically and printed in RESULT block. All checks are
informational — the user decides the verdict.

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Check</th>
      <th>Trigger</th>
      <th>Pass condition</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Exit code match</td>
      <td>when <code>expected_exit</code> is not None</td>
      <td><code>actual_exit == expected_exit</code> (case: None → skip check, print "exit check skipped")</td>
    </tr>
    <tr>
      <td>Expected strings</td>
      <td>if <code>expected_in_output</code> non-empty</td>
      <td>all strings found in combined stdout+stderr, **case-sensitive** exact substring match</td>
    </tr>
    <tr>
      <td>Error string scan</td>
      <td>when <code>expected_exit == 0</code></td>
      <td>none of <code>Traceback</code>, <code>Error:</code>, <code>CRITICAL</code> appear in output</td>
    </tr>
    <tr>
      <td>Output file count</td>
      <td>if <code>creates_files: True</code></td>
      <td>count of top-level entries in tmp dir that are not named <code>.capcat</code> or <code>Config</code>. If neither of those dirs exists, count all top-level entries.</td>
    </tr>
    <tr>
      <td>Log file exists</td>
      <td>if <code>-L <path></code> in cmd</td>
      <td>file at that path exists and <code>os.path.getsize() > 0</code></td>
    </tr>
    <tr>
      <td>Timeout flag</td>
      <td>always</td>
      <td>process completed within <code>timeout</code> seconds</td>
    </tr>
  </tbody>
</table>
</div>

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

<div class="table-container">
<table class="centered-table">
  <thead>
    <tr>
      <th>Group</th>
      <th>Pass</th>
      <th>Fail</th>
      <th>Skip</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>global</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <td>init</td>
      <td>3</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <td>single</td>
      <td>8</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <td>fetch</td>
      <td>10</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <td>bundle</td>
      <td>14</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <td>list</td>
      <td>5</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <td>add-source</td>
      <td>3</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <td>remove-source</td>
      <td>5</td>
      <td>0</td>
      <td>3</td>
    </tr>
    <tr>
      <td>generate-config</td>
      <td>3</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <td>tui</td>
      <td>3</td>
      <td>0</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>

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
