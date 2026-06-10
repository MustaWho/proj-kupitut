import { FormEvent, useEffect, useMemo, useState } from "react";
import { Ban, Edit, Eye, Plus, Save, Trash2, Upload } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";
import type { Category, Product, Sale, User, UserRole } from "../types";

const roleLabels: Record<UserRole, string> = {
  user: "Покупатель",
  seller: "Продавец",
  admin: "Администратор"
};

export function AdminPage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [sales, setSales] = useState<Sale[]>([]);
  const [activeTab, setActiveTab] = useState<"products" | "users" | "sales">("products");
  const [categoryName, setCategoryName] = useState("Электроника");
  const [name, setName] = useState("Беспроводные наушники");
  const [price, setPrice] = useState("199.90");
  const [discount, setDiscount] = useState(0);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [description, setDescription] = useState("Товар добавлен через КупиТут");
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [productIdSearch, setProductIdSearch] = useState(searchParams.get("productId") ?? "");
  const [userSearch, setUserSearch] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const isAdmin = user?.role === "admin";
  const isSeller = user?.role === "seller";
  const canManage = isAdmin || isSeller;

  const visibleProducts = useMemo(() => {
    const base = isAdmin
      ? products
      : isSeller && user
        ? products.filter((product) => product.seller_id === user.id)
        : [];
    if (!isAdmin || !productIdSearch.trim()) return base;
    return base.filter((product) => String(product.id) === productIdSearch.trim());
  }, [isAdmin, isSeller, productIdSearch, products, user]);

  const foundUsers = useMemo(() => {
    const query = userSearch.trim().toLowerCase();
    if (!query) return users;
    return users.filter(
      (item) =>
        String(item.id) === query ||
        item.email.toLowerCase().includes(query) ||
        item.username.toLowerCase().includes(query)
    );
  }, [userSearch, users]);

  const bannedUsers = users.filter((item) => !item.is_active);

  async function reload() {
    const [nextCategories, nextProducts] = await Promise.all([
      api.listCategories(),
      api.listProducts()
    ]);
    setCategories(nextCategories);
    setProducts(nextProducts);
    setCategoryId((current) => current || nextCategories[0]?.id || "");
  }

  async function reloadAdminData() {
    if (!isAdmin) return;
    const [nextUsers, nextSales] = await Promise.all([api.listUsers(), api.listSales()]);
    setUsers(nextUsers);
    setSales(nextSales);
  }

  useEffect(() => {
    if (canManage) {
      void reload();
    }
  }, [canManage]);

  useEffect(() => {
    void reloadAdminData();
  }, [isAdmin]);

  useEffect(() => {
    const productId = searchParams.get("productId");
    if (!productId || products.length === 0) return;
    const product = products.find((item) => String(item.id) === productId);
    if (product) {
      setProductIdSearch(productId);
      fillProduct(product);
    }
  }, [products, searchParams]);

  function fillProduct(product: Product) {
    setEditingId(product.id);
    setName(product.name);
    setPrice(product.price);
    setDiscount(product.discount_percent);
    setImageFile(null);
    setDescription(product.description ?? "");
    setCategoryId(product.category_id);
  }

  function clearProductForm() {
    setEditingId(null);
    setName("Беспроводные наушники");
    setPrice("199.90");
    setDiscount(0);
    setImageFile(null);
    setDescription("Товар добавлен через КупиТут");
  }

  async function createCategory(event: FormEvent) {
    event.preventDefault();
    if (!isAdmin) {
      setMessage("Категории может добавлять только администратор");
      return;
    }
    try {
      const category = await api.createCategory(categoryName);
      setCategories((current) => [...current, category]);
      setCategoryId(category.id);
      setMessage("Категория добавлена");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Не удалось добавить категорию");
    }
  }

  async function saveProduct(event: FormEvent) {
    event.preventDefault();
    if (!user || !canManage) {
      setMessage("Товары могут добавлять только продавцы и администраторы");
      return;
    }
    if (!categoryId) {
      setMessage("Сначала выберите категорию");
      return;
    }
    const currentProduct = editingId
      ? products.find((product) => product.id === editingId)
      : null;
    const payload = {
      name,
      price,
      discount_percent: discount,
      category_id: Number(categoryId),
      seller_id: currentProduct?.seller_id ?? user.id,
      description
    };

    try {
      let savedProduct: Product;
      if (editingId) {
        savedProduct = await api.updateProduct(editingId, payload);
        setMessage("Товар обновлён");
      } else {
        savedProduct = await api.createProduct(payload);
        setMessage("Товар добавлен");
      }
      if (imageFile) {
        await api.uploadProductImage(savedProduct.id, user.id, imageFile);
      }
      clearProductForm();
      await reload();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Не удалось сохранить товар");
    }
  }

  async function deleteProduct(product: Product) {
    if (!isAdmin && product.seller_id !== user?.id) {
      setMessage("Продавец может удалять только свои товары");
      return;
    }
    await api.deleteProduct(product.id);
    setProducts((current) => current.filter((item) => item.id !== product.id));
  }

  async function updateUserRole(target: User, role: "user" | "seller") {
    await api.updateUser(target.id, { role });
    await reloadAdminData();
  }

  async function setUserBan(target: User, isActive: boolean) {
    await api.updateUser(target.id, { is_active: isActive });
    await reloadAdminData();
  }

  if (!user) {
    return (
      <section className="page narrow">
        <h1>Управление</h1>
        <p className="empty">Войдите как продавец или администратор.</p>
        <Link className="button" to="/auth">
          Войти
        </Link>
      </section>
    );
  }

  if (!canManage) {
    return (
      <section className="page narrow">
        <h1>Управление</h1>
        <p className="empty">Покупатель не может управлять товарами. Зарегистрируйтесь как продавец.</p>
      </section>
    );
  }

  return (
    <section className="page admin-page">
      <div className="section-title">
        <div>
          <h1>Управление КупиТут</h1>
          <p>
            {isAdmin
              ? "Администратор управляет категориями, пользователями и товарами."
              : "Продавец управляет своими товарами."}
          </p>
        </div>
        <span>{visibleProducts.length} товаров</span>
      </div>

      {isAdmin && (
        <div className="segmented admin-tabs">
          <button
            type="button"
            className={activeTab === "products" ? "active" : ""}
            onClick={() => setActiveTab("products")}
          >
            Товары
          </button>
          <button
            type="button"
            className={activeTab === "users" ? "active" : ""}
            onClick={() => setActiveTab("users")}
          >
            Пользователи
          </button>
          <button
            type="button"
            className={activeTab === "sales" ? "active" : ""}
            onClick={() => setActiveTab("sales")}
          >
            Продажи
          </button>
        </div>
      )}

      {activeTab === "products" && (
        <>
          <div className="admin-grid">
            {isAdmin && (
              <form className="form-panel" onSubmit={createCategory}>
                <h2>Категория</h2>
                <label>
                  Название категории
                  <input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} />
                </label>
                <button className="button secondary" type="submit">
                  <Plus aria-hidden="true" />
                  Добавить
                </button>
              </form>
            )}

            <form className="form-panel" onSubmit={saveProduct}>
              <h2>{editingId ? "Редактирование товара" : "Новый товар"}</h2>
              <label>
                Название товара
                <input value={name} onChange={(event) => setName(event.target.value)} />
              </label>
              <label>
                Категория
                <select value={categoryId} onChange={(event) => setCategoryId(Number(event.target.value))}>
                  <option value="">Выберите категорию</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Цена, руб.
                <input value={price} type="number" min="0" step="0.01" onChange={(event) => setPrice(event.target.value)} />
              </label>
              <label>
                Процент скидки
                <input
                  value={discount}
                  type="number"
                  min="0"
                  max="100"
                  onChange={(event) => setDiscount(Number(event.target.value))}
                />
              </label>
              <label className="file-picker">
                <Upload aria-hidden="true" />
                <span>{imageFile ? imageFile.name : "Загрузить изображение товара"}</span>
                <input
                  aria-label="Изображение товара"
                  accept="image/png,image/jpeg,image/webp,image/gif"
                  type="file"
                  onChange={(event) => setImageFile(event.target.files?.[0] ?? null)}
                />
              </label>
              <label>
                Описание товара
                <textarea
                  value={description}
                  rows={6}
                  onChange={(event) => setDescription(event.target.value)}
                />
              </label>
              <button className="button" type="submit">
                <Save aria-hidden="true" />
                {editingId ? "Сохранить" : "Добавить товар"}
              </button>
              {editingId && (
                <button className="button secondary" type="button" onClick={clearProductForm}>
                  Отменить
                </button>
              )}
            </form>
          </div>

          {isAdmin && (
            <div className="toolbar-row">
              <input
                aria-label="Поиск товара по ID"
                placeholder="Поиск товара по ID"
                value={productIdSearch}
                onChange={(event) => setProductIdSearch(event.target.value)}
              />
              {productIdSearch && (
                <button className="button secondary" type="button" onClick={() => setProductIdSearch("")}>
                  Сбросить
                </button>
              )}
            </div>
          )}

          {message && <p className="status">{message}</p>}

          <div className="admin-list">
            {visibleProducts.map((product) => (
              <article className="cart-line admin-line" key={product.id}>
                <div>
                  <strong>{product.name}</strong>
                  <p>
                    ID {product.id} · {product.category.name} · {Number(product.price).toLocaleString("ru-RU")} ₽
                    {product.discount_percent > 0 ? ` · скидка ${product.discount_percent}%` : ""}
                  </p>
                </div>
                <Link className="button secondary" to={`/products/${product.id}`}>
                  <Eye aria-hidden="true" />
                  Карточка
                </Link>
                <button className="button secondary" type="button" onClick={() => fillProduct(product)}>
                  <Edit aria-hidden="true" />
                  Изменить
                </button>
                <button className="button danger" type="button" onClick={() => void deleteProduct(product)}>
                  <Trash2 aria-hidden="true" />
                  Удалить
                </button>
              </article>
            ))}
            {visibleProducts.length === 0 && <p className="empty">Товары не найдены.</p>}
          </div>
        </>
      )}

      {isAdmin && activeTab === "users" && (
        <div className="admin-section">
          <div className="toolbar-row">
            <input
              aria-label="Поиск пользователя"
              placeholder="ID, email или логин пользователя"
              value={userSearch}
              onChange={(event) => setUserSearch(event.target.value)}
            />
          </div>
          <div className="admin-list">
            {foundUsers.map((item) => (
              <article className="cart-line admin-line" key={item.id}>
                <div>
                  <strong>@{item.username}</strong>
                  <p>
                    ID {item.id} · {item.email} · {roleLabels[item.role]} ·{" "}
                    {item.is_active ? "активен" : "заблокирован"}
                  </p>
                </div>
                <select
                  aria-label="Роль пользователя"
                  value={item.role === "seller" ? "seller" : "user"}
                  disabled={item.role === "admin"}
                  onChange={(event) => void updateUserRole(item, event.target.value as "user" | "seller")}
                >
                  <option value="user">Покупатель</option>
                  <option value="seller">Продавец</option>
                </select>
                <Link className="button secondary" to={`/account/${item.id}`}>
                  <Eye aria-hidden="true" />
                  Профиль
                </Link>
                {item.is_active ? (
                  <button
                    className="button danger"
                    type="button"
                    disabled={item.role === "admin"}
                    onClick={() => void setUserBan(item, false)}
                  >
                    <Ban aria-hidden="true" />
                    Забанить
                  </button>
                ) : (
                  <button className="button secondary" type="button" onClick={() => void setUserBan(item, true)}>
                    Разбанить
                  </button>
                )}
              </article>
            ))}
          </div>

          <h2>Заблокированные пользователи</h2>
          <div className="admin-list">
            {bannedUsers.map((item) => (
              <article className="cart-line admin-line" key={item.id}>
                <div>
                  <strong>@{item.username}</strong>
                  <p>ID {item.id} · {item.email}</p>
                </div>
                <button className="button secondary" type="button" onClick={() => void setUserBan(item, true)}>
                  Снять блокировку
                </button>
              </article>
            ))}
            {bannedUsers.length === 0 && <p className="empty">Заблокированных пользователей нет.</p>}
          </div>
        </div>
      )}

      {isAdmin && activeTab === "sales" && (
        <div className="admin-list">
          {sales.map((sale) => (
            <article className="cart-line admin-line" key={sale.order_item_id}>
              <div>
                <strong>{sale.product.name}</strong>
                <p>
                  Товар ID {sale.product.id} · заказ ID {sale.order_id} · {sale.quantity} шт. ·{" "}
                  {Number(sale.total_price).toLocaleString("ru-RU")} ₽
                </p>
                <p>
                  Купил: @{sale.buyer.username} ID {sale.buyer.id} · Продавал:{" "}
                  {sale.seller ? `@${sale.seller.username} ID ${sale.seller.id}` : "не указан"}
                </p>
              </div>
              <Link className="button secondary" to={`/products/${sale.product.id}`}>
                <Eye aria-hidden="true" />
                Товар
              </Link>
            </article>
          ))}
          {sales.length === 0 && <p className="empty">Продаж пока нет.</p>}
        </div>
      )}
    </section>
  );
}
