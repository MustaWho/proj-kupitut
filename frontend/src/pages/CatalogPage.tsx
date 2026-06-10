import { useEffect, useState } from "react";
import { api } from "../api/client";
import { CatalogFilters } from "../components/CatalogFilters";
import { ProductCard } from "../components/ProductCard";
import { ErrorMessage, Loading } from "../components/Status";
import { useCart } from "../state/CartContext";
import type { Category, Product, ProductFilters } from "../types";

export function CatalogPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [filters, setFilters] = useState<ProductFilters>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const cart = useCart();

  useEffect(() => {
    void api.listCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .listProducts(filters)
      .then(setProducts)
      .catch((err) => setError(err instanceof Error ? err.message : "Не удалось загрузить товары"))
      .finally(() => setLoading(false));
  }, [filters]);

  return (
    <section className="page">
      <div className="section-title">
        <h1>Каталог</h1>
        <span>{products.length} товаров</span>
      </div>
      <CatalogFilters categories={categories} filters={filters} onChange={setFilters} />
      {loading && <Loading />}
      {error && <ErrorMessage message={error} />}
      <div className="product-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} onAdd={cart.add} />
        ))}
      </div>
      {!loading && !error && products.length === 0 && (
        <p className="empty">Товары не найдены. Измените фильтры или добавьте товар.</p>
      )}
    </section>
  );
}
