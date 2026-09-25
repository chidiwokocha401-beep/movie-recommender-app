import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { DEMO_USER_ID, getRecommendations, getSimilarUsers } from '../api/client';
import EmptyState from '../components/EmptyState';
import MovieCard from '../components/MovieCard';
import ScoreBadge from '../components/ScoreBadge';
import { MovieCardSkeleton } from '../components/Skeleton';

export default function Home() {
  const recs = useQuery({
    queryKey: ['recommendations', DEMO_USER_ID],
    queryFn: () => getRecommendations(DEMO_USER_ID),
  });
  const similar = useQuery({
    queryKey: ['similar-users', DEMO_USER_ID],
    queryFn: () => getSimilarUsers(DEMO_USER_ID),
  });

  return (
    <div>
      <h1>Recommended for you</h1>
      {recs.isPending && <MovieCardSkeleton />}
      {recs.isError && (
        <EmptyState title="Could not load" message="Is the API running?" />
      )}
      {recs.data?.length === 0 && (
        <EmptyState
          title="No recommendations yet"
          message="Rate a few movies and check back."
        />
      )}
      {recs.data?.map((r) => (
        <Link
          key={r.movie_id}
          to={`/movies/${r.movie_id}`}
          aria-label={r.title ?? `Movie ${r.movie_id}`}
        >
          <MovieCard title={r.title ?? `Movie ${r.movie_id}`}>
            <ScoreBadge score={r.score} />
          </MovieCard>
        </Link>
      ))}

      <h2>Similar users</h2>
      {similar.data?.length === 0 && (
        <EmptyState title="Nobody similar yet" message="Rate more movies." />
      )}
      <ul>
        {similar.data?.map((u) => (
          <li key={u.user_id}>
            User {u.user_id} — similarity {u.similarity.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}
