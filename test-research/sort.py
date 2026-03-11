"""Sorting implementation to optimize."""

comparisons = 0


def sort(arr: list[int]) -> list[int]:
    """Sort using Python's built-in sorted()."""
    global comparisons
    comparisons = 0
    return sorted(arr)
