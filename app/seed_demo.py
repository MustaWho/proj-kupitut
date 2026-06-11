"""Create demo users, categories, and products for local or Docker runs."""

from decimal import Decimal

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import Category, Product, User
from app.security import hash_password

DEMO_PASSWORD = "secret999"

DEMO_USERS = [
    {
        "email": "admin@kupitut-shop.ru",
        "username": "admin",
        "first_name": "Админ",
        "last_name": "КупиТут",
        "role": "admin",
    },
    {
        "email": "buyer@kupitut-shop.ru",
        "username": "buyer",
        "first_name": "Покупатель",
        "last_name": "КупиТут",
        "role": "user",
    },
    {
        "email": "seller@kupitut-shop.ru",
        "username": "seller",
        "first_name": "Продавец",
        "last_name": "КупиТут",
        "role": "seller",
    },
]

DEMO_CATEGORIES = ["Электроника", "Дом", "Книги", "Одежда"]

DEMO_PRODUCTS = [
    {
        "name": "Беспроводные наушники",
        "category": "Электроника",
        "price": Decimal("3990.00"),
        "discount_percent": 15,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
        "description": "Легкие наушники с мягкими амбушюрами, чистым звуком и зарядным кейсом.",
    },
    {
        "name": "Умная колонка",
        "category": "Электроника",
        "price": Decimal("5990.00"),
        "discount_percent": 10,
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=900&q=80",
        "description": "Колонка для музыки, напоминаний и управления умным домом.",
    },
    {
        "name": "Настольная лампа",
        "category": "Дом",
        "price": Decimal("2490.00"),
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=80",
        "description": "Минималистичная лампа для рабочего стола с мягким теплым светом.",
    },
    {
        "name": "Керамическая кружка",
        "category": "Дом",
        "price": Decimal("790.00"),
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=80",
        "description": "Удобная кружка для кофе и чая, подходит для ежедневного использования.",
    },
    {
        "name": "Книга по JavaScript",
        "category": "Книги",
        "price": Decimal("1890.00"),
        "discount_percent": 5,
        "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80",
        "description": "Практическое руководство по современному JavaScript для начинающих.",
    },
    {
        "name": "Худи КупиТут",
        "category": "Одежда",
        "price": Decimal("3290.00"),
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=900&q=80",
        "description": "Мягкое худи свободного кроя для прогулок, учебы и работы.",
    },
]


def get_or_create_user(db, values: dict[str, str]) -> User:
    user = db.scalar(select(User).where(User.username == values["username"]))
    if user:
        user.email = values["email"]
        user.first_name = values["first_name"]
        user.last_name = values["last_name"]
        user.role = values["role"]
        user.is_active = True
        return user
    user = User(
        **values,
        password_hash=hash_password(DEMO_PASSWORD),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_category(db, name: str) -> Category:
    category = db.scalar(select(Category).where(Category.name == name))
    if category:
        return category
    category = Category(name=name)
    db.add(category)
    db.flush()
    return category


def create_product_if_missing(
    db,
    values: dict[str, object],
    categories: dict[str, Category],
    seller: User,
) -> Product | None:
    existing = db.scalar(select(Product).where(Product.name == values["name"]))
    if existing:
        return None
    product = Product(
        name=str(values["name"]),
        category_id=categories[str(values["category"])].id,
        price=values["price"],
        discount_percent=int(values["discount_percent"]),
        image_url=str(values["image_url"]),
        description=str(values["description"]),
        seller_id=seller.id,
        rating=0,
        is_active=True,
    )
    db.add(product)
    return product


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        users = {item["username"]: get_or_create_user(db, item) for item in DEMO_USERS}
        categories = {
            name: get_or_create_category(db, name)
            for name in DEMO_CATEGORIES
        }
        created_products = 0
        for item in DEMO_PRODUCTS:
            if create_product_if_missing(db, item, categories, users["seller"]):
                created_products += 1

        db.commit()
        print("Демо-данные готовы.")
        print(f"Пользователи: admin, buyer, seller. Пароль: {DEMO_PASSWORD}")
        print(f"Добавлено новых товаров: {created_products}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
