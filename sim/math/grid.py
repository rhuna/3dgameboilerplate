from __future__ import annotations


def clamp_to_grid(value: float, size: int) -> int:
    return max(0, min(size - 1, int(value)))
