const BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

/** Auth stub (Slice 6 scope): every visitor acts as the demo user. */
export const DEMO_USER_ID = 1;

export type Movie = { movie_id: number; title: string };
export type Recommendation = {
  movie_id: number;
  title: string | null;
  score: number;
  rank: number;
};
export type SimilarUser = { user_id: number; similarity: number; rank: number };

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) throw new Error(`${init?.method ?? 'GET'} ${path}: ${res.status}`);
  return res.json() as Promise<T>;
}

export const listMovies = (search: string, limit = 20) =>
  req<Movie[]>(`/movies?${new URLSearchParams({ search, limit: String(limit) })}`);

export const getMovie = (id: number) => req<Movie>(`/movies/${id}`);

export const rateMovie = (user_id: number, movie_id: number, rating: number) =>
  req(`/ratings`, {
    method: 'POST',
    body: JSON.stringify({ user_id, movie_id, rating }),
  });

export const getRecommendations = (userId: number, k = 10) =>
  req<Recommendation[]>(`/users/${userId}/recommendations?k=${k}`);

export const getSimilarUsers = (userId: number, n = 5) =>
  req<SimilarUser[]>(`/users/${userId}/similar?n=${n}`);
