"""Shop API integration tests."""


def register_user(client, email: str = "buyer@example.com", username: str = "buyer") -> int:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": "secret123",
            "first_name": "Buyer",
            "last_name": "Tester",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    return int(body["user"]["id"])


def create_category(client, name: str = "Electronics") -> int:
    response = client.post("/api/v1/categories", json={"name": name})
    assert response.status_code == 201
    return int(response.json()["id"])


def create_product(
    client,
    category_id: int,
    name: str = "Wireless headphones",
    price: str = "199.90",
    rating: float = 4.5,
) -> int:
    response = client.post(
        "/api/v1/products",
        json={
            "name": name,
            "category_id": category_id,
            "price": price,
            "rating": rating,
            "description": "Comfortable everyday headphones",
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_auth_register_login_refresh_and_change_password(client) -> None:
    register_user(client)

    login = client.post(
        "/api/v1/auth/login",
        json={"login": "buyer", "password": "secret123"},
    )
    assert login.status_code == 200

    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login.json()["refresh_token"]},
    )
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]

    changed = client.post(
        "/api/v1/auth/change-password",
        json={
            "email": "buyer@example.com",
            "old_password": "secret123",
            "new_password": "newsecret123",
        },
    )
    assert changed.status_code == 204

    assert (
        client.post("/api/v1/auth/login", json={"login": "buyer", "password": "newsecret123"})
        .status_code
        == 200
    )


def test_catalog_filters_reviews_and_recommendations(client) -> None:
    user_id = register_user(client)
    category_id = create_category(client)
    another_category_id = create_category(client, "Books")
    product_id = create_product(client, category_id)
    recommended_id = create_product(client, category_id, "Portable speaker", "89.00", 4.8)
    create_product(client, another_category_id, "Notebook", "12.00", 4.9)

    filtered = client.get(
        "/api/v1/products",
        params={"category_id": category_id, "min_price": 50, "limit": 10},
    )
    assert filtered.status_code == 200
    assert {product["id"] for product in filtered.json()} == {product_id, recommended_id}

    review = client.post(
        f"/api/v1/products/{product_id}/reviews",
        json={"user_id": user_id, "rating": 5, "text": "Excellent sound and build quality"},
    )
    assert review.status_code == 201
    assert client.get(f"/api/v1/products/{product_id}").json()["reviews"][0]["rating"] == 5

    assert (
        client.post(f"/api/v1/users/{user_id}/views", json={"product_id": product_id}).status_code
        == 204
    )
    recommendations = client.get(f"/api/v1/users/{user_id}/recommendations").json()
    assert recommendations[0]["id"] == recommended_id


def test_cart_checkout_and_promotions(client) -> None:
    user_id = register_user(client)
    category_id = create_category(client)
    product_id = create_product(client, category_id, price="100.00")

    add_to_cart = client.post(
        f"/api/v1/users/{user_id}/cart",
        json={"product_id": product_id, "quantity": 2},
    )
    assert add_to_cart.status_code == 201
    item_id = add_to_cart.json()["id"]

    patched = client.patch(f"/api/v1/users/{user_id}/cart/{item_id}", json={"quantity": 3})
    assert patched.status_code == 200

    cart = client.get(f"/api/v1/users/{user_id}/cart", params={"product_id": product_id})
    assert cart.status_code == 200
    assert cart.json()["total_amount"] == "300.00"

    order = client.post(
        f"/api/v1/users/{user_id}/checkout",
        json={
            "customer_name": "Buyer Tester",
            "phone": "+79990000000",
            "address": "Moscow, Test street, 1",
        },
    )
    assert order.status_code == 200
    assert order.json()["total_amount"] == "300.00"
    assert client.get(f"/api/v1/users/{user_id}/cart").json()["items"] == []

    promotion = client.post(
        "/api/v1/promotions",
        json={
            "title": "Summer sale",
            "discount_percent": 15,
            "starts_at": "2026-06-01",
            "ends_at": "2026-06-30",
            "category_id": category_id,
        },
    )
    assert promotion.status_code == 201
    assert client.get("/api/v1/promotions", params={"active_only": True}).json()[0]["title"] == (
        "Summer sale"
    )
