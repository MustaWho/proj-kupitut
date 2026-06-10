import type { AuthResponse, Category, Product, ProductFilters, Promotion, UserRole } from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "/api/v1";

type RequestOptions = RequestInit & {
  query?: Record<string, string | number | boolean | undefined>;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = new URL(`${API_URL}${path}`, window.location.origin);
  Object.entries(options.query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const validationMessage = Array.isArray(body?.detail)
      ? body.detail.map((item: { msg?: string }) => item.msg).join("; ")
      : null;
    throw new Error(body?.error?.message ?? validationMessage ?? "Не удалось выполнить запрос");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  register(payload: {
    email: string;
    username: string;
    password: string;
    role?: UserRole;
    first_name?: string;
    last_name?: string;
  }) {
    return request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  login(payload: { login: string; password: string }) {
    return request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  listCategories() {
    return request<Category[]>("/categories");
  },
  createCategory(name: string) {
    return request<Category>("/categories", {
      method: "POST",
      body: JSON.stringify({ name })
    });
  },
  listProducts(filters: ProductFilters = {}) {
    return request<Product[]>("/products", {
      query: {
        category_id: filters.categoryId,
        min_price: filters.minPrice,
        max_price: filters.maxPrice,
        min_rating: filters.minRating,
        search: filters.search,
        seller_id: filters.sellerId
      }
    });
  },
  getProduct(productId: number) {
    return request<Product>(`/products/${productId}`);
  },
  createProduct(payload: {
    name: string;
    category_id: number;
    price: string;
    discount_percent?: number;
    seller_id?: number;
    description?: string;
    image_url?: string;
  }) {
    return request<Product>("/products", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  updateProduct(productId: number, payload: Partial<Product>) {
    return request<Product>(`/products/${productId}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });
  },
  deleteProduct(productId: number) {
    return request<void>(`/products/${productId}`, { method: "DELETE" });
  },
  createReview(productId: number, payload: { user_id: number; rating: number; text: string }) {
    return request(`/products/${productId}/reviews`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  recordView(userId: number, productId: number) {
    return request<void>(`/users/${userId}/views`, {
      method: "POST",
      body: JSON.stringify({ product_id: productId })
    });
  },
  recommendations(userId: number) {
    return request<Product[]>(`/users/${userId}/recommendations`);
  },
  addToBackendCart(userId: number, productId: number, quantity: number) {
    return request(`/users/${userId}/cart`, {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity })
    });
  },
  checkout(userId: number, payload: { customer_name: string; phone: string; address: string }) {
    return request(`/users/${userId}/checkout`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  listPromotions(activeOnly = true) {
    return request<Promotion[]>("/promotions", {
      query: { active_only: activeOnly }
    });
  },
  createPromotion(payload: Omit<Promotion, "id">) {
    return request<Promotion>("/promotions", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }
};
