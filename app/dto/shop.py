"""Shop request and response schemas."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, field_validator

from app.dto.base import ORMBaseModel


class CategoryCreate(ORMBaseModel):
    """Create category payload."""

    name: str = Field(min_length=2, max_length=120)


class CategoryRead(CategoryCreate):
    """Category response."""

    id: int
    created_at: datetime
    updated_at: datetime


class ProductBase(ORMBaseModel):
    """Shared product fields."""

    name: str = Field(min_length=2, max_length=180)
    category_id: int = Field(gt=0)
    price: Decimal = Field(ge=0, decimal_places=2)
    discount_percent: int = Field(default=0, ge=0, le=100)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True
    seller_id: int | None = Field(default=None, gt=0)


class ProductCreate(ProductBase):
    """Create product payload."""


class ProductUpdate(ORMBaseModel):
    """Update product payload."""

    name: str | None = Field(default=None, min_length=2, max_length=180)
    category_id: int | None = Field(default=None, gt=0)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    discount_percent: int | None = Field(default=None, ge=0, le=100)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    seller_id: int | None = Field(default=None, gt=0)


class ReviewUserRead(ORMBaseModel):
    """Public review author fields."""

    id: int
    username: str
    avatar_url: str | None = None


class ReviewRead(ORMBaseModel):
    """Product review response."""

    id: int
    user_id: int
    product_id: int
    rating: int
    text: str
    created_at: datetime
    user: ReviewUserRead | None = None


class ProductRead(ProductBase):
    """Product response with category and reviews."""

    id: int
    rating: float
    created_at: datetime
    updated_at: datetime
    category: CategoryRead
    reviews: list[ReviewRead] = []


class ReviewCreate(ORMBaseModel):
    """Create review payload."""

    user_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=3, max_length=2000)


class CartItemCreate(ORMBaseModel):
    """Add product to cart payload."""

    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0, le=100)


class CartItemUpdate(ORMBaseModel):
    """Update cart item payload."""

    quantity: int = Field(gt=0, le=100)


class CartItemRead(ORMBaseModel):
    """Cart item response."""

    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductRead


class CartRead(ORMBaseModel):
    """User cart with calculated total."""

    user_id: int
    items: list[CartItemRead]
    total_amount: Decimal


class CheckoutCreate(ORMBaseModel):
    """Checkout payload."""

    customer_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(min_length=5, max_length=40)
    address: str = Field(min_length=5, max_length=300)


class OrderItemRead(ORMBaseModel):
    """Order line response."""

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderRead(ORMBaseModel):
    """Order response."""

    id: int
    user_id: int
    customer_name: str
    phone: str
    address: str
    total_amount: Decimal
    status: str
    items: list[OrderItemRead]
    created_at: datetime


class SaleUserRead(ORMBaseModel):
    """Short user data for sales history."""

    id: int
    username: str
    email: str


class SaleProductRead(ORMBaseModel):
    """Short product data for sales history."""

    id: int
    name: str


class SaleRead(ORMBaseModel):
    """Sold product history line."""

    order_id: int
    order_item_id: int
    product: SaleProductRead
    buyer: SaleUserRead
    seller: SaleUserRead | None = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    sold_at: datetime


class ProductViewCreate(ORMBaseModel):
    """Record product view payload."""

    product_id: int = Field(gt=0)


class PromotionBase(ORMBaseModel):
    """Shared promotion fields."""

    title: str = Field(min_length=2, max_length=160)
    discount_percent: int = Field(ge=0, le=100)
    starts_at: date
    ends_at: date
    description: str | None = None
    is_active: bool = True
    product_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)

    @field_validator("ends_at")
    @classmethod
    def validate_dates(cls, value: date, info):  # type: ignore[no-untyped-def]
        """Promotion end date cannot precede its start date."""

        starts_at = info.data.get("starts_at")
        if starts_at and value < starts_at:
            raise ValueError("ends_at must be greater than or equal to starts_at")
        return value


class PromotionCreate(PromotionBase):
    """Create promotion payload."""


class PromotionUpdate(ORMBaseModel):
    """Update promotion payload."""

    title: str | None = Field(default=None, min_length=2, max_length=160)
    discount_percent: int | None = Field(default=None, ge=0, le=100)
    starts_at: date | None = None
    ends_at: date | None = None
    description: str | None = None
    is_active: bool | None = None
    product_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)


class PromotionRead(PromotionBase):
    """Promotion response."""

    id: int
    created_at: datetime
    updated_at: datetime
