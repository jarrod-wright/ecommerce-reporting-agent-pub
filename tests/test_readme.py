"""README verification harness (T14).

Machine-checks that README.md keeps its required structure and that every
relative link (and any badge image) resolves to a real path in the repo — so the
README cannot silently rot into broken links or a missing section.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"

REQUIRED_SECTIONS = [
    "Status",
    "Quickstart",
    "Architecture",
    "Security",
    "Crown jewels",
    "Known limitations",
    "License",
]


def _readme_text() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_exists_and_is_not_a_stub():
    assert README.is_file()
    assert len(_readme_text()) > 2048, "README looks like a stub (<2KB)"


def test_exactly_one_h1():
    h1s = [ln for ln in _readme_text().splitlines() if re.match(r"^# \S", ln)]
    assert len(h1s) == 1, f"expected exactly one H1, found {len(h1s)}"


@pytest.mark.parametrize("section", REQUIRED_SECTIONS)
def test_required_section_present(section):
    assert re.search(rf"^#{{2,3}} .*{re.escape(section)}", _readme_text(), re.M), (
        f"missing required section: {section}"
    )


def test_all_relative_links_resolve():
    """Every non-http markdown link/image target resolves to a real repo path."""
    text = _readme_text()
    # [text](target) for both links and ![alt](img) images
    targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
    broken = []
    for target in targets:
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:  # pure in-page anchor
            continue
        if not (REPO_ROOT / path_part).exists():
            broken.append(target)
    assert not broken, f"README links to non-existent paths: {broken}"
