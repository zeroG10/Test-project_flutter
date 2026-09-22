"""Cross-platform smoke example: shows the tagging contract every mobile test follows.

* ``@pytest.mark.chk("CHK-...")`` — the checklist item(s) this test proves (validated at
  collection, exported to JUnit properties).
* ``@allure.tag("CHK-...")``      — the same id for Allure, which trace_results.py reads.
* ``shared`` — runs on every ``--platform``; ``android`` / ``ios`` / ``flutter`` would scope it.

The CHK id and the screen are PLACEHOLDERS: point them at your app's real first screen and
the matching item in qa/mobile/<NN-module>/<module>-checklist.md.
"""

import allure
import pytest

from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.chk("CHK-AUTH-001")
@allure.tag("CHK-AUTH-001")
@allure.title("CHK-AUTH-001 App launches and shows the login screen")
def test_app_launches_to_login(driver, platform):
    # Oracle: qa/mobile/<NN-module>/<module>-checklist.md [CHK-AUTH-001] — first screen after a cold
    # start is Login. The anchor comes from screens/login_map.py; if it never appears the
    # explicit wait raises TimeoutException and the test is red with a screenshot attached.
    LoginPage(driver, platform).assert_open()
