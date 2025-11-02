"""
Test TTS audio generation for carousel narration
"""

from story_illustrator.core.tts_generator import TTSGenerator
from story_illustrator.utils.voice_manager import VoiceManager
from pathlib import Path

# Test text (Brad Pitt intro)
test_text = "Brad Pitt. 49 films spanning 1989 to 2025. Total box office: 7.6 billion dollars."

print("=" * 70)
print("TESTING TTS AUDIO GENERATION")
print("=" * 70)

# Initialize TTS
print("\n1. Loading TTS engine...")
tts = TTSGenerator()

# Get voice parameters
print("2. Loading documentary voice preset...")
vm = VoiceManager()
voice_params = vm.get_tts_params(preset_name='documentary')

print(f"   Voice parameters: {voice_params}")

# Generate audio
output_path = Path("voices/test/brad_pitt_intro.wav")
output_path.parent.mkdir(parents=True, exist_ok=True)

print(f"\n3. Generating audio...")
print(f"   Text: {test_text}")
print(f"   Output: {output_path}")

success = tts.generate_audio(
    text=test_text,
    output_path=output_path,
    **voice_params
)

if success:
    print("\n" + "=" * 70)
    print("SUCCESS! Audio generated")
    print("=" * 70)
    print(f"File: {output_path}")
    print(f"Size: {output_path.stat().st_size} bytes")
else:
    print("\nERROR: Audio generation failed")
