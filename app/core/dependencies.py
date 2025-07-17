from fastapi import Depends
from app.utils.http_client import HTTPClient
from app.services.external_apis.omdb_client import OMDBClient
from app.services.movie_service import MovieService


async def get_http_client() -> HTTPClient:
    """Dependency to get HTTP client"""
    return HTTPClient()


async def get_omdb_client(http_client: HTTPClient = Depends(get_http_client)) -> OMDBClient:
    """Dependency to get OMDB client"""
    return OMDBClient(http_client)


async def get_movie_service(omdb_client: OMDBClient = Depends(get_omdb_client)) -> MovieService:
    """Dependency to get movie service"""
    return MovieService(omdb_client)