from fastapi import APIRouter, HTTPException
from app.utils.cache import cache_manager
from app.models.api_responses import HealthResponse

router = APIRouter()

@router.get("/cache/status")
async def get_cache_status():
    """Get current cache status"""
    return {
        "cache_size": cache_manager.size(),
        "cache_info": "Cache is working normally"
    }

@router.delete("/cache/clear")
async def clear_cache():
    """Clear all cached data (for development/testing)"""
    cache_manager.clear()
    return {
        "message": "Cache cleared successfully",
        "cache_size": cache_manager.size()
    } 