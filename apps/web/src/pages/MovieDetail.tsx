import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { DEMO_USER_ID, getMovie, rateMovie } from '../api/client';
import EmptyState from '../components/EmptyState';
import RatingStars from '../components/RatingStars';
import { MovieCardSkeleton } from '../components/Skeleton';

export default function MovieDetail() {
  const id = Number(useParams().id);
  const queryClient = useQueryClient();
  const [saved, setSaved] = useState(false);
  const [myRating, setMyRating] = useState(0);
  const movie = useQuery({ queryKey: ['movie', id], queryFn: () => getMovie(id) });
  const rate = useMutation({
    mutationFn: (rating: number) => rateMovie(DEMO_USER_ID, id, rating),
    onSuccess: () => {
      setSaved(true);
      void queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });

  if (movie.isPending) return <MovieCardSkeleton />;
  if (movie.isError || !movie.data)
    return <EmptyState title="Not found" message="That movie does not exist." />;

  return (
    <div>
      <h1>{movie.data.title}</h1>
      <RatingStars
        value={myRating}
        onRate={(v) => {
          setMyRating(v);
          rate.mutate(v);
        }}
        label={`Rate ${movie.data.title}`}
      />
      {rate.isPending && <p>Saving…</p>}
      {saved && !rate.isPending && <p>Saved — recommendations will refresh.</p>}
    </div>
  );
}
