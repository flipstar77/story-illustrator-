"""
Voice Management for Chatterbox TTS
Handles voice presets, custom voices, and voice cloning
"""

from pathlib import Path
from typing import Dict, Optional, Union


class VoicePreset:
    """Predefined voice configurations"""

    PRESETS = {
        "documentary": {
            "name": "Documentary Narrator",
            "description": "Calm, authoritative voice for factual content",
            "exaggeration": 0.4,
            "temperature": 0.6,
            "cfg_weight": 0.7,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.2
        },
        "storyteller": {
            "name": "Storyteller",
            "description": "Expressive, engaging voice for narratives",
            "exaggeration": 1.2,
            "temperature": 1.0,
            "cfg_weight": 0.5,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.2
        },
        "news": {
            "name": "News Anchor",
            "description": "Professional, clear voice for announcements",
            "exaggeration": 0.5,
            "temperature": 0.7,
            "cfg_weight": 0.6,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.3
        },
        "dramatic": {
            "name": "Dramatic Reader",
            "description": "Theatrical, emotional voice for dramatic content",
            "exaggeration": 1.8,
            "temperature": 1.2,
            "cfg_weight": 0.4,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.1
        },
        "calm": {
            "name": "Calm Speaker",
            "description": "Soothing voice for relaxation content",
            "exaggeration": 0.3,
            "temperature": 0.5,
            "cfg_weight": 0.8,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.4
        },
        "energetic": {
            "name": "Energetic Host",
            "description": "Upbeat voice for exciting content",
            "exaggeration": 1.5,
            "temperature": 1.1,
            "cfg_weight": 0.5,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.2
        },
        "professional": {
            "name": "Professional Speaker",
            "description": "Polished voice for business content",
            "exaggeration": 0.6,
            "temperature": 0.7,
            "cfg_weight": 0.7,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.3
        },
        "conversational": {
            "name": "Conversational",
            "description": "Casual, friendly voice for informal content",
            "exaggeration": 0.9,
            "temperature": 0.9,
            "cfg_weight": 0.5,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.2
        }
    }

    @classmethod
    def get_preset(cls, preset_name: str) -> Dict:
        """Get voice preset parameters by name"""
        if preset_name not in cls.PRESETS:
            raise ValueError(
                f"Unknown preset: {preset_name}. "
                f"Available: {', '.join(cls.PRESETS.keys())}"
            )
        return cls.PRESETS[preset_name].copy()

    @classmethod
    def list_presets(cls) -> Dict[str, Dict]:
        """Get all available presets"""
        return cls.PRESETS.copy()

    @classmethod
    def get_preset_names(cls) -> list:
        """Get list of preset names"""
        return list(cls.PRESETS.keys())


class VoiceManager:
    """Manages custom voice samples and voice cloning"""

    def __init__(self, voices_dir: Union[str, Path] = None):
        """
        Initialize voice manager

        Args:
            voices_dir: Directory containing voice samples (default: project_root/voices)
        """
        if voices_dir is None:
            # Default to project root/voices
            project_root = Path(__file__).parent.parent.parent
            voices_dir = project_root / "voices"

        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.voices_dir / "narrators").mkdir(exist_ok=True)
        (self.voices_dir / "characters").mkdir(exist_ok=True)
        (self.voices_dir / "custom").mkdir(exist_ok=True)

    def list_voices(self, category: Optional[str] = None) -> Dict[str, Path]:
        """
        List available voice samples

        Args:
            category: Optional category filter ('narrators', 'characters', 'custom', or None for all)

        Returns:
            Dictionary mapping voice name to file path
        """
        voices = {}

        if category:
            search_dir = self.voices_dir / category
            if not search_dir.exists():
                return {}

            for voice_file in search_dir.glob("*.wav"):
                voices[voice_file.stem] = voice_file
        else:
            # Search all categories
            for category_dir in ["narrators", "characters", "custom"]:
                cat_path = self.voices_dir / category_dir
                if cat_path.exists():
                    for voice_file in cat_path.glob("*.wav"):
                        voices[f"{category_dir}/{voice_file.stem}"] = voice_file

        return voices

    def get_voice_path(self, voice_name: str, category: str = "custom") -> Optional[Path]:
        """
        Get path to a voice sample

        Args:
            voice_name: Name of the voice (without .wav extension)
            category: Category ('narrators', 'characters', 'custom')

        Returns:
            Path to voice file or None if not found
        """
        voice_path = self.voices_dir / category / f"{voice_name}.wav"

        if voice_path.exists():
            return voice_path

        # Try finding in all categories
        all_voices = self.list_voices()
        for name, path in all_voices.items():
            if voice_name in name:
                return path

        return None

    def add_voice(self, source_path: Union[str, Path],
                  voice_name: str,
                  category: str = "custom",
                  overwrite: bool = False) -> Path:
        """
        Add a new voice sample to the library

        Args:
            source_path: Path to source audio file
            voice_name: Name for the voice
            category: Category to save in
            overwrite: Whether to overwrite existing voice

        Returns:
            Path to saved voice file
        """
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        dest_path = self.voices_dir / category / f"{voice_name}.wav"

        if dest_path.exists() and not overwrite:
            raise FileExistsError(
                f"Voice '{voice_name}' already exists in category '{category}'. "
                f"Use overwrite=True to replace."
            )

        # Copy file
        import shutil
        shutil.copy2(source_path, dest_path)

        return dest_path

    @staticmethod
    def get_tts_params(preset_name: Optional[str] = None,
                      voice_clone_path: Optional[Union[str, Path]] = None,
                      **custom_params) -> Dict:
        """
        Get TTS parameters for voice generation

        Args:
            preset_name: Name of voice preset to use
            voice_clone_path: Path to voice sample for cloning
            **custom_params: Override any parameters

        Returns:
            Dictionary of TTS parameters
        """
        params = {}

        # Start with preset if specified
        if preset_name:
            params = VoicePreset.get_preset(preset_name)
            # Remove non-TTS fields
            params.pop('name', None)
            params.pop('description', None)

        # Add voice cloning if specified
        if voice_clone_path:
            params['audio_prompt_path'] = str(voice_clone_path)

        # Override with custom parameters
        params.update(custom_params)

        return params


def create_voice_manager(voices_dir: Optional[Union[str, Path]] = None) -> VoiceManager:
    """Factory function to create VoiceManager instance"""
    return VoiceManager(voices_dir)


def get_voice_presets() -> Dict[str, Dict]:
    """Get all available voice presets"""
    return VoicePreset.list_presets()


def get_voice_preset(preset_name: str) -> Dict:
    """Get specific voice preset"""
    return VoicePreset.get_preset(preset_name)


# Example usage
if __name__ == "__main__":
    # List all presets
    print("Available Voice Presets:")
    print("=" * 70)
    for name, config in VoicePreset.list_presets().items():
        print(f"\n{name.upper()}")
        print(f"  Name: {config['name']}")
        print(f"  Description: {config['description']}")
        print(f"  Exaggeration: {config['exaggeration']}")
        print(f"  Temperature: {config['temperature']}")

    # Voice manager
    print("\n" + "=" * 70)
    print("Custom Voices:")
    print("=" * 70)

    vm = VoiceManager()
    voices = vm.list_voices()

    if voices:
        for name, path in voices.items():
            print(f"  {name}: {path}")
    else:
        print("  No custom voices found.")
        print(f"  Add voices to: {vm.voices_dir}")
