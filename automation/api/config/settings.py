from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Fail-closed like BASE_URL in the web stack: no default target. conftest.py refuses
    # to start a session while this is empty or still the `<…>` placeholder.
    api_base_url: str = ""
    api_timeout_seconds: int = 30
    api_token: str = ""
    api_username: str = ""
    api_password: str = ""
    api_env: str = "staging"

    # Security module (modules.security in setup/project.yaml) — IDOR access-control
    # matrix, see tests/security/test_access_control.py. Empty = not configured; the
    # tests then skip loudly (Blocked), they never pass on an empty matrix.
    user_a_token: str = ""
    user_b_token: str = ""
    idor_resources: str = ""  # ';'-separated GET path templates with {id}
    idor_resource_ids: str = ""  # ';'-separated ids owned by USER A, aligned 1:1


settings = Settings()
