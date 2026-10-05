#!/usr/bin/env bash
# One named test run per platform, its results kept apart from every other run.
#
#   scripts/run.sh <ios|android> <name> [pytest args...]
#   scripts/run.sh android 02-auth tests/shared/test_authentication.py
#   EVIDENCE_VIDEO=auto scripts/run.sh ios final-1
#
# Writes Allure results to results/<platform>/<YYYY-MM-DD>-<name>/ (gitignored) plus RUN_INFO.txt
# (harness commit, command, start / end, exit code) — the run context trace_results.py and
# mobile_summary.py report. Refuses:
#   - a results folder that already exists (a run is never overwritten or mixed with another);
#   - uncommitted changes to tracked files (owner rule: commit before every run) — ALLOW_DIRTY=1
#     overrides for a throwaway debug run, and RUN_INFO.txt then says the tree was dirty;
#   - a second run of the SAME platform while one is going (one device per platform);
#   - a run of the OTHER platform while one is going, unless the two share nothing: each platform its
#     own test account and its own Appium server (.env: IOS_USER_* / ANDROID_USER_*,
#     IOS_APPIUM_PORT / ANDROID_APPIUM_PORT — PARALLEL-RUNS.md). Then iOS and Android run side by side.
# A plain `uv run pytest` without this script writes to results/_scratch/ (pyproject.toml).
# Both platforms, modules by name, devices and Appium started for you: scripts/qa.sh.
set -euo pipefail

MOBILE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
usage() { echo "usage: $0 <ios|android> <name> [pytest args...]" >&2; exit 2; }

[ $# -ge 2 ] || usage
PLATFORM="$1"
NAME="$2"
shift 2
case "$PLATFORM" in ios|android) ;; *) usage ;; esac
[[ "$NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "name: lower-case letters, digits and '-' only" >&2; exit 2; }

cd "$MOBILE_DIR"
OUT="results/$PLATFORM/$(date +%Y-%m-%d)-$NAME"
if [ -e "$OUT" ]; then
  echo "refused: $OUT already exists — pick another name; a run is never overwritten" >&2
  exit 3
fi

DIRTY="no"
# the harness the run STARTS on (a commit made while it runs must not be recorded as its harness)
HARNESS="$(git rev-parse --short HEAD) on $(git rev-parse --abbrev-ref HEAD)"
if ! git diff --quiet HEAD -- 2>/dev/null; then
  if [ "${ALLOW_DIRTY:-0}" != "1" ]; then
    echo "refused: uncommitted changes to tracked files — commit before the run (or ALLOW_DIRTY=1 for a debug run)" >&2
    git status --short --untracked-files=no >&2
    exit 3
  fi
  DIRTY="yes (ALLOW_DIRTY=1)"
fi

# Android: the emulator keeps the DNS server of the network it booted on (netsimd --host-dns).
# Once the Mac moves to another network, no name resolves on the device and every test ends
# Blocked at the UI login (module 09 Android run 4, after the Mac slept). Restart the emulator.
if [ "$PLATFORM" = "android" ]; then
  API_HOST="$(sed -n 's|^API_BASE_URL=https\{0,1\}://\([^/:]*\).*|\1|p' .env 2>/dev/null | head -1)"
  if [ -n "$API_HOST" ] && adb shell "ping -c 1 -W 5 $API_HOST" 2>&1 | grep -q "unknown host"; then
    echo "refused: the device cannot resolve $API_HOST (DNS) — the emulator keeps the DNS of the network it booted on; restart it" >&2
    exit 3
  fi
  # A hung System UI ("Application Not Responding: com.android.systemui") took UiAutomator2 down
  # 40 min into a final run and blocked every cold start after it (step 6, 2026-10-02)
  if adb shell dumpsys window 2>/dev/null | grep -q "mCurrentFocus=.*Application Not Responding"; then
    echo "refused: an 'Application Not Responding' window is up on the device — cold-boot the emulator (-no-snapshot-load)" >&2
    exit 3
  fi
fi

# What this platform's run uses: its Appium server, its account (a fingerprint, never the email)
# and whether the two platforms may run side by side.
eval "$(uv run python scripts/run_context.py "$PLATFORM")"

# One lock per platform. Ours is taken FIRST and the other platform's looked at after, so two runs
# starting in the same second cannot both miss each other.
LOCK="results/.run.$PLATFORM.lock"
OTHER_LOCK="results/.run.$OTHER_PLATFORM.lock"
mkdir -p "results/$PLATFORM"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "refused: another $PLATFORM run holds $LOCK ($(cat "$LOCK/owner" 2>/dev/null || echo unknown)) — one run per platform at a time" >&2
  exit 3
fi
echo "$PLATFORM $NAME pid $$" > "$LOCK/owner"
if [ -d "$OTHER_LOCK" ] && [ "$PARALLEL_OK" != "yes" ]; then
  rmdir "$LOCK" 2>/dev/null || rm -rf "$LOCK"
  echo "refused: a $OTHER_PLATFORM run is going ($(cat "$OTHER_LOCK/owner" 2>/dev/null || echo unknown)) and the platforms cannot run side by side: $PARALLEL_WHY (PARALLEL-RUNS.md)" >&2
  exit 3
fi

# RUN_INFO.txt is written when the run ends (also on Ctrl-C): pytest's --clean-alluredir
# (pyproject.toml) empties the results folder when the run starts.
STARTED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
CODE="interrupted"
finish() {
  if [ -d "$OUT" ]; then
    {
      echo "platform:  $PLATFORM"
      echo "name:      $NAME"
      echo "harness:   $HARNESS"
      echo "dirty:     $DIRTY"
      echo "command:   uv run pytest --platform=$PLATFORM --alluredir=$OUT $ARGS"
      echo "appium:    $APPIUM_URL"
      echo "account:   $ACCOUNT_KEY (fingerprint; parallel with $OTHER_PLATFORM: $PARALLEL_OK)"
      echo "video:     EVIDENCE_VIDEO=${EVIDENCE_VIDEO:-<default>}"
      echo "started:   $STARTED"
      echo "finished:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "exit code: $CODE"
    } > "$OUT/RUN_INFO.txt"
  fi
  rm -rf "$LOCK"
}
ARGS="$*"
trap finish EXIT
mkdir -p "$OUT"

# Close every Appium session a killed run left behind on THIS platform's server (we hold its lock;
# a live run of the other platform is on its own server, or it was refused above). A leftover
# session stops the device's UiAutomator2 server when its newCommandTimeout expires — under THIS
# run (module 02 run 4). Needs start_appium.sh's session_discovery.
APPIUM="$APPIUM_URL"
for sid in $(curl -s -m 10 "$APPIUM/appium/sessions" | python3 -c \
    'import json,sys; print(" ".join(s["id"] for s in json.load(sys.stdin).get("value") or [] if isinstance(s, dict)))' \
    2>/dev/null); do
  echo "closing a leftover Appium session $sid"
  curl -s -m 60 -X DELETE "$APPIUM/session/$sid" >/dev/null || true
done

# No idle sleep while the run goes: on battery the Mac slept 13.8 min a minute into module 09
# Android run 5 — the gesture in flight hung, the API connection died, one job cleanup failed.
# (`-i` does not stop a closed lid from sleeping.)
KEEP_AWAKE=()
command -v caffeinate >/dev/null && KEEP_AWAKE=(caffeinate -i)

set +e
# (bash 3.2 + set -u: an empty array is "unbound" — hence the ${…+…} form)
${KEEP_AWAKE[@]+"${KEEP_AWAKE[@]}"} uv run pytest --platform="$PLATFORM" --alluredir="$OUT" "$@"
CODE=$?
set -e
echo "results: $OUT (exit $CODE)"
exit "$CODE"
