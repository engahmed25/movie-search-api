from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    omdb_api_key: str
    omdb_base_url: str = "https://www.omdbapi.com/"
    tmdb_api_key: str
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    cache_ttl: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"


settings = Settings()