#!/bin/bash
# DebugDost verify gate: compile + tests + source-only secret scan. Exit 0 = pass.
set -e
cd "$(dirname "$0")/.."
python3 -m py_compile app.py
python3 -m pytest tests/ -q
if grep -rInE 'bc_live_|sk-[A-Za-z0-9]|ghp_|hf_[A-Za-z0-9]|api[_-]?key\s*=\s*["'\''][^"'\'']+["'\'']' --include='*.py' --include='*.md' --include='*.txt' --include='*.html' . --exclude-dir=__pycache__ --exclude-dir=.pytest_cache | grep -v 'BHARATCODE_API_KEY' | grep -v 'your_key_here' | grep -v 'api_key=api_key'; then
  echo "SECRET SCAN: FAIL — possible secret in source"
  exit 1
fi
echo "VERIFY: PASS"
