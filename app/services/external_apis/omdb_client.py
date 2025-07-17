from typing import List, Dict, Any, Optional
from app.services.external_apis.base import BaseMovieAPIClient
from app.models.movie import Movie, MovieSearchParams, MovieType
from app.utils.http_client import HTTPClient
from app.core.config import settings
from app.core.exceptions import ExternalAPIError, NotFoundError
from app.utils.cache import cache_manager


class OMDBClient(BaseMovieAPIClient):
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
        self.base_url = settings.omdb_base_url
        self.api_key = settings.omdb_api_key
    
    async def search_movies(self, params: MovieSearchParams) -> List[Movie]:
        """Search for movies using OMDB API"""
        
        # Validate API key
        if not self.api_key:
            raise ExternalAPIError("OMDB API key is not configured")
        
        # Generate cache key including filter parameters (excluding pagination)
        cache_key = cache_manager.generate_key(
            "omdb_search",
            title=params.title,
            actors=params.actors,
            genre=params.genre,
            type=params.type,
            year=params.year
        )
        
        # Check cache first
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        # Build search query (fetch first page, pagination handled in service layer)
        search_params = {
            "apikey": self.api_key,
            "page": 1
        }
        
        if params.title:
            search_params["s"] = params.title
        else:
            # OMDB requires a search term, so we'll use a popular movie for general search
            search_params["s"] = "movie"
        
        if params.type:
            search_params["type"] = params.type.value
        
        if params.year:
            search_params["y"] = params.year
        
        try:
            response = await self.http_client.get(self.base_url, params=search_params)
            
            if response.get("Response") == "False":
                error_msg = response.get("Error", "Unknown error")
                if "not found" in error_msg.lower():
                    return []
                if "invalid api key" in error_msg.lower():
                    raise ExternalAPIError("Invalid OMDB API key. Please check your API key configuration.")
                raise ExternalAPIError(f"OMDB API error: {error_msg}")
            
            movies = []
            search_results = response.get("Search", [])
            
            # Process each movie result - always get detailed information
            for movie_data in search_results:
                try:
                    # Get detailed movie information for all results
                    movie_id = movie_data.get("imdbID")
                    if movie_id:
                        detailed_movie = await self._get_detailed_movie_info(movie_id)
                        if detailed_movie and self._matches_filters(detailed_movie, params):
                            movies.append(detailed_movie)
                    else:
                        # Fallback to basic data if no IMDB ID
                        movie = self._transform_search_result(movie_data)
                        if self._matches_filters(movie, params):
                            movies.append(movie)
                except Exception as e:
                    # Log the error but continue processing other movies
                    print(f"Warning: Skipping movie due to error: {e}")
                    continue
            
            # Movies are already sorted by OMDB API relevance
            
            # Cache the result
            cache_manager.set(cache_key, movies)
            
            return movies
            
        except ExternalAPIError:
            raise
        except Exception as e:
            raise ExternalAPIError(f"Failed to search movies: {str(e)}")
    
    async def get_movie_details(self, movie_id: str) -> Movie:
        """Get detailed movie information by IMDB ID"""
        
        # Validate API key
        if not self.api_key:
            raise ExternalAPIError("OMDB API key is not configured")
        
        # Generate cache key
        cache_key = cache_manager.generate_key("omdb_details", movie_id)
        
        # Check cache first
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            "apikey": self.api_key,
            "i": movie_id,
            "plot": "full"
        }
        
        try:
            response = await self.http_client.get(self.base_url, params=params)
            
            if response.get("Response") == "False":
                error_msg = response.get("Error", "Unknown error")
                if "not found" in error_msg.lower():
                    raise NotFoundError(f"Movie not found: {movie_id}")
                if "invalid api key" in error_msg.lower():
                    raise ExternalAPIError("Invalid OMDB API key. Please check your API key configuration.")
                raise ExternalAPIError(f"OMDB API error: {error_msg}")
            
            movie = self._transform_response(response)
            
            # Cache the result
            cache_manager.set(cache_key, movie)
            
            return movie
            
        except (ExternalAPIError, NotFoundError):
            raise
        except Exception as e:
            raise ExternalAPIError(f"Failed to get movie details: {str(e)}")
    
    def _transform_search_result(self, data: Dict[str, Any]) -> Movie:
        """Transform OMDB search result to Movie model"""
        return Movie(
            title=data.get("Title", ""),
            year=data.get("Year", ""),
            imdb_id=data.get("imdbID", ""),
            type=self._map_type(data.get("Type", "")),
            poster=data.get("Poster", "") if data.get("Poster") != "N/A" else None,
            plot=data.get("Plot", "") if data.get("Plot") != "N/A" else None,
            director=data.get("Director", "") if data.get("Director") != "N/A" else None,
            actors=data.get("Actors", "") if data.get("Actors") != "N/A" else None,
            genre=data.get("Genre", "") if data.get("Genre") != "N/A" else None,
            imdb_rating=data.get("imdbRating", "") if data.get("imdbRating") != "N/A" else None,
            runtime=data.get("Runtime", "") if data.get("Runtime") != "N/A" else None,
            released=data.get("Released", "") if data.get("Released") != "N/A" else None
        )
    
    def _transform_response(self, data: Dict[str, Any]) -> Movie:
        """Transform detailed OMDB response to Movie model"""
        return Movie(
            title=data.get("Title", ""),
            year=data.get("Year", ""),
            imdb_id=data.get("imdbID", ""),
            type=self._map_type(data.get("Type", "")),
            poster=data.get("Poster", "") if data.get("Poster") != "N/A" else None,
            plot=data.get("Plot", "") if data.get("Plot") != "N/A" else None,
            director=data.get("Director", "") if data.get("Director") != "N/A" else None,
            actors=data.get("Actors", "") if data.get("Actors") != "N/A" else None,
            genre=data.get("Genre", "") if data.get("Genre") != "N/A" else None,
            imdb_rating=data.get("imdbRating", "") if data.get("imdbRating") != "N/A" else None,
            runtime=data.get("Runtime", "") if data.get("Runtime") != "N/A" else None,
            released=data.get("Released", "") if data.get("Released") != "N/A" else None
        )
    
    def _map_type(self, omdb_type: str) -> Optional[MovieType]:
        """Map OMDB type to our MovieType enum"""
        type_mapping = {
            "movie": MovieType.MOVIE,
            "series": MovieType.SERIES,
            "episode": MovieType.EPISODE
        }
        return type_mapping.get(omdb_type.lower())
    
    async def _get_detailed_movie_info(self, movie_id: str) -> Optional[Movie]:
        """Get detailed movie information for filtering purposes"""
        try:
            # Check cache first for detailed info
            cache_key = cache_manager.generate_key("omdb_details", movie_id)
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get detailed info from OMDB
            params = {
                "apikey": self.api_key,
                "i": movie_id,
                "plot": "full"  # Use full plot for complete detailed information
            }
            
            response = await self.http_client.get(self.base_url, params=params)
            
            if response.get("Response") == "False":
                return None
            
            movie = self._transform_response(response)
            
            # Cache the result
            cache_manager.set(cache_key, movie)
            
            return movie
            
        except Exception:
            # If we can't get detailed info, skip this movie
            return None
    
    def _matches_filters(self, movie: Movie, params: MovieSearchParams) -> bool:
        """Check if movie matches additional filters"""
        
        # Filter by actors (case-insensitive, partial match)
        if params.actors and movie.actors:
            actors_list = [actor.strip().lower() for actor in movie.actors.split(',')]
            search_actor = params.actors.lower().strip()
            if not any(search_actor in actor for actor in actors_list):
                return False
        
        # Filter by genre (case-insensitive, partial match)
        if params.genre and movie.genre:
            genres_list = [genre.strip().lower() for genre in movie.genre.split(',')]
            search_genre = params.genre.lower().strip()
            if not any(search_genre in genre for genre in genres_list):
                return False
        
        return True