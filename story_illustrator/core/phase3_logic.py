"""Phase 3: Video production with FFmpeg"""
import subprocess
from pathlib import Path


class VideoRenderer:
    """Handles video rendering with FFmpeg"""

    def __init__(self, logger=None):
        """
        Args:
            logger: Callable that takes (message, level) for logging
        """
        self.logger = logger or self._default_logger

    @staticmethod
    def _default_logger(message, level='INFO'):
        """Default logger that prints to console"""
        print(f"[{level}] {message}")

    def check_ffmpeg(self):
        """Check if ffmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except Exception:
            return False

    def compress_audio(self, audio_path, target_size_mb=20):
        """
        Compress audio file to meet size limit (e.g., for Whisper API)

        Args:
            audio_path: Path to audio file
            target_size_mb: Target size in megabytes

        Returns:
            Path to compressed file, or None if failed
        """
        audio_path = Path(audio_path)
        compressed_path = audio_path.with_stem(audio_path.stem + "_compressed")

        try:
            self.logger("🗜️ Compressing audio with ffmpeg...", "INFO")

            # Check ffmpeg availability
            if not self.check_ffmpeg():
                self.logger("❌ ffmpeg not found! Please install ffmpeg.", "ERROR")
                return None

            # Get audio duration
            probe_cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(audio_path)
            ]

            try:
                duration_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
                duration_sec = float(duration_result.stdout.strip())

                # Calculate target bitrate dynamically
                target_size_bytes = target_size_mb * 1024 * 1024
                target_bitrate = int((target_size_bytes * 8) / duration_sec)  # bits per second
                target_bitrate_k = max(16, min(64, target_bitrate // 1000))  # Clamp 16-64 kbps

                self.logger(f"📊 Audio duration: {duration_sec:.1f}s, target bitrate: {target_bitrate_k}k", "DEBUG")
            except Exception:
                # Fallback to conservative bitrate
                target_bitrate_k = 24
                self.logger(f"⚠️ Could not determine duration, using {target_bitrate_k}k", "DEBUG")

            # Compress audio
            cmd = [
                'ffmpeg', '-y', '-i', str(audio_path),
                '-ab', f'{target_bitrate_k}k',  # Dynamic bitrate
                '-ac', '1',     # Mono
                '-ar', '16000',  # Lower sample rate (Whisper optimized)
                '-map', '0:a',
                str(compressed_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                compressed_size_mb = compressed_path.stat().st_size / (1024 * 1024)
                self.logger(f"✓ Compressed to {compressed_size_mb:.1f} MB", "SUCCESS")
                return compressed_path
            else:
                self.logger(f"❌ Compression failed: {result.stderr}", "ERROR")
                return None

        except Exception as e:
            self.logger(f"❌ Compression error: {e}", "ERROR")
            return None

    def build_ffmpeg_command(self, image_files, duration, transition, transition_duration,
                            resolution, fps, voiceover, srt, music, music_volume, output_file):
        """
        Build ffmpeg command for video rendering

        Args:
            image_files: List of image file paths
            duration: Duration per image in seconds
            transition: Transition type ('crossfade' or 'none')
            transition_duration: Transition duration in seconds
            resolution: Video resolution (e.g., '1920x1080')
            fps: Frames per second
            voiceover: Path to voiceover audio file (optional)
            srt: Path to SRT subtitle file (optional, currently disabled)
            music: Path to background music file (optional)
            music_volume: Music volume (0.0 to 1.0)
            output_file: Path for output video file

        Returns:
            List of command arguments for ffmpeg
        """
        cmd = ['ffmpeg', '-y']  # -y to overwrite

        # Image inputs with loop
        for img in image_files:
            cmd.extend(['-loop', '1', '-i', str(img)])

        # Audio inputs
        audio_inputs = []
        if voiceover and Path(voiceover).exists():
            cmd.extend(['-i', str(voiceover)])
            audio_inputs.append('voiceover')

        if music and Path(music).exists():
            cmd.extend(['-i', str(music)])
            audio_inputs.append('music')

        # Filter complex for transitions and effects
        filter_parts = []

        # Scale, pad, and create video streams with constant framerate
        width, height = resolution.split('x')
        total_frames = int(duration * fps)

        for i in range(len(image_files)):
            # Create constant framerate video stream
            # Using format+fps to ensure CFR, then trim to exact frame count
            filter_parts.append(
                f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,"
                f"fps=fps={fps},trim=start_frame=0:end_frame={total_frames}[v{i}]"
            )

        # Apply transitions
        if transition == "crossfade" and len(image_files) > 1:
            # Crossfade between images
            current = "[v0]"
            for i in range(1, len(image_files)):
                # Calculate offset: (duration - transition_duration) for each clip
                offset = duration - transition_duration
                filter_parts.append(
                    f"{current}[v{i}]xfade=transition=fade:"
                    f"duration={transition_duration}:"
                    f"offset={offset}[v{i}out]"
                )
                current = f"[v{i}out]"
            video_output = current
        else:
            # Simple concatenation
            video_inputs = "".join([f"[v{i}]" for i in range(len(image_files))])
            filter_parts.append(f"{video_inputs}concat=n={len(image_files)}:v=1:a=0[vout]")
            video_output = "[vout]"

        # Audio mixing
        if audio_inputs:
            audio_idx = len(image_files)
            if len(audio_inputs) == 2:  # Both voiceover and music
                filter_parts.append(
                    f"[{audio_idx}:a]volume=1.0[voice];"
                    f"[{audio_idx+1}:a]volume={music_volume}[music];"
                    f"[voice][music]amix=inputs=2:duration=longest[aout]"
                )
                cmd.extend(['-filter_complex', ';'.join(filter_parts)])
                cmd.extend(['-map', video_output, '-map', '[aout]'])
            else:  # Just one audio
                cmd.extend(['-filter_complex', ';'.join(filter_parts)])
                cmd.extend(['-map', video_output, '-map', f'{audio_idx}:a'])
        else:
            cmd.extend(['-filter_complex', ';'.join(filter_parts)])
            cmd.extend(['-map', video_output])

        # TODO: Subtitles temporarily disabled - will fix in next update
        # The issue is that subtitles need to be in filter_complex BEFORE it's added to cmd

        # Output settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p'
        ])

        # Audio encoding (if audio present)
        if audio_inputs:
            cmd.extend(['-c:a', 'aac', '-b:a', '192k'])

        cmd.append(str(output_file))

        return cmd

    def render_video(self, image_files, output_file, duration=5, transition='crossfade',
                    transition_duration=1, resolution='1920x1080', fps=30,
                    voiceover=None, srt=None, music=None, music_volume=0.3):
        """
        Render video from images with optional audio

        Args:
            image_files: List of image file paths
            output_file: Path for output video
            duration: Duration per image in seconds
            transition: Transition type
            transition_duration: Transition duration
            resolution: Video resolution
            fps: Frames per second
            voiceover: Optional voiceover audio path
            srt: Optional SRT subtitle path (currently disabled)
            music: Optional background music path
            music_volume: Music volume (0.0-1.0)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger("Building ffmpeg command...", "INFO")

            cmd = self.build_ffmpeg_command(
                image_files, duration, transition, transition_duration,
                resolution, fps, voiceover, srt, music, music_volume, output_file
            )

            self.logger("Running ffmpeg...", "INFO")
            self.logger(f"Command: {' '.join(cmd[:5])}...", "DEBUG")

            # Run ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitor progress and collect all stderr
            stderr_output = []
            for line in process.stderr:
                stderr_output.append(line)
                if "frame=" in line or "time=" in line:
                    self.logger(line.strip(), "DEBUG")

            process.wait()

            if process.returncode == 0:
                self.logger(f"✅ Video rendered successfully!", "SUCCESS")
                self.logger(f"📁 Saved to: {output_file}", "SUCCESS")
                return True
            else:
                # Join all stderr lines for error message
                full_error = ''.join(stderr_output) if stderr_output else "Unknown error - no output from ffmpeg"
                self.logger(f"❌ ffmpeg failed with return code {process.returncode}", "ERROR")
                # Log last 20 lines of error for debugging
                error_lines = full_error.strip().split('\n')
                for line in error_lines[-20:]:
                    self.logger(line, "ERROR")
                return False

        except Exception as e:
            self.logger(f"❌ Render error: {e}", "ERROR")
            return False
