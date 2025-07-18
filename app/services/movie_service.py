from typing import List, Tuple, Optional
from app.models.movie import Movie, MovieSearchParams
from app.models.api_responses import SearchResponse
from app.services.external_apis.omdb_client import OMDBClient
from app.services.external_apis.tmdb_client import TMDBClient
from app.core.exceptions import ValidationError
import math


class MovieService:
    def __init__(self, omdb_client: OMDBClient, tmdb_client: Optional[TMDBClient] = None):
        self.omdb_client = omdb_client
        self.tmdb_client = tmdb_client
    
    async def search_movies(self, params: MovieSearchParams) -> SearchResponse:
        """Search for movies and return paginated results from both OMDB and TMDB"""
        
        # Validate search parameters
        self._validate_search_params(params)
        
        # Search movies using OMDB client
        omdb_movies = await self.omdb_client.search_movies(params)
        
        # Search movies using TMDB client if available
        tmdb_movies = []
        if self.tmdb_client:
            try:
                tmdb_movies = await self.tmdb_client.search_movies(params)
            except Exception as e:
                print(f"Warning: TMDB search failed: {e}")
        
        # Merge and normalize results
        merged_movies = self._merge_movie_results(omdb_movies, tmdb_movies)
        
        # Apply additional filters on merged dataset
        filtered_movies = self._apply_additional_filters(merged_movies, params)
        
        # Sort by relevance and rating
        sorted_movies = self._sort_movies(filtered_movies, params)
        
        # Apply pagination
        total_results = len(sorted_movies)
        start_index = (params.page - 1) * params.limit
        end_index = start_index + params.limit
        paginated_movies = sorted_movies[start_index:end_index]
        
        # Calculate total pages
        total_pages = math.ceil(total_results / params.limit) if total_results > 0 else 0
        
        return SearchResponse(
            movies=paginated_movies,
            total_results=total_results,
            page=params.page,
            total_pages=total_pages
        )
    
    async def get_movie_details(self, movie_id: str) -> Movie:
        """Get detailed information about a specific movie for imdb (testing)"""
        if not movie_id:
            raise ValidationError("Movie ID is required")
        
        return await self.omdb_client.get_movie_details(movie_id)
    
    def _merge_movie_results(self, omdb_movies: List[Movie], tmdb_movies: List[Movie]) -> List[Movie]:
        """Merge OMDB and TMDB results, removing duplicates and prioritizing OMDB data"""
        
        # Create a dictionary to track movies by title and year
        movie_map = {}
        
        # Add OMDB movies first (they have priority)
        for movie in omdb_movies:
            key = (movie.title.lower().strip(), movie.year)
            movie_map[key] = movie
        
        # Add TMDB movies only if not already present
        for movie in tmdb_movies:
            key = (movie.title.lower().strip(), movie.year)
            if key not in movie_map:
                movie_map[key] = movie
        
        return list(movie_map.values())
    
    def _apply_additional_filters(self, movies: List[Movie], params: MovieSearchParams) -> List[Movie]:
        """Apply additional filters on the merged dataset"""
        
        filtered_movies = []
        
        for movie in movies:
            # Filter by actors (case-insensitive, partial match)
            if params.actors and movie.actors:
                actors_list = [actor.strip().lower() for actor in movie.actors.split(',')]
                search_actor = params.actors.lower().strip()
                if not any(search_actor in actor for actor in actors_list):
                    continue
            
            # Filter by genre (case-insensitive, partial match)
            if params.genre and movie.genre:
                genres_list = [genre.strip().lower() for genre in movie.genre.split(',')]
                search_genre = params.genre.lower().strip()
                if not any(search_genre in genre for genre in genres_list):
                    continue
            
            # Filter by type
            if params.type and movie.type != params.type:
                continue
            
            # Filter by year
            if params.year and movie.year != params.year:
                continue
            
            filtered_movies.append(movie)
        
        return filtered_movies
    
    def _sort_movies(self, movies: List[Movie], params: MovieSearchParams) -> List[Movie]:
        """Sort movies by relevance and rating"""
        
        def sort_key(movie: Movie) -> tuple:
            # Title relevance (exact match gets priority)
            title_score = 0
            if params.title and movie.title:
                if params.title.lower() == movie.title.lower():
                    title_score = 0  # Exact match
                elif params.title.lower() in movie.title.lower():
                    title_score = 1  # Partial match
                else:
                    title_score = 2  # No match
            
            # Rating score (higher is better, so negate for ascending sort)
            rating_score = 0
            if movie.imdb_rating:
                try:
                    rating_score = -float(movie.imdb_rating)
                except (ValueError, TypeError):
                    rating_score = 0
            
            # Year score (more recent is better, so negate for ascending sort)
            year_score = 0
            if movie.year:
                try:
                    year_score = -int(movie.year)
                except (ValueError, TypeError):
                    year_score = 0
            
            return (title_score, rating_score, year_score)
        
        return sorted(movies, key=sort_key)
    
    def _validate_search_params(self, params: MovieSearchParams) -> None:
        """Validate search parameters"""
        
        # At least one search criterion should be provided
        if not any([params.title, params.actors, params.type, params.genre, params.year]):
            raise ValidationError("At least one search parameter is required")
        
        # Validate year format if provided
        if params.year:
            try:
                year_int = int(params.year)
                if year_int < 1900 or year_int > 2025:
                    raise ValidationError("Year must be between 1900 and 2025")
            except ValueError:
                raise ValidationError("Year must be a valid integer")