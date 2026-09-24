"""Job details — only what module 03 needs (module 04-order-details extends it).

Source: recon 3b (job_details_new.xml) and recon 4 (recon4_details_from_list.xml): the app bar
shows '<jobId> - <title>' as an element of type Other; the back button is labelled 'Back'.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE

JOB_DETAILS = Screen(
    id="job-details",
    anchor="root",
    elements={
        "root": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name BEGINSWITH 'Attachments ('"),
            note="the Attachments row exists on every job's details (recon 3b, 4)",
        ),
        "header": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == {text}"),
            note="parametrised by '<jobId> - <title>' — the app-bar title",
        ),
        "back": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Back'")),
    },
)
