"""Shop endpoints."""

from decimal import Decimal
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.config import settings
from app.controllers.dependencies import get_db
from app.dto.shop import (
    CartItemCreate,
    CartItemRead,
    CartItemUpdate,
    CartRead,
    CategoryCreate,
    CategoryRead,
    CheckoutCreate,
    OrderRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductViewCreate,
    PromotionCreate,
    PromotionRead,
    PromotionUpdate,
    ReviewCreate,
    ReviewRead,
    SaleRead,
)
from app.models import CartItem, Category, Order, Product, Promotion, Review
from app.services.shop_service import ShopService
from app.utils.images import save_replaced_image

router = APIRouter()


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Category:
    """Create a product category."""

    return await ShopService(db).create_category(payload)


@router.get("/categories", response_model=list[CategoryRead])
async def list_categories(db: Annotated[Session, Depends(get_db)]) -> list[Category]:
    """List product categories."""

    return await ShopService(db).list_categories()


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Product:
    """Create a product."""

    return await ShopService(db).create_product(payload)


@router.get("/products", response_model=list[ProductRead])
async def list_products(
    db: Annotated[Session, Depends(get_db)],
    category_id: Annotated[int | None, Query(gt=0)] = None,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    min_rating: Annotated[float | None, Query(ge=0, le=5)] = None,
    search: Annotated[str | None, Query(min_length=1, max_length=120)] = None,
    seller_id: Annotated[int | None, Query(gt=0)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[Product]:
    """List products with filters and pagination."""

    return await ShopService(db).list_products(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        search=search,
        seller_id=seller_id,
        offset=offset,
        limit=limit,
    )


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, db: Annotated[Session, Depends(get_db)]) -> Product:
    """Get product details with reviews."""

    return await ShopService(db).get_product(product_id)


@router.patch("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Product:
    """Update a product."""

    return await ShopService(db).update_product(product_id, payload)


@router.post("/products/{product_id}/image", response_model=ProductRead)
async def upload_product_image(
    product_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Query(gt=0)],
) -> Product:
    """Upload or replace a product image."""

    service = ShopService(db)
    await service.ensure_product_image_access(product_id, user_id)
    image_url = save_replaced_image(
        content=await request.body(),
        content_type=request.headers.get("content-type"),
        directory=Path(settings.media_dir) / "products",
        file_stem=f"product_{product_id}",
        public_prefix="/media/products",
    )
    return await service.update_product_image(product_id, user_id, image_url)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Delete a product."""

    await ShopService(db).delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/products/{product_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    product_id: int,
    payload: ReviewCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Review:
    """Create a product review."""

    return await ShopService(db).create_review(product_id, payload)


@router.post("/users/{user_id}/views", status_code=status.HTTP_204_NO_CONTENT)
async def record_view(
    user_id: int,
    payload: ProductViewCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Record a product view for recommendation history."""

    await ShopService(db).record_view(user_id, payload.product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users/{user_id}/recommendations", response_model=list[ProductRead])
async def recommendations(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[Product]:
    """Recommend products from the user's viewing history."""

    return await ShopService(db).recommendations(user_id, limit=limit)


@router.post(
    "/users/{user_id}/cart",
    response_model=CartItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_to_cart(
    user_id: int,
    payload: CartItemCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CartItem:
    """Add product to cart."""

    return await ShopService(db).add_to_cart(user_id, payload)


@router.get("/users/{user_id}/cart", response_model=CartRead)
async def list_cart(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    product_id: Annotated[int | None, Query(gt=0)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> CartRead:
    """List cart items with total amount."""

    items, total = await ShopService(db).list_cart(
        user_id=user_id,
        product_id=product_id,
        offset=offset,
        limit=limit,
    )
    return CartRead(user_id=user_id, items=items, total_amount=Decimal(total))


@router.patch("/users/{user_id}/cart/{item_id}", response_model=CartItemRead)
async def update_cart_item(
    user_id: int,
    item_id: int,
    payload: CartItemUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> CartItem:
    """Update cart item quantity."""

    return await ShopService(db).update_cart_item(user_id, item_id, payload)


@router.delete("/users/{user_id}/cart/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    user_id: int,
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Delete cart item."""

    await ShopService(db).delete_cart_item(user_id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/users/{user_id}/checkout", response_model=OrderRead)
async def checkout(
    user_id: int,
    payload: CheckoutCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Order:
    """Create an order from the user's cart."""

    return await ShopService(db).checkout(user_id, payload)


@router.get("/sales", response_model=list[SaleRead])
async def list_sales(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[dict[str, object]]:
    """List sold product history for the admin panel."""

    rows = await ShopService(db).list_sales(limit=limit)
    return [
        {
            "order_id": item.order_id,
            "order_item_id": item.id,
            "product": item.product,
            "buyer": item.order.user,
            "seller": item.product.seller,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.unit_price * item.quantity,
            "sold_at": item.order.created_at,
        }
        for item in rows
    ]


@router.get("/promotions", response_model=list[PromotionRead])
async def list_promotions(
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = False,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[Promotion]:
    """List advertising promotions."""

    return await ShopService(db).list_promotions(
        active_only=active_only,
        offset=offset,
        limit=limit,
    )


@router.post("/promotions", response_model=PromotionRead, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    payload: PromotionCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Promotion:
    """Create an advertising promotion."""

    return await ShopService(db).create_promotion(payload)


@router.patch("/promotions/{promotion_id}", response_model=PromotionRead)
async def update_promotion(
    promotion_id: int,
    payload: PromotionUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Promotion:
    """Update an advertising promotion."""

    return await ShopService(db).update_promotion(promotion_id, payload)


@router.delete("/promotions/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(
    promotion_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Delete an advertising promotion."""

    await ShopService(db).delete_promotion(promotion_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
