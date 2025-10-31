"""Phase 4: Multi-language SRT translation"""
from pathlib import Path


class SRTTranslator:
    """Handles multi-language SRT translation using OpenAI"""

    def __init__(self, api_key, logger=None):
        """
        Args:
            api_key: OpenAI API key
            logger: Callable that takes (message, level) for logging
        """
        self.api_key = api_key
        self.logger = logger or self._default_logger

    @staticmethod
    def _default_logger(message, level='INFO'):
        """Default logger that prints to console"""
        print(f"[{level}] {message}")

    def translate_srt(self, srt_path, target_languages):
        """
        Translate SRT file to multiple languages

        Args:
            srt_path: Path to original SRT file
            target_languages: List of language codes (e.g., ['de', 'es', 'fr'])

        Returns:
            Dictionary mapping language codes to output file paths
            {
                'de': Path('subtitle_de.srt'),
                'es': Path('subtitle_es.srt'),
                ...
            }
        """
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            srt_path = Path(srt_path)

            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()

            self.logger(f"📖 Original SRT: {len(srt_content)} chars", "INFO")

            results = {}

            for lang_code in target_languages:
                self.logger(f"🔄 Translating to {lang_code}...", "INFO")

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": f"Translate this SRT subtitle file to {lang_code}. "
                                          f"Keep timestamps and format exactly the same. Only translate the text."
                            },
                            {
                                "role": "user",
                                "content": srt_content
                            }
                        ]
                    )

                    translated = response.choices[0].message.content

                    output_path = srt_path.with_stem(f"{srt_path.stem}_{lang_code}")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(translated)

                    self.logger(f"✅ {lang_code}: {output_path.name}", "SUCCESS")
                    results[lang_code] = output_path

                except Exception as e:
                    self.logger(f"❌ {lang_code} failed: {e}", "ERROR")
                    results[lang_code] = None

            self.logger("🎉 Translation complete!", "SUCCESS")
            return results

        except Exception as e:
            self.logger(f"❌ Translation error: {e}", "ERROR")
            return {}


class WhisperTranscriber:
    """Handles speech-to-text transcription using OpenAI Whisper API"""

    def __init__(self, api_key, logger=None):
        """
        Args:
            api_key: OpenAI API key
            logger: Callable that takes (message, level) for logging
        """
        self.api_key = api_key
        self.logger = logger or self._default_logger

    @staticmethod
    def _default_logger(message, level='INFO'):
        """Default logger that prints to console"""
        print(f"[{level}] {message}")

    def transcribe_to_srt(self, audio_path):
        """
        Transcribe audio file to SRT format using Whisper API

        Args:
            audio_path: Path to audio file

        Returns:
            Path to generated SRT file, or None if failed
        """
        try:
            from openai import OpenAI
            import httpx

            # Create client with 10-minute timeout (Whisper can take a while for long audio)
            client = OpenAI(
                api_key=self.api_key,
                timeout=httpx.Timeout(600.0, connect=30.0)  # 10 min total, 30s connect
            )
            audio_path = Path(audio_path)

            self.logger(f"🎤 Transcribing: {audio_path.name}", "INFO")

            # Check file size (Whisper has 25 MB limit)
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
            self.logger(f"📊 Audio file size: {file_size_mb:.1f} MB", "INFO")

            if file_size_mb > 25:
                self.logger(f"⚠️ File too large ({file_size_mb:.1f} MB > 25 MB limit)", "ERROR")
                self.logger("Please compress the audio first using Phase 3's compression feature", "INFO")
                return None

            # Transcribe with Whisper
            self.logger("⏳ Uploading to Whisper API... (this may take a few minutes)", "INFO")
            with open(audio_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="srt"
                )

            # Save SRT
            srt_path = audio_path.with_suffix('.srt')
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(transcript)

            self.logger(f"✅ SRT generated successfully!", "SUCCESS")
            self.logger(f"📁 Saved to: {srt_path}", "SUCCESS")

            return srt_path

        except Exception as e:
            self.logger(f"❌ Whisper failed: {e}", "ERROR")

            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                self.logger("Invalid API Key! Get your API key at: https://platform.openai.com/api-keys", "ERROR")
            elif "file" in error_msg.lower() or "format" in error_msg.lower():
                self.logger("Audio file error! Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm", "ERROR")

            return None
