"""Run context and Allure grouping for the mobile stack (README "Allure report").

Everything here is derived from files in the repo — nothing is typed in by hand:

* module label ``02 · Authentication`` <- CHK feature code (``qa/shared/feature-codes.md``,
  slug -> code) + the module folder ``qa/mobile/02-authentication/``;
* product build <- ``BUILD_INFO.txt`` next to the build (``builds/<platform>/``);
* harness commit <- ``git rev-parse`` of this repository.

A value that cannot be read is reported as ``not recorded`` — never guessed.
"""

import json
import re
import subprocess
from functools import cache
from pathlib import Path

from config.settings import MOBILE_ROOT, normalize_platform, settings

REPO_ROOT = MOBILE_ROOT.parents[1]
FEATURE_CODES = REPO_ROOT / "qa" / "shared" / "feature-codes.md"
QA_MOBILE = REPO_ROOT / "qa" / "mobile"
NOT_RECORDED = "not recorded"
UNMAPPED_MODULE = "Unmapped (no CHK id)"
PLATFORM_TITLE = {"android": "Android", "ios": "iOS"}

_CODE_ROW = re.compile(r"^\|\s*`?([a-z0-9-]+)`?\s*\|\s*`?([A-Z]{2,5})`?\s*\|")
_CHK_CODE = re.compile(r"^CHK-([A-Z]{2,5})-\d{3,}$")

# Allure "Categories" tab: first match wins. The doctrine order — a red result is first
# checked against the expectation, a Blocked one is not a product verdict at all.
ALLURE_CATEGORIES = [
    {
        "name": "Blocked — environment, build, session or test data (not a product verdict)",
        "matchedStatuses": ["failed", "broken", "skipped"],
        "messageRegex": "(?s).*Blocked:.*",
    },
    {
        "name": "Expected element not shown in time — check the expectation, then the app",
        "matchedStatuses": ["failed", "broken"],
        "traceRegex": "(?s).*(TimeoutException|NoSuchElementException).*",
    },
    {
        "name": "Assertion failed — expected ≠ actual (possible product defect)",
        "matchedStatuses": ["failed"],
    },
    {
        "name": "Harness error — fix the test code, not the expectation",
        "matchedStatuses": ["broken"],
    },
]


@cache
def module_labels() -> dict[str, str]:
    """Feature code -> ``NN · Module`` for every module folder under qa/mobile/."""
    slug_to_code: dict[str, str] = {}
    if FEATURE_CODES.exists():
        for line in FEATURE_CODES.read_text(encoding="utf-8").splitlines():
            m = _CODE_ROW.match(line)
            if m:
                slug_to_code[m.group(1)] = m.group(2)
    labels: dict[str, str] = {}
    if QA_MOBILE.is_dir():
        for folder in sorted(p for p in QA_MOBILE.iterdir() if p.is_dir()):
            number, _, slug = folder.name.partition("-")
            if number.isdigit() and slug in slug_to_code:
                title = slug.replace("-", " ").capitalize()
                labels[slug_to_code[slug]] = f"{number} · {title}"
    return labels


def module_for(chk_ids: list[str] | tuple[str, ...]) -> str:
    """Module label of the first CHK id with a known feature code."""
    labels = module_labels()
    for chk_id in chk_ids:
        m = _CHK_CODE.match(chk_id)
        if m and m.group(1) in labels:
            return labels[m.group(1)]
    return UNMAPPED_MODULE


@cache
def build_info(platform: str) -> dict[str, str]:
    """``key: value`` lines of BUILD_INFO.txt beside the build; {} when there is none."""
    info_file = settings.app_path(normalize_platform(platform)).parent / "BUILD_INFO.txt"
    if not info_file.exists():
        return {}
    info: dict[str, str] = {}
    for line in info_file.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() and value.strip():
            info[key.strip()] = value.strip()
    return info


@cache
def harness_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return NOT_RECORDED
    return out.stdout.strip() or NOT_RECORDED


def env_label(platform: str) -> str:
    """One line per run configuration, read by trace_results.py (``env`` label)."""
    version = build_info(platform).get("version", NOT_RECORDED)
    return f"{PLATFORM_TITLE[platform]} · {settings.device_label(platform)} · build {version}"


def run_context(platform: str) -> dict[str, str]:
    """What produced the verdicts of this run — Allure "Environment" widget."""
    info = build_info(platform)
    return {
        "Platform": PLATFORM_TITLE[platform],
        "Device": settings.device_label(platform),
        "App": info.get("app", NOT_RECORDED),
        "App id": settings.app_id(platform),
        "Build": info.get("version", NOT_RECORDED),
        "App source": info.get("branch", NOT_RECORDED),
        "Build defines": info.get("defines", NOT_RECORDED),
        "App kind": f"{settings.app_kind} (driver: {settings.flutter_driver})",
        "Appium": settings.appium_url,
        "Harness commit": harness_commit(),
        "Video evidence": settings.evidence_video,
    }


def write_allure_run_files(results_dir: Path, platform: str) -> None:
    """environment.properties + categories.json into the Allure results directory."""
    results_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"{key.replace(' ', '.')}={value}" for key, value in run_context(platform).items()]
    (results_dir / "environment.properties").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (results_dir / "categories.json").write_text(
        json.dumps(ALLURE_CATEGORIES, indent=2, ensure_ascii=False), encoding="utf-8"
    )
