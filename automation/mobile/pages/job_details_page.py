"""Job details — behaviour over screens/job_details_map.py (module 03 uses the header only)."""

from pages.base_page import BasePage
from screens.job_details_map import JOB_DETAILS


class JobDetailsPage(BasePage):
    screen = JOB_DETAILS

    def expect_header(self, title_line: str, timeout: float | None = None) -> None:
        """The app bar shows '<jobId> - <title>' of the job that was opened."""
        self.visible("header", timeout, text=title_line)
