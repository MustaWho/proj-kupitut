import { FormEvent, useState } from "react";
import { Trash2 } from "lucide-react";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";
import { useCart } from "../state/CartContext";
import { productFinalPrice, validateCheckout } from "../state/cartLogic";

export function CartPage() {
  const cart = useCart();
  const auth = useAuth();
  const [customerName, setCustomerName] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  async function checkout(event: FormEvent) {
    event.preventDefault();
    const validation = validateCheckout({ customerName, phone, address });
    if (validation) {
      setMessage(validation);
      return;
    }
    if (!auth.user) {
      setMessage("Войдите, чтобы оформить заказ");
      return;
    }
    try {
      for (const line of cart.lines) {
        await api.addToBackendCart(auth.user.id, line.product.id, line.quantity);
      }
      await api.checkout(auth.user.id, {
        customer_name: customerName,
        phone,
        address
      });
      cart.clear();
      setMessage("Заказ оформлен");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Не удалось оформить заказ");
    }
  }

  return (
    <section className="page cart-page">
      <div className="section-title">
        <h1>Корзина</h1>
        <strong>{cart.total.toLocaleString("ru-RU")} ₽</strong>
      </div>
      <div className="cart-layout">
        <div className="cart-lines">
          {cart.lines.map((line) => (
            <article className="cart-line" key={line.product.id}>
              <div>
                <strong>{line.product.name}</strong>
                <p>{productFinalPrice(line.product).toLocaleString("ru-RU")} ₽</p>
              </div>
              <input
                aria-label={`Количество: ${line.product.name}`}
                type="number"
                min="1"
                value={line.quantity}
                onChange={(event) => cart.setQuantity(line.product.id, Number(event.target.value))}
              />
              <button
                className="icon-button"
                type="button"
                onClick={() => cart.remove(line.product.id)}
                title="Удалить"
              >
                <Trash2 aria-hidden="true" />
              </button>
            </article>
          ))}
          {cart.lines.length === 0 && <p className="empty">Корзина пуста.</p>}
        </div>
        <form className="form-panel" onSubmit={checkout}>
          <h2>Оформление заказа</h2>
          <input
            placeholder="Имя получателя"
            value={customerName}
            onChange={(event) => setCustomerName(event.target.value)}
          />
          <input placeholder="Телефон" value={phone} onChange={(event) => setPhone(event.target.value)} />
          <input placeholder="Адрес доставки" value={address} onChange={(event) => setAddress(event.target.value)} />
          {message && <p className="status">{message}</p>}
          <button className="button" type="submit" disabled={cart.lines.length === 0}>
            Оформить заказ
          </button>
        </form>
      </div>
    </section>
  );
}
