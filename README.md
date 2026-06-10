# Интернет-магазин

Проект итогового интернет-магазина: бэкенд на FastAPI и фронтенд на React. Пользователь может просматривать каталог, фильтровать товары, открывать карточку товара, добавлять позиции в корзину, оформлять заказ, оставлять отзывы, видеть акции и получать рекомендации на основе истории просмотров.

Фронтенд находится в папке `frontend/`.

## Стек

- Python 3.11+
- FastAPI
- Pydantic 2
- SQLAlchemy 2
- Alembic
- PostgreSQL 15
- Pytest
- Docker Compose
- React
- TypeScript
- Vite
- Nginx

## Возможности

- Регистрация, вход, обновление токена и смена пароля.
- Категории товаров и CRUD товаров для панели управления.
- Фильтрация каталога по категории, цене, рейтингу и поисковому запросу.
- Карточка товара с подробным описанием и отзывами.
- Корзина с изменением количества, расчётом суммы и сохранением в `localStorage`.
- Оформление заказа из корзины.
- Рекламные акции для главной страницы.
- История просмотров и рекомендации товаров.
- Миграции базы данных для всех сущностей магазина.
- React-фронтенд с маршрутизацией, API-клиентом, состоянием корзины и тестами.

## Быстрый запуск через Docker

```bash
docker compose up -d --build
```

После запуска:

- Фронтенд: http://localhost:8080
- Swagger API: http://localhost:8000/docs
- Проверка состояния API: http://localhost:8000/api/v1/health

Остановить проект:

```bash
docker compose down
```

## Локальный запуск бэкенда

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=sqlite+pysqlite:///./dev.db
python -m alembic upgrade head
uvicorn app.main:app --reload
```

Для PowerShell переменная окружения задаётся так:

```powershell
$env:DATABASE_URL="sqlite+pysqlite:///./dev.db"
```

## Локальный запуск фронтенда

```bash
cd frontend
npm install
npm run dev
```

По умолчанию фронтенд использует `/api/v1`. Если API запущен отдельно, задайте адрес:

```bash
set VITE_API_URL=http://localhost:8000/api/v1
```

## Проверки

```bash
python -m pytest
python -m flake8 app tests --max-line-length=100
cd frontend
npm run test
npm run build
```

## Основные эндпойнты

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/change-password`
- `POST /api/v1/categories`
- `GET /api/v1/categories`
- `POST /api/v1/products`
- `GET /api/v1/products`
- `GET /api/v1/products/{product_id}`
- `PATCH /api/v1/products/{product_id}`
- `DELETE /api/v1/products/{product_id}`
- `POST /api/v1/products/{product_id}/reviews`
- `POST /api/v1/users/{user_id}/views`
- `GET /api/v1/users/{user_id}/recommendations`
- `POST /api/v1/users/{user_id}/cart`
- `GET /api/v1/users/{user_id}/cart`
- `PATCH /api/v1/users/{user_id}/cart/{item_id}`
- `DELETE /api/v1/users/{user_id}/cart/{item_id}`
- `POST /api/v1/users/{user_id}/checkout`
- `GET /api/v1/promotions`
- `POST /api/v1/promotions`
- `PATCH /api/v1/promotions/{promotion_id}`
- `DELETE /api/v1/promotions/{promotion_id}`

## Модель данных

В домене магазина используются пользователи, категории, товары, отзывы, корзина, история просмотров, заказы, позиции заказа, refresh-токены и рекламные акции.

Старые эндпойнты проектов и задач оставлены для совместимости, но требования итогового задания покрывает API интернет-магазина.
