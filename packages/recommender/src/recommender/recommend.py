"""Top-K recommendations from precomputed user similarities.

Fixes the legacy prototype defect where per-movie scores were overwritten instead
of accumulated when several similar users rated the same movie: here every
candidate score is the similarity-weighted average over ALL similar raters.
"""

from __future__ import annotations

import numpy as np


def recommend_for_user(
    matrix: np.ndarray,
    similarities: np.ndarray,
    user_index: int,
    top_k: int = 10,
    min_similarity: float = 0.0,
    min_voters: int = 10,
) -> list[tuple[int, float]]:
    """Return ``[(item_index, predicted_rating)]`` sorted by score, best first.

    Only users with similarity ``>= min_similarity`` vote (excluding the user
    themselves), only items the user has not rated are candidates, and a
    candidate needs at least ``min_voters`` voters — otherwise a single
    high-similarity voter rating an obscure movie 5/5 would dominate the
    ranking. Returns an empty list when nothing can be recommended.
    """
    sims = similarities[user_index].astype(float).copy()
    sims[user_index] = -np.inf  # never self-recommend
    voters = sims >= min_similarity
    if not np.any(voters):
        return []

    mask = ~np.isnan(matrix)
    filled = np.where(mask, matrix, 0.0)

    vote_weights = np.where(voters, sims, 0.0)
    weighted_sum = vote_weights @ filled
    total_weight = vote_weights @ mask.astype(float)
    voter_count = voters.astype(float) @ mask.astype(float)

    candidates = ~mask[user_index] & (total_weight > 0) & (voter_count >= min_voters)
    if not np.any(candidates):
        return []

    predicted = weighted_sum[candidates] / total_weight[candidates]
    item_indices = np.nonzero(candidates)[0]
    order = np.argsort(predicted, kind="stable")[::-1][:top_k]
    return [(int(item_indices[i]), float(predicted[i])) for i in order]
