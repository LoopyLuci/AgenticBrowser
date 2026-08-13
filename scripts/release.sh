#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <version> [message]"
  exit 1
fi

VERSION="$1"
MESSAGE="${2:-chore: release $VERSION}"

if [ ! -f package.json ]; then
  echo "package.json not found"
  exit 1
fi

node -e "const fs=require('fs'); const p=JSON.parse(fs.readFileSync('package.json','utf8')); p.version='${VERSION}'; fs.writeFileSync('package.json', JSON.stringify(p, null, 2) + '\n');"

{
  echo ""
  echo "## [${VERSION}] - $(date +%Y-%m-%d)"
  echo "- ${MESSAGE}"
} >> CHANGELOG.md

echo "Updated package.json and CHANGELOG.md for ${VERSION}"
