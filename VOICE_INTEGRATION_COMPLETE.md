# Voice Integration Complete!

## What's Been Added

### 1. Voice Preset System ✅

**8 Professional Voice Presets:**
- `documentary` - Calm, authoritative for factual content
- `storyteller` - Expressive, engaging for narratives
- `news` - Professional, clear for announcements
- `dramatic` - Theatrical, emotional for drama
- `calm` - Soothing for relaxation content
- `energetic` - Upbeat for exciting content
- `professional` - Polished for business
- `conversational` - Casual, friendly for informal content

### 2. Voice Cloning Support ✅

- Clone ANY voice using a 10-15 second audio sample
- Reference audio support via `audio_prompt_path`
- Automatic voice characteristics matching
- Works with .wav, .mp3, .flac files

### 3. Voice Library Management ✅

**VoiceManager Class:**
- Organize voices in categories (narrators, characters, custom)
- List available voices
- Add new voices to library
- Get voice paths easily

**Directory Structure:**
```
voices/
├── narrators/     # Professional narrator voices
├── characters/    # Character voices for stories
└── custom/        # Your custom recordings
```

## Files Created

1. **[story_illustrator/utils/voice_manager.py](story_illustrator/utils/voice_manager.py)**
   - VoicePreset class with 8 presets
   - VoiceManager for custom voice management
   - Helper functions for easy integration

2. **[CHATTERBOX_VOICES.md](CHATTERBOX_VOICES.md)**
   - Complete voice guide
   - Recording tips
   - Usage examples
   - Troubleshooting

3. **[test_voices.py](test_voices.py)**
   - Demo script for all presets
   - Voice cloning examples
   - Library setup guide

## How to Use

### Quick Start - Use a Preset

```python
from story_illustrator.core.tts_generator import TTSGenerator
from story_illustrator.utils.voice_manager import VoiceManager

# Get parameters for a preset
vm = VoiceManager()
params = vm.get_tts_params(preset_name='documentary')

# Generate audio
tts = TTSGenerator()
tts.generate_audio(
    text="Tom Hanks began his career in 1980...",
    output_path="narration.wav",
    **params
)
```

### Voice Cloning

```python
# Clone a specific voice
params = vm.get_tts_params(
    voice_clone_path='voices/narrators/my_narrator.wav'
)

tts.generate_audio(
    text="Custom narration in cloned voice",
    output_path="output.wav",
    **params
)
```

### Combined Approach (Best Results!)

```python
# Use preset + voice clone
params = vm.get_tts_params(
    preset_name='documentary',  # Emotional tone from preset
    voice_clone_path='voices/my_voice.wav',  # Voice from clone
    exaggeration=0.6  # Custom override
)

tts.generate_audio(
    text="Best of both worlds!",
    output_path="output.wav",
    **params
)
```

## Integration with Carousel Videos

### Option 1: Command Line (Coming Soon)

```bash
python create_carousel_video.py --voice-preset documentary
python create_carousel_video.py --voice-clone voices/narrator.wav
```

### Option 2: Python Code

```python
from story_illustrator.utils.carousel_video_generator import CarouselVideoGenerator
from story_illustrator.utils.voice_manager import VoiceManager

vm = VoiceManager()
generator = CarouselVideoGenerator()

# Get voice parameters
voice_params = vm.get_tts_params(preset_name='documentary')

# Create carousel with custom voice
generator.create_carousel_from_csv(
    csv_path="actor_data.csv",
    enhanced_posters_dir="enhanced_posters/",
    voice_params=voice_params  # Pass voice configuration
)
```

## Recording Your Own Voices

### Equipment Needed
- USB microphone (Blue Yeti, Rode NT-USB, etc.)
- Quiet room
- Pop filter (optional but recommended)

### Recording Settings
- Format: WAV
- Sample rate: 44.1kHz or 48kHz
- Bit depth: 16-bit
- Duration: 10-15 seconds
- Content: Natural speech, not reading

### Example Recording Script
```
"Hey there! I'm excited to tell you about this fascinating story.
It's a journey through time with incredible moments and unexpected
twists. There are so many interesting details to explore. Let me
walk you through the whole adventure!"
```

### Adding to Library

```python
from story_illustrator.utils.voice_manager import VoiceManager

vm = VoiceManager()
vm.add_voice(
    source_path="my_recording.wav",
    voice_name="documentary_narrator",
    category="narrators"
)
```

## Testing the System

Run the test script to generate samples of all presets:

```bash
python test_voices.py
```

This creates demo samples in `voices/demo/` showing each preset's characteristics.

## Available Presets Details

| Preset | Exaggeration | Temperature | Best For |
|--------|--------------|-------------|----------|
| documentary | 0.4 | 0.6 | Facts, educational content |
| storyteller | 1.2 | 1.0 | Fiction, narratives |
| news | 0.5 | 0.7 | News, announcements |
| dramatic | 1.8 | 1.2 | Theatrical content |
| calm | 0.3 | 0.5 | Meditation, relaxation |
| energetic | 1.5 | 1.1 | Exciting, upbeat content |
| professional | 0.6 | 0.7 | Business, corporate |
| conversational | 0.9 | 0.9 | Casual, friendly chat |

## Next Steps

1. **Download Chatterbox Model** (automatic on first use)
   - Happens when you first run TTS
   - ~1-2 GB download from Hugging Face

2. **Test Presets**
   ```bash
   python test_voices.py
   ```

3. **Record Custom Voices**
   - Follow recording guide above
   - Add to `voices/` folder

4. **Use in Carousel Videos**
   - Tom Hanks enrichment will complete soon
   - Regenerate with voice narration
   - Test different voice styles!

## Troubleshooting

### "Voice sounds robotic"
- **Fix:** Increase temperature to 0.8-1.2

### "Voice too expressive"
- **Fix:** Reduce exaggeration to 0.3-0.6

### "Cloned voice doesn't match sample"
- **Fix:** Use longer sample (10-15 sec), better quality recording

### "Words repeating"
- **Fix:** Increase repetition_penalty to 1.5-2.0

## Summary

You now have:
- ✅ 8 professional voice presets
- ✅ Voice cloning capability
- ✅ Voice library management
- ✅ Complete documentation
- ✅ Test scripts
- ✅ Integration with Story Illustrator

**Everything is ready to generate professional narration for your carousel videos!**

---

For complete details, see:
- [CHATTERBOX_VOICES.md](CHATTERBOX_VOICES.md) - Full voice guide
- [test_voices.py](test_voices.py) - Demo script
- [story_illustrator/utils/voice_manager.py](story_illustrator/utils/voice_manager.py) - Source code
