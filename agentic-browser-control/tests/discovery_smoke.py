import subprocess

import pytest

REPO_ROOT = (
    __import__("pathlib").Path(__file__).resolve().parents[2]
    / "agentic-browser-control"
)


def test_control_server_reports_discovery_beacon_startup():
    proc = subprocess.Popen(
        ["node", str(REPO_ROOT / "dist" / "server.js")],
        cwd=str(REPO_ROOT),
        env={**__import__("os").environ, "PORT": "18771", "AGENTIC_CONTROL_SECRET": "test"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        output = ""
        ready = False
        for _ in range(60):
            line = proc.stdout.readline()
            if not line:
                break
            output += line
            if "Discovery beacon" in line:
                ready = True
                break
        assert ready, f"Discovery beacon startup message not found in control server logs: {output}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
