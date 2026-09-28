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

REASONS_MD = """\
# Why

## Kinds

| Kind | Title | What it means |
|---|---|---|
| person | A person's check | A judgement no assertion can make |

## Checks

| Checks | Kind | Why | Source |
|---|---|---|---|
| CHK-AUTH-005 | person | Layout is visual | 02 plan |
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
        "uuid": uid,
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
def run_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
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
        message="Skipped: Blocked: no signed-out Welcome after clear data + reinstall",
    )
    (results / "environment.properties").write_text(
        "Platform=iOS\nDevice=iPhone 17 · iOS 26.5\nBuild=1.1.1 (178)\nHarness.commit=abc1234\n",
        encoding="utf-8",
    )
    module = tmp_path / "qa" / "mobile" / "02-authentication"
    module.mkdir(parents=True)
    (module / "authentication-checklist.md").write_text(CHECKLIST_MD, encoding="utf-8")
    (tmp_path / "reasons.md").write_text(REASONS_MD, encoding="utf-8")
    real = bs.load_bugs
    monkeypatch.setattr(bs, "load_bugs", lambda: real(tmp_path / "qa" / "mobile"))
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
            "--reasons",
            str(run_dir / "reasons.md"),
            "--redact-env",
            str(run_dir / "no.env"),
            "--no-git",
            "--out-dir",
            str(out),
            *extra,
        ]
    )
    page = (out / "index.html").read_text(encoding="utf-8") if code == 0 else ""
    return code, page, out


def _module(out: Path) -> str:
    return (out / "02-authentication.html").read_text(encoding="utf-8")


def _file_bug(run_dir: Path, name: str, text: str) -> None:
    bugs = run_dir / "qa" / "mobile" / "02-authentication" / "bugs"
    bugs.mkdir(exist_ok=True)
    (bugs / f"{name}.md").write_text(text, encoding="utf-8")


BUG_MD = (
    "# BUG-AUTH-009 — Login content is wrong\n\n"
    "- **Severity:** S3 (minor) — **branch fired:** #3\n"
    "- **Priority:** *proposal* P3 — owner / PM decide.\n\n"
    "## Layer\n\n- [x] App (UI)\n- [ ] Backend\n\n"
    "## Evidence\n\n[shot.png](evidence/BUG-AUTH-009/shot.png) and "
    "[the test cases](../authentication-test-cases.md)\n\n"
    "## Regression info\n\n- Test case: `TC-AUTH-004` — red until the fix.\n"
)


def test_verdicts_match_trace_results(run_dir: Path) -> None:
    code, page, _ = _build(run_dir)
    assert code == 0
    # 5 checks, 4 automated: 001+002 passed, 003 failed (no bug), 004 blocked, 005 not automated
    assert "<b>5</b><span>checks in the QA checklist</span>" in page
    assert "<b>4</b><span>automated · 80%</span>" in page
    assert "<div class='kpi pass'><b>2</b>" in page
    assert "<div class='kpi fail'><b>1</b><span>failed, no defect yet" in page
    assert "<div class='kpi block'><b>1</b>" in page
    assert '<span class="pill fail">Failed</span>' in page  # a failure nobody explained
    row = "<td class='num'>5</td><td class='num'>4</td><td class='num'>2</td><td class='num'>1</td><td class='num'>1</td><td class='num'>1</td>"
    assert row in page


def test_known_defect_holds_its_check_red(run_dir: Path) -> None:
    _file_bug(run_dir, "BUG-AUTH-009", BUG_MD)
    _, page, out = _build(run_dir)
    assert '<span class="pill known">No unexpected failures</span>' in page
    assert "<div class='kpi known'><b>1</b><span>held red by 1 known defect" in page
    assert "<a href='bugs/BUG-AUTH-009.html'>BUG-AUTH-009</a>" in page
    assert "<td class='mono'>AUTH-003</td>" in page  # the check it holds red
    assert "P3 <span class='muted'>proposed</span>" in page
    assert "Held red" in _module(out)


def test_bug_page_renders_the_report(run_dir: Path) -> None:
    _file_bug(run_dir, "BUG-AUTH-009", BUG_MD)
    evidence = run_dir / "qa/mobile/02-authentication/bugs/evidence/BUG-AUTH-009"
    evidence.mkdir(parents=True)
    (evidence / "shot.png").write_bytes(b"x")
    _, _, out = _build(run_dir)
    bug = (out / "bugs" / "BUG-AUTH-009.html").read_text(encoding="utf-8")
    assert "<h2>Layer</h2>" in bug and "<li>☑ App (UI)</li>" in bug and "<li>☐ Backend</li>" in bug
    assert "<a class='shot' href='evidence/BUG-AUTH-009/shot.png'>" in bug
    assert (out / "bugs" / "evidence" / "BUG-AUTH-009" / "shot.png").exists()
    assert "../authentication-test-cases.md" not in bug  # the repository is not published
    assert "the test cases" in bug


def test_a_draft_not_filed_is_not_an_open_defect(run_dir: Path) -> None:
    _file_bug(run_dir, "BUG-AUTH-009", "> **Status: NOT FILED — owner's decision**\n" + BUG_MD)
    _, page, out = _build(run_dir)
    assert "Open defects · 0" in page
    assert not (out / "bugs" / "BUG-AUTH-009.html").exists()


def test_module_page_shows_every_check_with_its_reason(run_dir: Path) -> None:
    _, page, out = _build(run_dir)
    module = _module(out)
    for chk in ("CHK-AUTH-001", "CHK-AUTH-002", "CHK-AUTH-003", "CHK-AUTH-004", "CHK-AUTH-005"):
        assert f"<tr id='{chk}'>" in module
    assert "<b>A person&#x27;s check:</b> Layout is visual (02 plan)" in module
    # the blocked reason next to the verdict, without the harness prefixes
    assert "<div class='why'>no signed-out Welcome after clear data" in module
    assert "<a href='02-authentication.html'>02 · Authentication</a>" in page


def test_a_check_without_a_reason_is_reported(run_dir: Path) -> None:
    (run_dir / "reasons.md").write_text(REASONS_MD.replace("CHK-AUTH-005", "CHK-AUTH-099"))
    _, page, _ = _build(run_dir)
    assert "Reason missing" in page
    assert "check without a test and without a written reason: CHK-AUTH-005" in page


def test_expand_ids() -> None:
    assert bs.expand_ids("CHK-AUTH-081…-083, -090") == [
        "CHK-AUTH-081", "CHK-AUTH-082", "CHK-AUTH-083", "CHK-AUTH-090"
    ]
    assert bs.expand_ids("CHK-ORDD-023, -025 and CHK-PRF-030") == [
        "CHK-ORDD-023", "CHK-ORDD-025", "CHK-PRF-030"
    ]


def test_history_and_stability(run_dir: Path) -> None:
    runs = str(run_dir / "allure-results")
    _, page, _ = _build(run_dir, "--history-dir", runs, "--history-dir", runs)
    assert "The last <b>2</b> full runs gave the same verdict for every one of <b>3</b> tests" in page
    assert page.count("<td class='mono nowrap'>allure-results</td>") == 2


def test_titles_are_escaped(run_dir: Path) -> None:
    _, page, out = _build(run_dir)
    for html_text in (page, _module(out)):
        assert "<script>alert(1)</script>" not in html_text
    assert "&lt;script&gt;" in _module(out)


def test_evidence_is_copied_and_old_output_replaced(run_dir: Path) -> None:
    _, page, out = _build(run_dir)
    assets = out / "assets"
    stale = assets / "stale.png"
    stale.write_bytes(b"old")
    _, page, out = _build(run_dir)
    copied = sorted(p.name for p in assets.iterdir() if p.name != bs.MARKER)
    assert len(copied) == 4  # 2 checkpoints (one from a step) + failure shot + video
    assert not stale.exists()
    module = _module(out)
    assert "01 · welcome" in module and "02 · jobs-list" in module
    assert "<video controls" in module
    assert "<a class='shot' href='assets/t001-0-attachment.png'>" in page  # the strip


def test_public_copy_leaves_out_text_and_video(run_dir: Path) -> None:
    results = run_dir / "allure-results"
    data = json.loads((results / "t001-result.json").read_text(encoding="utf-8"))
    (results / "api-attachment.txt").write_text('{"jobs": ["someone else\'s job"]}')
    data["attachments"].append({"name": "GET /job → 200", "source": "api-attachment.txt"})
    (results / "t001-result.json").write_text(json.dumps(data), encoding="utf-8")
    _, _, out = _build(run_dir, "--public")
    module = _module(out)
    assert "someone else" not in module
    assert "GET /job → 200 — text, not in the shared copy" in module
    assert "<video" not in module
    assert not list((out / "assets").glob("*.mp4"))


def test_video_attached_in_a_fixture_teardown_is_found(run_dir: Path) -> None:
    results = run_dir / "allure-results"
    (results / "v-1-attachment.mp4").write_bytes(b"x")
    container = {
        "children": ["t010"],
        "afters": [{"name": "_screen_video::0", "attachments": [
            {"name": "video · test_registration", "source": "v-1-attachment.mp4", "type": "video/mp4"}
        ], "steps": []}],
    }
    (results / "c1-container.json").write_text(json.dumps(container), encoding="utf-8")
    _, _, out = _build(run_dir)
    assert (out / "assets" / "v-1-attachment.mp4").exists()
    assert "teardown · _screen_video" in _module(out)


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


def test_artifact_fragment_has_no_document_skeleton(run_dir: Path) -> None:
    _, _, out = _build(run_dir)
    fragment = (out / "page.html").read_text(encoding="utf-8")
    assert fragment.startswith("<title>Concert Mobile QA Report</title>")
    for tag in ("<!doctype", "<html", "<head>", "<body"):
        assert tag not in fragment.lower()
    # the three theme states: system dark, explicit dark, explicit light
    assert ':root:not([data-theme="light"])' in fragment
    assert ':root[data-theme="dark"]' in fragment
    # the other pages are whole documents
    assert _module(out).lower().startswith("<!doctype html>")


def test_test_account_is_hidden_in_text(run_dir: Path) -> None:
    env = run_dir / "test.env"
    env.write_text("APP_USER_EMAIL=secret.tech@example.org\nAPP_USER_PHONE=+12025550111\n")
    red = bs.Redactor(env, None)
    assert red.text("UI login as secret.tech@example.org") == "UI login as ‹test account›"
    assert red.text("phone (202) 555-0111 or +12025550111") == (
        "phone ‹test account› or ‹test account›"
    )


def test_redaction_box_pixelates_only_the_page_copy(tmp_path: Path) -> None:
    from PIL import Image, ImageDraw

    src = tmp_path / "shot-attachment.png"
    img = Image.new("RGB", (402, 100), (255, 255, 255))
    ImageDraw.Draw(img).text((20, 40), "secret.tech@example.org", fill=(0, 0, 0))
    img.save(src)
    boxes = tmp_path / "boxes.json"
    boxes.write_text(json.dumps({"points_width": 402, "boxes": {src.name: [[0, 30, 402, 60]]}}))
    copier = bs.AssetCopier(tmp_path / "out", bs.Redactor(None, boxes), tmp_path)
    copier(src)
    before = Image.open(src).crop((0, 30, 402, 60)).tobytes()
    after = Image.open(tmp_path / "out" / "assets" / src.name).crop((0, 30, 402, 60)).tobytes()
    assert before != after  # the copy is pixelated
    assert Image.open(src).crop((0, 30, 402, 60)).tobytes() == before  # the original untouched


def test_every_test_has_expandable_details(run_dir: Path) -> None:
    _, _, out = _build(run_dir)
    module = _module(out)
    assert module.count("<details class='test' id='t-") == 3
    assert "<p class='phase'>test</p>" in module
