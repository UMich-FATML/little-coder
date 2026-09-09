#!/usr/bin/env bash
# Apply vendor patches under patches/ to node_modules (idempotent).
# Run after every npm install; npm wipes node_modules edits.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

for p in patches/*.patch; do
  if patch -p1 --dry-run -R < "$p" > /dev/null 2>&1; then
    echo "already applied: $p"
  else
    patch -p1 < "$p"
    echo "applied: $p"
  fi
done
