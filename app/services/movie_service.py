from typing import List, Tuple
from app.models.movie import Movie, MovieSearchParams
from app.models.api_responses import SearchResponse
from app.services.external_apis.omdb_client import OMDBClient
from app.core.exceptions import ValidationError
import math


class MovieService:
    def __init__(self, omdb_client: OMDBClient):
        self.omdb_client = omdb_client
    
    async def search_movies(self, params: MovieSearchParams) -> SearchResponse:
        """Search for movies and return paginated results"""
        
        # Validate search parameters
        self._validate_search_params(params)
        
        # Search movies using OMDB client
        movies = await self.omdb_client.search_movies(params)
        
        # Apply pagination
        total_results = len(movies)
        start_index = (params.page - 1) * params.limit
        end_index = start_index + params.limit
        paginated_movies = movies[start_index:end_index]
        
        # Calculate total pages
        total_pages = math.ceil(total_results / params.limit) if total_results > 0 else 0
        
        return SearchResponse(
            movies=paginated_movies,
            total_results=total_results,
            page=params.page,
            total_pages=total_pages
        )
    
    async def get_movie_details(self, movie_id: str) -> Movie:
        """Get detailed information about a specific movie"""
        if not movie_id:
            raise ValidationError("Movie ID is required")
        
        return await self.omdb_client.get_movie_details(movie_id)
    
    def _validate_search_params(self, params: MovieSearchParams) -> None:
        """Validate search parameters"""
        
        # At least one search criterion should be provided
        if not any([params.title, params.actors, params.type, params.genre, params.year]):
            raise ValidationError("At least one search parameter is required")
        
        # Validate year format if provided
        if params.year:
            try:
                year_int = int(params.year)
                if year_int < 1900 or year_int > 2030:
                    raise ValidationError("Year must be between 1900 and 2030")
            except ValueError:
                raise ValidationError("Year must be a valid integer")