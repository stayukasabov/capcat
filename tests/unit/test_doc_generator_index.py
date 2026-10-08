"""Regression guard for the generated docs index timestamp.

`generate_index()` emitted the shell literal `$(date)` instead of a real
date, so every regenerated index claimed an uninterpolated timestamp.
"""

import datetime as dt
import importlib.util
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = PROJECT_ROOT / "scripts" / "doc_generator.py"


def _load_generator_module():
    spec = importlib.util.spec_from_file_location("doc_generator", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def generated_index(tmp_path):
    module = _load_generator_module()
    generator = module.DocumentationGenerator(analyzer=None, output_dir=str(tmp_path))
    # generate_api_docs() normally creates api/ earlier in the pipeline.
    (tmp_path / "api").mkdir()
    generator.generate_index()
    return (tmp_path / "api" / "index.md").read_text(encoding="utf-8")


def test_index_has_no_uninterpolated_shell_placeholder(generated_index):
    """The index must not ship a literal $(date) placeholder."""
    assert "$(date)" not in generated_index


def test_index_records_todays_date(generated_index):
    """The index must record a real generation date in ISO form."""
    match = re.search(r"Last generated:\s*(\d{4}-\d{2}-\d{2})", generated_index)
    assert match, "no 'Last generated: YYYY-MM-DD' line found in index"
    assert match.group(1) == dt.date.today().isoformat()
