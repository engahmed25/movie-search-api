from pydantic import BaseModel, Field
from typing import List, Optional, Any
from app.models.movie import Movie


class SearchResponse(BaseModel):
    movies: List[Movie] = Field(..., description="List of movies")
    total_results: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page")
    total_pages: int = Field(..., description="Total number of pages")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")


class HealthResponse(BaseModel):
    status: str = Field(..., description="API status")
    message: str = Field(..., description="Health check message")