#!/usr/bin/env bash
# Deprecated: use the faah CLI after `pip install faah`.
set -euo pipefail
if command -v faah >/dev/null 2>&1; then
  exec faah "$@"
fi
echo "faah: install the CLI first: pip install faah  (or: uv tool install faah)" >&2
echo "Then run: faah install" >&2
exit 1
