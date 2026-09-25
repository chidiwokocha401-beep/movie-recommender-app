# Movie Recommender App

User-based collaborative filtering recommender built on the MovieLens 100K dataset (`u.data`, `u.item`).

Given a user ID, it finds users with similar tastes and recommends movies they liked that the input user has not seen.

## How it works

1. **Similarity** (`movie-recommender-main/similarity_scores.py`):
   - `pearson_score()` – Pearson correlation over co-rated movies (-1 to 1). Returns 0 if no overlap or zero variance.
   - `euclidean_score()` – `1 / (1 + sqrt(sum squared diffs))` over co-rated movies.
2. **Find similar users** (`movie-recommender-main/collaborative_filtering.py` – `find_similar_users()`):
   - Scores the input user against every other user with Pearson, sorts descending, returns top-N.
3. **Recommend** (`movie-recommender-main/movie_recommender.py` – `get_recommendations()`):
   - Keeps users with similarity >= 0.8, collects movies they rated that the input user has not rated, weights by similarity, ranks highest first.

## Project structure

```
.
├── README.md
└── movie-recommender-main/
    ├── movie_recommender.py       # CLI: recommend movies for --user
    ├── collaborative_filtering.py # CLI: find similar users to --user
    ├── similarity_scores.py       # CLI: score --user1 --user2 with Euclidean|Pearson
    ├── u.data                     # MovieLens ratings: userID, movieID, rating, timestamp (tab-separated)
    └── u.item                     # MovieLens titles: movieID|title (latin-1)
```

## Requirements

- Python 3.10+
- `pandas`, `numpy`
- Git LFS (the 70MB chocolate sales CSV is stored with Git LFS)

```powershell
pip install pandas numpy
```

Clone with LFS support so the large data file downloads correctly:

```powershell
git lfs install
git clone <repo-url>
```

## Usage

Run from the `movie-recommender-main/` folder:

```powershell
cd movie-recommender-main

# 1. Similarity between two users
python similarity_scores.py --user1 1 --user2 2 --score-type Pearson
python similarity_scores.py --user1 1 --user2 2 --score-type Euclidean

# 2. Top-3 similar users
python collaborative_filtering.py --user 1

# 3. Movie recommendations
python movie_recommender.py --user 1
```

Example output:

```
Movie recommendations for 1:
1. Star Wars (1977)
2. Fargo (1996)
...
```

## Dataset

MovieLens 100K sample included as `u.data` (100,000 ratings, 943 users, 1682 movies) and `u.item` (movie IDs/titles). Format follows the original GroupLens release.

## Development (Slice 0 scaffold)

Monorepo layout — legacy prototype in `movie-recommender-main/` is untouched:

```
apps/api/            # FastAPI backend (Slice 4 fills in endpoints)
apps/web/            # React + TypeScript frontend (Slices 5-6 fill in UI)
packages/recommender/ # Shared recommendation core (Slice 2 ports the algorithms)
```

Bootstrap (one command per app):

```powershell
# API + recommender core (Python 3.10+)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e apps/api[dev] -e packages/recommender[dev]

# Web (Node 20+)
npm run bootstrap:web
```

Verify:

```powershell
pytest apps/api packages/recommender   # Python tests
ruff check apps/api packages/recommender
npm run lint --prefix apps/web; npm run build --prefix apps/web
```

Pre-commit (ruff for Python; ESLint runs in CI and via `npm run lint`):

```powershell
pip install pre-commit; pre-commit install
```

CI (`.github/workflows/ci.yml`) runs Python lint+tests and web lint+build on every PR and push to `main`.

## Limitations

- User-based only, no item-based or matrix factorization.
- In-memory `pandas` filtering per pair – slow on large data.
- Fixed 0.8 similarity cutoff can yield `No recommendations possible` for sparse users.
- No train/test evaluation.

## Next steps

- Accumulate (not overwrite) scores when multiple similar users rate the same movie.
- Lower/tune cutoff, add top-K weighting.
- Add `requirements.txt`, evaluation (precision/recall, RMSE), and precomputed similarity matrix.
