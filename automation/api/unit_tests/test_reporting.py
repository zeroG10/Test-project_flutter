"""Offline harness tests; run with unittest, without product conftest or Allure output."""

import json
import os
import unittest
from unittest.mock import patch

import httpx

from clients.base_client import ApiClient
from helpers.reporting import expect_status, redact, response_summary, safe_url
from helpers.schema_validator import validate_schema


class ReportingTests(unittest.TestCase):
    def test_schema_errors_do_not_attach_or_raise_secret_values(self):
        payload = {"token": "private-token"}
        schema = {"type": "object", "properties": {"token": {"type": "integer"}}}
        with (
            patch("helpers.schema_validator.allure.attach") as attach,
            self.assertRaises(AssertionError) as error,
        ):
            validate_schema(payload, schema)
        self.assertNotIn("private-token", str(error.exception))
        self.assertNotIn("private-token", attach.call_args.args[0])
        self.assertIn("failed type", str(error.exception))
        self.assertEqual(payload["token"], "private-token")
        validate_schema(payload, {"type": "object"})

    def test_nested_secrets_and_custom_fields_without_mutating_response(self):
        body = {
            "items": [{"accessToken": "token-value", "PASSWORD": "password-value"}],
            "customer_email": "private-value",
            "count": 2,
        }
        response = httpx.Response(200, json=body, headers={"Set-Cookie": "session=secret"})
        with patch.dict(os.environ, {"QA_REDACT_FIELDS": "customer-email"}):
            text = response_summary(response)
        for secret in ("token-value", "password-value", "private-value", "session=secret"):
            self.assertNotIn(secret, text)
        self.assertIn('"count": 2', text)
        self.assertEqual(response.json(), body)
        self.assertEqual(response.headers["set-cookie"], "session=secret")

    def test_unstructured_bodies_and_string_json_are_omitted(self):
        for response in (
            httpx.Response(500, text="raw-secret"),
            httpx.Response(500, json="raw-secret"),
        ):
            text = response_summary(response)
            self.assertNotIn("raw-secret", text)
            self.assertIn("omitted", text)

    def test_embedded_credentials_are_masked(self):
        value = {"message": 'Bearer abc.def token="two words" password=secret'}
        text = json.dumps(redact(value))
        for secret in ("abc.def", "two words", "=secret"):
            self.assertNotIn(secret, text)

    def test_status_checks_allow_expected_negative_and_reject_failed_cleanup(self):
        denied = httpx.Response(403, json={"token": "private-token", "error": "forbidden"})
        self.assertIs(expect_status(denied, 403, "GET /orders/1"), denied)
        with self.assertRaises(AssertionError) as error:
            expect_status(denied, 204, "DELETE /orders/1?key=query-secret")
        self.assertNotIn("private-token", str(error.exception))
        self.assertNotIn("query-secret", str(error.exception))
        self.assertIn("forbidden", str(error.exception))
        self.assertIn("expected 204", str(error.exception))

    def test_client_reports_redacted_data_but_sends_and_returns_original(self):
        seen = []

        def respond(request):
            seen.append(request)
            return httpx.Response(200, json={"refresh_token": "original-token", "ok": True})

        transport_client = httpx.Client(
            base_url="https://local.invalid", transport=httpx.MockTransport(respond)
        )
        with (
            patch("clients.base_client.httpx.Client", return_value=transport_client),
            patch("clients.base_client.allure.attach") as attach,
            patch("clients.base_client.allure.step") as step,
            ApiClient() as api,
        ):
            response = api.get("/session?code=query-secret")
        self.assertEqual(seen[0].url.params["code"], "query-secret")
        self.assertEqual(response.json()["refresh_token"], "original-token")
        self.assertNotIn("original-token", attach.call_args.args[0])
        self.assertNotIn("query-secret", step.call_args.args[0])

    def test_url_and_redirect_credentials_are_omitted(self):
        url = "https://user:password@local.invalid/path?code=query-secret#fragment-secret"
        self.assertNotIn("password", safe_url(url))
        response = httpx.Response(302, headers={"Location": url})
        summary = response_summary(response)
        for secret in ("password", "query-secret", "fragment-secret"):
            self.assertNotIn(secret, summary)


if __name__ == "__main__":
    unittest.main()
