from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.models.movie import Movie, MovieSearchParams


class BaseMovieAPIClient(ABC):
    """Abstract base class for movie API clients"""
    
    @abstractmethod
    async def search_movies(self, params: MovieSearchParams) -> List[Movie]:
        """Search for movies based on the provided parameters"""
        pass
    
    @abstractmethod
    async def get_movie_details(self, movie_id: str) -> Movie:
        """Get detailed information about a specific movie"""
        pass
    
    @abstractmethod
    def _transform_response(self, data: Dict[str, Any]) -> Movie:
        """Transform API response to Movie model"""
        pass