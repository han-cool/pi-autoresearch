# Autoresearch: Optimize toy benchmark

## Objective
Speed up `benchmark.js` — a deliberately slow number-summing script.
This is a test run to validate the autoresearch loop works end-to-end.

## How to Run
Run `./autoresearch.sh` — it runs the benchmark, verifies correctness, and emits metrics.

## Metrics
- **Primary (optimization target)**: elapsed_ms (ms, lower is better)
  - Wall-clock time for the summing computation.

## Files in Scope
- `benchmark.js` — the benchmark script (the thing to optimize)

## Off Limits
- `extensions/` — the extension code itself
- `skills/` — skill definitions
- `autoresearch.md` — this file

## Constraints
- The result must equal 1999999000000 (sum of 0..1999999)
- Must remain a single Node.js script (no external deps, no native addons)
- N must stay at 2_000_000
