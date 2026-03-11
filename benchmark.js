#!/usr/bin/env node
/**
 * Toy benchmark: sum numbers in a deliberately slow way.
 * The autoresearch loop should find ways to make it faster.
 */

const N = 2_000_000;

function slowSum(n) {
  return n * (n - 1) / 2;
}

const t0 = performance.now();
const result = slowSum(N);
const elapsed = performance.now() - t0;

console.log(`result=${result}`);
console.log(`METRIC elapsed_ms=${elapsed.toFixed(1)}`);
