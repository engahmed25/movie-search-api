import httpx
from typing import Dict, Any, Optional
from app.core.exceptions import ExternalAPIError


class HTTPClient:
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ExternalAPIError(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ExternalAPIError(f"Request error occurred: {str(e)}")
        except Exception as e:
            raise ExternalAPIError(f"Unexpected error: {str(e)}")
    
    async def close(self):
        await self.client.aclose()