#!/usr/bin/env python3
"""One command for a run: which platform (or both at once), what to run, and everything it needs
started.

    scripts/qa.sh <ios|android|both> <what> [--name NAME] [--sequential] [--dry-run]
                  [-- pytest args]

    what:  all                     the whole regression of the platform
           auth | 02 | order-list  one module — number, name or a unique part; several: 02,03
           tests/shared/…::test_x  a path or node id, passed to pytest as it is

    scripts/qa.sh both all                 # iOS and Android regression side by side
    scripts/qa.sh android auth             # one module on Android (its Android-only tests included)
    scripts/qa.sh ios 08,09 --name fix-1   # two modules on iOS → results/ios/<date>-fix-1/
    scripts/qa.sh both all --dry-run       # show the plan, start nothing

For each platform it boots the device if none is up, starts that platform's Appium server if it is
not answering, and hands the run to scripts/run.sh — which keeps its rules: a committed tree, a
results folder of its own, one run per platform. `both` runs the two side by side when they share
nothing (each its own test account and Appium server — PARALLEL-RUNS.md); otherwise it says why
not, and `--sequential` runs iOS, then Android. At the end: what passed, failed and could not run
on each platform. Exit code 0 only if every run's was 0."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

MOBILE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOBILE))

from config.settings import PLATFORMS, settings  # noqa: E402

SHARED = MOBILE / "tests" / "shared"
BOOT_TIMEOUT = 420  # seconds: a cold emulator boot on a busy Mac
APPIUM_TIMEOUT = 60
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# --------------------------------------------------------------------------- #
# What to run
# --------------------------------------------------------------------------- #


def modules() -> dict[str, str]:
    """``{"02": "authentication", …}`` — from the checklists' folders, qa/mobile/<NN-module>/."""
    found = {}
    for folder in sorted((MOBILE.parents[1] / "qa" / "mobile").glob("[0-9][0-9]-*")):
        number, _, slug = folder.name.partition("-")
        found[number] = slug.replace("-", "_")
    return found


def resolve_module(word: str) -> str:
    """A module's slug from its number, its name or a unique part of it
    (``auth`` → ``authentication``)."""
    known = modules()
    key = word.strip().lower().replace("-", "_")
    if key.zfill(2) in known:
        return known[key.zfill(2)]
    exact = [slug for slug in known.values() if slug == key]
    partial = [slug for slug in known.values() if key and key in slug]
    hits = exact or partial
    if len(hits) != 1:
        listing = ", ".join(f"{n} {s.replace('_', '-')}" for n, s in known.items())
        problem = "matches several modules" if hits else "is not a module"
        raise SystemExit(f"'{word}' {problem}. Modules: {listing}")
    return hits[0]


def targets(platform: str, what: str) -> list[str]:
    """The pytest paths of ``what`` on ``platform``: the shared tests and the platform's own."""
    own = MOBILE / "tests" / platform
    has_own = own.is_dir() and any(own.glob("test_*.py"))
    if what == "all":
        return ["tests/shared", *([f"tests/{platform}"] if has_own else [])]
    if "/" in what or "::" in what or what.endswith(".py"):
        return [what]
    paths: list[str] = []
    for word in what.split(","):
        slug = resolve_module(word)
        files = [SHARED / f"test_{slug}.py", *sorted(own.glob(f"test_*{slug}.py"))]
        existing = [str(f.relative_to(MOBILE)) for f in files if f.exists()]
        if not existing:
            raise SystemExit(f"module '{slug}' has no test file for {platform}")
        paths += existing
    return paths


# --------------------------------------------------------------------------- #
# What a run needs
# --------------------------------------------------------------------------- #


def sh(*cmd: str, timeout: float = 60) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def ios_booted() -> bool:
    listing = sh("xcrun", "simctl", "list", "devices", "booted").stdout
    return (
        re.search(rf"^\s*{re.escape(settings.ios_device_name)} \(", listing, re.MULTILINE)
        is not None
    )


def emulator_serial() -> str:
    """The running emulator's adb serial (``emulator-5554``), or "" — a phone on a USB cable is
    not it, and with two devices attached a bare ``adb shell`` answers "more than one device"."""
    found = re.search(r"^(emulator-\d+)\s+device$", sh("adb", "devices").stdout, re.MULTILINE)
    return found.group(1) if found else ""


def android_booted() -> bool:
    serial = emulator_serial()
    if not serial:
        return False
    done = sh("adb", "-s", serial, "shell", "getprop", "sys.boot_completed")
    return done.stdout.strip() == "1"


def device_command(platform: str) -> list[str]:
    if platform == "ios":
        return ["xcrun", "simctl", "boot", settings.ios_device_name]
    return [
        "emulator",
        "-avd",
        settings.android_device_name,
        *shlex.split(settings.android_emulator_args),
    ]


def ensure_device(platform: str, logs: Path) -> None:
    booted = ios_booted if platform == "ios" else android_booted
    if booted():
        print(f"  {platform}: device is up")
        return
    cmd = device_command(platform)
    print(f"  {platform}: booting — {' '.join(shlex.quote(c) for c in cmd)}")
    if platform == "ios":
        done = sh(*cmd, timeout=120)
        if done.returncode != 0 and "current state: Booted" not in done.stderr:
            raise SystemExit(f"Blocked: {done.stderr.strip() or 'simctl boot failed'}")
        subprocess.run(["open", "-a", "Simulator"], check=False)
        sh("xcrun", "simctl", "bootstatus", settings.ios_device_name, "-b", timeout=BOOT_TIMEOUT)
    else:
        log = (logs / "emulator.log").open("ab")
        subprocess.Popen(cmd, stdout=log, stderr=log, start_new_session=True)  # noqa: S603 — outlives this script
    deadline = time.monotonic() + BOOT_TIMEOUT
    while time.monotonic() < deadline:
        if booted():
            print(f"  {platform}: device is up")
            return
        time.sleep(5)
    raise SystemExit(
        f"Blocked: the {platform} device did not boot in {BOOT_TIMEOUT} s (see {logs})"
    )


def appium_url(platform: str) -> str:
    return f"http://{settings.appium_host}:{settings.appium_port_for(platform)}"


def appium_up(platform: str) -> bool:
    try:
        with urllib.request.urlopen(f"{appium_url(platform)}/status", timeout=5) as resp:  # noqa: S310 — local server
            return bool(json.load(resp).get("value", {}).get("ready"))
    except OSError:
        return False


def ensure_appium(platform: str, logs: Path) -> None:
    if appium_up(platform):
        print(f"  {platform}: Appium answers at {appium_url(platform)}")
        return
    print(f"  {platform}: starting Appium at {appium_url(platform)}")
    log = (logs / f"appium-{platform}.log").open("ab")
    subprocess.Popen(  # noqa: S603 — outlives this script, like the device
        ["bash", "scripts/start_appium.sh", platform],
        cwd=MOBILE,
        stdout=log,
        stderr=log,
        start_new_session=True,
    )
    deadline = time.monotonic() + APPIUM_TIMEOUT
    while time.monotonic() < deadline:
        if appium_up(platform):
            return
        time.sleep(2)
    raise SystemExit(
        f"Blocked: no Appium at {appium_url(platform)} after {APPIUM_TIMEOUT} s (see {log.name})"
    )


# --------------------------------------------------------------------------- #
# The runs
# --------------------------------------------------------------------------- #


def results_dir(platform: str, name: str) -> Path:
    return MOBILE / "results" / platform / f"{datetime.now():%Y-%m-%d}-{name}"


def summary(folder: Path) -> tuple[dict[str, int], list[str]]:
    """Passed / Failed / Blocked of a run, as trace_results reads the Allure statuses, and the
    red tests."""
    counts = {"Passed": 0, "Failed": 0, "Blocked": 0}
    red: list[str] = []
    for file in folder.glob("*-result.json"):
        try:
            result = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        status = {"passed": "Passed", "failed": "Failed", "broken": "Failed"}.get(
            result.get("status"), "Blocked"
        )
        counts[status] += 1
        if status != "Passed":
            red.append(f"{status}: {result.get('name', '?')}")
    return counts, sorted(red)


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    extra: list[str] = []
    if "--" in raw:
        cut = raw.index("--")
        raw, extra = raw[:cut], raw[cut + 1 :]
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("platform", choices=(*PLATFORMS, "both"))
    parser.add_argument("what", help="all | module(s) | a pytest path")
    parser.add_argument("--name", default="", help="the run's name (default: <what>-<HHMM>)")
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="with 'both': iOS, then Android — not side by side",
    )
    parser.add_argument("--dry-run", action="store_true", help="show the plan; start nothing")
    args = parser.parse_args(raw)

    platforms = ["ios", "android"] if args.platform == "both" else [args.platform]
    label = re.sub(r"[^a-z0-9]+", "-", args.what.lower().split("::")[-1]).strip("-")[:30] or "run"
    name = args.name or f"{label}-{datetime.now():%H%M}"
    if not NAME_RE.match(name):
        raise SystemExit("--name: lower-case letters, digits and '-' only")
    plan = {p: targets(p, args.what) for p in platforms}

    side_by_side = len(platforms) == 2 and not args.sequential
    if side_by_side:
        ok, why = settings.can_run_in_parallel()
        if not ok:
            raise SystemExit(
                f"iOS and Android cannot run side by side: {why}.\n"
                "See PARALLEL-RUNS.md, or add --sequential to run iOS, then Android."
            )

    print(f"run '{name}' — {' + '.join(platforms)}" + (" side by side" if side_by_side else ""))
    for p in platforms:
        print(f"  {p}: {' '.join(plan[p])}{' ' + ' '.join(extra) if extra else ''}")
        print(
            f"       Appium {appium_url(p)} · account {settings.account_key(p) or 'NOT SET'} · "
            f"results {results_dir(p, name).relative_to(MOBILE)}"
        )
    if args.dry_run:
        for p in platforms:
            up = (ios_booted if p == "ios" else android_booted)()
            device = "is up" if up else "would boot: " + " ".join(device_command(p))
            server = "answers" if appium_up(p) else "would start"
            print(f"  {p}: device {device} · Appium {server}")
        print("dry run: nothing started")
        return 0

    for p in platforms:
        if results_dir(p, name).exists():
            raise SystemExit(
                f"refused: {results_dir(p, name)} already exists — pick another --name"
            )
    logs = MOBILE / "results" / ".logs"
    logs.mkdir(parents=True, exist_ok=True)
    print("preparing:")
    for p in platforms:
        ensure_device(p, logs)
        ensure_appium(p, logs)

    def run_env(platform: str) -> dict[str, str]:
        """The run's environment: on Android, adb and the driver are pinned to the emulator."""
        env = dict(os.environ)
        if platform == "android" and emulator_serial():
            env["ANDROID_SERIAL"] = emulator_serial()
        return env

    codes: dict[str, int] = {}
    if side_by_side:
        running = {}
        for p in platforms:
            log_path = logs / f"{datetime.now():%Y-%m-%d}-{name}-{p}.log"
            print(f"  {p}: started — live log: tail -f {log_path.relative_to(MOBILE)}")
            running[p] = subprocess.Popen(  # noqa: S603
                ["bash", "scripts/run.sh", p, name, *plan[p], *extra],
                cwd=MOBILE,
                env=run_env(p),
                stdout=log_path.open("wb"),
                stderr=subprocess.STDOUT,
            )
        for p, proc in running.items():
            codes[p] = proc.wait()
    else:
        for p in platforms:
            codes[p] = subprocess.run(
                ["bash", "scripts/run.sh", p, name, *plan[p], *extra],
                cwd=MOBILE,
                env=run_env(p),
                check=False,
            ).returncode  # noqa: S603

    print("\nresult:")
    for p in platforms:
        folder = results_dir(p, name)
        counts, red = summary(folder)
        if not sum(counts.values()):
            where = folder.relative_to(MOBILE)
            print(f"  {p}: Blocked — no test result in {where} (exit {codes[p]}); nothing ran")
            continue
        print(
            f"  {p}: {counts['Passed']} passed · {counts['Failed']} failed · "
            f"{counts['Blocked']} blocked (exit {codes[p]}) — "
            f"allure serve {folder.relative_to(MOBILE)}"
        )
        for line in red:
            print(f"      {line}")
    print(
        "A red test is not re-run until green: first decide — the app (a bug), the test, "
        "or the environment."
    )
    return max(codes.values(), default=1)


if __name__ == "__main__":
    sys.exit(main())
