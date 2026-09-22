"""Fixture-based self-test for trace_results.py (layer-4 traceability closure).

Runs offline: an inline fake Playwright JSON report + fake allure result files
cover Passed / Failed / Blocked (skipped) / not-run / orphan-tag paths.

    cd automation/tools && uv run pytest
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import trace_results as tr

CHECKLIST_MD = """\
# QA Checklist: Authentication

## Access and Permissions

1. [CHK-AUTH-001] Check that the Login page is reachable without an authenticated session.
2. [CHK-AUTH-002] Check that the Login page denies access when credentials belong to a disabled account and shows the generic error text.
3. [CHK-AUTH-003] Check that the Set Password page blocks access when the token is expired.
4. [CHK-AUTH-004] Check that a manual-only item stays not run.

## Open questions

- Q1: something
"""

SHARED_MD = """\
## A01 Broken access control

- [ ] [CHK-SEC-001] IDOR: other user cannot read another user's object | pipes are escaped
- [x] [CHK-SEC-002] Anonymous cannot reach protected resources
"""

PLAYWRIGHT_JSON = {
    "config": {},
    "suites": [
        {
            "title": "auth.spec.ts",
            "file": "auth.spec.ts",
            "specs": [],
            "suites": [
                {
                    "title": "Login",
                    "file": "auth.spec.ts",
                    "specs": [
                        {
                            "title": "CHK-AUTH-001 login page reachable",
                            "tags": [
                                "CHK-AUTH-001",
                                "smoke",
                            ],  # json reporter strips '@'
                            "file": "auth.spec.ts",
                            "line": 12,
                            "tests": [
                                {
                                    "projectName": "chromium",
                                    "status": "expected",
                                    "annotations": [],
                                    "results": [{"status": "passed", "retry": 0}],
                                },
                                {
                                    "projectName": "firefox",
                                    "status": "expected",
                                    "annotations": [],
                                    "results": [{"status": "passed", "retry": 0}],
                                },
                            ],
                        },
                        {
                            "title": "disabled account is rejected",
                            "tags": ["@CHK-AUTH-002"],  # tag with '@' still extracted
                            "file": "auth.spec.ts",
                            "line": 30,
                            "tests": [
                                {
                                    "projectName": "chromium",
                                    "status": "unexpected",
                                    "annotations": [],
                                    "results": [
                                        {
                                            "status": "failed",
                                            "retry": 0,
                                            "error": {
                                                "message": "\x1b[31mError: expect(locator).toBeVisible()\x1b[39m\n\nCall log:\n  - waiting",
                                            },
                                        }
                                    ],
                                }
                            ],
                        },
                    ],
                    "suites": [],
                }
            ],
        }
    ],
    "stats": {},
}

ALLURE_RESULTS = [
    {
        "name": "test_expired_token",
        "fullName": "tests.smoke.test_set_password#test_expired_token",
        "status": "skipped",
        "statusDetails": {"message": "Skipped: staging build missing"},
        "labels": [
            {"name": "tag", "value": "CHK-AUTH-003"},
            {"name": "suite", "value": "smoke"},
        ],
    },
    {
        "name": "test_idor[other-user]",
        "fullName": "tests.security.test_access_control#test_idor",
        "status": "passed",
        "labels": [{"name": "tag", "value": "@pytest.mark.chk('CHK-SEC-001')"}],
    },
    {
        "name": "test_orphan",
        "fullName": "tests.smoke.test_misc#test_orphan",
        "status": "broken",
        "statusDetails": {"message": "RuntimeError: driver crashed"},
        "labels": [{"name": "tag", "value": "CHK-ZZZ-999"}],
    },
]


@pytest.fixture
def workspace(tmp_path: Path) -> dict[str, Path]:
    checklist = tmp_path / "checklist-authentication.md"
    checklist.write_text(CHECKLIST_MD, encoding="utf-8")
    shared = tmp_path / "checklist-owasp.md"
    shared.write_text(SHARED_MD, encoding="utf-8")
    pw = tmp_path / "results.json"
    pw.write_text(json.dumps(PLAYWRIGHT_JSON), encoding="utf-8")
    allure = tmp_path / "allure-results"
    allure.mkdir()
    for i, d in enumerate(ALLURE_RESULTS):
        (allure / f"{i:04d}-result.json").write_text(json.dumps(d), encoding="utf-8")
    (allure / "container.json").write_text("{}", encoding="utf-8")  # must be ignored
    return {
        "checklist": checklist,
        "shared": shared,
        "pw": pw,
        "allure": allure,
        "tmp": tmp_path,
    }


def test_checklist_parser_accepts_numbered_and_bullet_forms(workspace):
    items = tr.parse_checklists([workspace["checklist"], workspace["shared"]])
    ids = [it.chk_id for it in items]
    assert ids == [
        "CHK-AUTH-001",
        "CHK-AUTH-002",
        "CHK-AUTH-003",
        "CHK-AUTH-004",
        "CHK-SEC-001",
        "CHK-SEC-002",
    ]
    assert items[0].section == "Access and Permissions"
    assert items[4].section == "A01 Broken access control"


def test_playwright_loader_extracts_ids_from_tags_titles_and_ancestors(workspace):
    results = tr.load_playwright_results(workspace["pw"])
    assert len(results) == 3  # 2 projects for spec 1 + 1 for spec 2
    first = results[0]
    assert first.test_id == "auth.spec.ts:12 [chromium]"
    assert first.chk_ids == ("CHK-AUTH-001",)
    assert first.status == "passed"
    failed = results[2]
    assert failed.chk_ids == ("CHK-AUTH-002",)
    assert failed.status == "failed"
    assert (
        failed.detail == "Error: expect(locator).toBeVisible()"
    )  # ANSI stripped, first line only


def test_playwright_describe_level_tag_is_inherited_by_every_child(tmp_path):
    # Playwright applies a describe-level tag/title tag to all tests inside it,
    # so one failing child makes the whole CHK ID Failed — never partially green.
    report = {
        "suites": [
            {
                "title": "session.spec.ts",
                "file": "session.spec.ts",
                "specs": [],
                "suites": [
                    {
                        "title": "Session @CHK-AUTH-001",
                        "file": "session.spec.ts",
                        "suites": [],
                        "specs": [
                            {
                                "title": "keeps session",
                                "tags": [],
                                "file": "session.spec.ts",
                                "line": 5,
                                "tests": [
                                    {
                                        "projectName": "chromium",
                                        "status": "expected",
                                        "results": [{"status": "passed"}],
                                    }
                                ],
                            },
                            {
                                "title": "expires session",
                                "tags": [],
                                "file": "session.spec.ts",
                                "line": 9,
                                "tests": [
                                    {
                                        "projectName": "chromium",
                                        "status": "unexpected",
                                        "results": [
                                            {
                                                "status": "timedOut",
                                                "error": {"message": "Test timeout"},
                                            }
                                        ],
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        ]
    }
    p = tmp_path / "results.json"
    p.write_text(json.dumps(report), encoding="utf-8")
    results = tr.load_playwright_results(p)
    assert [r.chk_ids for r in results] == [("CHK-AUTH-001",), ("CHK-AUTH-001",)]
    assert [r.status for r in results] == ["passed", "failed"]
    assert tr.verdict_for(results) == "Failed"


def test_allure_loader_reads_tag_labels_and_maps_statuses(workspace):
    results = tr.load_allure_results(workspace["allure"])
    by_id = {r.chk_ids: r for r in results}
    skipped = by_id[("CHK-AUTH-003",)]
    assert skipped.status == "skipped"
    assert skipped.detail == "Skipped: staging build missing"
    marker = by_id[("CHK-SEC-001",)]  # pytest marker recorded as a tag label
    assert marker.status == "passed"
    assert (
        marker.test_id
        == "tests.security.test_access_control#test_idor (test_idor[other-user])"
    )
    assert by_id[("CHK-ZZZ-999",)].status == "failed"  # broken -> failed


def test_verdicts_and_summary(workspace):
    items = tr.parse_checklists([workspace["checklist"], workspace["shared"]])
    results = tr.load_playwright_results(workspace["pw"]) + tr.load_allure_results(
        workspace["allure"]
    )
    rows, orphans = tr.build_rows(items, results)
    verdicts = {r.item.chk_id: r.verdict for r in rows}
    assert verdicts == {
        "CHK-AUTH-001": "Passed",  # all tagged tests passed
        "CHK-AUTH-002": "Failed",  # one failed
        "CHK-AUTH-003": "Blocked",  # skipped, none failed
        "CHK-AUTH-004": "",  # no tagged test -> not run
        "CHK-SEC-001": "Passed",
        "CHK-SEC-002": "",
    }
    assert set(orphans) == {"CHK-ZZZ-999"}
    s = tr.summarize(rows)
    assert (s.total, s.automated, s.passed, s.failed, s.blocked, s.not_run) == (
        6,
        4,
        2,
        1,
        1,
        2,
    )
    assert s.not_run == s.total - (s.passed + s.failed + s.blocked)


@pytest.mark.parametrize(
    "statuses,expected",
    [
        ([], ""),
        (["passed"], "Passed"),
        (["passed", "passed"], "Passed"),
        (["passed", "skipped"], "Blocked"),
        (["skipped"], "Blocked"),
        (["passed", "skipped", "failed"], "Failed"),
    ],
)
def test_verdict_rules(statuses, expected):
    results = [tr.TestResult(f"t{i}", "allure", s) for i, s in enumerate(statuses)]
    assert tr.verdict_for(results) == expected


def test_playwright_flaky_and_unexecuted_are_never_green():
    flaky = {
        "projectName": "",
        "status": "flaky",
        "results": [
            {"status": "failed", "error": {"message": "boom"}},
            {"status": "passed"},
        ],
    }
    assert tr._playwright_test_status(flaky) == ("failed", "boom")
    unexecuted = {"projectName": "", "status": "skipped", "results": []}
    assert tr._playwright_test_status(unexecuted)[0] == "skipped"


def test_cli_dry_run_writes_nothing_and_prints_table(workspace, capsys):
    rc = tr.main(
        [
            "--platform",
            "web",
            "--checklist",
            str(workspace["checklist"]),
            "--checklist",
            str(workspace["shared"]),
            "--playwright-json",
            str(workspace["pw"]),
            "--allure-dir",
            str(workspace["allure"]),
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "| CHK-AUTH-001 |" in out and "| Passed |" in out
    assert "| CHK-AUTH-002 |" in out and "| Failed |" in out
    assert "| CHK-AUTH-003 |" in out and "| Blocked |" in out
    assert (
        "| CHK-AUTH-004 | Check that a manual-only item stays not run. | 0 |  | no tagged test"
        in out
    )
    assert (
        "IDOR: other user cannot read another user's object \\| pipes are escaped"
        in out
    )
    assert "## Tagged tests with no checklist item" in out and "CHK-ZZZ-999" in out
    assert "Summary: total=6 automated=4 Passed=2 Failed=1 Blocked=1 Not run=2" in out
    assert (
        not list(workspace["tmp"].glob("*.md.out"))
        and not (workspace["tmp"] / "report.md").exists()
    )


def test_cli_out_writes_report_and_truncates_check_text(workspace):
    out_md = workspace["tmp"] / "reports" / "trace.md"
    rc = tr.main(
        [
            "--platform",
            "mobile",
            "--checklist",
            str(workspace["checklist"]),
            "--allure-dir",
            str(workspace["allure"]),
            "--out",
            str(out_md),
        ]
    )
    assert rc == 0
    text = out_md.read_text(encoding="utf-8")
    assert text.startswith("# Automated traceability — mobile")
    long_row = next(ln for ln in text.splitlines() if ln.startswith("| CHK-AUTH-002 |"))
    check_cell = long_row.split(" | ")[1]
    assert len(check_cell) == tr.CHECK_TEXT_WIDTH and check_cell.endswith("…")


def test_empty_results_source_is_blocked_and_nonzero_exit(workspace, capsys):
    empty_dir = workspace["tmp"] / "empty-allure"
    empty_dir.mkdir()
    rc = tr.main(
        [
            "--platform",
            "api",
            "--checklist",
            str(workspace["checklist"]),
            "--allure-dir",
            str(empty_dir),
            "--dry-run",
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    assert "BLOCKED — empty run" in captured.out
    assert "Not run=4" in captured.out
    assert "Zero tests found" in captured.err


def test_cli_requires_a_results_source_and_out(workspace):
    with pytest.raises(SystemExit) as exc:
        tr.main(
            [
                "--platform",
                "web",
                "--checklist",
                str(workspace["checklist"]),
                "--dry-run",
            ]
        )
    assert exc.value.code == 2
    with pytest.raises(SystemExit) as exc:
        tr.main(
            [
                "--platform",
                "web",
                "--checklist",
                str(workspace["checklist"]),
                "--playwright-json",
                str(workspace["pw"]),
            ]
        )
    assert exc.value.code == 2


# --------------------------------------------------------------------------- #
# Canonical CHK id, corrupt results, run context
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("pool", "expected"),
    [
        ("CHK-AUTH-001 login", ("CHK-AUTH-001",)),
        ("@CHK-AUTH-1000 four digits stay valid", ("CHK-AUTH-1000",)),
        ("CHK-AB-001 two-letter code", ("CHK-AB-001",)),
        ("CHK-ABCDE-001 five-letter code", ("CHK-ABCDE-001",)),
        ("CHK-A-001 one-letter code is not an id", ()),
        ("CHK-ABCDEF-001 six letters is not an id", ()),
        ("CHK-AUTH-01 two digits is not an id", ()),
        ("CHK-AUTH1-001 digits in the code are not allowed", ()),
    ],
)
def test_canonical_chk_id_regex(pool, expected):
    # One contract with automation/{api,mobile}/conftest.py and the Sheets sync:
    # an id a runner accepts must never be invisible to traceability.
    assert tr.extract_chk_ids(pool) == expected


def test_checklist_parser_accepts_four_digit_ids(tmp_path: Path):
    md = tmp_path / "big-checklist.md"
    md.write_text(
        "# QA Checklist: Big\n\n## A\n\n1. [CHK-BIG-0999] item\n2. [CHK-BIG-1000] item\n",
        encoding="utf-8",
    )
    ids = [it.chk_id for it in tr.parse_checklist(md)]
    assert ids == ["CHK-BIG-0999", "CHK-BIG-1000"]


def test_corrupt_allure_result_blocks_the_whole_run(workspace, capsys):
    (workspace["allure"] / "9999-result.json").write_text("{not json", encoding="utf-8")
    out = workspace["tmp"] / "trace.md"
    rc = tr.main(
        [
            "--platform",
            "api",
            "--checklist",
            str(workspace["checklist"]),
            "--allure-dir",
            str(workspace["allure"]),
            "--out",
            str(out),
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    assert "Unreadable allure result" in captured.err
    assert "BLOCKED — results unreadable" in captured.out
    report = out.read_text(encoding="utf-8")
    assert "BLOCKED — results unreadable" in report
    assert "| Passed |" not in report and "| CHK-AUTH-001 |" not in report


def test_corrupt_playwright_json_blocks_the_whole_run(workspace, capsys):
    workspace["pw"].write_text("[]", encoding="utf-8")  # valid JSON, wrong shape
    rc = tr.main(
        [
            "--platform",
            "web",
            "--checklist",
            str(workspace["checklist"]),
            "--playwright-json",
            str(workspace["pw"]),
            "--dry-run",
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    assert "not a JSON object" in captured.err
    assert "no verdicts produced" in captured.out


def test_run_context_is_rendered_and_unknowns_are_not_guessed(workspace, capsys):
    rc = tr.main(
        [
            "--platform",
            "web",
            "--checklist",
            str(workspace["checklist"]),
            "--playwright-json",
            str(workspace["pw"]),
            "--allure-dir",
            str(workspace["allure"]),
            "--target",
            "https://staging.example.test",
            "--run-label",
            "smoke, chromium",
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "## Run context" in out
    assert "- Target: `https://staging.example.test`" in out
    assert "- Run label (suite / filter): `smoke, chromium`" in out
    assert "- Product build / version: *not recorded*" in out
    assert "Browser projects (Playwright): `chromium`" in out
    assert "Not covered by this run" in out


def test_build_run_context_reads_playwright_projects_and_allure_labels(workspace):
    sources = [
        ("playwright", workspace["pw"], tr.load_playwright_results(workspace["pw"])),
        ("allure", workspace["allure"], tr.load_allure_results(workspace["allure"])),
    ]
    ctx = tr.build_run_context(sources, build="1.2.3", commit="abc1234")
    assert ctx.build == "1.2.3"
    assert ctx.harness_commit == "abc1234"
    assert "chromium" in ctx.projects
    lines = "\n".join(tr.render_run_context(ctx))
    assert "`1.2.3`" in lines and "`abc1234`" in lines
