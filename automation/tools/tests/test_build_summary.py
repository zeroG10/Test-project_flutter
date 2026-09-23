"""Offline self-test for build_summary.py: a synthetic allure-results directory with a
passed, a failed and a blocked (skipped) test, checkpoint screenshots and a video.

    cd automation/tools && uv run pytest tests/test_build_summary.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import build_summary as bs

CHECKLIST_MD = """\
# QA Checklist: Authentication

## Welcome

1. [CHK-AUTH-001] Welcome is shown.
2. [CHK-AUTH-002] Session skips Welcome.
3. [CHK-AUTH-003] Login shows its content.
4. [CHK-AUTH-004] Registration shows its fields.
5. [CHK-AUTH-005] A manual-only item.
"""


def _result(
    tmp: Path,
    uid: str,
    name: str,
    status: str,
    chk: list[str],
    start: int,
    message: str = "",
    attachments: list[tuple[str, str]] = (),
) -> None:
    atts = []
    for att_name, ext in attachments:
        source = f"{uid}-{len(atts)}-attachment.{ext}"
        (tmp / source).write_bytes(b"x")
        atts.append({"name": att_name, "source": source, "type": "image/png"})
    data = {
        "name": name,
        "fullName": f"tests.shared.test_auth#{uid}",
        "status": status,
        "statusDetails": {"message": message} if message else {},
        "start": start,
        "stop": start + 20_000,
        "labels": [{"name": "suite", "value": "02 · Authentication"}]
        + [{"name": "tag", "value": c} for c in chk]
        + [{"name": "feature", "value": f"TC-AUTH-{uid[-3:]}"}],
        # checkpoints sit inside steps (allure.step) — must be found there too
        "steps": [{"name": "step", "attachments": atts[:1], "steps": []}],
        "attachments": atts[1:],
    }
    (tmp / f"{uid}-result.json").write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    results = tmp_path / "allure-results"
    results.mkdir()
    _result(
        results,
        "t001",
        "TC-AUTH-001 Welcome <script>alert(1)</script>",
        "passed",
        ["CHK-AUTH-001", "CHK-AUTH-002"],
        1_000_000,
        attachments=[("01 · welcome", "png"), ("02 · jobs-list", "png")],
    )
    _result(
        results,
        "t004",
        "TC-AUTH-004 Login content",
        "failed",
        ["CHK-AUTH-003"],
        1_030_000,
        message="AssertionError: expected 'Log in'",
        attachments=[("screenshot-on-failure-call", "png"), ("video · test_login", "mp4")],
    )
    _result(
        results,
        "t010",
        "TC-AUTH-010 Registration",
        "skipped",
        ["CHK-AUTH-004"],
        1_060_000,
        message="Blocked: no signed-out Welcome after clear data + reinstall",
    )
    (results / "environment.properties").write_text(
        "Platform=iOS\nDevice=iPhone 17 · iOS 26.5\nBuild=1.1.1 (178)\nHarness.commit=abc1234\n",
        encoding="utf-8",
    )
    module = tmp_path / "qa" / "mobile" / "02-authentication"
    module.mkdir(parents=True)
    (module / "authentication-checklist.md").write_text(CHECKLIST_MD, encoding="utf-8")
    return tmp_path


def _build(run_dir: Path, *extra: str) -> tuple[int, str, Path]:
    out = run_dir / "summary"
    code = bs.main(
        [
            "--allure-dir",
            str(run_dir / "allure-results"),
            "--checklist",
            str(run_dir / "qa/mobile/02-authentication/authentication-checklist.md"),
            "--run-label",
            "pytest --platform=ios",
            "--out-dir",
            str(out),
            *extra,
        ]
    )
    page = (out / "index.html").read_text(encoding="utf-8") if code == 0 else ""
    return code, page, out


def test_verdicts_match_trace_results(run_dir: Path) -> None:
    code, page, _ = _build(run_dir)
    assert code == 0
    assert "<b>2 / 5</b>checklist items" in page  # 001+002 passed of 5
    assert "3</b>automated tests: 1 passed, 1 failed, 1 blocked" in page
    # per module: 5 items, 4 automated, 2 passed, 1 failed, 1 blocked, 1 not run
    assert "<td>02 · Authentication</td><td>5</td><td>4</td><td>2</td><td>1</td><td>1</td><td>1</td>" in page


def test_attention_list_and_run_context(run_dir: Path) -> None:
    _, page, _ = _build(run_dir)
    assert "AssertionError: expected &#x27;Log in&#x27;" in page
    assert "Blocked: no signed-out Welcome" in page
    assert "<dd>abc1234</dd>" in page
    assert "<dd>pytest --platform=ios</dd>" in page
    assert "manual-time comparison not recorded" in page


def test_manual_estimate_only_when_given(run_dir: Path) -> None:
    _, page, _ = _build(run_dir, "--manual-minutes-per-check", "20")
    assert "≈ 1.0 h</b>the same 3 checks by hand" in page  # 2 passed + 1 failed


def test_titles_are_escaped(run_dir: Path) -> None:
    _, page, _ = _build(run_dir)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_evidence_is_copied_and_old_output_replaced(run_dir: Path) -> None:
    _, page, out = _build(run_dir)
    assets = out / "assets"
    stale = assets / "stale.png"
    stale.write_bytes(b"old")
    _, page, out = _build(run_dir)
    copied = sorted(p.name for p in assets.iterdir() if p.name != bs.MARKER)
    assert len(copied) == 4  # 2 checkpoints (one from a step) + failure shot + video
    assert not stale.exists()
    assert "01 · welcome" in page and "02 · jobs-list" in page
    assert "<video controls" in page


def test_foreign_assets_folder_is_never_deleted(tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    keep = assets / "someone-else.png"
    keep.write_bytes(b"x")
    bs.AssetCopier(tmp_path)
    assert keep.exists()


def test_empty_run_is_blocked(tmp_path: Path) -> None:
    (tmp_path / "allure-results").mkdir()
    checklist = tmp_path / "c.md"
    checklist.write_text(CHECKLIST_MD, encoding="utf-8")
    code = bs.main(
        ["--allure-dir", str(tmp_path / "allure-results"), "--checklist", str(checklist)]
    )
    assert code == 2
