"""
Carousel Video Generation Module
Handles creating horizontal scrolling carousel videos from enhanced posters
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class CarouselVideoGenerator:
    """Generates horizontal scrolling carousel videos with overlays"""

    def __init__(self, ffmpeg_path=None):
        """
        Initialize video generator

        Args:
            ffmpeg_path: Path to ffmpeg executable (optional, uses default if not provided)
        """
        self.ffmpeg_path = ffmpeg_path or r'C:\Users\Tobias\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe'
        self.video_width = 1920
        self.video_height = 1080
        self.fps = 30
        self.scroll_speed = 120  # pixels per second

    def create_horizontal_strip(self, poster_paths, spacing=40, background_color=(20, 20, 30), max_height=1500, force_regenerate=False):
        """
        Create a horizontal strip image from posters

        Args:
            poster_paths: List of paths to poster images
            spacing: Space between posters in pixels
            background_color: RGB tuple for background
            max_height: Maximum height for posters (default 1500px to avoid huge images)
            force_regenerate: If True, delete old strip file and create new one

        Returns:
            Tuple of (strip_path, strip_dimensions)
        """
        if not poster_paths:
            raise ValueError("No poster paths provided")

        # First pass: find the dimensions to use (normalize all posters to same height)
        target_height = max_height
        poster_dimensions = []

        for poster_path in poster_paths:
            img = Image.open(poster_path)
            width, height = img.size

            # Calculate width when scaled to target height
            if height > target_height:
                scale = target_height / height
                scaled_width = int(width * scale)
            elif height < target_height:
                # Also scale up smaller images to target height for uniformity
                scale = target_height / height
                scaled_width = int(width * scale)
            else:
                scaled_width = width

            poster_dimensions.append((scaled_width, target_height))

        # Calculate canvas size based on actual scaled dimensions
        total_width = sum(w for w, h in poster_dimensions) + spacing * (len(poster_paths) + 1)
        canvas_height = target_height

        print(f"  Target poster height: {target_height}px (all posters will be scaled to this height)")
        print(f"  Canvas size: {total_width}x{canvas_height} pixels")

        # Create canvas
        canvas = Image.new('RGB', (total_width, canvas_height), color=background_color)

        # Second pass: paste all posters with uniform sizing
        x_offset = spacing
        for poster_path, (target_width, target_height_val) in zip(poster_paths, poster_dimensions):
            img = Image.open(poster_path)
            # Resize to exact target dimensions
            img = img.resize((target_width, target_height_val), Image.Resampling.LANCZOS)
            canvas.paste(img, (x_offset, 0))
            x_offset += target_width + spacing

        # Save strip (use PNG for large dimensions, JPEG has 65500px limit)
        # Use unique filename if force_regenerate to avoid locked files
        if force_regenerate:
            import time
            timestamp = int(time.time())
            strip_path = Path(poster_paths[0]).parent / f"carousel_strip_{timestamp}.png"
        else:
            strip_path = Path(poster_paths[0]).parent / "carousel_strip.png"

        canvas.save(strip_path)
        print(f"  Saved strip: {strip_path}")

        return strip_path, (total_width, canvas_height)

    def create_video_overlay(self, actor_name, total_movies):
        """
        Create top and bottom overlay bars for video

        Args:
            actor_name: Name to display in top bar
            total_movies: Number of movies to display in bottom bar

        Returns:
            PIL Image object with overlay
        """
        overlay = Image.new('RGBA', (self.video_width, self.video_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Load fonts
        try:
            title_font = ImageFont.truetype("arialbd.ttf", 58)
            subtitle_font = ImageFont.truetype("arial.ttf", 36)
        except:
            try:
                title_font = ImageFont.truetype("arial.ttf", 58)
                subtitle_font = ImageFont.truetype("arial.ttf", 36)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

        # Top bar with gradient
        top_bar_height = 100
        for i in range(top_bar_height):
            alpha = int(200 * (1 - i / top_bar_height))
            draw.rectangle(
                [(0, i), (self.video_width, i + 1)],
                fill=(5, 10, 20, alpha)
            )

        # Actor name in top bar
        actor_text = f"{actor_name.upper()} FILMOGRAPHY"
        text_bbox = draw.textbbox((0, 0), actor_text, font=title_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (self.video_width - text_width) // 2

        # Draw text shadow
        draw.text((text_x + 2, 22), actor_text, fill='#000000', font=title_font)
        draw.text((text_x, 20), actor_text, fill='#FFD700', font=title_font)

        # Bottom bar with gradient
        bottom_bar_height = 80
        bottom_start = self.video_height - bottom_bar_height
        for i in range(bottom_bar_height):
            alpha = int(200 * (i / bottom_bar_height))
            draw.rectangle(
                [(0, bottom_start + i), (self.video_width, bottom_start + i + 1)],
                fill=(5, 10, 20, alpha)
            )

        # Movie count in bottom bar
        count_text = f"{total_movies} MOVIES"
        count_bbox = draw.textbbox((0, 0), count_text, font=subtitle_font)
        count_width = count_bbox[2] - count_bbox[0]
        count_x = (self.video_width - count_width) // 2

        draw.text((count_x + 1, bottom_start + 26), count_text, fill='#000000', font=subtitle_font)
        draw.text((count_x, bottom_start + 25), count_text, fill='#CCCCCC', font=subtitle_font)

        return overlay

    def generate_video(self, strip_path, strip_dimensions, overlay_path, output_path, duration=None):
        """
        Generate carousel video with FFmpeg

        Args:
            strip_path: Path to horizontal strip image
            strip_dimensions: Tuple of (width, height) of strip
            overlay_path: Path to overlay image
            output_path: Where to save output video
            duration: Video duration in seconds (optional, auto-calculated if not provided)

        Returns:
            True if successful, False otherwise
        """
        total_width, poster_height = strip_dimensions

        # Calculate scaled dimensions
        scale_factor = self.video_height / poster_height
        scaled_width = int(total_width * scale_factor)

        # Calculate duration
        if duration is None:
            scroll_distance = scaled_width - self.video_width
            duration = scroll_distance / self.scroll_speed

        print(f"\nVideo settings:")
        print(f"  - Original strip: {total_width}x{poster_height}")
        print(f"  - Scaled strip: {scaled_width}x{self.video_height}")
        print(f"  - Output resolution: {self.video_width}x{self.video_height}")
        print(f"  - Scroll speed: {self.scroll_speed} pixels/second")
        print(f"  - Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"  - FPS: {self.fps}")
        print(f"  - Direction: Right to Left")

        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-loop', '1',
            '-i', str(strip_path),
            '-loop', '1',
            '-i', str(overlay_path),
            '-filter_complex',
            f"[0:v]scale=-1:{self.video_height},crop={self.video_width}:{self.video_height}:'min(iw-{self.video_width},(iw-{self.video_width})*t/{duration})':0[bg];[bg][1:v]overlay=0:0:format=auto",
            '-t', str(duration),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '23',
            '-r', str(self.fps),
            str(output_path)
        ]

        print("\nRunning ffmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("\n" + "=" * 70)
            print("SUCCESS!")
            print("=" * 70)
            print(f"Carousel video created: {output_path}")
            print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print("=" * 70)
            return True
        else:
            print(f"\nERROR: ffmpeg failed")
            print(result.stderr[-1000:])
            return False

    def create_carousel_from_posters(self, poster_paths, actor_name, output_path, force_regenerate=True):
        """
        Complete workflow: create carousel video from poster list

        Args:
            poster_paths: List of paths to enhanced posters
            actor_name: Actor name for overlay
            output_path: Where to save output video
            force_regenerate: If True, create new strip files with unique names

        Returns:
            True if successful, False otherwise
        """
        print("=" * 70)
        print(f"CREATING CAROUSEL VIDEO FOR {actor_name.upper()}")
        print("=" * 70)

        # Step 1: Create horizontal strip
        print("\nStep 1: Creating horizontal strip image...")
        strip_path, strip_dimensions = self.create_horizontal_strip(poster_paths, force_regenerate=force_regenerate)

        # Step 2: Create video overlay
        print("\nStep 2: Creating video overlay with top/bottom bars...")
        overlay_img = self.create_video_overlay(actor_name, len(poster_paths))
        # Use unique overlay filename if force_regenerate
        if force_regenerate:
            import time
            timestamp = int(time.time())
            overlay_path = Path(strip_path).parent / f"video_overlay_{timestamp}.png"
        else:
            overlay_path = Path(strip_path).parent / "video_overlay.png"
        overlay_img.save(overlay_path)
        print(f"  Saved overlay: {overlay_path}")

        # Step 3: Generate video
        print("\nStep 3: Creating carousel video with horizontal scroll and overlay...")
        success = self.generate_video(strip_path, strip_dimensions, overlay_path, output_path)

        if success:
            print("\nEnhanced features:")
            print("  [OK] Professional rounded info boxes with borders")
            print("  [OK] Text shadows for better readability")
            print("  [OK] Top bar with actor name")
            print("  [OK] Bottom bar with movie count")
            print("  [OK] Darker gradient overlays")
            print("=" * 70)

        return success
