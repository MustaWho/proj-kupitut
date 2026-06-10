import { describe, expect, it } from "vitest";
import { cartReducer, cartTotal, validateCheckout } from "./cartLogic";
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

describe("cartReducer", () => {
  it("добавляет товар и увеличивает количество при повторном добавлении", () => {
    const one = cartReducer([], { type: "add", product, quantity: 2 });
    const two = cartReducer(one, { type: "add", product, quantity: 3 });

    expect(two).toHaveLength(1);
    expect(two[0].quantity).toBe(5);
    expect(cartTotal(two)).toBe(500);
  });

  it("удаляет товар, если количество меньше одного", () => {
    const lines = cartReducer([{ product, quantity: 1 }], {
      type: "setQuantity",
      productId: product.id,
      quantity: 0
    });

    expect(lines).toHaveLength(0);
  });
});

describe("validateCheckout", () => {
  it("возвращает сообщения для обязательных полей", () => {
    expect(validateCheckout({ customerName: "", phone: "12345", address: "Москва" })).toBe(
      "Введите имя получателя"
    );
    expect(validateCheckout({ customerName: "Анна", phone: "1", address: "Москва" })).toBe(
      "Введите телефон"
    );
  });

  it("принимает корректные данные заказа", () => {
    expect(
      validateCheckout({
        customerName: "Анна",
        phone: "+79990000000",
        address: "Москва, Тестовая улица, 1"
      })
    ).toBeNull();
  });
});
