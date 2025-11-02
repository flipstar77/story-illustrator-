# Chatterbox TTS Voice Guide

Complete guide to using different voices with Chatterbox TTS in Story Illustrator.

## Available Voice Options

### 1. Default Pre-trained Voices

Chatterbox comes with built-in speaker embeddings. You can use different voice characteristics by adjusting parameters:

**Voice Parameters:**
- `exaggeration` (0.25-2.0): Voice expressiveness
  - 0.25-0.5: Calm, neutral narrator
  - 0.5-1.0: Normal conversational (default)
  - 1.0-2.0: Dramatic, expressive

- `temperature` (0.05-5.0): Pronunciation variation
  - 0.05-0.5: Very consistent, robotic
  - 0.5-1.0: Natural variation (default 0.8)
  - 1.0-5.0: More creative, less consistent

**Example Presets:**
```python
# Documentary Narrator (calm, authoritative)
{
    "exaggeration": 0.4,
    "temperature": 0.6,
    "cfg_weight": 0.7
}

# Storyteller (expressive, engaging)
{
    "exaggeration": 1.2,
    "temperature": 1.0,
    "cfg_weight": 0.5
}

# News Anchor (professional, clear)
{
    "exaggeration": 0.5,
    "temperature": 0.7,
    "cfg_weight": 0.6
}

# Dramatic Reader (theatrical, emotional)
{
    "exaggeration": 1.8,
    "temperature": 1.2,
    "cfg_weight": 0.4
}
```

### 2. Voice Cloning (Custom Voices)

Clone ANY voice using a reference audio sample!

**Requirements:**
- Audio file: .wav, .mp3, or .flac
- Duration: 5-30 seconds (optimal: 10-15 seconds)
- Quality: Clear speech, minimal background noise
- Content: Natural speech (not reading, just talking)

**How to Use:**
```python
from story_illustrator.core.tts_generator import TTSGenerator

tts = TTSGenerator()
tts.generate_audio(
    text="Your narration text here",
    output_path="output.wav",
    audio_prompt_path="voices/my_voice.wav"  # Your reference audio
)
```

**Tips for Best Results:**
- Use high-quality recordings (44.1kHz or 48kHz)
- Record in a quiet environment
- Speak naturally, not reading
- Include variety in pitch and tone
- Avoid music or sound effects

### 3. Pre-made Voice Samples

You can download professional voice samples or create your own library:

**Recommended Sources:**
1. **Record your own voices** - Best results, fully customizable
2. **Professional voice actors** - Hire for custom samples
3. **Free voice datasets** - LibriVox, Common Voice
4. **Text-to-speech samples** - Use other TTS for reference

**Voice Library Structure:**
```
story-illustrator/
└── voices/
    ├── narrators/
    │   ├── male_deep_narrator.wav
    │   ├── female_warm_narrator.wav
    │   └── neutral_documentary.wav
    ├── characters/
    │   ├── old_wise_man.wav
    │   ├── young_energetic.wav
    │   └── mysterious_villain.wav
    └── custom/
        └── my_voice.wav
```

## Using Voices in Story Illustrator

### Method 1: Command Line

When generating carousel videos:
```bash
python create_carousel_video.py --voice-preset storyteller
python create_carousel_video.py --voice-clone voices/narrator.wav
```

### Method 2: Python Code

```python
from story_illustrator.utils.carousel_video_generator import CarouselVideoGenerator

generator = CarouselVideoGenerator()

# Use preset
generator.create_carousel_from_csv(
    csv_path="actor_data.csv",
    voice_preset="documentary"
)

# Use custom voice
generator.create_carousel_from_csv(
    csv_path="actor_data.csv",
    voice_clone_path="voices/my_narrator.wav"
)
```

### Method 3: Via GUI (Story Illustrator V3)

Coming soon - voice selection dropdown in Phase 3!

## Voice Preset Library

### Built-in Presets

| Preset Name | Use Case | Exaggeration | Temperature | CFG Weight |
|------------|----------|--------------|-------------|------------|
| `documentary` | Facts, information | 0.4 | 0.6 | 0.7 |
| `storyteller` | Fiction, narratives | 1.2 | 1.0 | 0.5 |
| `news` | News, announcements | 0.5 | 0.7 | 0.6 |
| `dramatic` | Theatrical content | 1.8 | 1.2 | 0.4 |
| `calm` | Meditation, relaxation | 0.3 | 0.5 | 0.8 |
| `energetic` | Exciting content | 1.5 | 1.1 | 0.5 |
| `professional` | Business, corporate | 0.6 | 0.7 | 0.7 |
| `conversational` | Casual, friendly | 0.9 | 0.9 | 0.5 |

## Creating Your Own Voice Samples

### Recording Tips

1. **Equipment:**
   - USB microphone (Blue Yeti, Rode NT-USB, etc.)
   - Quiet room with soft furnishings
   - Pop filter (reduces plosives)

2. **Recording Settings:**
   - Sample rate: 44.1kHz or 48kHz
   - Bit depth: 16-bit or 24-bit
   - Format: WAV (uncompressed)

3. **What to Say:**
   - Speak naturally for 10-15 seconds
   - Include variety: statements, questions, emotions
   - Avoid: reading lists, monotone, artificial voices

**Example Script for Recording:**
> "Hey there! I'm excited to share this story with you. It's a fascinating journey through time, filled with incredible moments and unexpected twists. Let's dive in!"

### Processing Your Sample

```python
# Script to prepare voice samples
from story_illustrator.utils.voice_processor import prepare_voice_sample

prepare_voice_sample(
    input_path="raw_recording.wav",
    output_path="voices/my_voice.wav",
    trim_silence=True,
    normalize=True,
    target_duration=12  # seconds
)
```

## Advanced: Multiple Voices

For complex projects with multiple characters:

```python
voices = {
    "narrator": "voices/documentary_narrator.wav",
    "character_a": "voices/old_man.wav",
    "character_b": "voices/young_woman.wav"
}

# Generate different parts with different voices
for section, voice_path in voices.items():
    tts.generate_audio(
        text=scripts[section],
        output_path=f"audio/{section}.wav",
        audio_prompt_path=voice_path
    )
```

## Troubleshooting

### Voice Sounds Distorted
- **Cause:** Exaggeration too high
- **Fix:** Reduce exaggeration to 0.5-1.0

### Voice Too Robotic
- **Cause:** Temperature too low
- **Fix:** Increase temperature to 0.8-1.2

### Voice Keeps Repeating Words
- **Cause:** Repetition penalty too low
- **Fix:** Increase repetition_penalty to 1.5-2.0

### Cloned Voice Doesn't Sound Like Sample
- **Cause:** Poor quality reference audio
- **Fix:**
  - Use longer sample (10-15 seconds)
  - Record in quiet environment
  - Speak naturally, not reading
  - Use high-quality microphone

## Examples

### Example 1: Movie Documentary

```python
tts = TTSGenerator()

# Professional documentary style
tts.generate_audio(
    text="Tom Hanks began his career in 1980...",
    output_path="narration.wav",
    exaggeration=0.4,
    temperature=0.6,
    cfg_weight=0.7
)
```

### Example 2: Story Time

```python
# Expressive storytelling
tts.generate_audio(
    text="Once upon a time, in a land far away...",
    output_path="story.wav",
    exaggeration=1.3,
    temperature=1.1,
    cfg_weight=0.5
)
```

### Example 3: Custom Voice Clone

```python
# Clone Morgan Freeman's voice (with permission/sample)
tts.generate_audio(
    text="Welcome to the actor carousel experience.",
    output_path="intro.wav",
    audio_prompt_path="voices/morgan_freeman_sample.wav",
    exaggeration=0.6,
    temperature=0.8
)
```

## Next Steps

1. **Download Chatterbox voices** from Hugging Face (automatic on first use)
2. **Record custom voice samples** for your projects
3. **Experiment with presets** to find your preferred style
4. **Build a voice library** for different content types

## Resources

- Chatterbox TTS: https://github.com/resemble-ai/Chatterbox
- Voice Recording Guide: https://wiki.audacityteam.org/wiki/Recording_Tips
- Free Voice Datasets: https://commonvoice.mozilla.org/

---

**Pro Tip:** The best voice is one that matches your content! Documentary content works well with calm, authoritative voices, while entertainment content shines with expressive, energetic narration.
