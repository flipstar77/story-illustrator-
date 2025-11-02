"""
Perplexity AI Research Module
Automatically research and gather data for slideshow videos
"""

import requests
import json
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Optional
from .api_keys import get_perplexity_key


class PerplexityResearcher:
    """
    Use Perplexity AI to research topics and generate structured data
    for slideshow videos
    """

    def __init__(self):
        self.api_key = get_perplexity_key(required=True)
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"  # Best for research (updated 2025)

    def research(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Send research query to Perplexity AI

        Args:
            prompt: Research question or topic
            model: Optional model override

        Returns:
            Research results as text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model or self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise research assistant. Provide accurate, factual information with specific numbers, dates, and sources when available."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,  # Low temperature for factual accuracy
            "max_tokens": 4000
        }

        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    def research_actor_filmography(
        self,
        actor_name: str,
        include_earnings: bool = True,
        include_box_office: bool = True,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Research an actor's filmography with financial data

        Args:
            actor_name: Name of the actor
            include_earnings: Include actor's salary per movie
            include_box_office: Include box office performance
            min_year: Minimum year to include
            max_year: Maximum year to include

        Returns:
            DataFrame with movie data
        """
        # Build research query
        year_filter = ""
        if min_year and max_year:
            year_filter = f" between {min_year} and {max_year}"
        elif min_year:
            year_filter = f" from {min_year} onwards"
        elif max_year:
            year_filter = f" up to {max_year}"

        financial_data = []
        if include_earnings:
            financial_data.append("actor's salary/earnings per movie")
        if include_box_office:
            financial_data.append("movie budget")
            financial_data.append("box office gross (worldwide)")

        financial_str = ", ".join(financial_data) if financial_data else ""

        prompt = f"""
Research {actor_name}'s complete filmography{year_filter}.

For each movie, provide:
1. Movie title
2. Release year
3. Role/character name
4. {financial_str if financial_str else "Genre"}

Format the response as a structured list with clear separation between movies.
Focus on major theatrical releases and notable films.
Include specific dollar amounts where available.

Please provide accurate, verified information only.
"""

        # Get research results
        result = self.research(prompt)

        # Parse into structured data
        movies = self._parse_filmography(result, actor_name)

        return pd.DataFrame(movies)

    def research_topic_timeline(
        self,
        topic: str,
        num_events: int = 10,
        focus: str = "major milestones"
    ) -> pd.DataFrame:
        """
        Research a topic and create a timeline of events

        Args:
            topic: Topic to research (e.g., "Tesla company history", "Bitcoin evolution")
            num_events: Number of key events to include
            focus: What to focus on (milestones, achievements, controversies, etc.)

        Returns:
            DataFrame with timeline data
        """
        prompt = f"""
Research the history and timeline of: {topic}

Provide the top {num_events} most important events, focusing on {focus}.

For each event, include:
1. Date (year or specific date)
2. Event title/name
3. Key data point or metric (number, percentage, amount, etc.)
4. Brief description (1-2 sentences)
5. Why it's significant

Format as a clear, chronological list.
Include specific numbers and data where relevant.
"""

        result = self.research(prompt)
        events = self._parse_timeline(result, topic)

        return pd.DataFrame(events)

    def research_comparison(
        self,
        items: List[str],
        criteria: List[str],
        context: str = ""
    ) -> pd.DataFrame:
        """
        Research and compare multiple items across criteria

        Args:
            items: List of items to compare (e.g., ["iPhone 15", "Samsung S24", "Pixel 8"])
            criteria: What to compare (e.g., ["price", "battery life", "camera quality"])
            context: Additional context (e.g., "smartphones in 2024")

        Returns:
            DataFrame with comparison data
        """
        items_str = ", ".join(items)
        criteria_str = ", ".join(criteria)

        prompt = f"""
Compare the following {context}: {items_str}

Provide specific data for each item across these criteria:
{criteria_str}

For each criterion, include:
- Exact numbers/specifications where applicable
- Objective measurements (not opinions)
- Current/latest data

Format as a clear comparison table with specific values.
"""

        result = self.research(prompt)
        comparison = self._parse_comparison(result, items, criteria)

        return pd.DataFrame(comparison)

    def generate_slideshow_data(
        self,
        topic: str,
        num_slides: int = 10,
        style: str = "timeline"
    ) -> pd.DataFrame:
        """
        Generate complete slideshow data for a topic

        Args:
            topic: Topic to research
            num_slides: Number of slides to generate
            style: Style of slideshow ("timeline", "facts", "comparison", "story")

        Returns:
            DataFrame ready for slideshow generation
        """
        prompt = f"""
Create data for a {num_slides}-slide video about: {topic}

For each slide, provide:
1. Slide number (1-{num_slides})
2. Slide title (short, impactful)
3. Key data point (number, date, statistic - make it prominent)
4. Narration text (2-3 sentences, engaging and informative)
5. Image description (for AI image generation)

Style: {style}

Make it engaging, factual, and suitable for a motivational/educational video.
Include specific numbers and data points that create impact.

Format each slide clearly with all 5 elements.
"""

        result = self.research(prompt)
        slides = self._parse_slideshow_data(result)

        # Create DataFrame
        df = pd.DataFrame(slides)

        # Ensure proper columns
        required_columns = [
            'slide_number',
            'title',
            'data_point',
            'narration_text',
            'image_prompt'
        ]

        for col in required_columns:
            if col not in df.columns:
                df[col] = ""

        return df[required_columns]

    def _parse_filmography(self, text: str, actor_name: str) -> List[Dict]:
        """Parse filmography text into structured data"""
        # This is a simplified parser - can be enhanced with more sophisticated parsing
        movies = []

        lines = text.strip().split('\n')
        current_movie = {}

        for line in lines:
            line = line.strip()
            if not line:
                if current_movie:
                    movies.append(current_movie)
                    current_movie = {}
                continue

            # Try to extract movie information
            # This is a basic implementation - enhance based on actual Perplexity response format
            if any(char.isdigit() for char in line[:10]):  # Likely has a year
                if 'title' not in current_movie:
                    current_movie['title'] = line
                    current_movie['actor'] = actor_name

        if current_movie:
            movies.append(current_movie)

        return movies

    def _parse_timeline(self, text: str, topic: str) -> List[Dict]:
        """Parse timeline text into structured events"""
        events = []

        # Basic parsing - enhance based on actual response format
        lines = text.strip().split('\n')
        current_event = {'topic': topic}

        for line in lines:
            line = line.strip()
            if not line:
                if len(current_event) > 1:
                    events.append(current_event)
                    current_event = {'topic': topic}
                continue

            # Extract event data
            if any(char.isdigit() for char in line[:20]):
                if 'date' not in current_event:
                    current_event['event'] = line

        if len(current_event) > 1:
            events.append(current_event)

        return events

    def _parse_comparison(
        self,
        text: str,
        items: List[str],
        criteria: List[str]
    ) -> List[Dict]:
        """Parse comparison text into structured data"""
        comparisons = []

        # Basic parsing - enhance based on actual response format
        for item in items:
            comparison = {'item': item}
            for criterion in criteria:
                # Extract criterion value from text
                # This is simplified - enhance with better parsing
                comparison[criterion] = ""

            comparisons.append(comparison)

        return comparisons

    def _parse_slideshow_data(self, text: str) -> List[Dict]:
        """Parse slideshow data from research results using regex"""
        slides = []

        # Split by slide markers (e.g., "Slide 1", "Slide 2", etc.)
        # Use regex to find all slides
        slide_pattern = r'Slide (\d+)\s*(.*?)(?=Slide \d+|$)'
        matches = re.findall(slide_pattern, text, re.DOTALL | re.IGNORECASE)

        for slide_num, slide_content in matches:
            slide = {
                'slide_number': int(slide_num),
                'title': '',
                'data_point': '',
                'narration_text': '',
                'image_prompt': ''
            }

            # Extract title (usually in bold after "Slide Title:")
            title_match = re.search(r'\*\*Slide Title:\*\*\s*(.*?)(?:\n|$)', slide_content)
            if title_match:
                slide['title'] = title_match.group(1).strip()

            # Extract data point (usually after "Key Data Point:")
            data_match = re.search(r'\*\*Key Data Point:\*\*\s*(.*?)(?:\n|$)', slide_content)
            if data_match:
                slide['data_point'] = data_match.group(1).strip()

            # Extract narration text (usually after "Narration Text:")
            narration_match = re.search(r'\*\*Narration Text:\*\*\s*(.*?)(?=\*\*Image Description:|$)', slide_content, re.DOTALL)
            if narration_match:
                # Clean up the narration text - remove extra whitespace and newlines
                narration = narration_match.group(1).strip()
                narration = re.sub(r'\s+', ' ', narration)  # Replace multiple whitespace with single space
                narration = re.sub(r'\[\d+\]', '', narration)  # Remove citation numbers like [1][2]
                slide['narration_text'] = narration

            # Extract image description (usually after "Image Description:")
            image_match = re.search(r'\*\*Image Description:\*\*\s*(.*?)(?:---|$)', slide_content, re.DOTALL)
            if image_match:
                slide['image_prompt'] = image_match.group(1).strip()

            # Only add slide if we got at least title and narration
            if slide['title'] and slide['narration_text']:
                slides.append(slide)

        return slides


# Convenience functions

def research_actor_movies(actor_name: str, output_csv: Optional[str] = None) -> pd.DataFrame:
    """
    Quick function to research actor's movies and save to CSV

    Example:
        df = research_actor_movies("Tom Cruise", "tom_cruise_movies.csv")
    """
    researcher = PerplexityResearcher()
    df = researcher.research_actor_filmography(actor_name)

    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Saved to {output_csv}")

    return df


def create_slideshow_from_topic(
    topic: str,
    num_slides: int = 10,
    output_csv: Optional[str] = None
) -> pd.DataFrame:
    """
    Quick function to create slideshow data from any topic

    Example:
        df = create_slideshow_from_topic(
            "Tom Cruise career highlights",
            num_slides=10,
            output_csv="tom_cruise_slideshow.csv"
        )
    """
    researcher = PerplexityResearcher()
    df = researcher.generate_slideshow_data(topic, num_slides)

    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Saved slideshow data to {output_csv}")

    return df


# Example usage
if __name__ == "__main__":
    # Example 1: Research Tom Cruise movies
    print("Researching Tom Cruise filmography...")
    researcher = PerplexityResearcher()

    df = researcher.generate_slideshow_data(
        topic="Tom Cruise career: major movies, earnings, and box office performance",
        num_slides=12,
        style="timeline"
    )

    print("\nGenerated slideshow data:")
    print(df)

    # Save to CSV
    output_path = Path("data/tom_cruise_slideshow.csv")
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")

    # Example 2: Generate slideshow for any topic
    print("\n" + "="*60)
    print("Researching Tesla company milestones...")

    df2 = researcher.generate_slideshow_data(
        topic="Tesla Inc. major milestones and achievements",
        num_slides=10,
        style="timeline"
    )

    print(df2)
    df2.to_csv("data/tesla_milestones.csv", index=False)
