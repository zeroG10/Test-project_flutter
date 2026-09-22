from typing import Any

import allure
import httpx

from config.settings import settings
from helpers.reporting import response_summary, safe_url


class ApiClient:
    """Thin wrapper around httpx.Client with Allure logging and shared defaults."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float | None = None,
    ):
        self._client = httpx.Client(
            base_url=base_url or settings.api_base_url,
            timeout=timeout or settings.api_timeout_seconds,
            headers=self._default_headers(token),
        )

    @staticmethod
    def _default_headers(token: str | None) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        tok = token if token is not None else settings.api_token
        if tok:
            headers["Authorization"] = f"Bearer {tok}"
        return headers

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        with allure.step(f"{method.upper()} {safe_url(path)}"):
            response = self._client.request(method, path, **kwargs)
            allure.attach(
                response_summary(response),
                name="response",
                attachment_type=allure.attachment_type.TEXT,
            )
            return response

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
