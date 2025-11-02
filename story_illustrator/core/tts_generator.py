"""Text-to-Speech generation using Chatterbox TTS"""
from pathlib import Path
from typing import Optional, Union


class TTSGenerator:
    """Handles text-to-speech generation with Chatterbox"""

    def __init__(self, logger=None, device=None):
        """
        Args:
            logger: Callable that takes (message, level) for logging
            device: Device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.logger = logger or self._default_logger
        self.model = None
        self.device = device or self._auto_detect_device()
        self.torch = None
        self.ta = None

    @staticmethod
    def _default_logger(message, level='INFO'):
        """Default logger that prints to console"""
        print(f"[{level}] {message}")

    def _auto_detect_device(self):
        """Auto-detect best available device"""
        try:
            import torch
            self.torch = torch
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        except:
            return "cpu"

    def load_model(self):
        """Load Chatterbox TTS model (lazy loading)"""
        if self.model is None:
            try:
                self.logger(f"🔄 Loading Chatterbox TTS model on {self.device}...", "INFO")
                from chatterbox.tts import ChatterboxTTS
                self.model = ChatterboxTTS.from_pretrained(device=self.device)
                self.logger("✅ Chatterbox TTS model loaded successfully!", "SUCCESS")
            except Exception as e:
                self.logger(f"❌ Failed to load Chatterbox TTS: {e}", "ERROR")
                raise
        return self.model

    def generate_audio(self,
                      text: str,
                      output_path: Union[str, Path],
                      audio_prompt_path: Optional[str] = None,
                      exaggeration: float = 0.5,
                      temperature: float = 0.8,
                      cfg_weight: float = 0.5,
                      min_p: float = 0.05,
                      top_p: float = 1.0,
                      repetition_penalty: float = 1.2) -> bool:
        """
        Generate speech audio from text

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file (.wav)
            audio_prompt_path: Optional reference audio for voice cloning
            exaggeration: Voice exaggeration (0.25-2.0, default 0.5)
            temperature: Sampling temperature (0.05-5.0, default 0.8)
            cfg_weight: Classifier-free guidance weight (0.0-1.0, default 0.5)
            min_p: Min-p sampling threshold (0.0-1.0, default 0.05)
            top_p: Top-p sampling threshold (0.0-1.0, default 1.0)
            repetition_penalty: Repetition penalty (1.0-2.0, default 1.2)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load model if not already loaded
            model = self.load_model()

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self.logger(f"🎙️ Generating speech for text: {text[:50]}...", "INFO")

            # Generate audio
            wav = model.generate(
                text,
                audio_prompt_path=audio_prompt_path,
                exaggeration=exaggeration,
                temperature=temperature,
                cfg_weight=cfg_weight,
                min_p=min_p,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
            )

            # Save audio
            if self.ta is None:
                import torchaudio as ta
                self.ta = ta
            self.ta.save(str(output_path), wav, model.sr)

            self.logger(f"✅ Audio saved to: {output_path}", "SUCCESS")
            return True

        except Exception as e:
            self.logger(f"❌ TTS generation failed: {e}", "ERROR")
            return False

    def generate_narration_for_sections(self,
                                       sections: list,
                                       output_dir: Union[str, Path],
                                       combine: bool = True,
                                       audio_prompt_path: Optional[str] = None,
                                       **tts_params) -> Optional[Path]:
        """
        Generate narration audio for multiple story sections

        Args:
            sections: List of text sections to narrate
            output_dir: Directory to save audio files
            combine: If True, combine all sections into one audio file
            audio_prompt_path: Optional reference audio for voice cloning
            **tts_params: Additional parameters for TTS generation

        Returns:
            Path to combined audio file if combine=True, else None
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            audio_files = []

            # Generate audio for each section
            for i, section_text in enumerate(sections, 1):
                section_path = output_dir / f"section_{i:03d}.wav"

                self.logger(f"📝 Generating audio for section {i}/{len(sections)}", "INFO")

                success = self.generate_audio(
                    text=section_text,
                    output_path=section_path,
                    audio_prompt_path=audio_prompt_path,
                    **tts_params
                )

                if success:
                    audio_files.append(section_path)
                else:
                    self.logger(f"⚠️ Failed to generate audio for section {i}", "WARNING")

            if not audio_files:
                self.logger("❌ No audio files generated", "ERROR")
                return None

            # Combine audio files if requested
            if combine and len(audio_files) > 1:
                return self._combine_audio_files(audio_files, output_dir / "combined_narration.wav")
            elif combine and len(audio_files) == 1:
                return audio_files[0]
            else:
                self.logger(f"✅ Generated {len(audio_files)} audio files", "SUCCESS")
                return None

        except Exception as e:
            self.logger(f"❌ Narration generation failed: {e}", "ERROR")
            return None

    def _combine_audio_files(self, audio_files: list, output_path: Path) -> Optional[Path]:
        """Combine multiple audio files into one"""
        try:
            self.logger(f"🔗 Combining {len(audio_files)} audio files...", "INFO")

            # Load all audio files
            waveforms = []
            sample_rate = None

            for audio_file in audio_files:
                waveform, sr = ta.load(str(audio_file))
                if sample_rate is None:
                    sample_rate = sr
                elif sr != sample_rate:
                    # Resample if necessary
                    resampler = ta.transforms.Resample(sr, sample_rate)
                    waveform = resampler(waveform)

                waveforms.append(waveform)

            # Concatenate waveforms
            combined = torch.cat(waveforms, dim=1)

            # Save combined audio
            ta.save(str(output_path), combined, sample_rate)

            self.logger(f"✅ Combined audio saved to: {output_path}", "SUCCESS")
            return output_path

        except Exception as e:
            self.logger(f"❌ Audio combination failed: {e}", "ERROR")
            return None
