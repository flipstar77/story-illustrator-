"""
Universal Actor Filmography Enrichment Script

Standard enrichment for ALL actors with:
- IMDB ratings
- Rotten Tomatoes scores
- Production budgets
- Salary data (if available)

Usage:
    python enrich_actor_data.py <actor_folder_name>

Example:
    python enrich_actor_data.py tom_hanks
    python enrich_actor_data.py johnny_depp
"""

import pandas as pd
from pathlib import Path
from story_illustrator.utils.perplexity_researcher import PerplexityResearcher
from story_illustrator.utils.api_keys import get_perplexity_key
from story_illustrator.utils.carousel_poster_enhancer import CarouselPosterEnhancer
from story_illustrator.utils.carousel_video_generator import CarouselVideoGenerator
import time
import sys


def enrich_actor_filmography(actor_folder, regenerate_posters=True, regenerate_video=True):
    """
    Complete enrichment workflow for any actor

    Args:
        actor_folder: Actor folder name (e.g., 'tom_hanks', 'johnny_depp')
        regenerate_posters: Whether to regenerate enhanced posters
        regenerate_video: Whether to regenerate carousel video
    """

    actor_path = Path(f"output/actor_analysis/{actor_folder}")

    if not actor_path.exists():
        print(f"[ERROR] Actor folder not found: {actor_path}")
        return

    # Find the CSV file
    csv_files = list(actor_path.glob("*_filmography*.csv"))
    if not csv_files:
        print(f"[ERROR] No filmography CSV found in {actor_path}")
        return

    csv_path = csv_files[0]
    actor_name = actor_folder.replace('_', ' ').title()

    print("=" * 70)
    print(f"ENRICHING {actor_name.upper()} FILMOGRAPHY")
    print("=" * 70)
    print(f"CSV: {csv_path.name}")
    print("=" * 70)

    # Load data
    df = pd.read_csv(csv_path)
    print(f"\n[OK] Loaded {len(df)} movies")

    # Add standard columns if they don't exist
    standard_columns = ['imdb_rating', 'rotten_tomatoes', 'budget']
    for col in standard_columns:
        if col not in df.columns:
            df[col] = ''
            print(f"[ADD] Added column: {col}")

    # Initialize Perplexity researcher (API key loaded from .env automatically)
    researcher = PerplexityResearcher()

    print("\n" + "=" * 70)
    print("STEP 1: ENRICHING WITH RATINGS & BUDGET DATA")
    print("=" * 70)

    # Process each movie
    enriched_count = 0
    for idx, row in df.iterrows():
        title = row['title']
        year = row['year']

        # Skip if already has all ratings
        has_imdb = pd.notna(row.get('imdb_rating')) and str(row['imdb_rating']).strip() != ''
        has_rt = pd.notna(row.get('rotten_tomatoes')) and str(row['rotten_tomatoes']).strip() != ''
        has_budget = pd.notna(row.get('budget')) and str(row['budget']).strip() != ''

        if has_imdb and has_rt and has_budget:
            print(f"[{idx+1}/{len(df)}] {title} ({year}) - Already enriched [OK]")
            enriched_count += 1
            continue

        print(f"\n[{idx+1}/{len(df)}] Researching: {title} ({year})")

        # Query Perplexity for all data
        query = f"""For the movie "{title}" ({year}) starring {actor_name}, provide ONLY these exact values:

1. IMDB rating (format: "7.8" or "N/A")
2. Rotten Tomatoes score (format: "85%" or "N/A")
3. Production budget (format: "$50 million" or "N/A")

Format your response EXACTLY as:
IMDB: 7.8
RT: 85%
Budget: $50 million

If data is not available, use "N/A" for that field."""

        try:
            response = researcher.research(query)
            print(f"Response:\n{response}")

            # Parse response
            imdb = ""
            rt = ""
            budget = ""

            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('IMDB:'):
                    imdb = line.replace('IMDB:', '').strip()
                    if imdb.lower() == 'n/a':
                        imdb = ''
                elif line.startswith('RT:'):
                    rt = line.replace('RT:', '').strip()
                    if rt.lower() == 'n/a':
                        rt = ''
                elif line.startswith('Budget:'):
                    budget = line.replace('Budget:', '').strip()
                    if budget.lower() == 'n/a':
                        budget = ''

            # Update dataframe
            if imdb:
                df.at[idx, 'imdb_rating'] = imdb
                print(f"  [OK] IMDB: {imdb}")
            if rt:
                df.at[idx, 'rotten_tomatoes'] = rt
                print(f"  [OK] RT: {rt}")
            if budget:
                df.at[idx, 'budget'] = budget
                print(f"  [OK] Budget: {budget}")

            # Save progress after each movie
            df.to_csv(csv_path, index=False)
            enriched_count += 1
            print(f"  [SAVED] Progress saved ({enriched_count}/{len(df)})")

            # Rate limiting
            time.sleep(2)

        except Exception as e:
            print(f"  [ERROR] Failed: {e}")
            continue

    print("\n" + "=" * 70)
    print("STEP 1 COMPLETE: DATA ENRICHMENT")
    print("=" * 70)
    print(f"Enriched: {enriched_count}/{len(df)} movies")
    print(f"Updated CSV: {csv_path}")

    # Step 2: Regenerate enhanced posters
    if regenerate_posters:
        print("\n" + "=" * 70)
        print("STEP 2: REGENERATING ENHANCED POSTERS")
        print("=" * 70)

        enhanced_posters_dir = actor_path / "enhanced_posters"
        enhanced_posters_dir.mkdir(exist_ok=True)

        enhancer = CarouselPosterEnhancer()
        enhanced_posters = enhancer.batch_enhance_posters(
            csv_path=csv_path,
            output_dir=enhanced_posters_dir
        )

        print(f"\n[OK] Generated {len(enhanced_posters)} enhanced posters")
        print(f"Output: {enhanced_posters_dir}")

    # Step 3: Regenerate carousel video
    if regenerate_video:
        print("\n" + "=" * 70)
        print("STEP 3: GENERATING CAROUSEL VIDEO")
        print("=" * 70)

        output_video = actor_path / f"carousel_video_enriched.mp4"

        generator = CarouselVideoGenerator()
        video_path = generator.create_carousel_from_csv(
            csv_path=csv_path,
            enhanced_posters_dir=enhanced_posters_dir,
            output_path=output_video
        )

        print(f"\n[OK] Carousel video created: {video_path}")

    print("\n" + "=" * 70)
    print(f"[COMPLETE] {actor_name.upper()} ENRICHMENT FINISHED")
    print("=" * 70)
    print(f"\nCSV: {csv_path}")
    if regenerate_posters:
        print(f"Posters: {enhanced_posters_dir}")
    if regenerate_video:
        print(f"Video: {output_video}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enrich_actor_data.py <actor_folder_name>")
        print("\nExample:")
        print("  python enrich_actor_data.py tom_hanks")
        print("  python enrich_actor_data.py johnny_depp")
        print("\nAvailable actors:")

        actor_analysis_dir = Path("output/actor_analysis")
        if actor_analysis_dir.exists():
            for actor_dir in sorted(actor_analysis_dir.iterdir()):
                if actor_dir.is_dir():
                    print(f"  - {actor_dir.name}")
        sys.exit(1)

    actor_folder = sys.argv[1]
    enrich_actor_filmography(actor_folder)
