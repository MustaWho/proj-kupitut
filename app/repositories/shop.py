"""Shop persistence operations."""

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    CartItem,
    Category,
    Product,
    ProductView,
    Promotion,
    Review,
)


class ShopCRUD:
    """Persistence operations for shop entities."""

    def get_category(self, db: Session, category_id: int) -> Category | None:
        return db.get(Category, category_id)

    def get_category_by_name(self, db: Session, name: str) -> Category | None:
        return db.scalar(select(Category).where(func.lower(Category.name) == name.lower()))

    def list_categories(self, db: Session) -> list[Category]:
        return list(db.scalars(select(Category).order_by(Category.name)))

    def create_category(self, db: Session, name: str) -> Category:
        category = Category(name=name)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def get_product(self, db: Session, product_id: int) -> Product | None:
        return db.scalar(
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.category), selectinload(Product.reviews))
        )

    def list_products(
        self,
        db: Session,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_rating: float | None = None,
        search: str | None = None,
        seller_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        query = select(Product).options(
            selectinload(Product.category),
            selectinload(Product.reviews),
        )
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        if min_rating is not None:
            query = query.where(Product.rating >= min_rating)
        if search:
            query = query.where(Product.name.ilike(f"%{search}%"))
        if seller_id is not None:
            query = query.where(Product.seller_id == seller_id)
        query = query.order_by(Product.id).offset(offset).limit(limit)
        return list(db.scalars(query))

    def create_product(self, db: Session, values: dict[str, object]) -> Product:
        product = Product(**values)
        db.add(product)
        db.commit()
        db.refresh(product)
        return self.get_product(db, product.id) or product

    def update_product(self, db: Session, product: Product, values: dict[str, object]) -> Product:
        for field, value in values.items():
            setattr(product, field, value)
        db.commit()
        db.refresh(product)
        return self.get_product(db, product.id) or product

    def delete_product(self, db: Session, product: Product) -> None:
        db.delete(product)
        db.commit()

    def create_review(self, db: Session, values: dict[str, object]) -> Review:
        review = Review(**values)
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    def add_view(self, db: Session, user_id: int, product_id: int) -> ProductView:
        view = ProductView(user_id=user_id, product_id=product_id)
        db.add(view)
        db.commit()
        db.refresh(view)
        return view

    def viewed_category_ids(self, db: Session, user_id: int) -> list[int]:
        rows = db.execute(
            select(Product.category_id)
            .join(ProductView, ProductView.product_id == Product.id)
            .where(ProductView.user_id == user_id)
            .group_by(Product.category_id)
            .order_by(desc(func.count(ProductView.id)))
        )
        return [int(row[0]) for row in rows]

    def viewed_product_ids(self, db: Session, user_id: int) -> list[int]:
        return list(
            db.scalars(select(ProductView.product_id).where(ProductView.user_id == user_id))
        )

    def list_recommendations(self, db: Session, user_id: int, limit: int = 10) -> list[Product]:
        category_ids = self.viewed_category_ids(db, user_id)
        viewed_ids = self.viewed_product_ids(db, user_id)
        query = select(Product).options(
            selectinload(Product.category),
            selectinload(Product.reviews),
        )
        if category_ids:
            query = query.where(Product.category_id.in_(category_ids))
        if viewed_ids:
            query = query.where(Product.id.not_in(viewed_ids))
        query = query.where(Product.is_active.is_(True)).order_by(Product.rating.desc(), Product.id)
        return list(db.scalars(query.limit(limit)))

    def get_cart_item(self, db: Session, item_id: int) -> CartItem | None:
        return db.scalar(
            select(CartItem)
            .where(CartItem.id == item_id)
            .options(
                selectinload(CartItem.product).selectinload(Product.category),
                selectinload(CartItem.product).selectinload(Product.reviews),
            )
        )

    def get_cart_item_by_product(
        self, db: Session, user_id: int, product_id: int
    ) -> CartItem | None:
        return db.scalar(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
        )

    def list_cart_items(
        self,
        db: Session,
        user_id: int,
        product_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[CartItem]:
        query = (
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(
                selectinload(CartItem.product).selectinload(Product.category),
                selectinload(CartItem.product).selectinload(Product.reviews),
            )
        )
        if product_id is not None:
            query = query.where(CartItem.product_id == product_id)
        return list(db.scalars(query.order_by(CartItem.id).offset(offset).limit(limit)))

    def save_cart_item(self, db: Session, item: CartItem) -> CartItem:
        db.add(item)
        db.commit()
        db.refresh(item)
        return self.get_cart_item(db, item.id) or item

    def delete_cart_item(self, db: Session, item: CartItem) -> None:
        db.delete(item)
        db.commit()

    def list_promotions(
        self, db: Session, active_only: bool = False, offset: int = 0, limit: int = 100
    ) -> list[Promotion]:
        query = select(Promotion).order_by(Promotion.id)
        if active_only:
            query = query.where(Promotion.is_active.is_(True))
        return list(db.scalars(query.offset(offset).limit(limit)))

    def get_promotion(self, db: Session, promotion_id: int) -> Promotion | None:
        return db.get(Promotion, promotion_id)

    def create_promotion(self, db: Session, values: dict[str, object]) -> Promotion:
        promotion = Promotion(**values)
        db.add(promotion)
        db.commit()
        db.refresh(promotion)
        return promotion

    def update_promotion(
        self, db: Session, promotion: Promotion, values: dict[str, object]
    ) -> Promotion:
        for field, value in values.items():
            setattr(promotion, field, value)
        db.commit()
        db.refresh(promotion)
        return promotion

    def delete_promotion(self, db: Session, promotion: Promotion) -> None:
        db.delete(promotion)
        db.commit()


shop_crud = ShopCRUD()
