"""Vectorized user-similarity metrics over a user-item rating matrix.

The matrix has shape (n_users, n_items) with ``numpy.nan`` for missing ratings.
All metrics ignore NaN entries and return 0 when two users share no co-rated
items or a denominator vanishes.
"""

from __future__ import annotations

import numpy as np


def pearson_similarity(matrix: np.ndarray) -> np.ndarray:
    """Pearson correlation for every user pair, over co-rated items only.

    Means and variances are computed on each pair's co-rated set, matching the
    textbook definition (and the legacy prototype).
    """
    filled = np.where(np.isnan(matrix), 0.0, matrix)
    mask = (~np.isnan(matrix)).astype(float)
    filled_sq = filled**2

    co_rated = mask @ mask.T
    sum_x = filled @ mask.T  # Σ of i's ratings over items both rated
    sum_y = mask @ filled.T  # Σ of j's ratings over items both rated
    sum_xx = filled_sq @ mask.T
    sum_yy = mask @ filled_sq.T
    sum_xy = filled @ filled.T

    with np.errstate(invalid="ignore", divide="ignore"):
        numerator = sum_xy - sum_x * sum_y / co_rated
        denom_x = sum_xx - sum_x**2 / co_rated
        denom_y = sum_yy - sum_y**2 / co_rated
        denominator = np.sqrt(denom_x * denom_y)
        sim = np.where(denominator > 0, numerator / denominator, 0.0)

    sim = np.where(co_rated > 0, sim, 0.0)
    np.fill_diagonal(sim, (mask.sum(axis=1) > 0).astype(float))
    return np.clip(sim, -1.0, 1.0)


def co_rated_counts(matrix: np.ndarray) -> np.ndarray:
    """Number of co-rated items for every user pair."""
    mask = (~np.isnan(matrix)).astype(float)
    return mask @ mask.T


def significance_weighted(
    similarities: np.ndarray, counts: np.ndarray, gamma: float = 50.0
) -> np.ndarray:
    """Discount similarities backed by few co-rated items.

    Pairs sharing exactly two movies always correlate at ±1 — pure noise that
    would otherwise dominate the voter pool. Scaling by
    ``min(n_common, gamma) / gamma`` (Herlocker et al.) fixes that.
    ``gamma <= 0`` disables weighting (returns similarities unchanged).
    """
    if gamma <= 0:
        return similarities.copy()
    with np.errstate(invalid="ignore", divide="ignore"):
        weight = np.where(counts > 0, np.minimum(counts, gamma) / gamma, 0.0)
    return similarities * weight


def euclidean_similarity(matrix: np.ndarray) -> np.ndarray:
    """1 / (1 + euclidean distance) for every user pair, over co-rated items."""
    filled = np.where(np.isnan(matrix), 0.0, matrix)
    mask = (~np.isnan(matrix)).astype(float)
    filled_sq = filled**2

    dist_sq = filled_sq @ mask.T + mask @ filled_sq.T - 2.0 * (filled @ filled.T)
    dist_sq = np.maximum(dist_sq, 0.0)

    co_rated = mask @ mask.T
    with np.errstate(invalid="ignore", divide="ignore"):
        sim = np.where(co_rated > 0, 1.0 / (1.0 + np.sqrt(dist_sq)), 0.0)
    np.fill_diagonal(sim, (mask.sum(axis=1) > 0).astype(float))
    return sim
