#!/usr/bin/env bash
# Start an Appium server. Install drivers once (scripts/doctor.sh tells you which are missing):
#   appium driver install uiautomator2
#   appium driver install xcuitest
#   appium driver install --source=npm appium-flutter-integration-driver   # only for FLUTTER_DRIVER=integration
#
#   scripts/start_appium.sh            the shared server (APPIUM_PORT, default 4723)
#   scripts/start_appium.sh ios        the iOS server      (IOS_APPIUM_PORT, else APPIUM_PORT)
#   scripts/start_appium.sh android    the Android server  (ANDROID_APPIUM_PORT, else APPIUM_PORT)
# One server per platform is what lets iOS and Android run at the same time (PARALLEL-RUNS.md);
# scripts/qa.sh starts the ones a run needs.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PORT="${APPIUM_PORT:-4723}"
if [ $# -ge 1 ]; then
  PORT="$(uv run python scripts/run_context.py "$1" --get APPIUM_PORT)"
fi
# session_discovery (local server only): scripts/run.sh lists and closes sessions a killed run left
# behind — such a session, when its newCommandTimeout expires, stops the UiAutomator2 server under the
# NEXT run (seven tests errored in one such case).
exec appium --address "${APPIUM_HOST:-127.0.0.1}" --port "$PORT" --log-level info \
  --allow-insecure "*:session_discovery"
