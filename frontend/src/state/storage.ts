import type { CartLine } from "../types";

const CART_KEY = "shop_cart";
const AUTH_KEY = "shop_auth";

export function loadCart(): CartLine[] {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY) ?? "[]") as CartLine[];
  } catch {
    return [];
  }
}

export function saveCart(lines: CartLine[]) {
  localStorage.setItem(CART_KEY, JSON.stringify(lines));
}

export function loadAuth<T>(): T | null {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

export function saveAuth(value: unknown) {
  localStorage.setItem(AUTH_KEY, JSON.stringify(value));
}

export function clearAuth() {
  localStorage.removeItem(AUTH_KEY);
}
