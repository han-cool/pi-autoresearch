#!/bin/bash
set -euo pipefail

# Pre-check
if ! command -v node &>/dev/null; then
  echo "ERROR: node not found" >&2
  exit 1
fi

# Quick syntax check
node --check benchmark.js 2>&1 || { echo "ERROR: syntax error in benchmark.js" >&2; exit 1; }

# Run benchmark
output=$(node benchmark.js 2>&1)
echo "$output"

# Verify correctness — expected sum of 0..1999999 = 1999999000000
result=$(echo "$output" | sed -n 's/^result=\([0-9]*\)/\1/p')
expected=1999999000000
if [[ "$result" != "$expected" ]]; then
  echo "ERROR: wrong result $result, expected $expected" >&2
  exit 1
fi

# Emit metric
elapsed=$(echo "$output" | sed -n 's/^METRIC elapsed_ms=\([0-9.]*\)/\1/p')
echo "METRIC elapsed_ms=$elapsed"
