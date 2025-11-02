"""
Carousel Poster Enhancement Module
Handles adding professional overlays and styling to movie posters
"""

import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pandas as pd


class CarouselPosterEnhancer:
    """Enhances movie posters with professional overlays for carousel videos"""

    def __init__(self):
        self.overlay_height = 380
        self.box_spacing = 30
        self.box_padding = 20

    @staticmethod
    def normalize_money(value):
        """Normalize money values to consistent format"""
        if not value or value == '' or value.lower() == 'unknown':
            return None

        value = str(value).strip()

        billion_match = re.search(r'\$?([\d.]+)\s*[Bb]', value)
        if billion_match:
            amount = float(billion_match.group(1)) * 1000
            return f"${amount:.0f}M"

        million_match = re.search(r'\$?([\d.]+)\s*[Mm]', value)
        if million_match:
            amount = float(million_match.group(1))
            return f"${amount:.0f}M"

        million_word = re.search(r'\$?([\d.]+)\s*million', value, re.IGNORECASE)
        if million_word:
            amount = float(million_word.group(1))
            return f"${amount:.0f}M"

        return value

    def _load_fonts(self):
        """Load fonts with fallback options"""
        try:
            return {
                'title': ImageFont.truetype("arialbd.ttf", 75),
                'label': ImageFont.truetype("arial.ttf", 42),
                'value': ImageFont.truetype("arialbd.ttf", 56),
                'small': ImageFont.truetype("arial.ttf", 36)
            }
        except:
            try:
                return {
                    'title': ImageFont.truetype("arial.ttf", 75),
                    'label': ImageFont.truetype("arial.ttf", 42),
                    'value': ImageFont.truetype("arial.ttf", 56),
                    'small': ImageFont.truetype("arial.ttf", 36)
                }
            except:
                default_font = ImageFont.load_default()
                return {
                    'title': default_font,
                    'label': default_font,
                    'value': default_font,
                    'small': default_font
                }

    def _create_gradient_overlay(self, width, height):
        """Create gradient overlay background"""
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Enhanced gradient effect
        for i in range(self.overlay_height):
            alpha = int(240 * (i / self.overlay_height))
            overlay_draw.rectangle(
                [(0, height - self.overlay_height + i), (width, height - self.overlay_height + i + 1)],
                fill=(10, 15, 25, alpha)
            )

        # Solid bottom section
        overlay_draw.rectangle(
            [(0, height - 280), (width, height)],
            fill=(10, 15, 25, 245)
        )

        return overlay

    def _draw_title_with_shadow(self, draw, title, year, y_offset, fonts):
        """Draw movie title with shadow effect, breaking long titles into 2 lines"""
        year_text = f"({year})"

        # Check if title is too long (threshold: 30 characters)
        max_width = 1920  # Max width for title text (poster width - margins)
        title_bbox = draw.textbbox((0, 0), title, font=fonts['title'])
        title_width = title_bbox[2] - title_bbox[0]

        if len(title) > 30 or title_width > max_width:
            # Break title into 2 lines at a logical point
            words = title.split()
            mid_point = len(words) // 2

            # Try to split at a natural break (conjunctions, prepositions)
            split_words = ['and', 'the', 'of', 'in', 'or', '&', 'vs', 'vs.']
            for i, word in enumerate(words):
                if word.lower() in split_words and abs(i - mid_point) <= 2:
                    mid_point = i
                    break

            line1 = ' '.join(words[:mid_point])
            line2 = ' '.join(words[mid_point:])

            # Draw line 1
            draw.text((32, y_offset + 2), line1, fill='#000000', font=fonts['title'])
            draw.text((30, y_offset), line1, fill='#FFFFFF', font=fonts['title'])

            # Draw line 2
            line_height = 75  # Spacing between lines
            draw.text((32, y_offset + line_height + 2), line2, fill='#000000', font=fonts['title'])
            draw.text((30, y_offset + line_height), line2, fill='#FFFFFF', font=fonts['title'])

            # Year next to second line
            line2_bbox = draw.textbbox((30, y_offset + line_height), line2, font=fonts['title'])
            year_x = line2_bbox[2] + 15
            draw.text((year_x + 2, y_offset + line_height + 8), year_text, fill='#000000', font=fonts['label'])
            draw.text((year_x, y_offset + line_height + 6), year_text, fill='#888888', font=fonts['label'])
        else:
            # Single line title
            draw.text((32, y_offset + 2), title, fill='#000000', font=fonts['title'])
            draw.text((30, y_offset), title, fill='#FFFFFF', font=fonts['title'])

            # Year next to title
            title_bbox = draw.textbbox((30, y_offset), title, font=fonts['title'])
            year_x = title_bbox[2] + 15
            draw.text((year_x + 2, y_offset + 8), year_text, fill='#000000', font=fonts['label'])
            draw.text((year_x, y_offset + 6), year_text, fill='#888888', font=fonts['label'])

    def _draw_info_box(self, draw, label, value, x_pos, y_pos, color, fonts):
        """Draw an info box with border and text"""
        label_bbox = draw.textbbox((0, 0), label, font=fonts['small'])
        value_bbox = draw.textbbox((0, 0), value, font=fonts['value'])
        box_width = max(label_bbox[2] - label_bbox[0], value_bbox[2] - value_bbox[0]) + self.box_padding * 2

        # Draw box background with border
        draw.rounded_rectangle(
            [(x_pos, y_pos - 15), (x_pos + box_width, y_pos + 140)],
            radius=12,
            fill=(25, 35, 50, 220),
            outline=color,
            width=3
        )

        draw.text((x_pos + self.box_padding, y_pos), label, fill='#B0B0B0', font=fonts['small'])
        draw.text((x_pos + self.box_padding, y_pos + 50), value, fill=self._get_value_color(label), font=fonts['value'])

        return box_width

    @staticmethod
    def _get_value_color(label):
        """Get appropriate color for value based on label"""
        if 'CHARACTER' in label:
            return '#FFD700'
        elif 'BOX OFFICE' in label:
            return '#00FF7F'
        elif 'PAYCHECK' in label:
            return '#FFD700'
        elif 'BUDGET' in label:
            return '#87CEEB'  # Sky blue for budget
        elif 'IMDB' in label:
            return '#F5C518'  # IMDB yellow
        elif 'ROTTEN' in label:
            return '#FA320A'  # Rotten Tomatoes red
        return '#FFFFFF'

    def enhance_poster(self, poster_path, title, year, character='', box_office='', salary='',
                      imdb_rating='', rotten_tomatoes='', budget='', output_path=None, target_size=(2000, 3000)):
        """
        Add professional text overlay to movie poster

        Args:
            poster_path: Path to original poster image
            title: Movie title
            year: Release year
            character: Character name (optional)
            box_office: Box office earnings (optional)
            salary: Actor salary (optional)
            imdb_rating: IMDB rating (optional, e.g., "7.8/10")
            rotten_tomatoes: Rotten Tomatoes score (optional, e.g., "85%")
            budget: Production budget (optional, e.g., "$50 million")
            output_path: Where to save enhanced poster (optional, defaults to poster_path)
            target_size: Target dimensions for all posters (width, height) - default 2000x3000

        Returns:
            Path to enhanced poster
        """
        # Load image
        img = Image.open(poster_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Normalize to target size for consistent text rendering
        # All posters will be resized to the same dimensions before adding overlays
        if img.size != target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)

        width, height = target_size

        # Normalize financial data
        box_office_norm = self.normalize_money(box_office)
        salary_norm = self.normalize_money(salary)
        budget_norm = self.normalize_money(budget)

        # Create and apply gradient overlay
        overlay = self._create_gradient_overlay(width, height)
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')
        draw = ImageDraw.Draw(img)

        # Load fonts
        fonts = self._load_fonts()

        # Draw title with shadow
        y_offset = height - 350
        self._draw_title_with_shadow(draw, title, year, y_offset, fonts)

        # Draw info boxes
        y_offset = height - 240
        current_x = 40

        # Character box (if available)
        if character and str(character).strip():
            box_width = self._draw_info_box(
                draw, "CHARACTER", str(character), current_x, y_offset,
                (100, 120, 150), fonts
            )
            current_x += box_width + self.box_spacing

        # Budget box
        if budget_norm:
            box_width = self._draw_info_box(
                draw, "BUDGET", budget_norm, current_x, y_offset,
                (70, 130, 180), fonts
            )
            current_x += box_width + self.box_spacing

        # Box Office box
        if box_office_norm:
            box_width = self._draw_info_box(
                draw, "BOX OFFICE", box_office_norm, current_x, y_offset,
                (100, 200, 150), fonts
            )
            current_x += box_width + self.box_spacing

        # Salary box
        if salary_norm:
            box_width = self._draw_info_box(
                draw, "PAYCHECK", salary_norm, current_x, y_offset,
                (255, 215, 0), fonts
            )
            current_x += box_width + self.box_spacing

        # IMDB rating box
        if imdb_rating and str(imdb_rating).strip() and str(imdb_rating).lower() != 'unknown':
            box_width = self._draw_info_box(
                draw, "IMDB", str(imdb_rating), current_x, y_offset,
                (245, 197, 24), fonts
            )
            current_x += box_width + self.box_spacing

        # Rotten Tomatoes box
        if rotten_tomatoes and str(rotten_tomatoes).strip() and str(rotten_tomatoes).lower() != 'unknown':
            self._draw_info_box(
                draw, "ROTTEN TOM.", str(rotten_tomatoes), current_x, y_offset,
                (250, 50, 10), fonts
            )

        # Save
        if output_path is None:
            output_path = poster_path
        img.save(output_path, quality=95)
        return output_path

    def batch_enhance_posters(self, csv_path, poster_column='poster_path', output_dir=None):
        """
        Enhance multiple posters from a CSV file

        Args:
            csv_path: Path to CSV with movie data
            poster_column: Column name containing poster paths
            output_dir: Directory to save enhanced posters (optional)

        Returns:
            List of enhanced poster paths
        """
        df = pd.read_csv(csv_path)
        df = df.sort_values('year')

        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        enhanced_posters = []

        for idx, row in df.iterrows():
            # Handle NaN or missing poster paths
            poster_path_value = row.get(poster_column, '')
            if pd.isna(poster_path_value) or not str(poster_path_value).strip():
                print(f"  [SKIP] No poster path: {row['title']}")
                continue

            original_poster = Path(str(poster_path_value))

            if not original_poster.exists():
                print(f"  [SKIP] Missing: {row['title']}")
                continue

            # Handle NaN values
            character = row.get('character', '')
            if pd.isna(character):
                character = ''

            box_office = row.get('box_office', '')
            if pd.isna(box_office):
                box_office = ''

            salary = row.get('salary', '')
            if pd.isna(salary):
                salary = ''

            imdb_rating = row.get('imdb_rating', '')
            if pd.isna(imdb_rating):
                imdb_rating = ''

            rotten_tomatoes = row.get('rotten_tomatoes', '')
            if pd.isna(rotten_tomatoes):
                rotten_tomatoes = ''

            budget = row.get('budget', '')
            if pd.isna(budget):
                budget = ''

            # Determine output path
            if output_dir:
                output_path = output_dir / f"{original_poster.stem}_enhanced.jpg"
            else:
                output_path = original_poster.parent / f"{original_poster.stem}_enhanced.jpg"

            print(f"  [{row['year']}] {row['title']}...", end=" ")

            try:
                self.enhance_poster(
                    poster_path=original_poster,
                    title=row['title'],
                    year=row['year'],
                    character=character,
                    box_office=box_office,
                    salary=salary,
                    imdb_rating=imdb_rating,
                    rotten_tomatoes=rotten_tomatoes,
                    budget=budget,
                    output_path=output_path
                )
                enhanced_posters.append(output_path)
                print("OK")
            except Exception as e:
                print(f"ERROR: {e}")

        return enhanced_posters
