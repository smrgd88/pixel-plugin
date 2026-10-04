#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/validate-mcp-contract.py" --bundled
python3 "$SCRIPT_DIR/test-mcp-warnings.py"
python3 "$SCRIPT_DIR/test-mcp-export-analysis.py"
python3 "$SCRIPT_DIR/test-mcp-review-fixes.py"
exec python3 "$SCRIPT_DIR/test-mcp-safety.py"
