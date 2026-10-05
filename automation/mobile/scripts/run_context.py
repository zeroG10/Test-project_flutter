#!/usr/bin/env python3
"""What a run of one platform uses, for the shell scripts — as ``KEY=value`` lines
(``eval``-safe), or one value with ``--get KEY``. No secret is printed: the account appears only
as its fingerprint.

    uv run python scripts/run_context.py ios      # APPIUM_URL=… ACCOUNT_KEY=… PARALLEL_OK=yes
    uv run python scripts/run_context.py android --get APPIUM_PORT
"""

import shlex
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import PLATFORMS, normalize_platform, settings  # noqa: E402


def context(platform: str) -> dict[str, str]:
    p = normalize_platform(platform)
    other = next(x for x in PLATFORMS if x != p)
    ok, why = settings.can_run_in_parallel()
    port = settings.appium_port_for(p)
    return {
        "APPIUM_PORT": str(port),
        "APPIUM_URL": f"http://{settings.appium_host}:{port}",
        "ACCOUNT_KEY": settings.account_key(p),
        "OTHER_PLATFORM": other,
        "PARALLEL_OK": "yes" if ok else "no",
        "PARALLEL_WHY": why,
        "API_HOST": urlparse(settings.api_base_url).hostname or "",
        "DEVICE_NAME": settings.android_device_name if p == "android" else settings.ios_device_name,
    }


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        values = context(argv[0])
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    if len(argv) == 3 and argv[1] == "--get":
        print(values[argv[2]])
        return 0
    for key, value in values.items():
        print(f"{key}={shlex.quote(value)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
