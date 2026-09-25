export default function EmptyState({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return (
    <div className="empty" role="status">
      <h3 className="empty__title">{title}</h3>
      <p>{message}</p>
    </div>
  );
}
