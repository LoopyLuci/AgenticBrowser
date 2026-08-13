#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="${1:-certs}"
DAYS_THRESHOLD="${2:-30}"

if [ ! -f "${CERT_DIR}/cert.pem" ] || [ ! -f "${CERT_DIR}/key.pem" ]; then
  echo "Missing certs, generating..."
  ./scripts/generate-certs.sh "${CERT_DIR}"
  exit 0
fi

EXPIRY=$(openssl x509 -in "${CERT_DIR}/cert.pem" -noout -enddate 2>/dev/null | cut -d= -f2)
if [ -z "${EXPIRY}" ]; then
  echo "Failed to read cert expiry"
  exit 1
fi

EXP_EPOCH=$(date -d "${EXPIRY}" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "${EXPIRY}" +%s 2>/dev/null)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( (EXP_EPOCH - NOW_EPOCH) / 86400 ))

if [ "${DAYS_LEFT}" -lt "${DAYS_THRESHOLD}" ]; then
  echo "Cert expires in ${DAYS_LEFT} days (threshold: ${DAYS_THRESHOLD}), rotating..."
  ./scripts/generate-certs.sh "${CERT_DIR}"
  echo "Cert rotated successfully"
else
  echo "Cert valid for ${DAYS_LEFT} more days, no rotation needed"
fi
