import { Link } from "react-router-dom";
import { api } from "../api/client";
import { ProductCard } from "../components/ProductCard";
import { ErrorMessage, Loading } from "../components/Status";
import { useAsync } from "../hooks/useAsync";
import { useAuth } from "../state/AuthContext";
import { useCart } from "../state/CartContext";
import type { UserRole } from "../types";

const roleLabels: Record<UserRole, string> = {
  user: "Покупатель",
  seller: "Продавец",
  admin: "Администратор"
};

export function AccountPage() {
  const auth = useAuth();
  const cart = useCart();
  const { data, loading, error } = useAsync(
    () => (auth.user ? api.recommendations(auth.user.id) : Promise.resolve([])),
    [auth.user?.id]
  );

  if (!auth.user) {
    return (
      <section className="page narrow">
        <h1>Личный кабинет</h1>
        <p className="empty">Войдите, чтобы увидеть рекомендации по истории просмотров.</p>
        <Link className="button" to="/auth">
          Войти
        </Link>
      </section>
    );
  }

  return (
    <section className="page">
      <div className="section-title">
        <div>
          <h1>Личный кабинет</h1>
          <p>{auth.user.email}</p>
        </div>
        <span className="pill">{roleLabels[auth.user.role]}</span>
      </div>
      <h2>Рекомендации для вас</h2>
      {loading && <Loading />}
      {error && <ErrorMessage message={error} />}
      <div className="product-grid">
        {(data ?? []).map((product) => (
          <ProductCard key={product.id} product={product} onAdd={cart.add} />
        ))}
      </div>
      {!loading && !error && data?.length === 0 && (
        <p className="empty">Откройте несколько товаров, и здесь появятся персональные рекомендации.</p>
      )}
    </section>
  );
}
