export function MovieCardSkeleton() {
  return (
    <div className="movie-card" aria-hidden="true">
      <div className="movie-card__poster skeleton" />
      <div style={{ flex: 1 }}>
        <div className="skeleton" style={{ height: '1.25rem', width: '60%' }} />
        <div
          className="skeleton"
          style={{ height: '0.875rem', width: '40%', marginTop: '0.5rem' }}
        />
      </div>
    </div>
  );
}

export default function Skeleton({ label = 'Loading…' }: { label?: string }) {
  return (
    <div role="status" aria-label={label}>
      <MovieCardSkeleton />
    </div>
  );
}
