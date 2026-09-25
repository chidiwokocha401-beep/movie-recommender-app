import { useRef, useState } from 'react';

type Props = {
  value?: number;
  onRate?: (value: number) => void;
  label?: string;
  readOnly?: boolean;
};

/** 1–5 star rating. Keyboard: Tab to the group, arrows move, Enter/Space rates. */
export default function RatingStars({
  value = 0,
  onRate,
  label = 'Your rating',
  readOnly = false,
}: Props) {
  const [hover, setHover] = useState(0);
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  const shown = hover || value;

  const move = (index: number) => {
    const next = (index + 5) % 5;
    refs.current[next]?.focus();
  };

  return (
    <div
      className="stars"
      role="group"
      aria-label={label}
      onMouseLeave={() => setHover(0)}
    >
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          ref={(el) => {
            refs.current[star - 1] = el;
          }}
          type="button"
          role="radio"
          aria-checked={value === star}
          aria-label={`${star} star${star > 1 ? 's' : ''}`}
          tabIndex={star === (value || 1) ? 0 : -1}
          disabled={readOnly}
          className={star <= shown ? 'star star--on' : 'star'}
          onClick={() => onRate?.(star)}
          onMouseEnter={() => !readOnly && setHover(star)}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight' || e.key === 'ArrowUp') move(star);
            if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') move(star - 2);
          }}
        >
          <span aria-hidden="true">★</span>
        </button>
      ))}
    </div>
  );
}
