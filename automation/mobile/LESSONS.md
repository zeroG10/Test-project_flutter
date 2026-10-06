# LESSONS.md — what cost time on the first mobile product, so it does not cost it again

Written from the first mobile product this template automated: a Flutter app, driven through the native drivers
(XCUITest on an iPhone simulator, UiAutomator2 on an Android emulator), against a shared, slow test environment;
iOS first, Android added on the same suite. Each lesson is the mechanism, then the case that taught it. Read it
before the first recon of a mobile product; add a lesson when something costs a day — a mechanism, not a story.

## The tree lies — what the accessibility tree says is not what the user sees

- **Flutter exposes only what is on screen.** An off-screen row is absent from the tree, not hidden: "no row X"
  proves nothing until the list was scrolled through. Read long lists by scrolling and collecting, with a check
  that the scroll actually moved (a walk that "moved" more than the drag is a lost walk — read again from the top).
- **"Visible" in the tree can be undrawn on the screen.** An error label stayed in the tree, reported visible,
  long after it disappeared from the screen; an empty-state picture was in the tree with `visible=false` while
  drawn. Where the tree and the screen disagree, the oracle is the pixels (`helpers/pixels.py`: a colour, a
  region's brightness) — calibrated once against the real screens, never guessed.
- **Stale nodes after "back".** On return to a list, the cards were in the tree but marked invisible and carried
  old values. Count by presence after the screen settled; never assert "nothing there" on the first read.
- **Two layers, one label.** A list item and the title of the screen it opens can carry the same label; a toast's
  text can merge with a banner's. Anchor on the element's type or container (`screens/` maps), use "contains" for
  merged toasts, and never take "a label is present" as "this screen is open".
- **iOS lists hidden elements first.** XCUITest `find_elements` returned off-screen matches (empty rect) before the
  visible ones: "the n-th on screen" comes from the page source, read when two consecutive sources agree.

## Typing and gestures

- **Android `send_keys` replaces, it does not type.** UiAutomator2 sets the text (ACTION_SET_TEXT): the field's
  current text is replaced, a masked field takes it digit by digit, and Flutter accepts it only into a FOCUSED
  field — tap, let the focus settle, then type. Typing through the IME (`mobile: type`) can drop the first key:
  read the field back and retype once if it differs (`pages/base_page.py`).
- **A keyboard moves the layout.** Coordinates from a screenshot taken before the keyboard opened are wrong after;
  tests use locators, never coordinates. On iOS, `hide_keyboard()` presses Done — which may submit the form.
- **Flutter flings.** A drag released at once keeps scrolling; hold the finger before release (longer on Android),
  drag near the edge where nothing is tappable, and wait for the list to stop before tapping a card.
- **An edge swipe "back" is ignored while the screen is still sliding in.** Use the app's own Back control.
- **A picker or gallery grid settles late.** Two reads a moment apart must agree before a tap lands in it.
- **UiSelector strings are not unescaped on the device.** `\\.` in a quoted value never matches; write `[.]`.
  The offline evaluator of Android locators (`unit_tests/android_dumps.py`) follows the device, not Python.

## The device and the machine

- **The emulator keeps the DNS of the network it booted on.** After the Mac changed network nothing resolved and
  every test went Blocked at sign-in. Boot it with fixed DNS servers (`ANDROID_EMULATOR_ARGS`); `run.sh` refuses a
  run when the device cannot resolve the API host.
- **Pin the device's time zone and read dates from the device.** The Mac's automatic time zone switched mid-run and
  date checks missed by hours. Expected dates are built from the device's own time (`driver.get_device_time`), the
  emulator boots with `-timezone`.
- **A sleeping Mac breaks a run.** On battery it slept a minute into a run: the gesture in flight hung and a cleanup
  failed. `run.sh` holds the machine awake (`caffeinate -i`); a closed lid still sleeps — say so to whoever runs it.
- **A hung System UI takes the driver down.** "Application Not Responding: System UI" stopped UiAutomator2 and every
  cold start after it; `run.sh` refuses to start with such a window up, the fix is a cold boot.
- **A killed run leaves a session that kills the next one.** Its `newCommandTimeout` expired under the next run and
  stopped the driver there. `run.sh` closes leftover sessions first (Appium's `session_discovery`); never kill
  pytest without closing its session.
- **A long Android run outlives its driver.** Start a fresh session per module and revive a dead one (conftest);
  one session for a whole regression lost it to an unrelated crash.
- **A phone on a USB cable is a second device.** A bare `adb shell` then answers "more than one device"; pin the
  run to the emulator (`ANDROID_SERIAL`, `qa.sh` does it).
- **A busy Mac doubles a run.** Indexing after a restart, a crashing driver of a peripheral — runs took twice as long.
  Wait until the load settles before a run that matters.

## The app's state and data

- **A permission prompt answered once is remembered.** "Don't allow" on the notifications prompt came back on the
  next cold start only after the app's flags were reset; a test that answers a prompt restores the permission in
  its `finally`. On Android 13+ clearing the app's data brings the prompt back.
- **`mobile: clearApp` on a recent iOS broke the app's container.** Reinstall instead of clearing.
- **Seed through the API, sweep before you seed.** Every record a test creates carries a marker the cleanup refuses
  to go without; ids must not be prefixes of each other when a list is searched with "contains"; a run interrupted
  midway leaves records the next run's preconditions sweep first.
- **Generated data must be free on the server.** A "fictional" phone range was partly taken by people testing by hand;
  check before use (`free_fictional_*`), Blocked when none is free.
- **The app keeps a cache the server does not.** Offline, the app showed records the server had deleted and named
  them in a reconnect dialog; tests that cross offline start from a clean app or close that dialog.
- **The app's log tells why.** A Flutter app's own log (the Dart VM service — `scripts/recon/app_logs.py`) named
  reasons logcat did not; it holds tokens — read it, never commit it.

## Running

- **A rate limit can be shared by everything behind one address.** The test environment refused code confirmations
  (`429 Too Many Requests`) after about three in a minute — for any account from the same machine, and the app showed
  it as "Incorrect code.". One platform stayed under it; two at once did not (`PARALLEL-RUNS.md`). Sign in through
  the UI once per run where the product allows, and keep sign-in-heavy modules to one platform at a time.
- **Prove red before trusting green.** `--prove-red` breaks every expected text a test routes through `expected`;
  three tests passed it once because they asserted nothing through it — a real gap, found only this way.
- **Repeat before you report.** Three consecutive identical full runs separated the app's red from the harness's:
  the first two series stopped on environment faults (a hung System UI, a time-zone flip), each fixed in the harness
  before the series restarted. Report the run context of every verdict.
- **A second platform changes shared code.** Lock the first platform's locators while the second is added
  (`unit_tests/test_ios_locator_guard.py`) and re-run the first before release (`SECOND-PLATFORM.md`).
