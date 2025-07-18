# Movie Search API - Filtering Guide
##Summary

OMDB: Uses title, year, and type as direct query parameters
TMDB: Uses title and year as direct query parameters
Additional Filters: Both APIs collect initial data, then apply additional filters for actor and genre on the retrieved results using case-insensitive partial matching
Movie Service: Also applies an additional layer of filtering in the _apply_additional_filters method to ensure consistency across merged results from both APIs
The filtering is done post-retrieval because these external APIs don't support direct filtering by actors or genres in their search endpoints, so the system fetches broader results and then narrows them down based on the specified criteria.

## Overview

The Movie Search API now supports advanced filtering that applies filters **after** getting data from both OMDB and TMDB APIs. The system fetches data from both sources, merges and normalizes the results, then applies comprehensive filtering for accurate and comprehensive results.

## How Filtering Works

### 1. Multi-Source Search Flow
```
User Request → OMDB API Search → TMDB API Search → Merge & Normalize → Apply Filters → Sort → Return Results
```

### 2. Comprehensive Data Retrieval

The API now fetches detailed movie information from multiple sources:

- **OMDB Integration**: Fetches complete detailed movie information with IMDB ratings
- **TMDB Integration**: Fetches additional movies and TV shows with comprehensive metadata
- **Data Merging**: Combines results from both sources, removing duplicates
- **Normalization**: Standardizes data format across different APIs
- **Accurate filtering**: All filters work on complete merged dataset

## Supported Filter Parameters

### Title Search
- **Parameter**: `title`
- **Type**: String
- **Description**: Search movies by title
- **Example**: `/api/v1/movies/search?title=batman`

### Actor Filtering
- **Parameter**: `actors`
- **Type**: String
- **Description**: Filter movies by actor names (case-insensitive, partial match)
- **Example**: `/api/v1/movies/search?title=batman&actors=Christian Bale`
- **Note**: Uses detailed movie information for accurate results

### Genre Filtering
- **Parameter**: `genre`
- **Type**: String
- **Description**: Filter movies by genre (case-insensitive, partial match)
- **Example**: `/api/v1/movies/search?title=batman&genre=Action`
- **Note**: Uses detailed movie information for accurate results

### Type Filtering
- **Parameter**: `type`
- **Type**: Enum (`movie`, `series`, `episode`)
- **Description**: Filter by content type
- **Example**: `/api/v1/movies/search?title=batman&type=movie`

### Year Filtering
- **Parameter**: `year`
- **Type**: String (4-digit year)
- **Description**: Filter movies by release year
- **Example**: `/api/v1/movies/search?title=batman&year=2008`
- **Validation**: Must be between 1900 and 2025

### Pagination
- **Parameters**: `page` (default: 1), `limit` (default: 10, max: 100)
- **Description**: Control result pagination
- **Example**: `/api/v1/movies/search?title=batman&page=2&limit=5`

## Advanced Filtering Examples

### 1. Multiple Filters
```http
GET /api/v1/movies/search?title=batman&actors=Christian Bale&genre=Action&type=movie
```

### 2. Actor Search with Partial Match
```http
GET /api/v1/movies/search?title=batman&actors=Bale
```
This will match "Christian Bale", "Gareth Bale", etc.

### 3. Genre Search with Partial Match
```http
GET /api/v1/movies/search?title=batman&genre=Act
```
This will match "Action", "Action/Adventure", etc.

## Performance Optimizations

### 1. Caching System
- **Search Results**: Cached for 5 minutes (configurable)
- **Detailed Movie Info**: Cached separately for efficient filtering
- **Cache Key**: Generated from filter parameters only (title, actors, genre, type, year)
- **Pagination**: Applied after caching, doesn't affect cache keys for better efficiency

### 2. Multi-Source Data Integration
- **OMDB + TMDB**: Fetch data from both APIs simultaneously
- **Smart merging**: OMDB data takes priority, TMDB fills gaps
- **Duplicate removal**: Eliminates duplicates based on title and year
- **Error handling**: Skip invalid movies, continue processing

### 3. Filtering Logic
```python
# Actor filtering (case-insensitive, partial match)
actors_list = [actor.strip().lower() for actor in movie.actors.split(',')]
search_actor = params.actors.lower().strip()
match = any(search_actor in actor for actor in actors_list)

# Genre filtering (case-insensitive, partial match)
genres_list = [genre.strip().lower() for genre in movie.genre.split(',')]
search_genre = params.genre.lower().strip()
match = any(search_genre in genre for genre in genres_list)
```

## API Response Format

### Success Response (Now with Full Detailed Data)
```json
{
  "movies": [
    {
      "title": "The Dark Knight",
      "year": "2008",
      "imdb_id": "tt0468569",
      "type": "movie",
      "poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
      "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the city streets. The partnership proves to be effective, but they soon find themselves prey to a reign of chaos unleashed by a rising criminal mastermind known to the terrified citizens of Gotham as the Joker.",
      "director": "Christopher Nolan",
      "actors": "Christian Bale, Heath Ledger, Aaron Eckhart, Michael Caine",
      "genre": "Action, Crime, Drama",
      "imdb_rating": "9.0",
      "runtime": "152 min",
      "released": "18 Jul 2008"
    }
  ],
  "total_results": 1,
  "page": 1,
  "total_pages": 1
}
```

### Error Response
```json
{
  "detail": "At least one search parameter is required"
}
```

## Error Handling

### 1. Validation Errors (400)
- Missing search parameters
- Invalid year format
- Invalid page/limit values

### 2. External API Errors (503)
- OMDB API key issues
- Network connectivity problems
- API rate limits

### 3. Not Found Errors (404)
- Movie not found by ID

## Usage Examples

### Python Client Example
```python
import requests

# Basic search
response = requests.get(
    "http://localhost:8000/api/v1/movies/search",
    params={"title": "batman", "limit": 5}
)

# Advanced filtering
response = requests.get(
    "http://localhost:8000/api/v1/movies/search",
    params={
        "title": "batman",
        "actors": "Christian Bale",
        "genre": "Action",
        "type": "movie",
        "year": "2008"
    }
)
```

### JavaScript/Fetch Example
```javascript
// Basic search
const response = await fetch(
    '/api/v1/movies/search?title=batman&limit=5'
);

// Advanced filtering
const response = await fetch(
    '/api/v1/movies/search?' + new URLSearchParams({
        title: 'batman',
        actors: 'Christian Bale',
        genre: 'Action',
        type: 'movie',
        year: '2008'
    })
);
```

## Configuration

### Environment Variables
```bash
# Required - OMDB API
OMDB_API_KEY=your_omdb_api_key_here

# Required - TMDB API
TMDB_API_KEY=your_tmdb_api_key_here

# Optional
OMDB_BASE_URL=https://www.omdbapi.com/
TMDB_BASE_URL=https://api.themoviedb.org/3
CACHE_TTL=300  # Cache TTL in seconds
```

### Getting API Keys

**OMDB API Key:**
1. Visit: http://www.omdbapi.com/apikey.aspx
2. Sign up for a free account
3. Get your API key

**TMDB API Key:**
1. Visit: https://www.themoviedb.org/settings/api
2. Create a free account
3. Request an API key
4. Get your API key

**Set Environment Variables:**
```bash
export OMDB_API_KEY=your_omdb_key
export TMDB_API_KEY=your_tmdb_key
```

## Best Practices

### 1. Use Appropriate Filters
- Use `title` for basic searches
- Add `actors` or `genre` for precise filtering (now included in all results)
- Use `type` to filter between movies and series

### 2. Pagination
- Always use reasonable `limit` values (10-50)
- Implement proper pagination for large result sets

### 3. Error Handling
- Always check response status codes
- Handle 503 errors (external API issues) gracefully
- Implement retry logic for transient failures

### 4. Performance
- Cache results on the client side when appropriate
- Avoid frequent identical requests
- Use specific search terms to reduce result sets
- **Note**: All searches now fetch detailed data, which may be slower but provides complete information

## Testing

Run the example tests:
```bash
# Set your API key
export OMDB_API_KEY=your_api_key_here

# Run the example
python example_usage.py

# Run the filtering test
python test_filtering.py
```

## Troubleshooting

### Common Issues

1. **"OMDB API key is not configured"**
   - Set the `OMDB_API_KEY` environment variable

2. **"At least one search parameter is required"**
   - Provide at least one of: title, actors, type, genre, year

3. **503 Service Unavailable**
   - Check your OMDB API key
   - Verify internet connectivity
   - Check OMDB API status

4. **Empty results with filters**
   - Try broader search terms
   - Check spelling of actor names or genres
   - Use partial matches instead of exact matches

5. **Same results for different filters (Cache Issue)**
   - **Fixed**: Cache keys now include all parameters
   - Clear cache: `DELETE /api/v1/debug/cache/clear`
   - Check cache status: `GET /api/v1/debug/cache/status` 
