#!/usr/bin/env python3
"""
Example usage of the Movie Search API with improved filtering
"""
import asyncio
import json
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)

def test_api_endpoints():
    """Test the API endpoints with various filtering scenarios"""
    
    print("Movie Search API - Filtering Examples")
    print("=" * 50)
    
    # Test 1: Basic title search (now with detailed data)
    print("\n1. Basic title search for 'batman' (with detailed data):")
    response = client.get("/api/v1/movies/search?title=batman&limit=3")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_results']} movies")
        for movie in data['movies']:
            print(f"  - {movie['title']} ({movie['year']})")
            print(f"    Director: {movie.get('director', 'N/A')}")
            print(f"    Actors: {movie.get('actors', 'N/A')}")
            print(f"    Genre: {movie.get('genre', 'N/A')}")
            print(f"    IMDB Rating: {movie.get('imdb_rating', 'N/A')}")
            print(f"    Runtime: {movie.get('runtime', 'N/A')}")
            if movie.get('plot'):
                plot_preview = movie['plot'][:100] + "..." if len(movie['plot']) > 100 else movie['plot']
                print(f"    Plot: {plot_preview}")
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test 2: Filter by actor
    print("\n2. Search 'batman' movies with actor 'Christian Bale':")
    response = client.get("/api/v1/movies/search?title=batman&actors=Christian Bale&limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_results']} movies")
        for movie in data['movies']:
            print(f"  - {movie['title']} ({movie['year']})")
            print(f"    Actors: {movie.get('actors', 'N/A')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test 3: Filter by genre
    print("\n3. Search 'batman' movies in 'Action' genre:")
    response = client.get("/api/v1/movies/search?title=batman&genre=Action&limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_results']} movies")
        for movie in data['movies']:
            print(f"  - {movie['title']} ({movie['year']})")
            print(f"    Genre: {movie.get('genre', 'N/A')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test 4: Filter by type
    print("\n4. Search 'batman' movies (type=movie):")
    response = client.get("/api/v1/movies/search?title=batman&type=movie&limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_results']} movies")
        for movie in data['movies']:
            print(f"  - {movie['title']} ({movie['year']}) - Type: {movie.get('type', 'N/A')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test 5: Multiple filters
    print("\n5. Search 'batman' movies with actor 'Christian Bale' in 'Action' genre:")
    response = client.get("/api/v1/movies/search?title=batman&actors=Christian Bale&genre=Action&limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_results']} movies")
        for movie in data['movies']:
            print(f"  - {movie['title']} ({movie['year']})")
            print(f"    Actors: {movie.get('actors', 'N/A')}")
            print(f"    Genre: {movie.get('genre', 'N/A')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Test 6: Filter by year
    print("\n6. Search 'batman' movies from 2008:")
    response = client.get("/api/v1/movies/search?title=batman&year=2008&limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_results']} movies")
        for movie in data['movies']:
            print(f"  - {movie['title']} ({movie['year']})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def test_error_handling():
    """Test error handling scenarios"""
    
    print("\n" + "=" * 50)
    print("Testing Error Handling")
    print("=" * 50)
    
    # Test 1: No search parameters
    print("\n1. Testing with no search parameters:")
    response = client.get("/api/v1/movies/search")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.json()}")
    
    # Test 2: Invalid year
    print("\n2. Testing with invalid year:")
    response = client.get("/api/v1/movies/search?title=batman&year=invalid")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.json()}")
    
    # Test 3: Invalid page number
    print("\n3. Testing with invalid page number:")
    response = client.get("/api/v1/movies/search?title=batman&page=0")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.json()}")

def test_pagination():
    """Test pagination functionality"""
    
    print("\n" + "=" * 50)
    print("Testing Pagination (Cache Efficient)")
    print("=" * 50)
    
    # Test pagination - all requests should use same cache
    print("\n1. Testing pagination with 'batman' search:")
    
    # First request
    print("   First request (page=1, limit=3):")
    response1 = client.get("/api/v1/movies/search?title=batman&page=1&limit=3")
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"   Page {data1['page']} of {data1['total_pages']}")
        print(f"   Total results: {data1['total_results']}")
        print("   Movies on this page:")
        for movie in data1['movies']:
            print(f"     - {movie['title']} ({movie['year']})")
    
    # Second request - different pagination, should use cache
    print("\n   Second request (page=2, limit=5) - should be faster:")
    response2 = client.get("/api/v1/movies/search?title=batman&page=2&limit=5")
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"   Page {data2['page']} of {data2['total_pages']}")
        print(f"   Total results: {data2['total_results']} (same as first request)")
        print("   Movies on this page:")
        for movie in data2['movies']:
            print(f"     - {movie['title']} ({movie['year']})")
    
    if response1.status_code == 200 and response2.status_code == 200:
        if data1['total_results'] == data2['total_results']:
            print("\n   ✅ Cache working: Same total results for different pagination")
        else:
            print("\n   ❌ Issue: Different total results")
    else:
        print(f"Error: {response1.status_code if response1.status_code != 200 else response2.status_code}")

if __name__ == "__main__":
    print("Starting Movie Search API Tests...")
    print("Note: Make sure to set your OMDB_API_KEY environment variable")
    print("You can get a free API key at: http://www.omdbapi.com/apikey.aspx")
    
    # Run tests
    test_api_endpoints()
    test_error_handling()
    test_pagination()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50) 