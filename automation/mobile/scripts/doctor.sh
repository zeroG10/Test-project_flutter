#!/usr/bin/env bash
# Mobile toolchain doctor — one row per prerequisite: OK / MISSING / WARN + a fix hint.
#
#   scripts/doctor.sh [android|ios|all] [--with-mcp]   default: all on macOS, android elsewhere
#
# --with-mcp also probes the `mobile` MCP server (setup/check_mcp.py). Off by default: it
# may download the package on a cold npx cache, and it is a discovery channel, not the gate.
#
# Exit 1 when a REQUIRED item is MISSING (WARN rows never fail: optional tools and inputs).
# Reads APP_KIND / FLUTTER_DRIVER / build paths from .env by plain KEY=VALUE parsing — the
# file is never sourced. Works with the stock macOS bash 3.2.
set -u

MOBILE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OS="$(uname -s)"
TARGET=""
WITH_MCP=0
for arg in "$@"; do
  case "$arg" in
    --with-mcp) WITH_MCP=1 ;;
    -*) echo "usage: $0 [android|ios|all] [--with-mcp]" >&2; exit 2 ;;
    *) TARGET="$arg" ;;
  esac
done

if [ -z "$TARGET" ]; then
  if [ "$OS" = "Darwin" ]; then TARGET=all; else TARGET=android; fi
fi
case "$TARGET" in
  android|ios|all) ;;
  *) echo "usage: $0 [android|ios|all] [--with-mcp]" >&2; exit 2 ;;
esac
if [ "$TARGET" != "android" ] && [ "$OS" != "Darwin" ]; then
  echo "note: iOS tooling needs macOS — checking android only" >&2
  TARGET=android
fi
WANT_ANDROID=0
WANT_IOS=0
[ "$TARGET" = "android" ] && WANT_ANDROID=1
[ "$TARGET" = "ios" ] && WANT_IOS=1
if [ "$TARGET" = "all" ]; then WANT_ANDROID=1; WANT_IOS=1; fi

# --- .env (data, not code) ---------------------------------------------------------------
env_get() { # env_get KEY DEFAULT
  local v=""
  if [ -f "$MOBILE_DIR/.env" ]; then
    v="$(grep -E "^[[:space:]]*$1=" "$MOBILE_DIR/.env" | tail -n 1 | cut -d= -f2- \
        | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
              -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'\$/\1/")"
  fi
  printf '%s' "${v:-$2}"
}
APP_KIND="$(env_get APP_KIND native | tr '[:upper:]' '[:lower:]')"
FLUTTER_DRIVER="$(env_get FLUTTER_DRIVER native | tr '[:upper:]' '[:lower:]')"
FLUTTER_ENABLED="$(env_get FLUTTER_ENABLED false | tr '[:upper:]' '[:lower:]')"
if [ "$FLUTTER_ENABLED" = "true" ] || [ "$FLUTTER_ENABLED" = "1" ]; then APP_KIND=flutter; fi
ANDROID_APP_PATH="$(env_get ANDROID_APP_PATH ./builds/android/app-debug.apk)"
IOS_APP_PATH="$(env_get IOS_APP_PATH ./builds/ios/App.app)"

# --- table -------------------------------------------------------------------------------
FAILED=0
row()  { printf '%-8s %-27s %-44.44s %s\n' "$1" "$2" "$3" "$4"; }
ok()   { row OK "$1" "$2" ""; }
warn() { row WARN "$1" "$2" "$3"; }
miss() { row MISSING "$1" "$2" "$3"; FAILED=1; }
skip() { row "-" "$1" "$2" ""; }

echo "Mobile doctor — target=$TARGET  app_kind=$APP_KIND  flutter_driver=$FLUTTER_DRIVER  os=$OS"
echo
row STATUS ITEM DETAIL "FIX"
row "------" "----" "------" "---"

# --- shared ------------------------------------------------------------------------------
if [ -f "$MOBILE_DIR/.env" ]; then
  ok ".env" "present"
else
  warn ".env" "not found — defaults in use" "cp .env.example .env"
fi

if command -v uv >/dev/null 2>&1; then
  ok "uv" "$(uv --version 2>/dev/null | head -n 1 | cut -d" " -f1-2)"
else
  miss "uv" "not on PATH" "brew install uv   (or: curl -LsSf https://astral.sh/uv/install.sh | sh)"
fi

if command -v node >/dev/null 2>&1; then
  ok "node" "$(node --version 2>/dev/null)"
else
  miss "node" "not on PATH" "brew install node   (>= 18, required by Appium)"
fi

HAVE_APPIUM=0
DRIVERS_JSON=""
if command -v appium >/dev/null 2>&1; then
  ok "appium" "v$(appium --version 2>/dev/null | tail -n 1)"
  HAVE_APPIUM=1
  DRIVERS_JSON="$(appium driver list --installed --json 2>/dev/null || true)"
else
  miss "appium" "not on PATH" "npm install -g appium"
fi

has_driver() { printf '%s' "$DRIVERS_JSON" | grep -q "\"$1\":"; }
driver_version() {
  printf '%s\n' "$DRIVERS_JSON" | grep -A 3 "\"$1\":" | grep '"version"' | head -n 1 \
    | sed 's/.*: *"\([^"]*\)".*/\1/'
}
check_driver() { # check_driver NAME REQUIRED(1|0) HINT
  if [ "$HAVE_APPIUM" != 1 ]; then
    if [ "$2" = 1 ]; then miss "driver: $1" "appium missing" "$3"; else warn "driver: $1" "appium missing" "$3"; fi
    return
  fi
  if has_driver "$1"; then
    ok "driver: $1" "v$(driver_version "$1")"
  elif [ "$2" = 1 ]; then
    miss "driver: $1" "not installed" "$3"
  else
    warn "driver: $1" "not installed (optional)" "$3"
  fi
}

# --- android -----------------------------------------------------------------------------
if [ "$WANT_ANDROID" = 1 ]; then
  SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
  if [ -n "$SDK" ] && [ -d "$SDK" ]; then
    ok "ANDROID_HOME" "$SDK"
  elif [ -n "$SDK" ]; then
    miss "ANDROID_HOME" "set to $SDK — no such directory" "install the SDK (Android Studio > SDK Manager) or fix the path"
  else
    miss "ANDROID_HOME" "ANDROID_HOME / ANDROID_SDK_ROOT unset" "export ANDROID_HOME=\$HOME/Library/Android/sdk   (Linux: \$HOME/Android/Sdk)"
  fi

  ADB="$(command -v adb 2>/dev/null || true)"
  if [ -z "$ADB" ] && [ -n "$SDK" ] && [ -x "$SDK/platform-tools/adb" ]; then ADB="$SDK/platform-tools/adb"; fi
  if [ -n "$ADB" ]; then
    ok "adb" "$("$ADB" version 2>/dev/null | head -n 1)"
  else
    miss "adb" "not found" "SDK Manager > Android SDK Platform-Tools; add \$ANDROID_HOME/platform-tools to PATH"
  fi

  EMU="$(command -v emulator 2>/dev/null || true)"
  if [ -z "$EMU" ] && [ -n "$SDK" ] && [ -x "$SDK/emulator/emulator" ]; then EMU="$SDK/emulator/emulator"; fi
  if [ -n "$EMU" ]; then
    AVD_LIST="$("$EMU" -list-avds 2>/dev/null | grep -v '^INFO' || true)"
    AVDS="$(printf '%s\n' "$AVD_LIST" | grep -c . || true)"
    if [ "${AVDS:-0}" -gt 0 ]; then
      ok "emulator" "$AVDS AVD(s): $(printf '%s\n' "$AVD_LIST" | tr '\n' ' ')"
    else
      warn "emulator" "installed, no AVD defined" "Android Studio > Device Manager > Create device   (or avdmanager create avd)"
    fi
  else
    miss "emulator" "not found" "SDK Manager > Android Emulator; add \$ANDROID_HOME/emulator to PATH"
  fi

  if java -version >/dev/null 2>&1; then
    ok "java" "$(java -version 2>&1 | head -n 1)"
  else
    miss "java" "no Java runtime" "brew install --cask temurin@17; export JAVA_HOME=\$(/usr/libexec/java_home -v 17)"
  fi

  check_driver uiautomator2 1 "appium driver install uiautomator2"
else
  skip "android" "not in target ($TARGET)"
fi

# --- ios ---------------------------------------------------------------------------------
if [ "$WANT_IOS" = 1 ]; then
  XC="$(xcode-select -p 2>/dev/null || true)"
  case "$XC" in
    *Xcode*.app*)
      ok "xcode" "$(xcodebuild -version 2>/dev/null | head -n 1) at $XC" ;;
    "")
      miss "xcode" "xcode-select -p failed" "install Xcode (App Store); sudo xcode-select -s /Applications/Xcode.app/Contents/Developer" ;;
    *)
      miss "xcode" "CLT only: $XC" "install Xcode (App Store); sudo xcode-select -s /Applications/Xcode.app/Contents/Developer; sudo xcodebuild -runFirstLaunch" ;;
  esac

  SIMS="$(xcrun simctl list devices available 2>/dev/null || true)"
  if [ -n "$SIMS" ]; then
    TOTAL="$(printf '%s\n' "$SIMS" | grep -cE '\((Shutdown|Booted)\)' || true)"
    BOOTED="$(printf '%s\n' "$SIMS" | grep -c '(Booted)' || true)"
    if [ "${TOTAL:-0}" -gt 0 ]; then
      ok "simulators" "$TOTAL available, $BOOTED booted"
    else
      warn "simulators" "simctl works, no simulators" "Xcode > Settings > Platforms > install an iOS runtime"
    fi
  else
    miss "simulators" "xcrun simctl unavailable" "needs full Xcode — see the xcode row"
  fi

  check_driver xcuitest 1 "appium driver install xcuitest"
else
  skip "ios" "not in target ($TARGET)"
fi

# --- flutter (app kind) ------------------------------------------------------------------
if [ "$APP_KIND" = "flutter" ]; then
  if command -v flutter >/dev/null 2>&1; then
    ISSUES="$(flutter doctor 2>/dev/null | grep -cE '^\[(!|✗)\]' || true)"
    if [ "${ISSUES:-0}" -eq 0 ]; then
      ok "flutter" "$(flutter --version 2>/dev/null | head -n 1)"
    else
      warn "flutter" "flutter doctor reports $ISSUES issue(s)" "flutter doctor -v"
    fi
  else
    warn "flutter" "SDK not on PATH (needed only to BUILD the app)" "https://docs.flutter.dev/get-started/install"
  fi
  if [ "$FLUTTER_DRIVER" = "integration" ]; then
    check_driver flutter-integration 1 "appium driver install --source=npm appium-flutter-integration-driver"
  else
    check_driver flutter-integration 0 "only for FLUTTER_DRIVER=integration: appium driver install --source=npm appium-flutter-integration-driver"
  fi
else
  skip "flutter" "APP_KIND=$APP_KIND — not a Flutter app"
fi

# --- inputs & optional -------------------------------------------------------------------
build_check() { # build_check LABEL PATH
  local p="$2"
  case "$p" in
    /*) ;;
    *) p="$MOBILE_DIR/${p#./}" ;;
  esac
  local shown="${p#"$MOBILE_DIR"/}"
  if [ -e "$p" ]; then
    ok "build: $1" "$shown"
  else
    warn "build: $1" "not found: $shown" "drop the build there (builds/README.md) — runs are Blocked until it exists"
  fi
}
[ "$WANT_ANDROID" = 1 ] && build_check android "$ANDROID_APP_PATH"
[ "$WANT_IOS" = 1 ] && build_check ios "$IOS_APP_PATH"

if command -v allure >/dev/null 2>&1; then
  ok "allure" "$(allure --version 2>/dev/null | head -n 1)"
else
  warn "allure" "CLI not found (report viewing only)" "brew install allure"
fi

# --- discovery channel (NOT the gate) ----------------------------------------------------
# The `mobile` MCP server is how an agent reads real screens (accessibility tree) to author
# screen maps and run exploratory sessions — mobile has no crawler like the web recon tool.
# It is never required for an Appium run, so this row is WARN at worst. It is opt-in because
# a cold npx cache downloads the package; a silent failure here costs an hour of guessed ids.
MCP_CHECK="$MOBILE_DIR/../../setup/check_mcp.py"
if [ "$WITH_MCP" != 1 ]; then
  skip "mobile MCP" "not probed — re-run with --with-mcp"
elif [ ! -f "$MCP_CHECK" ]; then
  warn "mobile MCP" "setup/check_mcp.py missing from this clone" "restore it from the template"
elif ! command -v python3 >/dev/null 2>&1; then
  warn "mobile MCP" "python3 not found — cannot probe" "install python3, or probe by hand"
else
  MCP_OUT="$(python3 "$MCP_CHECK" mobile 2>&1 || true)"
  MCP_ROW="$(printf '%s\n' "$MCP_OUT" | grep -E '^(OK|FAIL|SKIP) +mobile' | head -n 1)"
  MCP_DETAIL="$(printf '%s' "$MCP_ROW" | awk '{ $1=""; $2=""; sub(/^ +/, ""); print }')"
  case "$MCP_ROW" in
    OK*)   ok   "mobile MCP" "$MCP_DETAIL" ;;
    SKIP*) warn "mobile MCP" "${MCP_DETAIL:-not verified}" "python3 setup/check_mcp.py mobile" ;;
    *)     warn "mobile MCP" "${MCP_DETAIL:-no answer}" "python3 setup/check_mcp.py mobile — full error + fix hint" ;;
  esac
fi

# --- verdict -----------------------------------------------------------------------------
echo
if [ "$FAILED" = 1 ]; then
  echo "RESULT: MISSING required items for target=$TARGET — fix the rows above. A run now would be Blocked, not green."
  exit 1
fi
echo "RESULT: OK — required toolchain for target=$TARGET present (WARN rows are optional tools or inputs)."
exit 0
