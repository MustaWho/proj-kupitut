import { FormEvent, useEffect, useMemo, useState } from "react";
import { Plus, Save, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";
import type { Category, Product } from "../types";

export function AdminPage() {
  const { user } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [categoryName, setCategoryName] = useState("Электроника");
  const [name, setName] = useState("Беспроводные наушники");
  const [price, setPrice] = useState("199.90");
  const [discount, setDiscount] = useState(0);
  const [imageUrl, setImageUrl] = useState("");
  const [description, setDescription] = useState("Товар добавлен через КупиТут");
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const isAdmin = user?.role === "admin";
  const isSeller = user?.role === "seller";
  const canManage = isAdmin || isSeller;

  const visibleProducts = useMemo(() => {
    if (isAdmin) return products;
    if (isSeller && user) return products.filter((product) => product.seller_id === user.id);
    return [];
  }, [isAdmin, isSeller, products, user]);

  async function reload() {
    const [nextCategories, nextProducts] = await Promise.all([
      api.listCategories(),
      api.listProducts()
    ]);
    setCategories(nextCategories);
    setProducts(nextProducts);
    setCategoryId((current) => current || nextCategories[0]?.id || "");
  }

  useEffect(() => {
    if (canManage) {
      void reload();
    }
  }, [canManage]);

  function fillProduct(product: Product) {
    setEditingId(product.id);
    setName(product.name);
    setPrice(product.price);
    setDiscount(product.discount_percent);
    setImageUrl(product.image_url ?? "");
    setDescription(product.description ?? "");
    setCategoryId(product.category_id);
  }

  function clearProductForm() {
    setEditingId(null);
    setName("Беспроводные наушники");
    setPrice("199.90");
    setDiscount(0);
    setImageUrl("");
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
    const payload = {
      name,
      price,
      discount_percent: discount,
      category_id: Number(categoryId),
      seller_id: user.id,
      image_url: imageUrl || undefined,
      description
    };

    try {
      if (editingId) {
        await api.updateProduct(editingId, payload);
        setMessage("Товар обновлён");
      } else {
        await api.createProduct(payload);
        setMessage("Товар добавлен");
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
          <p>{isAdmin ? "Администратор управляет категориями и всеми товарами." : "Продавец управляет своими товарами."}</p>
        </div>
        <span>{visibleProducts.length} товаров</span>
      </div>

      <div className="admin-grid">
        {isAdmin && (
          <form className="form-panel" onSubmit={createCategory}>
            <h2>Категория</h2>
            <input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} />
            <button className="button secondary" type="submit">
              <Plus aria-hidden="true" />
              Добавить
            </button>
          </form>
        )}

        <form className="form-panel" onSubmit={saveProduct}>
          <h2>{editingId ? "Редактирование товара" : "Новый товар"}</h2>
          <input value={name} onChange={(event) => setName(event.target.value)} />
          <select value={categoryId} onChange={(event) => setCategoryId(Number(event.target.value))}>
            <option value="">Категория</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          <input value={price} type="number" min="0" step="0.01" onChange={(event) => setPrice(event.target.value)} />
          <input
            aria-label="Скидка"
            value={discount}
            type="number"
            min="0"
            max="100"
            onChange={(event) => setDiscount(Number(event.target.value))}
          />
          <input
            aria-label="Ссылка на изображение"
            placeholder="Ссылка на изображение"
            value={imageUrl}
            onChange={(event) => setImageUrl(event.target.value)}
          />
          <input
            aria-label="Описание"
            placeholder="Описание"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
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

      {message && <p className="status">{message}</p>}

      <div className="admin-list">
        {visibleProducts.map((product) => (
          <article className="cart-line" key={product.id}>
            <div>
              <strong>{product.name}</strong>
              <p>
                {product.category.name} · {Number(product.price).toLocaleString("ru-RU")} ₽
                {product.discount_percent > 0 ? ` · скидка ${product.discount_percent}%` : ""}
              </p>
            </div>
            <button className="icon-button" type="button" onClick={() => fillProduct(product)} title="Изменить">
              <Save aria-hidden="true" />
            </button>
            <button className="icon-button" type="button" onClick={() => void deleteProduct(product)} title="Удалить">
              <Trash2 aria-hidden="true" />
            </button>
          </article>
        ))}
        {visibleProducts.length === 0 && <p className="empty">Товаров пока нет.</p>}
      </div>
    </section>
  );
}
