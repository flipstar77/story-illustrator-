"""
Movie Poster Downloader
Downloads movie posters from TMDB (The Movie Database)
"""

import requests
import os
from pathlib import Path
from typing import Optional
from .api_keys import get_api_key


class MoviePosterDownloader:
    """
    Download movie posters from TMDB

    Requires TMDB API key in .env file as TMDB_API_KEY
    Get your free key at: https://www.themoviedb.org/settings/api
    """

    def __init__(self):
        # TMDB API key is optional - will try to use if available
        self.api_key = os.getenv('TMDB_API_KEY')
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/original"

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[dict]:
        """
        Search for a movie by title and optionally year

        Args:
            title: Movie title
            year: Optional release year for better accuracy

        Returns:
            Movie data dict or None if not found
        """
        if not self.api_key:
            print("Warning: TMDB_API_KEY not found in .env file")
            return None

        # TMDB supports both API key and Bearer token
        # Check if it's a Bearer token (JWT) or regular API key
        if self.api_key.startswith('eyJ'):
            # Bearer token (JWT)
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'accept': 'application/json'
            }
            params = {'query': title}
        else:
            # Regular API key
            headers = {}
            params = {
                'api_key': self.api_key,
                'query': title
            }

        if year:
            params['year'] = year

        try:
            response = requests.get(
                f"{self.base_url}/search/movie",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            results = response.json().get('results', [])

            if results:
                return results[0]  # Return first (most relevant) result

            return None

        except Exception as e:
            print(f"Error searching for movie '{title}': {e}")
            return None

    def download_poster(
        self,
        movie_title: str,
        year: Optional[int] = None,
        output_dir: str = "output/posters",
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Download movie poster

        Args:
            movie_title: Title of the movie
            year: Optional release year
            output_dir: Directory to save poster
            filename: Optional custom filename (will auto-generate if not provided)

        Returns:
            Path to downloaded poster or None if failed
        """
        # Search for the movie
        movie = self.search_movie(movie_title, year)

        if not movie:
            print(f"Movie not found: {movie_title}")
            return None

        poster_path = movie.get('poster_path')

        if not poster_path:
            print(f"No poster available for: {movie_title}")
            return None

        # Download the poster
        poster_url = f"{self.image_base_url}{poster_path}"

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename
        if not filename:
            # Clean movie title for filename
            clean_title = "".join(c for c in movie_title if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_title = clean_title.replace(' ', '_')
            if year:
                filename = f"{clean_title}_{year}.jpg"
            else:
                filename = f"{clean_title}.jpg"

        output_file = output_path / filename

        try:
            response = requests.get(poster_url, timeout=30)
            response.raise_for_status()

            with open(output_file, 'wb') as f:
                f.write(response.content)

            print(f"Downloaded poster: {output_file}")
            return str(output_file)

        except Exception as e:
            print(f"Error downloading poster for '{movie_title}': {e}")
            return None

    def download_posters_batch(
        self,
        movies: list,
        output_dir: str = "output/posters"
    ) -> dict:
        """
        Download posters for multiple movies

        Args:
            movies: List of dicts with 'title' and optionally 'year' keys
            output_dir: Directory to save posters

        Returns:
            Dict mapping movie titles to poster file paths
        """
        results = {}

        for movie in movies:
            title = movie.get('title')
            year = movie.get('year')

            if not title:
                continue

            poster_path = self.download_poster(title, year, output_dir)
            results[title] = poster_path

        return results


# Convenience function
def download_movie_poster(title: str, year: Optional[int] = None, output_dir: str = "output/posters") -> Optional[str]:
    """
    Quick function to download a single movie poster

    Example:
        poster_path = download_movie_poster("Top Gun Maverick", 2022)
    """
    downloader = MoviePosterDownloader()
    return downloader.download_poster(title, year, output_dir)
