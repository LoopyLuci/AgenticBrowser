import json
import os
import re
import sys
import zipfile
from pathlib import Path

REQUIRED_FILES = [
    "agenticbrowser-manifest.json",
    "agenticbrowser-sidepanel.html",
    "agenticbrowser-sidepanel.js",
    "agenticbrowser-sidepanel.css",
    "agenticbrowser-background.js",
    "agenticbrowser-content.js",
]

ALLOWED_TOP_LEVEL = {
    "agenticbrowser-manifest.json",
    "agenticbrowser-sidepanel.html",
    "agenticbrowser-sidepanel.js",
    "agenticbrowser-sidepanel.css",
    "agenticbrowser-background.js",
    "agenticbrowser-content.js",
    "agenticbrowser-extension-chrome.zip",
    "agenticbrowser-extension-firefox.zip",
}

MANIFEST_REQUIRED_KEYS = ["manifest_version", "name", "version", "permissions"]


def validate_release(root: Path) -> int:
    failures = 0
    print(f"Validating release directory: {root}")
    if not root.exists() or not root.is_dir():
        print("Missing release directory")
        return 1

    files = sorted(p.name for p in root.iterdir() if p.is_file())
    unexpected = [f for f in files if f not in ALLOWED_TOP_LEVEL]
    if unexpected:
        print(f"Unexpected top-level files: {unexpected}")
        failures += 1
    missing = [f for f in REQUIRED_FILES if f not in files]
    if missing:
        print(f"Missing expected artifacts: {missing}")
        failures += 1

    manifest_path = root / "agenticbrowser-manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            missing_keys = [k for k in MANIFEST_REQUIRED_KEYS if k not in manifest]
            if missing_keys:
                print(f"manifest missing keys: {missing_keys}")
                failures += 1
            if manifest.get("name") != "AgenticBrowser":
                print(f"Unexpected manifest name: {manifest.get('name')}")
                failures += 1
            if not re.match(r"^\d+\.\d+\.\d+$", str(manifest.get("version", ""))):
                print(f"Unexpected manifest version format: {manifest.get('version')}")
                failures += 1
        except Exception as e:
            print(f"manifest.json parse error: {e}")
            failures += 1
    else:
        print("Missing manifest.json")
        failures += 1

    for zip_name in ["agenticbrowser-extension-chrome.zip", "agenticbrowser-extension-firefox.zip"]:
        zip_path = root / zip_name
        if not zip_path.exists():
            print(f"Missing zip: {zip_name}")
            failures += 1
            continue
        try:
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
                if not any("manifest" in n.lower() for n in names):
                    print(f"{zip_name} missing manifest entry")
                    failures += 1
                if not any(n.lower().endswith(".html") for n in names):
                    print(f"{zip_name} missing HTML entry")
                    failures += 1
                if not any(n.lower().endswith(".js") for n in names):
                    print(f"{zip_name} missing JS entry")
                    failures += 1
        except Exception as e:
            print(f"{zip_name} read error: {e}")
            failures += 1

    if failures == 0:
        print("Release validation passed")
    else:
        print(f"Release validation failed: {failures} issue(s)")
    return failures


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("release")
    sys.exit(0 if validate_release(root) == 0 else 1)
