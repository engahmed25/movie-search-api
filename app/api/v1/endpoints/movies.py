from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.models.movie import Movie, MovieSearchParams, MovieType
from app.models.api_responses import SearchResponse, ErrorResponse
from app.services.movie_service import MovieService
from app.core.dependencies import get_movie_service
from app.core.exceptions import ValidationError, ExternalAPIError, NotFoundError


router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_movies(
    title: Optional[str] = Query(None, description="Search by movie title"),
    actors: Optional[str] = Query(None, description="Search by actors"),
    type: Optional[MovieType] = Query(None, description="Filter by type (movie, series, episode)"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    year: Optional[str] = Query(None, description="Filter by year"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of results per page"),
    movie_service: MovieService = Depends(get_movie_service)
):
    """
    Search for movies by various criteria.
    
    At least one search parameter is required.
    """
    try:
        search_params = MovieSearchParams(
            title=title,
            actors=actors,
            type=type,
            genre=genre,
            year=year,
            page=page,
            limit=limit
        )
        
        return await movie_service.search_movies(search_params)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExternalAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{movie_id}", response_model=Movie)
async def get_movie_details(
    movie_id: str,
    movie_service: MovieService = Depends(get_movie_service)
):
    """
    Get detailed information about a specific movie by IMDB ID.
    """
    try:
        return await movie_service.get_movie_details(movie_id)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ExternalAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")