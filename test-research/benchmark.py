"""Benchmark harness for sort.py — DO NOT MODIFY."""

import random
import time
import sys
import tracemalloc

# Fixed seed for reproducibility
random.seed(42)
N = 100_000
data = [random.randint(-1_000_000, 1_000_000) for _ in range(N)]
expected = sorted(data)

# Import the sort implementation
import sort as sort_module
from sort import sort

# Warmup
sort(data[:1000])

# Benchmark: median of 3 runs
times = []
peak_mem = 0
final_comparisons = 0

for _ in range(3):
    arr = data[:]
    tracemalloc.start()
    t0 = time.perf_counter_ns()
    result = sort(arr)
    t1 = time.perf_counter_ns()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_us = (t1 - t0) / 1000
    times.append(elapsed_us)
    peak_mem = max(peak_mem, peak)
    final_comparisons = sort_module.comparisons

times.sort()
median_us = times[1]  # median of 3
memory_kb = peak_mem / 1024

# Verify correctness
if result != expected:
    print("ERROR: sort produced incorrect output!", file=sys.stderr)
    # Show first mismatch
    for i, (a, b) in enumerate(zip(result, expected)):
        if a != b:
            print(f"  First mismatch at index {i}: got {a}, expected {b}", file=sys.stderr)
            break
    if len(result) != len(expected):
        print(f"  Length mismatch: got {len(result)}, expected {len(expected)}", file=sys.stderr)
    sys.exit(1)

print(f"Sorted {N} integers correctly")
print(f"METRIC sort_µs={median_us:.0f}")
print(f"METRIC comparisons={final_comparisons}")
print(f"METRIC memory_kb={memory_kb:.1f}")
