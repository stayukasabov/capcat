"""Guard the canonical project URL baked into shipped HTML templates.

The project site moved from capcat.org to stayukasabov.github.io/capcat.
The retired domain is not owned by the project, so a stale link in a
generated archive sends readers somewhere outside our control.
"""

import re
from pathlib import Path

import pytest

import capcat

CANONICAL_URL = "https://stayukasabov.github.io/capcat/"
RETIRED_DOMAIN = "capcat.org"

LOGO_ANCHOR = re.compile(
    r'<a\s+href="([^"]*)"[^>]*>\s*<svg[^>]*class="capcat-logo"',
    re.IGNORECASE | re.DOTALL,
)


def _template_dir() -> Path:
    return Path(capcat.__file__).parent / "templates"


def _templates() -> list[Path]:
    return sorted(_template_dir().glob("*.html"))


def test_templates_ship_with_package():
    """templates/ must exist and contain HTML files."""
    assert _templates(), f"no HTML templates found in {_template_dir()}"


@pytest.mark.parametrize("template", _templates(), ids=lambda p: p.name)
def test_template_does_not_reference_retired_domain(template):
    """No shipped template may link to the retired capcat.org domain."""
    text = template.read_text(encoding="utf-8")
    assert RETIRED_DOMAIN not in text, (
        f"{template.name} references retired domain {RETIRED_DOMAIN}; "
        f"use {CANONICAL_URL}"
    )


@pytest.mark.parametrize("template", _templates(), ids=lambda p: p.name)
def test_template_logo_links_to_canonical_url(template):
    """Each template's capcat logo must link to the canonical site URL."""
    text = template.read_text(encoding="utf-8")
    hrefs = LOGO_ANCHOR.findall(text)
    assert hrefs, f"{template.name} has no anchor wrapping a .capcat-logo svg"
    for href in hrefs:
        assert href == CANONICAL_URL, (
            f"{template.name} logo links to {href!r}, expected {CANONICAL_URL!r}"
        )
