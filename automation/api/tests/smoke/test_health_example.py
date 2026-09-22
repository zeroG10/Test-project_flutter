import allure
import pytest


# Tagging (see automation/README.md → "IDs and tags"): every test carries the checklist
# IDs it proves, as BOTH a pytest marker (filtering / traceability) and an Allure tag
# (report). CHK-API-001 is a placeholder — replace it with the real [CHK-…] ID from
# qa/{web,mobile}/<NN-module>/<module>-checklist.md (or qa/shared/checklists/). A CHK ID
# with no tagged test is "not run", never green.
@pytest.mark.smoke
@pytest.mark.chk("CHK-API-001")
@allure.tag("CHK-API-001")
@allure.title("API health endpoint returns 200")
def test_health_returns_200(api):
    # TODO: replace `/health` with the real endpoint of your API
    response = api.get("/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
