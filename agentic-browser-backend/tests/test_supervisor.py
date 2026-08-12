from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_ROOT = REPO_ROOT / "agentic-browser-control"


REQUIRED_CONTROL_FILES = [
    "src/server.ts",
    "src/chat/forwarder.ts",
    "src/middleware/auth.ts",
    "src/ws/index.ts",
]


def test_control_plane_required_files_exist():
    for rel in REQUIRED_CONTROL_FILES:
        assert (CONTROL_ROOT / rel).exists(), f"Missing control file: {rel}"


def test_control_plane_discovery_module_exists():
    assert (CONTROL_ROOT / "src" / "discovery" / "udp.ts").exists()
