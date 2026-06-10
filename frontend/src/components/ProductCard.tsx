import { Link } from "react-router-dom";
import { ShoppingCart, Star } from "lucide-react";
import type { Product } from "../types";

type ProductCardProps = {
  product: Product;
  onAdd: (product: Product) => void;
};

function discountedPrice(product: Product) {
  const price = Number(product.price);
  return product.discount_percent > 0 ? price * (1 - product.discount_percent / 100) : price;
}

export function ProductCard({ product, onAdd }: ProductCardProps) {
  const hasDiscount = product.discount_percent > 0;

  return (
    <article className="product-card">
      <Link className="product-media" to={`/products/${product.id}`}>
        {hasDiscount && <span className="discount-badge">-{product.discount_percent}%</span>}
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} />
        ) : (
          <span>{product.category.name}</span>
        )}
      </Link>
      <div className="product-body">
        <div>
          <Link className="product-title" to={`/products/${product.id}`}>
            {product.name}
          </Link>
          <p>{product.description ?? "Описание товара будет добавлено позже."}</p>
        </div>
        <div className="product-footer">
          <div className="price-block">
            <strong>{discountedPrice(product).toLocaleString("ru-RU")} ₽</strong>
            {hasDiscount && <span>{Number(product.price).toLocaleString("ru-RU")} ₽</span>}
          </div>
          <span className="rating">
            <Star aria-hidden="true" />
            {product.rating.toFixed(1)}
          </span>
          <button className="icon-button" type="button" onClick={() => onAdd(product)} title="В корзину">
            <ShoppingCart aria-hidden="true" />
          </button>
        </div>
      </div>
    </article>
  );
}
