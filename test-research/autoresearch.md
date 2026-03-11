# Autoresearch: Optimize sorting algorithm

## Objective
Find the fastest sorting implementation for a 100k-element integer array.
The benchmark measures wall-clock time in microseconds.

## How to Run
Run `./autoresearch.sh` — it compiles and benchmarks the sort implementation.

## Metrics
- **Primary (optimization target)**: sort_µs (µs, lower is better)
- **Secondary (tradeoff monitoring)**: comparisons (count), memory_kb (kb)

## Files in Scope
- `sort.py` — the sorting implementation to optimize

## Off Limits
- `benchmark.py` — the benchmark harness (read-only)
- `autoresearch.sh` — the runner script

## Constraints
- Must produce a correctly sorted output (benchmark verifies this)
- Pure Python only, no C extensions or ctypes
- Must handle duplicates and negative numbers
