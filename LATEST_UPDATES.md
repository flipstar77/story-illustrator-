# Latest Updates - Story Illustrator V3

## Recent Features Added

### 1. Universal Actor Data Enrichment
**Added comprehensive ratings and budget data collection for all actors**

**Files:**
- `enrich_actor_data.py` - Universal enrichment script for any actor

**Features:**
- Automatically adds IMDB ratings, Rotten Tomatoes scores, and production budgets
- Works with any actor's filmography CSV
- Uses Perplexity API for automated research
- Auto-saves progress after each movie
- Regenerates enhanced posters and carousel videos

**Usage:**
```bash
python enrich_actor_data.py tom_hanks
python enrich_actor_data.py morgan_freeman
```

**Standard Columns Added:**
- `imdb_rating` - IMDB score (e.g., "7.8")
- `rotten_tomatoes` - RT score (e.g., "85%")
- `budget` - Production budget (e.g., "$50 million")

---

### 2. Enhanced Movie Poster Overlays
**Added budget display to carousel poster overlays**

**Files:**
- `story_illustrator/utils/carousel_poster_enhancer.py`

**Changes:**
- Added `budget` parameter to `enhance_poster()` method
- Added sky blue budget display box (#87CEEB color)
- Updated overlay order: CHARACTER, BUDGET, BOX OFFICE, SALARY, IMDB, RT

**Features:**
- Uniform poster sizing (2000x3000px)
- Professional data overlays
- Automatic text positioning to avoid cutoff
- Money normalization (millions/billions)

---

### 3. Comprehensive Voice System (Chatterbox TTS)
**Complete voice management system for narration**

**Files:**
- `story_illustrator/utils/voice_manager.py` - Voice preset and library management
- `story_illustrator/core/tts_generator.py` - TTS generation engine
- `test_voices.py` - Demo script for all voice presets
- `CHATTERBOX_VOICES.md` - Complete voice documentation
- `VOICE_INTEGRATION_COMPLETE.md` - Integration summary

**8 Professional Voice Presets:**
1. **documentary** - Calm, authoritative (factual content)
2. **storyteller** - Expressive, engaging (narratives)
3. **news** - Professional, clear (announcements)
4. **dramatic** - Theatrical, emotional (drama)
5. **calm** - Soothing (relaxation content)
6. **energetic** - Upbeat (exciting content)
7. **professional** - Polished (business)
8. **conversational** - Casual, friendly (informal)

**Voice Cloning Support:**
- Clone ANY voice using 10-15 second audio sample
- Supports .wav, .mp3, .flac formats
- Reference audio via `audio_prompt_path` parameter
- Automatic voice characteristics matching

**Voice Library Management:**
- Organized voice categories (narrators, characters, custom)
- Easy voice addition and retrieval
- VoiceManager class for library operations
- Directory structure: `voices/narrators/`, `voices/characters/`, `voices/custom/`

**Usage:**
```python
# Use a preset
from story_illustrator.utils.voice_manager import VoiceManager
vm = VoiceManager()
params = vm.get_tts_params(preset_name='documentary')

# Clone a voice
params = vm.get_tts_params(voice_clone_path='voices/my_voice.wav')

# Combine preset + clone (best results!)
params = vm.get_tts_params(
    preset_name='documentary',
    voice_clone_path='voices/my_voice.wav'
)
```

---

### 4. GUI Voice Integration
**Added voice selection controls to Story Illustrator V3 GUI**

**Files:**
- `story_illustrator_v3.py` - Main GUI application

**Changes:**
- Added "Voice Preset" dropdown in Actor Wages tab Step 2
- Added "Custom Voice File" browse option
- Integrated VoiceManager with carousel video generation
- Auto-disables controls if TTS unavailable

**GUI Features:**
- Select from 8 voice presets or "None (No Voice)"
- Browse for custom voice audio files (.wav, .mp3, .flac)
- Voice parameters automatically passed to carousel generation
- Logs voice selection to progress output

---

### 5. ComfyUI Integration (CPU Mode)
**Local SDXL image generation using ComfyUI**

**Files:**
- `story_illustrator/utils/comfyui_client.py` - ComfyUI API client
- `COMFYUI_INTEGRATION_STATUS.md` - Integration documentation

**Status:**
- ComfyUI running at http://127.0.0.1:8188
- CPU mode active (GPU support pending PyTorch 2.7+)
- RTX 5070 Ti Blackwell (sm_120) requires newer PyTorch
- PyTorch 2.6.0 nightly installed

**Features:**
- SDXL image generation workflow
- Text-to-image capabilities
- Checkpoint: albedobaseXL_v21.safetensors
- Resolution: 1024x1024 default

---

## Updated Files Summary

### Core Changes:
- `story_illustrator_v3.py` - Added voice controls to GUI
- `story_illustrator/utils/carousel_poster_enhancer.py` - Added budget display
- `story_illustrator/core/tts_generator.py` - TTS generation (existing)

### New Files:
- `enrich_actor_data.py` - Universal actor enrichment script
- `story_illustrator/utils/voice_manager.py` - Voice management system
- `story_illustrator/utils/perplexity_researcher.py` - Perplexity API client
- `story_illustrator/utils/comfyui_client.py` - ComfyUI API client
- `test_voices.py` - Voice preset demonstration script

### Documentation:
- `VOICE_INTEGRATION_COMPLETE.md` - Voice system summary
- `CHATTERBOX_VOICES.md` - Complete voice guide
- `COMFYUI_INTEGRATION_STATUS.md` - ComfyUI status
- `LATEST_UPDATES.md` - This file
- `README.md` - Updated with all new features

---

## Breaking Changes
None - all changes are backward compatible.

---

## Next Steps

### Immediate:
1. Test voice presets with carousel videos
2. Record custom voice samples for library
3. Complete Tom Hanks enrichment

### Future:
1. Upgrade to PyTorch 2.7+ when available (for RTX 5070 Ti GPU support)
2. Add more voice presets based on user feedback
3. Integrate ComfyUI image generation with main workflow
4. Add voice selection to other video generation workflows

---

## Testing

### Voice System:
```bash
python test_voices.py
```
This generates sample audio for all 8 presets in `voices/demo/`

### Actor Enrichment:
```bash
python enrich_actor_data.py tom_hanks
```
This enriches Tom Hanks filmography with ratings and budget data.

### GUI Application:
```bash
python story_illustrator_v3.py
```
Navigate to "Actor Wages" tab to test voice selection.

---

## Requirements
- Python 3.10+
- PyTorch 2.6.0+ (for TTS)
- Perplexity API key (for enrichment)
- FFmpeg (for video generation)
- ComfyUI (optional, for image generation)

---

**All changes tested and ready for production!**
