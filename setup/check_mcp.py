#!/usr/bin/env python3
"""Probe every MCP server in .mcp.json with a real MCP handshake.

    python3 setup/check_mcp.py [server ...]

One row per server: it is started exactly as an agent would start it, sent
``initialize`` + ``tools/list``, and judged on what it answers — not on whether
the command exists. A server that starts and then dies on a broken dependency
(the usual npx-cache failure) looks healthy to every other check and fails only
here, which is the point.

stdlib only, no uv/venv needed. Exit 1 if any server FAILED; a server skipped
for a missing credential is reported and does not fail the run (it is a setup
step, not a defect). Nothing is written and no device is touched: `initialize`
and `tools/list` are read-only handshakes.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MCP_JSON = REPO / ".mcp.json"
TIMEOUT_S = 90  # a cold npx cache downloads the package on the first run

ENV_REF = re.compile(r"\$\{([A-Z0-9_]+)\}")

HANDSHAKE = (
    json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "check_mcp", "version": "1.0"},
        },
    })
    + "\n"
    + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
    + "\n"
    + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    + "\n"
)

# Failure signatures worth naming, because the fix is not obvious from the traceback.
HINTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"MODULE_NOT_FOUND|Cannot find module"),
        "broken npx cache — rm -rf ~/.npm/_npx and re-run (the package is re-downloaded)",
    ),
    (re.compile(r"EACCES|permission denied", re.I), "permission problem on the npx/node cache"),
    (re.compile(r"ENOTFOUND|ETIMEDOUT|EAI_AGAIN|network", re.I), "no network — the package could not be fetched"),
    (re.compile(r"401|403|unauthorized|invalid token", re.I), "credential rejected — check the token in the shell env"),
)


def row(status: str, name: str, detail: str, fix: str = "") -> None:
    print(f"{status:<8} {name:<12} {detail:<52.52} {fix}")


def hint_for(text: str) -> str:
    for pattern, hint in HINTS:
        if pattern.search(text):
            return hint
    return ""


def resolve_env(raw: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Expand ${VAR} from the shell env. Returns (env, names that are unset)."""
    env, missing = dict(os.environ), []
    for key, value in raw.items():
        def swap(m: re.Match[str]) -> str:
            name = m.group(1)
            if not os.environ.get(name):
                missing.append(name)
                return ""
            return os.environ[name]

        env[key] = ENV_REF.sub(swap, value)
    return env, missing


def probe(name: str, spec: dict) -> bool | None:
    """True = answered, False = failed, None = skipped (missing credential)."""
    command = spec.get("command")
    if not command:
        row("SKIP", name, "no `command` (remote server?) — not probed here")
        return None

    env, missing = resolve_env(spec.get("env") or {})
    if missing:
        row("SKIP", name, f"{', '.join(sorted(set(missing)))} not set in the shell env",
            "export it, then re-run — the server is not verified until you do")
        return None

    argv = [command, *spec.get("args", [])]
    try:
        done = subprocess.run(
            argv, input=HANDSHAKE, capture_output=True, text=True,
            timeout=TIMEOUT_S, cwd=REPO, env=env,
        )
    except FileNotFoundError:
        row("FAIL", name, f"command not found: {command}", "install it (node/npx, uv, …)")
        return False
    except subprocess.TimeoutExpired:
        row("FAIL", name, f"no answer in {TIMEOUT_S}s",
            "first run downloads the package — re-run; if it repeats, see the hint below")
        return False

    server, tools = None, None
    for line in done.stdout.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("id") == 1 and "result" in message:
            server = message["result"].get("serverInfo", {})
        if message.get("id") == 2 and "result" in message:
            tools = message["result"].get("tools", [])

    if server is None:
        blob = f"{done.stderr}\n{done.stdout}"
        first = next((ln for ln in done.stderr.splitlines() if ln.strip()), "no output")
        row("FAIL", name, first[:52], hint_for(blob) or "run the command by hand to see the full error")
        return False

    version = server.get("version", "?")
    count = "?" if tools is None else str(len(tools))
    row("OK", name, f"{server.get('name', name)} v{version} — {count} tools")
    return True


def main(argv: list[str]) -> int:
    if not MCP_JSON.is_file():
        print(f"no {MCP_JSON} — nothing to check", file=sys.stderr)
        return 2
    servers = json.loads(MCP_JSON.read_text()).get("mcpServers", {})
    wanted = argv or list(servers)
    unknown = [n for n in wanted if n not in servers]
    if unknown:
        print(f"unknown server(s): {', '.join(unknown)}. Known: {', '.join(servers)}", file=sys.stderr)
        return 2

    print(f"MCP servers in {MCP_JSON.relative_to(REPO)} — started and asked for their tool list\n")
    row("STATUS", "SERVER", "DETAIL", "FIX")
    row("------", "------", "------", "---")
    results = {name: probe(name, servers[name]) for name in wanted}

    failed = [n for n, r in results.items() if r is False]
    skipped = [n for n, r in results.items() if r is None]
    print()
    if failed:
        print(f"RESULT: {len(failed)} server(s) FAILED: {', '.join(failed)} — "
              "an agent asked to use them would be Blocked, not silently degraded.")
        return 1
    if skipped:
        print(f"RESULT: OK — every probed server answered; not verified: {', '.join(skipped)}.")
        return 0
    print("RESULT: OK — every server answered.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
