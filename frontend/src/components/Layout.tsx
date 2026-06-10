import { Link, NavLink, Outlet } from "react-router-dom";
import { LogOut, ShoppingCart, Store } from "lucide-react";
import { useAuth } from "../state/AuthContext";
import { useCart } from "../state/CartContext";

export function Layout() {
  const { user, logout } = useAuth();
  const { count } = useCart();
  const canManage = user?.role === "seller" || user?.role === "admin";

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/">
          <Store aria-hidden="true" />
          КупиТут
        </Link>
        <nav className="nav">
          <NavLink to="/catalog">Каталог</NavLink>
          <NavLink to="/account">Кабинет</NavLink>
          {canManage && <NavLink to="/admin">Управление</NavLink>}
        </nav>
        <div className="topbar-actions">
          <Link className="cart-link" to="/cart" aria-label="Корзина">
            <ShoppingCart aria-hidden="true" />
            <span>{count}</span>
          </Link>
          {user ? (
            <button className="icon-button" type="button" onClick={logout} title="Выйти">
              <LogOut aria-hidden="true" />
            </button>
          ) : (
            <Link className="button secondary" to="/auth">
              Войти
            </Link>
          )}
        </div>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
