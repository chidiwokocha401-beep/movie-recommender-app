export default function ScoreBadge({ score }: { score: number }) {
  const level = score >= 4 ? 'high' : score >= 3 ? 'mid' : 'low';
  return (
    <span className={`badge badge--${level}`} aria-label={`Predicted score ${score}`}>
      ★ {score.toFixed(1)}
    </span>
  );
}
