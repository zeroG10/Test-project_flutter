"""Stream the app's own logs (debug build) while tests or a recon run — diagnosis only.

The Flutter debug build publishes a Dart VM service; its URL is printed to the simulator's log
("The Dart VM service is listening on http://127.0.0.1:<port>/<token>/") on every launch. This
script follows the newest URL (the tests relaunch the app before each test), subscribes to the
Logging, Stdout and Stderr streams and appends every line to <out-file>. Nothing is sent to
the app; stop it with Ctrl-C / kill.

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/app_logs.py <out-file> [--seconds 1800]

Why: Q-ORDD-6 — attachments do not load on the simulator and the app's reason is only in its
own logs (developer.log / print), not in the simulator's unified log.
"""

import argparse
import base64
import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

import websocket

URL = re.compile(r"Dart VM service is listening on (http://127\.0\.0\.1:\d+/[^\s]+/)")
STREAMS = ("Logging", "Stdout", "Stderr")


def newest_url() -> str | None:
    out = subprocess.run(
        ["xcrun", "simctl", "spawn", "booted", "log", "show", "--last", "2m", "--style",
         "compact", "--predicate", 'process == "Runner"'],
        capture_output=True, text=True, timeout=60,
    ).stdout  # fmt: skip
    found = URL.findall(out)
    return found[-1] if found else None


def ws_url(http: str) -> str:
    return "ws://" + http.removeprefix("http://").rstrip("/") + "/ws"


def text_of(event: dict) -> str:
    kind = event.get("kind", "")
    if kind == "Logging":
        record = event.get("logRecord", {})
        name = (record.get("loggerName") or {}).get("valueAsString", "")
        message = (record.get("message") or {}).get("valueAsString", "")
        error = (record.get("error") or {}).get("valueAsString", "")
        return f"[log {name}] {message}" + (f" | error: {error}" if error and error != "null" else "")
    if kind in ("WriteEvent",):
        return base64.b64decode(event.get("bytes", "")).decode("utf-8", "replace").rstrip()
    return json.dumps(event)[:300]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("--seconds", type=int, default=1800)
    args = parser.parse_args()
    out = Path(args.out)
    end = time.monotonic() + args.seconds
    current, sock = None, None
    with out.open("a", encoding="utf-8") as log:
        while time.monotonic() < end:
            url = newest_url()
            if url and url != current:
                if sock is not None:
                    sock.close()
                try:
                    sock = websocket.create_connection(ws_url(url), timeout=5)
                    for i, stream in enumerate(STREAMS):
                        sock.send(json.dumps({"jsonrpc": "2.0", "id": str(i), "method": "streamListen",
                                              "params": {"streamId": stream}}))  # fmt: skip
                    current = url
                    log.write(f"\n==== {datetime.now():%H:%M:%S} connected {url}\n")
                    log.flush()
                except (OSError, websocket.WebSocketException) as exc:
                    log.write(f"==== {datetime.now():%H:%M:%S} connect failed {url}: {exc}\n")
                    sock, current = None, None
            if sock is None:
                time.sleep(2)
                continue
            deadline = time.monotonic() + 5  # read for a while, then look for a newer launch
            while time.monotonic() < deadline:
                try:
                    message = json.loads(sock.recv())
                except websocket.WebSocketTimeoutException:
                    continue
                except (OSError, websocket.WebSocketException, ValueError):
                    sock, current = None, None
                    break
                event = (message.get("params") or {}).get("event")
                if event:
                    log.write(f"{datetime.now():%H:%M:%S.%f}"[:-3] + f" {text_of(event)}\n")
                    log.flush()


if __name__ == "__main__":
    main()
