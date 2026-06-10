import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { CartPage } from "./CartPage";
import type { Product } from "../types";

const product: Product = {
  id: 1,
  name: "Наушники",
  category_id: 1,
  category: { id: 1, name: "Электроника" },
  price: "100.00",
  rating: 4.5,
  discount_percent: 0,
  is_active: true,
  reviews: []
};

vi.mock("../state/AuthContext", () => ({
  useAuth: () => ({ user: null })
}));

vi.mock("../state/CartContext", () => ({
  useCart: () => ({
    lines: [{ product, quantity: 2 }],
    total: 200,
    setQuantity: vi.fn(),
    remove: vi.fn(),
    clear: vi.fn()
  })
}));

describe("CartPage", () => {
  it("проверяет данные заказа перед отправкой", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <CartPage />
      </MemoryRouter>
    );

    await user.click(screen.getByRole("button", { name: "Оформить заказ" }));

    expect(screen.getByText("Введите имя получателя")).toBeInTheDocument();
  });
});
