"""Jobs list — first screen of a signed-in technician (module 03; used as the landing check
of the Authentication suite). Only what module 02 needs; module 03 extends it.

Source: Appium tree qa/shared/recon-dumps/ios-2026-09-23/jobs_list.xml (recon 3b) and the
empty state seen in recon 3c.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE

JOBS_LIST = Screen(
    id="jobs-list",
    anchor="root",
    elements={
        "root": El(ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Jobs list'")),
        "empty-state": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'No jobs'")),
        # Tab names carry a counter ("1\nNotifications\nTab 2 of 3") — match the stable tail.
        "tab-jobs": El(ios=(_P, "name ENDSWITH 'Tab 1 of 3'")),
        "tab-notifications": El(ios=(_P, "name ENDSWITH 'Tab 2 of 3'")),
        "tab-profile": El(ios=(_P, "name ENDSWITH 'Tab 3 of 3'")),
    },
)
