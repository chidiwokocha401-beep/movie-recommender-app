import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { listMovies } from '../api/client';
import Input from '../components/Input';
import MovieCard from '../components/MovieCard';

export default function Search() {
  const [query, setQuery] = useState('');
  const results = useQuery({
    queryKey: ['movies', query],
    queryFn: () => listMovies(query),
    enabled: query.trim().length > 0,
  });

  return (
    <div>
      <h1>Search movies</h1>
      <Input
        label="Search movies"
        type="search"
        placeholder="Star Wars…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {results.data?.map((m) => (
        <Link key={m.movie_id} to={`/movies/${m.movie_id}`} aria-label={m.title}>
          <MovieCard title={m.title} />
        </Link>
      ))}
    </div>
  );
}
