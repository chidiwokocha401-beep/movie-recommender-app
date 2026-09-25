import type { ReactNode } from 'react';
import ScoreBadge from './ScoreBadge';

type Props = {
  title: string;
  subtitle?: string;
  score?: number;
  children?: ReactNode;
};

export default function MovieCard({ title, subtitle, score, children }: Props) {
  return (
    <article className="movie-card">
      <div className="movie-card__poster" aria-hidden="true">
        {title.charAt(0)}
      </div>
      <div>
        <h3 className="movie-card__title">{title}</h3>
        {subtitle && <p className="movie-card__subtitle">{subtitle}</p>}
        {score !== undefined && <ScoreBadge score={score} />}
        {children}
      </div>
    </article>
  );
}
