"""Full ordered test catalog — 74 acceptance tests.

Sentinels replaced at runtime by run_acceptance.py:
  __FIXTURE_URL__  → file://<tmp_dir>/mock_feed.xml
  __TMP__          → absolute path of the test's tmp dir
"""
from __future__ import annotations

TESTS: list[dict] = [
    # ── global (7) ────────────────────────────────────────────────────────────
    {
        "id": 1, "group": "global", "label": "No args prints help",
        "cmd": ["capcat"],
        "expected_exit": 0, "expected_in_output": ["capcat"],
        "creates_files": False, "needs_init": False, "pre_init": False,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
    {
        "id": 2, "group": "global", "label": "--help flag",
        "cmd": ["capcat", "--help"],
        "expected_exit": 0, "expected_in_output": ["Usage"],
        "creates_files": False, "needs_init": False, "pre_init": False,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
    {
        "id": 3, "group": "global", "label": "-h flag",
        "cmd": ["capcat", "-h"],
        "expected_exit": 0, "expected_in_output": ["Usage"],
        "creates_files": False, "needs_init": False, "pre_init": False,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
    {
        "id": 4, "group": "global", "label": "--version prints version",
        "cmd": ["capcat", "--version"],
        "expected_exit": 0, "expected_in_output": ["capcat"],
        "creates_files": False, "needs_init": False, "pre_init": False,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
    {
        "id": 5, "group": "global", "label": "-L logs to file",
        "cmd": ["capcat", "-L", "__TMP__/capcat.log", "fetch", "hn", "--count", "1"],
        "expected_exit": 0, "expected_in_output": [],
        "creates_files": True, "needs_init": True, "pre_init": False,
        "is_tui": False, "passthrough": False, "timeout": 60, "fixture": None,
    },
    {
        "id": 6, "group": "global", "label": "-L missing filename exits 1",
        "cmd": ["capcat", "-L"],
        "expected_exit": 1, "expected_in_output": [],
        "creates_files": False, "needs_init": False, "pre_init": False,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
    {
        "id": 7, "group": "global", "label": "Unknown command exits 1",
        "cmd": ["capcat", "unknowncmd_xyz"],
        "expected_exit": 1, "expected_in_output": [],
        "creates_files": False, "needs_init": False, "pre_init": False,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
    # ── init (3) ──────────────────────────────────────────────────────────────
    {
        "id": 8, "group": "init", "label": "Fresh init",
        "cmd": ["capcat", "init"],
        "expected_exit": 0, "expected_in_output": ["initialized"],
        "creates_files": False, "needs_init": False, "pre_init": False,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
    {
        "id": 9, "group": "init", "label": "Already init'd exits 1",
        "cmd": ["capcat", "init"],
        "expected_exit": 1, "expected_in_output": [],
        "creates_files": False, "needs_init": False, "pre_init": True,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
    {
        "id": 10, "group": "init", "label": "--reinit on existing succeeds",
        "cmd": ["capcat", "init", "--reinit"],
        "expected_exit": 0, "expected_in_output": [],
        "creates_files": False, "needs_init": False, "pre_init": True,
        "is_tui": False, "passthrough": False, "timeout": 30, "fixture": None,
    },
]
