"""The app-wide offline banner and the "Connection restored" dialog (Android stage, step 5).

Source: recon A2 — qa/shared/recon-2026-10-01-android-offline.md, dumps
qa/shared/recon-dumps/android-2026-10-01-offline/ (``list_offline.xml``,
``auth_login_offline_6s.xml``, ``online_restored.xml``). Android only: the iOS simulator's
network cannot be switched off, so no iOS recon exists for these elements.

The banner lies under the app bar on every screen (y 283–409 px) and over the content there
(D-OFF-7, owner 2026-10-01: a UI remark). For ~5 s after the connection drops it reads "Slow or no
internet connection. Check the Internet settings and try again." with a ✕; then "No internet
connection." with "Try again" and a ✕. Its label lands on a full-window node ([0,0][1080,2400]), so
the node's rect says nothing about where the banner is drawn.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_U = AppiumBy.ANDROID_UIAUTOMATOR

BANNER_TEXTS = (
    "No internet connection.",
    "Slow or no internet connection. Check the Internet settings and try again.",
)
# Java regex for descriptionMatches: either text, also inside a merged label ("Photo added
# successfully\nSlow or no internet …" while a toast is up — recon A2, photo_offline_saving)
# A dot is [.] — no backslashes: the UiSelector string is unescaped once more on the device, and
# "\\." never matched there (offline run 0307-r1), although the offline evaluator accepted it.
_BANNER_RE = (
    "(?s).*(No internet connection[.]|Slow or no internet connection[.] Check the Internet "
    "settings and try again[.]).*"
)
_TRY_AGAIN = 'new UiSelector().className("android.view.View").description("Try again")'
_BUTTON = 'new UiSelector().className("android.widget.Button").description("{}")'

OFFLINE_BANNER = Screen(
    id="offline-banner",
    anchor="message",
    elements={
        "message": El(
            android=(_U, f'new UiSelector().descriptionMatches("{_BANNER_RE}")'),
            note="Android only (step 5): either banner text (recon A2 row 1); the notifications "
            "screen's own offline texts have no final period and do not match",
        ),
        "try-again": El(
            android=(_U, _TRY_AGAIN),
            note="Android only (step 5): the compact banner's link (a View); the notifications "
            "screen's 'Try again' is a Button and does not match",
        ),
        "close": El(
            android=(_U, _TRY_AGAIN),
            note="Android only (step 5). TESTABILITY DEFECT: the ✕ has no name. The map names the "
            "nearest labelled anchor (Try again); OfflineBanner.close() taps right of it "
            "(recon A2: ✕ [954,288][1038,372])",
        ),
    },
)

CONNECTION_RESTORED = Screen(
    id="connection-restored",
    anchor="title",
    elements={
        "title": El(
            android=(_A, "Connection restored"),
            note="Android only (step 5): after the network returns while a job is unfinished",
        ),
        "message": El(
            android=(
                _U,
                'new UiSelector().descriptionStartsWith("You have an unfinished job(s)")',
            ),
            note="Android only (step 5): 'You have an unfinished job(s) <job id - title>[, …]. "
            "Submit your deliverables now' (recon A2 row 12)",
        ),
        "cancel": El(android=(_U, _BUTTON.format("Cancel")), note="Android only (step 5)"),
        "submit": El(android=(_U, _BUTTON.format("Submit")), note="Android only (step 5)"),
    },
)
