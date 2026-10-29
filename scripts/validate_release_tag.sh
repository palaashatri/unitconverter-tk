#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: validate_release_tag.sh <tag-name> <source-sha>" >&2
  exit 2
fi

tag_name="$1"
source_sha="$2"

if [[ ! "$source_sha" =~ ^[0-9a-fA-F]{40}$ ]]; then
  echo "Release source must be a full 40-character commit SHA." >&2
  exit 1
fi

if ! tag_sha="$(git rev-parse --verify --quiet "refs/tags/${tag_name}^{commit}")"; then
  echo "Release tag does not resolve to a commit." >&2
  exit 1
fi

tag_sha_lower="$(printf '%s' "$tag_sha" | tr '[:upper:]' '[:lower:]')"
source_sha_lower="$(printf '%s' "$source_sha" | tr '[:upper:]' '[:lower:]')"
if [[ "$tag_sha_lower" != "$source_sha_lower" ]]; then
  echo "Release tag does not point to the requested source commit." >&2
  exit 1
fi
