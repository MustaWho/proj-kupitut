import { createContext, useContext, useEffect, useMemo, useReducer, type ReactNode } from "react";
import type { CartLine, Product } from "../types";
import { cartReducer, cartTotal } from "./cartLogic";
import { loadCart, saveCart } from "./storage";

type CartState = {
  lines: CartLine[];
  total: number;
  count: number;
  add: (product: Product, quantity?: number) => void;
  setQuantity: (productId: number, quantity: number) => void;
  remove: (productId: number) => void;
  clear: () => void;
};

const CartContext = createContext<CartState | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, dispatch] = useReducer(cartReducer, undefined, loadCart);

  useEffect(() => {
    saveCart(lines);
  }, [lines]);

  const value = useMemo<CartState>(
    () => ({
      lines,
      total: cartTotal(lines),
      count: lines.reduce((sum, line) => sum + line.quantity, 0),
      add(product, quantity = 1) {
        dispatch({ type: "add", product, quantity });
      },
      setQuantity(productId, quantity) {
        dispatch({ type: "setQuantity", productId, quantity });
      },
      remove(productId) {
        dispatch({ type: "remove", productId });
      },
      clear() {
        dispatch({ type: "clear" });
      }
    }),
    [lines]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used inside CartProvider");
  }
  return context;
}
