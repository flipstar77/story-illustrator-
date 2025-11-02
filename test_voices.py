"""
Test script to demonstrate Chatterbox TTS voice capabilities
Shows all presets and how to use custom voices
"""

from story_illustrator.utils.voice_manager import VoiceManager, VoicePreset
from story_illustrator.core.tts_generator import TTSGenerator
from pathlib import Path


def demo_voice_presets():
    """Demonstrate all voice presets"""
    print("=" * 70)
    print("CHATTERBOX TTS VOICE PRESETS DEMO")
    print("=" * 70)

    test_text = "Welcome to the actor carousel. This is a demonstration of different voice styles."

    output_dir = Path("voices/demo")
    output_dir.mkdir(parents=True, exist_ok=True)

    tts = TTSGenerator()

    print("\nGenerating samples for each preset...\n")

    for preset_name in VoicePreset.get_preset_names():
        preset = VoicePreset.get_preset(preset_name)

        print(f"[{preset_name.upper()}]")
        print(f"  {preset['description']}")
        print(f"  Exaggeration: {preset['exaggeration']}, Temperature: {preset['temperature']}")

        output_path = output_dir / f"preset_{preset_name}.wav"

        try:
            # Get TTS parameters (remove description fields)
            tts_params = {k: v for k, v in preset.items()
                         if k not in ['name', 'description']}

            tts.generate_audio(
                text=test_text,
                output_path=output_path,
                **tts_params
            )
            print(f"  Saved: {output_path}")

        except Exception as e:
            print(f"  ERROR: {e}")

        print()

    print("=" * 70)
    print(f"All voice samples saved to: {output_dir}")
    print("=" * 70)


def demo_voice_cloning():
    """Demonstrate voice cloning"""
    print("\n" + "=" * 70)
    print("VOICE CLONING DEMO")
    print("=" * 70)

    vm = VoiceManager()

    # List available custom voices
    voices = vm.list_voices()

    if not voices:
        print("\nNo custom voices found yet.")
        print(f"Add voice samples to: {vm.voices_dir}")
        print("\nExample: Place a 10-15 second voice recording as:")
        print(f"  {vm.voices_dir}/narrators/my_narrator.wav")
        return

    print("\nAvailable Custom Voices:")
    for name, path in voices.items():
        print(f"  - {name}: {path}")

    print("\nTo use a custom voice:")
    print("""
    tts = TTSGenerator()
    tts.generate_audio(
        text="Your text here",
        output_path="output.wav",
        audio_prompt_path="voices/narrators/my_narrator.wav"
    )
    """)


def demo_combined_approach():
    """Demonstrate combining preset with voice clone"""
    print("\n" + "=" * 70)
    print("COMBINED APPROACH: Preset + Voice Clone")
    print("=" * 70)

    print("""
You can combine a voice preset with voice cloning for best results:

    from story_illustrator.utils.voice_manager import VoiceManager

    vm = VoiceManager()
    params = vm.get_tts_params(
        preset_name='documentary',        # Use documentary preset
        voice_clone_path='voices/narrator.wav',  # Clone this voice
        exaggeration=0.6                   # Override exaggeration
    )

    tts = TTSGenerator()
    tts.generate_audio(
        text="Your narration",
        output_path="output.wav",
        **params
    )

This gives you the voice characteristics from the clone, with the
emotional tone and pacing from the preset!
    """)


def create_voice_library_guide():
    """Show how to build a voice library"""
    print("\n" + "=" * 70)
    print("BUILDING YOUR VOICE LIBRARY")
    print("=" * 70)

    print("""
Recommended Voice Library Structure:

voices/
├── narrators/
│   ├── documentary_male.wav      # Deep, authoritative male voice
│   ├── documentary_female.wav    # Clear, professional female voice
│   ├── storyteller_warm.wav      # Warm, engaging narrator
│   └── news_anchor.wav            # Crisp, neutral news voice
│
├── characters/
│   ├── old_wise_man.wav          # Elderly, wise character
│   ├── young_energetic.wav       # Young, enthusiastic character
│   ├── villain_mysterious.wav    # Dark, mysterious antagonist
│   └── hero_confident.wav        # Confident, strong protagonist
│
└── custom/
    ├── my_voice.wav               # Your own voice
    ├── friend_voice.wav           # Friend's voice (with permission)
    └── professional_vo.wav        # Hired voice actor sample

Tips for Recording Voice Samples:
1. Duration: 10-15 seconds of natural speech
2. Quality: Use a good USB microphone in a quiet room
3. Content: Speak naturally, not reading - just talking
4. Format: WAV file, 44.1kHz or 48kHz, 16-bit
5. Variety: Include different emotions and pitch variations

Example Recording Script:
"Hey there! I'm excited to tell you about this. It's really fascinating
how all of this came together. There are so many interesting details to
explore. Let me walk you through the whole story!"
    """)


if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print(" " * 15 + "CHATTERBOX TTS VOICE SYSTEM")
    print("=" * 70)

    demo_voice_presets()
    demo_voice_cloning()
    demo_combined_approach()
    create_voice_library_guide()

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
1. Run this script to generate preset samples:
   python test_voices.py

2. Record or find voice samples and add them to voices/ folder

3. Use voices in carousel videos:
   python create_carousel_video.py --voice-preset documentary
   python create_carousel_video.py --voice-clone voices/my_voice.wav

4. Check CHATTERBOX_VOICES.md for complete documentation
    """)
    print("=" * 70)
