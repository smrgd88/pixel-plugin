#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/validate-mcp-contract.py" --bundled
exec python3 "$SCRIPT_DIR/test-mcp-warnings.py"
