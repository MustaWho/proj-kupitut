"""Shop business logic."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.dto.shop import (
    CartItemCreate,
    CartItemUpdate,
    CategoryCreate,
    CheckoutCreate,
    ProductCreate,
    ProductUpdate,
    PromotionCreate,
    PromotionUpdate,
    ReviewCreate,
)
from app.models import CartItem, Category, Order, OrderItem, Product, Promotion, Review, User
from app.repositories.shop import shop_crud
from app.utils.exceptions import BadRequestError, ConflictError, NotFoundError


class ShopService:
    """Use cases for catalog, cart, orders, reviews, and promotions."""

    def __init__(self, db: Session):
        self.db = db

    async def create_category(self, payload: CategoryCreate) -> Category:
        if shop_crud.get_category_by_name(self.db, payload.name):
            raise ConflictError("Такая категория уже существует")
        return shop_crud.create_category(self.db, payload.name.strip())

    async def list_categories(self) -> list[Category]:
        return shop_crud.list_categories(self.db)

    async def create_product(self, payload: ProductCreate) -> Product:
        self._ensure_category(payload.category_id)
        values = payload.model_dump()
        values["rating"] = 0
        seller_id = values.get("seller_id")
        if seller_id is not None:
            self._ensure_seller(int(seller_id))
        return shop_crud.create_product(self.db, values)

    async def list_products(
        self,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_rating: float | None = None,
        search: str | None = None,
        seller_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        return shop_crud.list_products(
            self.db,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            search=search,
            seller_id=seller_id,
            offset=offset,
            limit=limit,
        )

    async def get_product(self, product_id: int) -> Product:
        product = shop_crud.get_product(self.db, product_id)
        if product is None:
            raise NotFoundError("Товар не найден")
        return product

    async def update_product(self, product_id: int, payload: ProductUpdate) -> Product:
        product = await self.get_product(product_id)
        values = payload.model_dump(exclude_unset=True)
        if "category_id" in values:
            self._ensure_category(int(values["category_id"]))
        if "seller_id" in values and values["seller_id"] is not None:
            self._ensure_seller(int(values["seller_id"]))
        return shop_crud.update_product(self.db, product, values)

    async def delete_product(self, product_id: int) -> None:
        product = await self.get_product(product_id)
        shop_crud.delete_product(self.db, product)

    async def create_review(self, product_id: int, payload: ReviewCreate) -> Review:
        await self.get_product(product_id)
        self._ensure_user(payload.user_id)
        values = payload.model_dump()
        values["product_id"] = product_id
        try:
            review = shop_crud.create_review(self.db, values)
        except Exception:
            self.db.rollback()
            raise ConflictError("Пользователь уже оставил отзыв на этот товар")
        self._recalculate_product_rating(product_id)
        return review

    async def record_view(self, user_id: int, product_id: int) -> None:
        self._ensure_user(user_id)
        await self.get_product(product_id)
        shop_crud.add_view(self.db, user_id, product_id)

    async def recommendations(self, user_id: int, limit: int = 10) -> list[Product]:
        self._ensure_user(user_id)
        recommendations = shop_crud.list_recommendations(self.db, user_id, limit=limit)
        if recommendations:
            return recommendations
        return shop_crud.list_products(self.db, min_rating=4, offset=0, limit=limit)

    async def add_to_cart(self, user_id: int, payload: CartItemCreate) -> CartItem:
        self._ensure_user(user_id)
        await self.get_product(payload.product_id)
        item = shop_crud.get_cart_item_by_product(self.db, user_id, payload.product_id)
        if item:
            item.quantity += payload.quantity
        else:
            item = CartItem(
                user_id=user_id,
                product_id=payload.product_id,
                quantity=payload.quantity,
            )
        return shop_crud.save_cart_item(self.db, item)

    async def list_cart(
        self,
        user_id: int,
        product_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[CartItem], Decimal]:
        self._ensure_user(user_id)
        items = shop_crud.list_cart_items(
            self.db,
            user_id=user_id,
            product_id=product_id,
            offset=offset,
            limit=limit,
        )
        total = sum(
            Decimal(item.quantity) * self._product_price_with_discount(item.product)
            for item in items
        )
        return items, total

    async def update_cart_item(
        self,
        user_id: int,
        item_id: int,
        payload: CartItemUpdate,
    ) -> CartItem:
        item = shop_crud.get_cart_item(self.db, item_id)
        if item is None or item.user_id != user_id:
            raise NotFoundError("Позиция корзины не найдена")
        item.quantity = payload.quantity
        return shop_crud.save_cart_item(self.db, item)

    async def delete_cart_item(self, user_id: int, item_id: int) -> None:
        item = shop_crud.get_cart_item(self.db, item_id)
        if item is None or item.user_id != user_id:
            raise NotFoundError("Позиция корзины не найдена")
        shop_crud.delete_cart_item(self.db, item)

    async def checkout(self, user_id: int, payload: CheckoutCreate) -> Order:
        items, total = await self.list_cart(user_id)
        if not items:
            raise BadRequestError("Корзина пуста")
        order = Order(user_id=user_id, total_amount=total, **payload.model_dump())
        self.db.add(order)
        self.db.flush()
        for item in items:
            self.db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=self._product_price_with_discount(item.product),
                )
            )
            self.db.delete(item)
        self.db.commit()
        self.db.refresh(order)
        return order

    async def list_promotions(
        self, active_only: bool = False, offset: int = 0, limit: int = 100
    ) -> list[Promotion]:
        return shop_crud.list_promotions(
            self.db,
            active_only=active_only,
            offset=offset,
            limit=limit,
        )

    async def create_promotion(self, payload: PromotionCreate) -> Promotion:
        self._validate_promotion_target(payload.product_id, payload.category_id)
        return shop_crud.create_promotion(self.db, payload.model_dump())

    async def update_promotion(self, promotion_id: int, payload: PromotionUpdate) -> Promotion:
        promotion = shop_crud.get_promotion(self.db, promotion_id)
        if promotion is None:
            raise NotFoundError("Акция не найдена")
        values = payload.model_dump(exclude_unset=True)
        product_id = values.get("product_id", promotion.product_id)
        category_id = values.get("category_id", promotion.category_id)
        self._validate_promotion_target(product_id, category_id)
        return shop_crud.update_promotion(self.db, promotion, values)

    async def delete_promotion(self, promotion_id: int) -> None:
        promotion = shop_crud.get_promotion(self.db, promotion_id)
        if promotion is None:
            raise NotFoundError("Акция не найдена")
        shop_crud.delete_promotion(self.db, promotion)

    def _ensure_user(self, user_id: int) -> User:
        user = self.db.get(User, user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    def _ensure_category(self, category_id: int) -> Category:
        category = shop_crud.get_category(self.db, category_id)
        if category is None:
            raise NotFoundError("Категория не найдена")
        return category

    def _ensure_seller(self, user_id: int) -> User:
        user = self._ensure_user(user_id)
        if user.role not in {"seller", "admin"}:
            raise BadRequestError("Товары могут добавлять только продавцы и администраторы")
        return user

    def _validate_promotion_target(
        self, product_id: int | None, category_id: int | None
    ) -> None:
        if product_id is None and category_id is None:
            raise BadRequestError("Акция должна быть привязана к товару или категории")
        if product_id is not None:
            product = shop_crud.get_product(self.db, product_id)
            if product is None:
                raise NotFoundError("Товар не найден")
        if category_id is not None:
            self._ensure_category(category_id)

    def _recalculate_product_rating(self, product_id: int) -> None:
        product = shop_crud.get_product(self.db, product_id)
        if product is None or not product.reviews:
            return
        product.rating = sum(review.rating for review in product.reviews) / len(product.reviews)
        self.db.commit()

    def _product_price_with_discount(self, product: Product) -> Decimal:
        price = Decimal(product.price)
        if product.discount_percent <= 0:
            return price
        return price * (Decimal(100 - product.discount_percent) / Decimal(100))
