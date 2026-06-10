import { Link } from "react-router-dom";
import { api } from "../api/client";
import { ProductCard } from "../components/ProductCard";
import { ErrorMessage, Loading } from "../components/Status";
import { useAsync } from "../hooks/useAsync";
import { useCart } from "../state/CartContext";

export function HomePage() {
  const cart = useCart();
  const { data: products, loading, error } = useAsync(() => api.listProducts(), []);
  const saleProducts = (products ?? []).filter((product) => product.discount_percent > 0).slice(0, 4);
  const regularProducts = (products ?? [])
    .filter((product) => product.discount_percent === 0)
    .slice(0, 12);

  return (
    <section className="home-page">
      <div className="hero">
        <div>
          <h1>КупиТут</h1>
          <p>Маркетплейс для покупателей, продавцов и администраторов.</p>
        </div>
        <Link className="button" to="/catalog">
          Перейти в каталог
        </Link>
      </div>

      <section className="section">
        <div className="section-title">
          <h2>Товары по акции</h2>
          <Link to="/catalog">Все товары</Link>
        </div>
        {loading && <Loading />}
        {error && <ErrorMessage message={error} />}
        <div className="product-grid home-products">
          {saleProducts.map((product) => (
            <ProductCard key={product.id} product={product} onAdd={cart.add} />
          ))}
        </div>
        {!loading && !error && saleProducts.length === 0 && (
          <p className="empty">Акционных товаров пока нет. Продавцы могут добавить скидку в разделе управления.</p>
        )}
      </section>

      <section className="section">
        <div className="section-title">
          <h2>Популярные товары</h2>
          <span>Плитка до 4 строк</span>
        </div>
        <div className="product-grid home-products">
          {regularProducts.map((product) => (
            <ProductCard key={product.id} product={product} onAdd={cart.add} />
          ))}
        </div>
        {!loading && !error && regularProducts.length === 0 && (
          <p className="empty">Товары пока не добавлены.</p>
        )}
      </section>
    </section>
  );
}
