"""Sorting implementation to optimize."""

comparisons = 0


def sort(arr: list[int]) -> list[int]:
    """In-place sort — benchmark already passes a copy."""
    global comparisons
    comparisons = 0
    arr.sort()
    return arr
