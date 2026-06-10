export function Loading() {
  return <p className="status">Загрузка...</p>;
}

export function ErrorMessage({ message }: { message: string }) {
  return <p className="status error">{message}</p>;
}
