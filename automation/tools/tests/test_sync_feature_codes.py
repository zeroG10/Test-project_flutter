"""Self-test for the feature-code resolution in sync_checklist_to_sheets.py.

Offline: no Sheets access — only the registry parser, the resolution order
(--feature-code > qa/shared/feature-codes.md > filename fallback) and the
--target derivation from the per-module checklist path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import sync_checklist_to_sheets as sync

REGISTRY_MD = """\
# Feature codes

| slug | code | platform/notes |
|---|---|---|
| authentication | AUTH | web + mobile (separate sheets) |
| `checklist-order-list.md` | ordl | mobile — slug normalised from filename |
| managers-checklist | MGR | web |

Text outside the table is ignored. | not | a | row without leading pipe
"""


@pytest.fixture
def registry(tmp_path: Path) -> Path:
    p = tmp_path / "feature-codes.md"
    p.write_text(REGISTRY_MD, encoding="utf-8")
    return p


def test_parse_registry_normalises_slugs_and_codes(registry):
    assert sync.parse_feature_codes(registry) == {
        "authentication": "AUTH",
        "order-list": "ORDL",
        "managers": "MGR",
    }


def test_missing_registry_is_optional(tmp_path):
    assert sync.parse_feature_codes(tmp_path / "nope.md") == {}
    assert sync.DEFAULT_FEATURE_PREFIX_MAP == {}


def test_invalid_code_fails_loudly(tmp_path):
    p = tmp_path / "feature-codes.md"
    p.write_text(
        "| slug | code |\n|---|---|\n| surveys | SURVEYS1 |\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="Invalid feature code"):
        sync.parse_feature_codes(p)


def test_conflicting_duplicate_slug_fails(tmp_path):
    p = tmp_path / "feature-codes.md"
    p.write_text(
        "| slug | code |\n|---|---|\n| a-b | AB |\n| a-b | ABC |\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="mapped to both"):
        sync.parse_feature_codes(p)


def test_resolution_order(registry, tmp_path, capsys):
    fmap = sync.parse_feature_codes(registry)
    # registry hit, both filename conventions
    assert (
        sync.derive_feature_code(tmp_path / "authentication-checklist.md", fmap)
        == "AUTH"
    )
    assert (
        sync.derive_feature_code(tmp_path / "checklist-authentication.md", fmap)
        == "AUTH"
    )
    # CLI override wins over registry
    assert (
        sync.derive_feature_code(
            tmp_path / "authentication-checklist.md", fmap, "login"
        )
        == "LOGIN"
    )
    # fallback: first 4 letters of the slug, with a WARN
    assert (
        sync.derive_feature_code(tmp_path / "checklist-photo-tags.md", fmap) == "PHOT"
    )
    assert "[WARN] No feature mapping for 'photo-tags'" in capsys.readouterr().out
    # invalid override is rejected
    with pytest.raises(SystemExit, match="--feature-code"):
        sync.derive_feature_code(tmp_path / "x-checklist.md", fmap, "toolong")


def test_registry_default_path_is_qa_shared():
    assert sync.FEATURE_CODES_FILE == sync.REPO_ROOT / "qa" / "shared" / "feature-codes.md"


def test_per_module_layout_slug_and_target(registry, tmp_path):
    # The real layout: qa/<platform>/<NN-module>/<module>-checklist.md
    web = tmp_path / "qa" / "web" / "01-authentication" / "authentication-checklist.md"
    mobile = tmp_path / "qa" / "mobile" / "01-authentication" / "authentication-checklist.md"
    shared = tmp_path / "qa" / "shared" / "checklists" / "checklist-owasp-top10.md"
    fmap = sync.parse_feature_codes(registry)
    # slug strips "-checklist", ignores the NN- module folder
    assert sync.normalize_slug(web.stem) == "authentication"
    assert sync.derive_feature_code(web, fmap) == "AUTH"
    assert sync.derive_feature_code(mobile, fmap) == "AUTH"
    assert sync.normalize_slug(shared.stem) == "owasp-top10"
    # --target from the platform folder right after qa/
    assert sync.derive_target(web) == "web"
    assert sync.derive_target(mobile) == "mobile"
    assert sync.derive_target(shared) == "web"
    # relative paths as typed on the CLI work too
    assert sync.derive_target(Path("../../qa/web/01-authentication/authentication-checklist.md")) == "web"
    # the platform segment is the one after the LAST qa/ — a parent folder named
    # web/ or qa/ does not decide
    assert sync.derive_target(Path("/home/web/qa/mobile/02-orders/orders-checklist.md")) == "mobile"
    # neither platform in the path -> None (caller must ask, never default)
    assert sync.derive_target(tmp_path / "qa" / "_templates" / "checklist.md") is None
    assert sync.derive_target(tmp_path / "somewhere" / "x-checklist.md") is None


def test_parse_markdown_uses_registry(registry, tmp_path):
    md = tmp_path / "checklist-order-list.md"
    md.write_text(
        "# QA Checklist: Order list\n\n## List\n\n1. [CHK-ORDL-001] Check A.\n2. Check B.\n",
        encoding="utf-8",
    )
    parsed = sync.parse_markdown(md, sync.parse_feature_codes(registry))
    assert parsed.feature_code == "ORDL"
    assert [it.check_id for it in parsed.items] == ["CHK-ORDL-001", None]
    assert sync.assign_missing_ids(parsed, existing_max=1) == 1
    assert parsed.items[1].check_id == "CHK-ORDL-002"
