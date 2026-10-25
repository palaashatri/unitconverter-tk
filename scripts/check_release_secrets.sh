#!/usr/bin/env bash
set -euo pipefail

required_secrets=(
  WINDOWS_SIGNING_CERTIFICATE
  WINDOWS_SIGNING_PASSWORD
  APPLE_CERTIFICATE
  APPLE_CERTIFICATE_PASSWORD
  APPLE_ID
  APPLE_APP_SPECIFIC_PASSWORD
  APPLE_TEAM_ID
)
missing_secrets=()

for name in "${required_secrets[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    missing_secrets+=("$name")
  fi
done

if (( ${#missing_secrets[@]} > 0 )); then
  printf 'Missing required signing secrets: %s\n' "${missing_secrets[*]}" >&2
  exit 1
fi
