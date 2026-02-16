# Troubleshooting

## Exit Code -9 / "Capcat exited with error code: -9"

**Symptom**: Running `./capcat` returns `Capcat exited with error code: -9`.

**Root Cause**: Missing `pynput` dependency. The Python import fails at startup and the wrapper reports the process exit as -9.

**Fix**:
```bash
source venv/bin/activate
pip install pynput
```

Or rebuild all dependencies:
```bash
./scripts/fix_dependencies.sh --force
```

**Confirm working**:
```bash
./capcat list sources
```

**Why pynput is required**: The `lb` (Lobsters) and `hn` (Hacker News) sources use `pynput` for keyboard input handling in interactive/TUI mode. It is listed in `requirements.txt` but may be absent if the venv was built before the requirement was added or after a partial install.

---

## Diagnostic Script

`test_exit_9_diagnosis.py` in the project root runs systematic capcat operations with timeout protection to identify which operation triggers a failure. Use it when exit codes are unexpected:

```bash
source venv/bin/activate
python test_exit_9_diagnosis.py
```

Output categorises each test as PASS, FAIL, TIMEOUT, or KILLED (exit -9/137/143).

---

## Other Common Issues

See `CLAUDE.md` → "Common Issues" section for dependency rebuild, module not found, and source failure diagnostics.
