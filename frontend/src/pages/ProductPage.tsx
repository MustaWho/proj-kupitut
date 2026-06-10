import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Edit, ShoppingCart, Star, Trash2 } from "lucide-react";
import { api } from "../api/client";
import { ErrorMessage, Loading } from "../components/Status";
import { useAuth } from "../state/AuthContext";
import { useCart } from "../state/CartContext";
import { productFinalPrice } from "../state/cartLogic";
import type { Product } from "../types";

export function ProductPage() {
  const { productId } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reviewText, setReviewText] = useState("");
  const [rating, setRating] = useState(5);
  const auth = useAuth();
  const cart = useCart();
  const navigate = useNavigate();
  const id = Number(productId);
  const canSeeProductId = auth.user?.role === "seller" || auth.user?.role === "admin";
  const isAdmin = auth.user?.role === "admin";

  useEffect(() => {
    setLoading(true);
    api
      .getProduct(id)
      .then((next) => {
        setProduct(next);
        if (auth.user) {
          void api.recordView(auth.user.id, next.id);
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Не удалось загрузить товар"))
      .finally(() => setLoading(false));
  }, [auth.user, id]);

  async function submitReview(event: FormEvent) {
    event.preventDefault();
    if (!auth.user || !product) {
      setError("Войдите, чтобы оставить отзыв");
      return;
    }
    await api.createReview(product.id, {
      user_id: auth.user.id,
      rating,
      text: reviewText
    });
    setReviewText("");
    setProduct(await api.getProduct(product.id));
  }

  async function deleteProduct() {
    if (!product || !isAdmin) return;
    await api.deleteProduct(product.id);
    navigate("/catalog");
  }

  if (loading) return <Loading />;
  if (error && !product) return <ErrorMessage message={error} />;
  if (!product) return <ErrorMessage message="Товар не найден" />;

  return (
    <section className="product-page">
      <div className="product-photo">
        {product.discount_percent > 0 && <span className="discount-badge">-{product.discount_percent}%</span>}
        {product.image_url ? <img src={product.image_url} alt={product.name} /> : product.category.name}
      </div>
      <div className="product-detail">
        <span className="pill">{product.category.name}</span>
        {canSeeProductId && <span className="product-id">ID товара: {product.id}</span>}
        <h1>{product.name}</h1>
        <p>{product.description ?? "Подробное описание появится позже."}</p>
        <div className="detail-row">
          <div className="price-block">
            <strong>{productFinalPrice(product).toLocaleString("ru-RU")} ₽</strong>
            {product.discount_percent > 0 && (
              <span>{Number(product.price).toLocaleString("ru-RU")} ₽</span>
            )}
          </div>
          <span className="rating">
            <Star aria-hidden="true" />
            {product.rating.toFixed(1)}
          </span>
        </div>
        <button className="button" type="button" onClick={() => cart.add(product)}>
          <ShoppingCart aria-hidden="true" />
          В корзину
        </button>
        {isAdmin && (
          <div className="admin-product-actions">
            <Link className="button secondary" to={`/admin?productId=${product.id}`}>
              <Edit aria-hidden="true" />
              Изменить
            </Link>
            <button className="button danger" type="button" onClick={() => void deleteProduct()}>
              <Trash2 aria-hidden="true" />
              Удалить
            </button>
          </div>
        )}
      </div>
      <section className="reviews">
        <h2>Отзывы</h2>
        <form className="review-form" onSubmit={submitReview}>
          <select value={rating} onChange={(event) => setRating(Number(event.target.value))}>
            {[5, 4, 3, 2, 1].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <input
            value={reviewText}
            minLength={3}
            placeholder="Ваш отзыв"
            onChange={(event) => setReviewText(event.target.value)}
          />
          <button className="button secondary" type="submit">
            Отправить
          </button>
        </form>
        {error && <ErrorMessage message={error} />}
        {product.reviews.map((review) => (
          <article className="review" key={review.id}>
            <div className="review-author">
              <div className="avatar-small">
                {review.user?.avatar_url ? (
                  <img src={review.user.avatar_url} alt={review.user.username} />
                ) : (
                  (review.user?.username ?? "П").slice(0, 1).toUpperCase()
                )}
              </div>
              <div>
                <strong>{review.user?.username ?? `Пользователь ${review.user_id}`}</strong>
                <span>{review.rating}/5</span>
              </div>
            </div>
            <p>{review.text}</p>
          </article>
        ))}
      </section>
    </section>
  );
}
