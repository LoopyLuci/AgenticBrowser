import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CERTS_DIR = REPO_ROOT / "certs"


def test_ssl_files_exist():
    assert (CERTS_DIR / "cert.pem").exists()
    assert (CERTS_DIR / "key.pem").exists()


def test_ssl_cert_has_localhost_cn():
    result = subprocess.run(
        ["openssl", "x509", "-in", str(CERTS_DIR / "cert.pem"), "-noout", "-subject"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "CN=localhost" in result.stdout


def test_ssl_cert_validity_period():
    result = subprocess.run(
        ["openssl", "x509", "-in", str(CERTS_DIR / "cert.pem"), "-noout", "-startdate", "-enddate"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "notBefore" in result.stdout or "startdate=" in result.stdout
    assert "notAfter" in result.stdout or "enddate=" in result.stdout


def test_ssl_key_is_private_key():
    text = (CERTS_DIR / "key.pem").read_text()
    assert "BEGIN PRIVATE KEY" in text or "BEGIN RSA PRIVATE KEY" in text


def test_ssl_cert_matches_key():
    result = subprocess.run(
        [
            "openssl",
            "x509",
            "-noout",
            "-modulus",
            "-in",
            str(CERTS_DIR / "cert.pem"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    cert_mod = result.stdout.strip().split("=", 1)[-1]

    result = subprocess.run(
        [
            "openssl",
            "rsa",
            "-noout",
            "-modulus",
            "-in",
            str(CERTS_DIR / "key.pem"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    key_mod = result.stdout.strip().split("=", 1)[-1]
    assert cert_mod == key_mod
