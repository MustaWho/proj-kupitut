"""FastAPI dependencies for API v1."""

from app.database.session import get_session

get_db = get_session
