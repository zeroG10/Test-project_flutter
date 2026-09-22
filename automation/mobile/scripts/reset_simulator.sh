#!/usr/bin/env bash
# Reset iOS simulator state. Pass device UDID or name as first arg, defaults to "iPhone 15".
set -euo pipefail
DEVICE="${1:-iPhone 15}"
xcrun simctl shutdown "$DEVICE" || true
xcrun simctl erase "$DEVICE"
xcrun simctl boot "$DEVICE"
