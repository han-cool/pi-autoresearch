#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

# Pre-check
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found" >&2
  exit 1
fi

# Quick syntax check
python3 -c "import py_compile; py_compile.compile('sort.py', doraise=True)" 2>&1 || {
  echo "ERROR: syntax error in sort.py" >&2
  exit 1
}

# Run benchmark
python3 benchmark.py
