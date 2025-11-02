"""
Narration Script Generator for Carousel Videos
Generates synchronized narration scripts that align with poster timing
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple


class NarrationScriptGenerator:
    """Generates narration scripts synchronized with carousel video timing"""

    def __init__(self, scroll_speed=120, poster_width=1000, poster_spacing=40):
        """
        Initialize narration generator

        Args:
            scroll_speed: Pixels per second for carousel scroll
            poster_width: Width of each poster in pixels (at video height)
            poster_spacing: Spacing between posters in pixels
        """
        self.scroll_speed = scroll_speed
        self.poster_width = poster_width
        self.poster_spacing = poster_spacing

        # Calculate time per poster
        self.time_per_poster = (poster_width + poster_spacing) / scroll_speed

    def generate_statistical_summary(self, df: pd.DataFrame, actor_name: str) -> Dict[str, str]:
        """
        Generate statistical summary for intro/outro

        Args:
            df: DataFrame with actor's filmography
            actor_name: Actor's name

        Returns:
            Dict with 'intro' and 'outro' text
        """
        movie_count = len(df)
        year_start = df['year'].min()
        year_end = df['year'].max()
        years_span = year_end - year_start

        # Calculate statistics
        total_box_office = 0
        avg_imdb = 0
        imdb_count = 0

        for _, row in df.iterrows():
            # Box office
            if pd.notna(row.get('box_office')) and row.get('box_office'):
                try:
                    bo_str = str(row['box_office']).replace('$', '').replace(',', '').strip()
                    if 'million' in bo_str.lower():
                        amount = float(bo_str.lower().replace('million', '').strip())
                        total_box_office += amount
                    elif 'billion' in bo_str.lower():
                        amount = float(bo_str.lower().replace('billion', '').strip())
                        total_box_office += amount * 1000
                except:
                    pass

            # IMDB rating
            if pd.notna(row.get('imdb_rating')) and row.get('imdb_rating'):
                try:
                    rating_str = str(row['imdb_rating']).replace('/10', '').strip()
                    rating = float(rating_str)
                    avg_imdb += rating
                    imdb_count += 1
                except:
                    pass

        if imdb_count > 0:
            avg_imdb = avg_imdb / imdb_count

        # Format box office
        if total_box_office >= 1000:
            bo_text = f"${total_box_office/1000:.1f} billion"
        else:
            bo_text = f"${total_box_office:.0f} million"

        # Generate intro
        intro = f"{actor_name}. {movie_count} films spanning {year_start} to {year_end}."
        if total_box_office > 0:
            intro += f" Total box office: {bo_text}."
        if avg_imdb > 0:
            intro += f" Average IMDB rating: {avg_imdb:.1f}."

        # Generate outro
        outro = f"From {year_start} to {year_end}. {actor_name}'s remarkable journey through cinema."

        return {
            'intro': intro,
            'outro': outro,
            'stats': {
                'movie_count': movie_count,
                'years_span': years_span,
                'total_box_office': total_box_office,
                'avg_imdb': avg_imdb
            }
        }

    def generate_movie_narration(self, row: pd.Series, time_available: float, actor_name: str = None) -> str:
        """
        Generate narration text for a single movie

        Args:
            row: DataFrame row with movie data
            time_available: Seconds available for this movie's narration
            actor_name: Actor's name (optional, for character mentions)

        Returns:
            Narration text string
        """
        title = row['title']
        year = row['year']

        # Base narration (always included)
        narration = f"{year}, {title}."

        # Add character if available
        if actor_name and pd.notna(row.get('character')) and row.get('character'):
            character = str(row['character'])
            if character.strip():
                narration += f" {actor_name} as {character}."

        # If we have more time, add ratings and box office
        if time_available > 5:
            # Add IMDB rating
            if pd.notna(row.get('imdb_rating')) and row.get('imdb_rating'):
                rating = str(row['imdb_rating']).replace('/10', '').strip()
                narration += f" IMDB {rating}."

            # Add box office
            if pd.notna(row.get('box_office')) and row.get('box_office'):
                bo = str(row['box_office'])
                narration += f" {bo} box office."

        return narration

    def generate_complete_script(self, csv_path: str, actor_name: str) -> Dict:
        """
        Generate complete narration script for carousel video

        Args:
            csv_path: Path to actor's filmography CSV
            actor_name: Actor's name

        Returns:
            Dict with script segments and timing
        """
        df = pd.read_csv(csv_path)
        df = df.sort_values('year')

        # Generate statistical summary
        summary = self.generate_statistical_summary(df, actor_name)

        # Generate movie-by-movie narration
        movie_narrations = []
        for idx, row in df.iterrows():
            narration = self.generate_movie_narration(row, self.time_per_poster, actor_name)
            movie_narrations.append({
                'movie': row['title'],
                'year': row['year'],
                'text': narration,
                'duration': self.time_per_poster
            })

        return {
            'intro': {
                'text': summary['intro'],
                'duration': 10  # 10 seconds for intro
            },
            'movies': movie_narrations,
            'outro': {
                'text': summary['outro'],
                'duration': 5  # 5 seconds for outro
            },
            'stats': summary['stats'],
            'total_duration': 15 + (len(movie_narrations) * self.time_per_poster)
        }

    def save_script_to_file(self, script: Dict, output_path: str):
        """
        Save narration script to text file

        Args:
            script: Script dictionary from generate_complete_script()
            output_path: Path to save text file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("CAROUSEL VIDEO NARRATION SCRIPT\n")
            f.write("=" * 70 + "\n\n")

            # Intro
            f.write(f"[INTRO - {script['intro']['duration']} seconds]\n")
            f.write(f"{script['intro']['text']}\n\n")

            # Movies
            f.write(f"[MOVIES - {len(script['movies'])} films]\n\n")
            for movie in script['movies']:
                f.write(f"[{movie['year']}] {movie['movie']} ({movie['duration']:.1f}s)\n")
                f.write(f"{movie['text']}\n\n")

            # Outro
            f.write(f"[OUTRO - {script['outro']['duration']} seconds]\n")
            f.write(f"{script['outro']['text']}\n\n")

            # Statistics
            f.write("=" * 70 + "\n")
            f.write("STATISTICS\n")
            f.write("=" * 70 + "\n")
            f.write(f"Total movies: {script['stats']['movie_count']}\n")
            f.write(f"Years span: {script['stats']['years_span']}\n")
            if script['stats']['total_box_office'] > 0:
                f.write(f"Total box office: ${script['stats']['total_box_office']:.0f}M\n")
            if script['stats']['avg_imdb'] > 0:
                f.write(f"Average IMDB: {script['stats']['avg_imdb']:.1f}\n")
            f.write(f"\nTotal duration: {script['total_duration']:.1f} seconds\n")


# Example usage
if __name__ == "__main__":
    generator = NarrationScriptGenerator(scroll_speed=120)

    # Example: Generate script for Brad Pitt
    csv_path = "output/actor_analysis/brad_pitt/brad_pitt_complete_filmography_with_posters.csv"
    actor_name = "Brad Pitt"

    if Path(csv_path).exists():
        script = generator.generate_complete_script(csv_path, actor_name)

        # Save to file
        output_path = Path(csv_path).parent / "narration_script.txt"
        generator.save_script_to_file(script, output_path)

        print(f"Narration script generated: {output_path}")
        print(f"Total duration: {script['total_duration']:.1f} seconds")
        print(f"Intro: {script['intro']['text']}")
    else:
        print(f"CSV not found: {csv_path}")
