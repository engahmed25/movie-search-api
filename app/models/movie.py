from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class MovieType(str, Enum):
    MOVIE = "movie"
    SERIES = "series"
    EPISODE = "episode"


class Movie(BaseModel):
    title: str = Field(..., description="Movie title")
    year: Optional[str] = Field(None, description="Release year")
    imdb_id: Optional[str] = Field(None, description="IMDB ID")
    type: Optional[MovieType] = Field(None, description="Type of content")
    poster: Optional[str] = Field(None, description="Poster URL")
    plot: Optional[str] = Field(None, description="Plot summary")
    director: Optional[str] = Field(None, description="Director")
    actors: Optional[str] = Field(None, description="Main actors")
    genre: Optional[str] = Field(None, description="Genre")
    imdb_rating: Optional[str] = Field(None, description="IMDB rating")
    runtime: Optional[str] = Field(None, description="Runtime")
    released: Optional[str] = Field(None, description="Release date")


class MovieSearchParams(BaseModel):
    title: Optional[str] = Field(None, description="Search by title")
    actors: Optional[str] = Field(None, description="Search by actors")
    type: Optional[MovieType] = Field(None, description="Filter by type")
    genre: Optional[str] = Field(None, description="Filter by genre")
    year: Optional[str] = Field(None, description="Filter by year")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Number of results per page")