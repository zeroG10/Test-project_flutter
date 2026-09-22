"""Retry on *transport* failures only — never on a verdict.

`retry_on_transport_error` re-runs the wrapped callable (max 3 attempts, exponential
backoff, bounded) only when httpx could not complete the exchange at all:
`httpx.TransportError` (connection refused/reset, DNS, proxy) and
`httpx.TimeoutException` (connect/read/write/pool timeout).

It deliberately does NOT retry:
  - assertion failures — the check already decided; re-rolling until green is a
    fabricated pass (doctrine rule 1);
  - 4xx/5xx responses — the server's verdict. httpx returns them as ordinary
    `Response` objects, and even `raise_for_status()` raises `HTTPStatusError`,
    which is not a transport error and is not caught here.

Wrap the request, not the test — keep assertions outside the retried scope:

    @retry_on_transport_error
    def get_health(api):
        return api.get("/health")

    def test_health(api):
        assert get_health(api).status_code == 200

If all attempts fail, the original httpx exception is re-raised (`reraise=True`), so
an unreachable environment shows up as an error — i.e. Blocked — never as green.
"""

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

retry_on_transport_error = retry(
    retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    reraise=True,
)
