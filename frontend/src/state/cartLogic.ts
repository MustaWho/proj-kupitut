import type { CartLine, Product } from "../types";

export type CartAction =
  | { type: "add"; product: Product; quantity?: number }
  | { type: "setQuantity"; productId: number; quantity: number }
  | { type: "remove"; productId: number }
  | { type: "clear" };

export function productFinalPrice(product: Product): number {
  const price = Number(product.price);
  return product.discount_percent > 0 ? price * (1 - product.discount_percent / 100) : price;
}

export function cartReducer(lines: CartLine[], action: CartAction): CartLine[] {
  if (action.type === "clear") {
    return [];
  }

  if (action.type === "remove") {
    return lines.filter((line) => line.product.id !== action.productId);
  }

  if (action.type === "setQuantity") {
    if (action.quantity < 1) {
      return lines.filter((line) => line.product.id !== action.productId);
    }
    return lines.map((line) =>
      line.product.id === action.productId ? { ...line, quantity: action.quantity } : line
    );
  }

  const quantity = action.quantity ?? 1;
  const existing = lines.find((line) => line.product.id === action.product.id);
  if (existing) {
    return lines.map((line) =>
      line.product.id === action.product.id
        ? { ...line, quantity: line.quantity + quantity }
        : line
    );
  }
  return [...lines, { product: action.product, quantity }];
}

export function cartTotal(lines: CartLine[]): number {
  return lines.reduce((sum, line) => sum + productFinalPrice(line.product) * line.quantity, 0);
}

export function validateCheckout(values: {
  customerName: string;
  phone: string;
  address: string;
}): string | null {
  if (values.customerName.trim().length < 2) {
    return "Введите имя получателя";
  }
  if (values.phone.trim().length < 5) {
    return "Введите телефон";
  }
  if (values.address.trim().length < 5) {
    return "Введите адрес доставки";
  }
  return null;
}
