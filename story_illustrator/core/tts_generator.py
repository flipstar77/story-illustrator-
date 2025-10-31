"""Text-to-Speech generation for voiceovers"""
from pathlib import Path
import subprocess


class TTSGenerator:
    """Handles text-to-speech generation for voiceovers"""

    def __init__(self, backend='kokoro', logger=None):
        """
        Args:
            backend: TTS backend to use ('kokoro', 'chatterbox', 'elevenlabs')
            logger: Callable that takes (message, level) for logging
        """
        self.backend = backend
        self.logger = logger or self._default_logger

    @staticmethod
    def _default_logger(message, level='INFO'):
        """Default logger that prints to console"""
        print(f"[{level}] {message}")

    def check_kokoro_available(self):
        """Check if Kokoro library is installed"""
        try:
            import kokoro
            return True
        except ImportError:
            return False

    def generate_with_kokoro(self, text, output_path, voice='af_bella', speed=1.0):
        """
        Generate speech using Kokoro-82M library

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            voice: Voice model to use
            speed: Speech speed multiplier

        Returns:
            Path to generated audio file, or None if failed
        """
        try:
            import kokoro
            import soundfile as sf

            self.logger(f"🎤 Generating voiceover with Kokoro ({voice})...", "INFO")

            # Generate audio
            audio_data, sample_rate = kokoro.generate(
                text=text,
                voice=voice,
                speed=speed
            )

            # Save to file
            output_path = Path(output_path)
            sf.write(str(output_path), audio_data, sample_rate)

            self.logger(f"✅ Voiceover generated: {output_path.name}", "SUCCESS")
            return output_path

        except Exception as e:
            self.logger(f"❌ Kokoro generation failed: {e}", "ERROR")
            return None

    def generate_with_chatterbox(self, text, output_path, chatterbox_path=None):
        """
        Generate speech using Chatterbox CLI

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            chatterbox_path: Path to Chatterbox executable

        Returns:
            Path to generated audio file, or None if failed
        """
        try:
            if chatterbox_path is None:
                # Try common locations
                possible_paths = [
                    "chatterbox.exe",
                    "C:\\Program Files\\Chatterbox\\chatterbox.exe",
                    "C:\\Program Files (x86)\\Chatterbox\\chatterbox.exe"
                ]
                for path in possible_paths:
                    if Path(path).exists():
                        chatterbox_path = path
                        break

            if not chatterbox_path or not Path(chatterbox_path).exists():
                self.logger("❌ Chatterbox not found!", "ERROR")
                return None

            self.logger("🎤 Generating voiceover with Chatterbox...", "INFO")

            # Write text to temp file
            text_file = Path(output_path).with_suffix('.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)

            # Run Chatterbox
            cmd = [str(chatterbox_path), '--input', str(text_file), '--output', str(output_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and Path(output_path).exists():
                self.logger(f"✅ Voiceover generated: {Path(output_path).name}", "SUCCESS")
                text_file.unlink()  # Clean up temp file
                return Path(output_path)
            else:
                self.logger(f"❌ Chatterbox failed: {result.stderr}", "ERROR")
                return None

        except Exception as e:
            self.logger(f"❌ Chatterbox generation failed: {e}", "ERROR")
            return None

    def generate(self, text, output_path, **kwargs):
        """
        Generate speech using configured backend

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            **kwargs: Backend-specific options

        Returns:
            Path to generated audio file, or None if failed
        """
        if self.backend == 'kokoro':
            return self.generate_with_kokoro(text, output_path, **kwargs)
        elif self.backend == 'chatterbox':
            return self.generate_with_chatterbox(text, output_path, **kwargs)
        else:
            self.logger(f"❌ Unknown TTS backend: {self.backend}", "ERROR")
            return None

    def generate_for_sections(self, sections, output_folder, voice='af_bella', speed=1.0):
        """
        Generate voiceovers for multiple sections

        Args:
            sections: List of section dicts with 'title' and 'text'
            output_folder: Folder to save audio files
            voice: Voice model to use (for Kokoro)
            speed: Speech speed multiplier

        Returns:
            Dict mapping section index to audio file path
        """
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)

        results = {}

        for i, section in enumerate(sections):
            self.logger(f"📝 Section {i+1}/{len(sections)}: {section['title']}", "INFO")

            # Generate filename
            audio_file = output_folder / f"section_{i+1:02d}_voiceover.wav"

            # Generate audio
            result = self.generate(
                text=section['text'],
                output_path=audio_file,
                voice=voice,
                speed=speed
            )

            results[i] = result

            if result:
                self.logger(f"✅ Section {i+1} complete", "SUCCESS")
            else:
                self.logger(f"❌ Section {i+1} failed", "ERROR")

        success_count = sum(1 for r in results.values() if r)
        self.logger(f"🎉 Generated {success_count}/{len(sections)} voiceovers", "SUCCESS")

        return results
