from fastapi import APIRouter
from app.api.v1.endpoints import movies, debug

api_router = APIRouter()

api_router.include_router(
    movies.router,
    prefix="/movies",
    tags=["movies"]
)

api_router.include_router(
    debug.router,
    prefix="/debug",
    tags=["debug"]
)