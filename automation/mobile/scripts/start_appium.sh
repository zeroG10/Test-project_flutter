#!/usr/bin/env bash
# Start the Appium server. Install drivers once (scripts/doctor.sh tells you which are missing):
#   appium driver install uiautomator2
#   appium driver install xcuitest
#   appium driver install --source=npm appium-flutter-integration-driver   # only for FLUTTER_DRIVER=integration
set -euo pipefail
# session_discovery (local server only): scripts/run.sh lists and closes sessions a killed run left
# behind — such a session, when its newCommandTimeout expires, stops the UiAutomator2 server under the
# NEXT run (Android stage, module 02 run 4: seven tests errored).
appium --address "${APPIUM_HOST:-127.0.0.1}" --port "${APPIUM_PORT:-4723}" --log-level info \
  --allow-insecure "*:session_discovery"
