from typing import List, Dict, Any, Optional
from app.services.external_apis.base import BaseMovieAPIClient
from app.models.movie import Movie, MovieSearchParams, MovieType
from app.utils.http_client import HTTPClient
from app.core.config import settings
from app.core.exceptions import ExternalAPIError, NotFoundError
from app.utils.cache import cache_manager


class TMDBClient(BaseMovieAPIClient):
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
        self.base_url = settings.tmdb_base_url
        self.api_key = settings.tmdb_api_key
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
    
    async def search_movies(self, params: MovieSearchParams) -> List[Movie]:
        """Search for movies using TMDB API"""
        
        # Validate API key
        if not self.api_key:
            raise ExternalAPIError("TMDB API key is not configured")
        
        # Generate cache key including filter parameters (excluding pagination)
        cache_key = cache_manager.generate_key(
            "tmdb_search",
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
        
        movies = []
        
        # TMDB has different endpoints for movies and TV shows
        if params.type == MovieType.SERIES:
            movies.extend(await self._search_tv_shows(params))
        elif params.type == MovieType.MOVIE:
            movies.extend(await self._search_movies_only(params))
        else:
            # Search both movies and TV shows if no type specified
            movies.extend(await self._search_movies_only(params))
            movies.extend(await self._search_tv_shows(params))
        
        # Apply additional filters
        filtered_movies = []
        for movie in movies:
            if self._matches_filters(movie, params):
                filtered_movies.append(movie)
        
        # Remove duplicates based on title and year
        unique_movies = self._remove_duplicates(filtered_movies)
        
        # Cache the result
        cache_manager.set(cache_key, unique_movies)
        
        return unique_movies
    
    async def _search_movies_only(self, params: MovieSearchParams) -> List[Movie]:
        """Search for movies only using TMDB API"""
        
        # Build search query for movies
        search_params = {
            "api_key": self.api_key,
            "query": params.title or "popular",
            "page": 1,
            "include_adult": False
        }
        
        if params.year:
            search_params["year"] = params.year
        
        try:
            response = await self.http_client.get(
                f"{self.base_url}/search/movie",
                params=search_params
            )
            
            movies = []
            results = response.get("results", [])
            
            # Get detailed info for each movie if we need additional filtering
            for movie_data in results:
                try:
                    if params.actors or params.genre:
                        # Get detailed movie information including cast and genres
                        detailed_movie = await self._get_detailed_movie_info(movie_data["id"])
                        if detailed_movie:
                            movies.append(detailed_movie)
                    else:
                        # Use basic search result data
                        movie = self._transform_search_result(movie_data, MovieType.MOVIE)
                        if movie:
                            movies.append(movie)
                except Exception as e:
                    print(f"Warning: Skipping movie due to error: {e}")
                    continue
            
            return movies
            
        except Exception as e:
            raise ExternalAPIError(f"Failed to search movies from TMDB: {str(e)}")
    
    async def _search_tv_shows(self, params: MovieSearchParams) -> List[Movie]:
        """Search for TV shows using TMDB API"""
        
        # Build search query for TV shows
        search_params = {
            "api_key": self.api_key,
            "query": params.title or "popular",
            "page": 1,
            "include_adult": False
        }
        
        if params.year:
            search_params["first_air_date_year"] = params.year
        
        try:
            response = await self.http_client.get(
                f"{self.base_url}/search/tv",
                params=search_params
            )
            
            movies = []
            results = response.get("results", [])
            
            # Get detailed info for each TV show if we need additional filtering
            for tv_data in results:
                try:
                    if params.actors or params.genre:
                        # Get detailed TV show information including cast and genres
                        detailed_movie = await self._get_detailed_tv_info(tv_data["id"])
                        if detailed_movie:
                            movies.append(detailed_movie)
                    else:
                        # Use basic search result data
                        movie = self._transform_search_result(tv_data, MovieType.SERIES)
                        if movie:
                            movies.append(movie)
                except Exception as e:
                    print(f"Warning: Skipping TV show due to error: {e}")
                    continue
            
            return movies
            
        except Exception as e:
            raise ExternalAPIError(f"Failed to search TV shows from TMDB: {str(e)}")
    
    async def _get_detailed_movie_info(self, movie_id: int) -> Optional[Movie]:
        """Get detailed movie information including cast and genres"""
        
        try:
            # Check cache first
            cache_key = cache_manager.generate_key("tmdb_movie_details", movie_id)
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get movie details with credits
            params = {
                "api_key": self.api_key,
                "append_to_response": "credits"
            }
            
            response = await self.http_client.get(
                f"{self.base_url}/movie/{movie_id}",
                params=params
            )
            
            movie = self._transform_detailed_movie_response(response)
            
            # Cache the result
            cache_manager.set(cache_key, movie)
            
            return movie
            
        except Exception as e:
            print(f"Warning: Failed to get detailed movie info for ID {movie_id}: {e}")
            return None
    
    async def _get_detailed_tv_info(self, tv_id: int) -> Optional[Movie]:
        """Get detailed TV show information including cast and genres"""
        
        try:
            # Check cache first
            cache_key = cache_manager.generate_key("tmdb_tv_details", tv_id)
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get TV show details with credits
            params = {
                "api_key": self.api_key,
                "append_to_response": "credits"
            }
            
            response = await self.http_client.get(
                f"{self.base_url}/tv/{tv_id}",
                params=params
            )
            
            movie = self._transform_detailed_tv_response(response)
            
            # Cache the result
            cache_manager.set(cache_key, movie)
            
            return movie
            
        except Exception as e:
            print(f"Warning: Failed to get detailed TV info for ID {tv_id}: {e}")
            return None
    
    # async def get_movie_details(self, movie_id: str) -> Movie:
    #     """Get detailed information about a specific movie by TMDB ID"""
        
    #     if not self.api_key:
    #         raise ExternalAPIError("TMDB API key is not configured")
        
    #     try:
    #         # Try to parse as integer (TMDB ID)
    #         tmdb_id = int(movie_id)
            
    #         # Try movie first
    #         movie = await self._get_detailed_movie_info(tmdb_id)
    #         if movie:
    #             return movie
            
    #         # Try TV show if movie not found
    #         movie = await self._get_detailed_tv_info(tmdb_id)
    #         if movie:
    #             return movie
            
    #         raise NotFoundError(f"Movie/TV show not found with TMDB ID: {movie_id}")
            
    #     except ValueError:
    #         raise NotFoundError(f"Invalid TMDB ID format: {movie_id}")
    #     except (ExternalAPIError, NotFoundError):
    #         raise
    #     except Exception as e:
    #         raise ExternalAPIError(f"Failed to get movie details: {str(e)}")
    
    def _transform_search_result(self, data: Dict[str, Any], content_type: MovieType) -> Optional[Movie]:
        """Transform TMDB search result to Movie model"""
        
        try:
            if content_type == MovieType.MOVIE:
                return Movie(
                    title=data.get("title", ""),
                    year=data.get("release_date", "")[:4] if data.get("release_date") else None,
                    imdb_id=None,  # TMDB doesn't provide IMDB ID in search results
                    type=MovieType.MOVIE,
                    poster=f"{self.image_base_url}{data.get('poster_path')}" if data.get("poster_path") else None,
                    plot=data.get("overview", "") if data.get("overview") else None,
                    director=None,  # Not available in search results
                    actors=None,    # Not available in search results
                    genre=None,     # Not available in search results
                    imdb_rating=str(data.get("vote_average", "")) if data.get("vote_average") else None,
                    runtime=None,   # Not available in search results
                    released=data.get("release_date", "") if data.get("release_date") else None
                )
            else:  # TV Show
                return Movie(
                    title=data.get("name", ""),
                    year=data.get("first_air_date", "")[:4] if data.get("first_air_date") else None,
                    imdb_id=None,
                    type=MovieType.SERIES,
                    poster=f"{self.image_base_url}{data.get('poster_path')}" if data.get("poster_path") else None,
                    plot=data.get("overview", "") if data.get("overview") else None,
                    director=None,
                    actors=None,
                    genre=None,
                    imdb_rating=str(data.get("vote_average", "")) if data.get("vote_average") else None,
                    runtime=None,
                    released=data.get("first_air_date", "") if data.get("first_air_date") else None
                )
        except Exception as e:
            print(f"Warning: Failed to transform search result: {e}")
            return None
    
    def _transform_detailed_movie_response(self, data: Dict[str, Any]) -> Movie:
        """Transform detailed TMDB movie response to Movie model"""
        
        # Extract cast information
        cast = data.get("credits", {}).get("cast", [])
        actors = ", ".join([actor["name"] for actor in cast[:5]])  # Top 5 actors
        
        # Extract crew information (director)
        crew = data.get("credits", {}).get("crew", [])
        directors = [person["name"] for person in crew if person.get("job") == "Director"]
        director = ", ".join(directors) if directors else None
        
        # Extract genres
        genres = data.get("genres", [])
        genre = ", ".join([g["name"] for g in genres]) if genres else None
        
        return Movie(
            title=data.get("title", ""),
            year=data.get("release_date", "")[:4] if data.get("release_date") else None,
            imdb_id=data.get("imdb_id", None),
            type=MovieType.MOVIE,
            poster=f"{self.image_base_url}{data.get('poster_path')}" if data.get("poster_path") else None,
            plot=data.get("overview", "") if data.get("overview") else None,
            director=director,
            actors=actors if actors else None,
            genre=genre,
            imdb_rating=str(data.get("vote_average", "")) if data.get("vote_average") else None,
            runtime=f"{data.get('runtime', '')} min" if data.get("runtime") else None,
            released=data.get("release_date", "") if data.get("release_date") else None
        )
    
    def _transform_detailed_tv_response(self, data: Dict[str, Any]) -> Movie:
        """Transform detailed TMDB TV response to Movie model"""
        
        # Extract cast information
        cast = data.get("credits", {}).get("cast", [])
        actors = ", ".join([actor["name"] for actor in cast[:5]])  # Top 5 actors
        
        # Extract crew information (creators)
        creators = data.get("created_by", [])
        director = ", ".join([creator["name"] for creator in creators]) if creators else None
        
        # Extract genres
        genres = data.get("genres", [])
        genre = ", ".join([g["name"] for g in genres]) if genres else None
        
        # Calculate average episode runtime
        episode_runtimes = data.get("episode_run_time", [])
        runtime = f"{episode_runtimes[0]} min" if episode_runtimes else None
        
        return Movie(
            title=data.get("name", ""),
            year=data.get("first_air_date", "")[:4] if data.get("first_air_date") else None,
            imdb_id=None,  # TMDB doesn't provide IMDB ID for TV shows
            type=MovieType.SERIES,
            poster=f"{self.image_base_url}{data.get('poster_path')}" if data.get("poster_path") else None,
            plot=data.get("overview", "") if data.get("overview") else None,
            director=director,
            actors=actors if actors else None,
            genre=genre,
            imdb_rating=str(data.get("vote_average", "")) if data.get("vote_average") else None,
            runtime=runtime,
            released=data.get("first_air_date", "") if data.get("first_air_date") else None
        )
    
    def _transform_response(self, data: Dict[str, Any]) -> Movie:
        """Transform TMDB response to Movie model (required by base class)"""
        # This method is required by the base class
        # For TMDB, we use the specific transform methods above
        return self._transform_detailed_movie_response(data)
    
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
    
    def _remove_duplicates(self, movies: List[Movie]) -> List[Movie]:
        """Remove duplicate movies based on title and year"""
        seen = set()
        unique_movies = []
        
        for movie in movies:
            # Create a key based on title and year
            key = (movie.title.lower().strip(), movie.year)
            if key not in seen:
                seen.add(key)
                unique_movies.append(movie)
        
        return unique_movies 