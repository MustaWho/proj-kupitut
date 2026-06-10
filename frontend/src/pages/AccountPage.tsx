import { useEffect, useState, type ChangeEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { Upload } from "lucide-react";
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
  const { userId } = useParams();
  const [avatarMessage, setAvatarMessage] = useState<string | null>(null);
  const [roleMessage, setRoleMessage] = useState<string | null>(null);
  const [roleOverride, setRoleOverride] = useState<"user" | "seller" | null>(null);
  const viewedUserId = userId ? Number(userId) : auth.user?.id;
  const isAdminViewingOther =
    Boolean(userId) && auth.user?.role === "admin" && viewedUserId !== auth.user.id;
  const {
    data: viewedUser,
    loading: userLoading,
    error: userError
  } = useAsync(
    () =>
      isAdminViewingOther && viewedUserId
        ? api.getUser(viewedUserId)
        : Promise.resolve(auth.user),
    [auth.user?.id, auth.user?.role, isAdminViewingOther, viewedUserId]
  );
  const { data, loading, error } = useAsync(
    () => (viewedUser ? api.recommendations(viewedUser.id) : Promise.resolve([])),
    [viewedUser?.id]
  );

  useEffect(() => {
    setRoleOverride(null);
  }, [viewedUser?.id]);

  async function uploadAvatar(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!auth.user || !file || isAdminViewingOther) return;
    setAvatarMessage(null);
    try {
      const user = await api.uploadAvatar(auth.user.id, file);
      auth.updateUser(user);
      setAvatarMessage("Аватар обновлён");
    } catch (err) {
      setAvatarMessage(err instanceof Error ? err.message : "Не удалось загрузить аватар");
    } finally {
      event.target.value = "";
    }
  }

  async function changeViewedRole(role: "user" | "seller") {
    if (!viewedUser || auth.user?.role !== "admin") return;
    setRoleMessage(null);
    try {
      await api.updateUser(viewedUser.id, { role });
      setRoleOverride(role);
      setRoleMessage("Роль пользователя обновлена");
    } catch (err) {
      setRoleMessage(err instanceof Error ? err.message : "Не удалось изменить роль");
    }
  }

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

  if (userLoading) return <Loading />;
  if (userError) return <ErrorMessage message={userError} />;
  if (!viewedUser) return <ErrorMessage message="Пользователь не найден" />;

  return (
    <section className="page">
      <div className="account-head">
        <div className="avatar-large">
          {viewedUser.avatar_url ? (
            <img src={viewedUser.avatar_url} alt={viewedUser.username} />
          ) : (
            viewedUser.username.slice(0, 1).toUpperCase()
          )}
        </div>
        <div className="account-id">
          <strong>@{viewedUser.username}</strong>
          <span>ID пользователя: {viewedUser.id}</span>
        </div>
        {!isAdminViewingOther && (
          <label className="file-picker compact">
            <Upload aria-hidden="true" />
            <span>Загрузить аватар</span>
            <input
              aria-label="Аватар пользователя"
              accept="image/png,image/jpeg,image/webp,image/gif"
              type="file"
              onChange={(event) => void uploadAvatar(event)}
            />
          </label>
        )}
      </div>
      {avatarMessage && <p className="status">{avatarMessage}</p>}
      {isAdminViewingOther && (
        <div className="form-panel admin-role-panel">
          <h2>Профиль пользователя</h2>
          <p>ID: {viewedUser.id}</p>
          <p>Email: {viewedUser.email}</p>
          <p>Статус: {viewedUser.is_active ? "активен" : "заблокирован"}</p>
          <select
            aria-label="Роль пользователя"
            value={(roleOverride ?? viewedUser.role) === "seller" ? "seller" : "user"}
            onChange={(event) => void changeViewedRole(event.target.value as "user" | "seller")}
          >
            <option value="user">Покупатель</option>
            <option value="seller">Продавец</option>
          </select>
          {roleMessage && <p className="status">{roleMessage}</p>}
        </div>
      )}
      <div className="section-title">
        <div>
          <h1>Личный кабинет</h1>
          <p>{viewedUser.email}</p>
        </div>
        <span className="pill">{roleLabels[roleOverride ?? viewedUser.role]}</span>
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
