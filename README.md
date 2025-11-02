# Story Illustrator V3

A complete workflow tool for creating illustrated story videos with automated image generation, video rendering, multi-language subtitles, and AI-powered content creation.

## 🎯 Features

### Phase 1: Story Chunking
- **Manual Mode**: Copy prompt to ChatGPT for chunking
- **API Mode**: Automatic chunking using GPT-4o-mini (~$0.001-0.003 per story)
- Parses sections and creates folder structure
- Auto-saves projects for resuming later

### Phase 2: Image Generation
- **Browser Automation** (Legacy): PyAutoGUI-based automation for ChatGPT
- **ComfyUI Integration** (NEW): Local SDXL image generation via ComfyUI API
  - Automated workflow execution
  - Text overlay support (titles + data points)
  - Professional slideshow image generation
  - No browser automation needed

### Phase 3: Video Production
- FFmpeg-based video rendering with customizable settings
  - Image duration (1-30 seconds)
  - Transitions (crossfade, none)
  - Resolution (1080p, 720p, 4K)
  - FPS (15-60)
  - Music volume control
- Voiceover + background music mixing
- **Chatterbox TTS Integration**: Local text-to-speech generation
- **Audio compression** (auto-compress >25MB files for Whisper)
- **SRT subtitle generation** via OpenAI Whisper API
- Open videos folder and last video directly from UI
- Progress monitoring with detailed error logging

### Phase 4: Multi-Language Subtitles
- Translate SRT to 10 languages simultaneously
- Uses GPT-4o-mini for accurate translations
- Preserves timestamps and formatting
- Perfect for YouTube multi-language captions

### NEW: Actor Carousel Video Generator
**Automated social media content creation for actors & filmographies**

- **Universal Actor Enrichment** (`enrich_actor_data.py`)
  - Perplexity API research for any actor
  - Automatic IMDB ratings, Rotten Tomatoes scores, production budgets, and **actor salaries**
  - TMDB poster downloads with retry logic
  - Auto-saves progress after each movie
  - Works for any actor - just provide their folder name

- **Professional Poster Overlays** (`carousel_poster_enhancer.py`)
  - Uniform 2000x3000px sizing for consistent scrolling
  - **Smart title line-breaking** - automatically splits long titles at natural word breaks
  - Color-coded data boxes: Character (blue), Budget (sky blue), Box Office (green), Salary (gold), IMDB (yellow), RT (red)
  - Professional gradient overlays and shadows

- **Carousel Video Generation** (`carousel_video_generator.py`)
  - Smooth horizontal scrolling at 120 px/s (8.7s per poster)
  - Top/bottom overlay bars with actor name and film count
  - FFmpeg-based high-quality rendering
  - Automatic timestamp-based file management

- **TTS Narration System** (`tts_generator.py` + `narration_script_generator.py`)
  - 8 professional voice presets (documentary, storyteller, news, dramatic, calm, energetic, professional, conversational)
  - Voice cloning support using 10-15 second audio samples
  - Synchronized timing calculations for carousel scroll
  - Statistical summaries (intro/outro) with aggregate data
  - Movie-by-movie narration with character names, ratings, and box office

**Quick Start:**
```bash
python enrich_actor_data.py brad_pitt
# Enriches all 49 Brad Pitt movies, generates enhanced posters, creates carousel video
```

### NEW: Slideshow Video Generator
- **CSV-Driven Workflow**: Create slideshow videos from structured data
- **ComfyUI + SDXL**: Automated image generation with text overlays
- **Chatterbox TTS**: Narration generation for each slide
- **FFmpeg Assembly**: Professional video compilation
  - Semi-transparent overlay bars
  - Centered title and data text
  - Customizable slide durations

## 📁 Project Structure

```
story_illustrator/
├── story_illustrator_v3.py          # Main application (clean, 650 lines)
├── story_illustrator_v2.py          # Legacy monolithic version (1460 lines)
├── slideshow_generator.py           # Slideshow video generator
├── create_carousel_video.py         # Actor carousel video creator
├── enrich_actor_data.py             # Universal actor enrichment script
├── test_tts_narration.py            # TTS audio generation test
├── test_voices.py                   # Voice preset demonstration
├── story_illustrator/               # Modular components
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── project_manager.py      # Project save/load
│   │   ├── phase1_logic.py         # Story chunking
│   │   ├── phase2_logic.py         # Image automation
│   │   ├── phase3_logic.py         # Video rendering
│   │   ├── phase4_logic.py         # SRT translation
│   │   └── tts_generator.py        # Chatterbox TTS integration
│   └── utils/
│       ├── __init__.py
│       ├── config.py                # Configuration management
│       ├── api_keys.py              # API key management (Perplexity, TMDB)
│       ├── comfyui_client.py        # ComfyUI API client
│       ├── slideshow_image_generator.py  # SDXL + text overlays
│       ├── carousel_poster_enhancer.py   # Poster generation with ratings & smart title breaking
│       ├── carousel_video_generator.py   # Carousel video rendering with FFmpeg
│       ├── movie_poster_downloader.py    # TMDB poster fetching
│       ├── perplexity_researcher.py      # Perplexity API research
│       ├── narration_script_generator.py # Synchronized narration script generation
│       └── voice_manager.py              # Voice preset & library management
├── workflows/
│   └── sdxl_slideshow.json          # NEW: ComfyUI SDXL workflow template
├── examples/
│   └── sample_slideshow.csv         # NEW: Sample slideshow data
├── projects/                         # Saved projects (auto-created)
├── story_images/                     # Section folders with images
├── videos/                           # Rendered videos
└── output/
    └── actor_analysis/               # NEW: Actor research & carousel videos
        ├── johnny_depp/
        ├── tom_cruise/
        └── ...
```

## 🚀 Installation

### Requirements
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
pyautogui>=0.9.54
pyperclip>=1.9.0
openai>=1.0.0
pandas>=2.0.0
pillow>=10.0.0
requests>=2.31.0
websocket-client>=1.6.0
torch>=2.0.0  # For Chatterbox TTS (optional)
torchaudio>=2.0.0  # For Chatterbox TTS (optional)
```

### External Dependencies
- **FFmpeg**: Required for video rendering
  - Download: https://ffmpeg.org/download.html
  - Add to PATH or use: `C:\Users\Tobias\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe`

### Optional: ComfyUI Integration
- **ComfyUI**: For local SDXL image generation
  - Installed at: `C:\Users\Tobias\ComfyUI\`
  - Start server: `cd C:\Users\Tobias\ComfyUI && venv\Scripts\python.exe main.py`
  - Access UI: http://127.0.0.1:8188
  - Required model: `sd_xl_base_1.0.safetensors` (6.5GB)

### Optional: Chatterbox TTS
- **PyTorch + TorchAudio**: For local text-to-speech
  - Requires GPU with CUDA support (or CPU fallback)
  - Model downloads automatically on first use

### API Keys Required
- **OpenAI API Key**: For GPT-4o-mini (chunking, translation) and Whisper (SRT)
- **Perplexity API Key**: For actor research (optional)
- **TMDB API Key**: For movie poster downloads (optional)

## 📖 Usage

### Quick Start

```bash
python story_illustrator_v3.py
```

### Workflow

**Phase 1: Chunk Your Story**
1. Load a story text file
2. Option A: Click "Chunk via API" (automatic)
3. Option B: Click "Copy Prompt" → paste in ChatGPT → copy response → Phase 2
4. Project is auto-saved

**Phase 2: Generate Images**
1. Select your project from dropdown
2. Configure settings (images per section, delays)
3. Click "Start Automation"
4. Switch to browser, ChatGPT should be open
5. Script will automatically send prompts and "go on" commands
6. Download images manually to section folders

**Phase 3: Create Videos**
1. Select project and section
2. Enter OpenAI API key (for SRT generation)
3. Browse for voiceover audio (optional)
4. Browse for background music (optional)
5. Click "Render Video"
6. Video saved to `videos/` folder

**Phase 4: Multi-Language Subtitles**
1. Select SRT file (or use one from Phase 3)
2. Choose target languages
3. Click "Translate to All Languages"
4. Upload all SRT files to YouTube for multi-language support

## 🏗️ Architecture

### Modular Design

The codebase is split into logical modules:

**Core Logic Modules** (`story_illustrator/core/`):
- Each phase has its own module with focused responsibility
- Clean interfaces with logger injection
- No UI dependencies - pure business logic
- Easily testable and reusable

**Utility Modules** (`story_illustrator/utils/`):
- Configuration management with auto-save
- Shared helpers and constants

**Main Application** (`story_illustrator_v3.py`):
- Pure UI code using Tkinter
- Orchestrates modules
- Event handling and threading
- ~650 lines vs 1460 in monolithic version

### Key Design Patterns

1. **Separation of Concerns**: UI completely separated from logic
2. **Dependency Injection**: Loggers injected for flexibility
3. **Project-Based Workflow**: All work saved and resumable
4. **Threaded Operations**: Long-running tasks don't block UI
5. **Error Handling**: Comprehensive logging and user feedback

## 🔧 Configuration

Config is stored in `story_illustrator_v2_config.json`:

```json
{
  "openai_api_key": "sk-...",
  "phase1_prompt": "...",
  "last_project": "My_Story_20251030_123456"
}
```

Projects are stored in `projects/`:

```json
{
  "name": "My_Story_20251030_123456",
  "created": "2025-10-30T12:34:56",
  "sections": [
    {
      "title": "The Awakening",
      "text": "Full section text...",
      "folder": "story_images/section_01_The_Awakening"
    }
  ]
}
```

## 💡 Tips & Best Practices

### For Story Chunking
- **API Mode**: Fast, reliable, cheap (~$0.001 per story)
- **Manual Mode**: Use if API has issues or for more control

### For Image Generation
- Use delays of 120-180 seconds for ChatGPT to generate images
- Test with 1-2 sections first before running full automation
- Keep browser window focused during automation

### For Video Rendering
- **Audio Compression**: Automatic for files >25 MB (Whisper limit)
- **Subtitles**: Currently disabled in video, but SRT files generated for YouTube
- **Music Volume**: Default 30% - adjust as needed

### For Multi-Language SRT
- Cost: ~$0.002 for 10 languages (GPT-4o-mini is very cheap)
- Upload all SRT files to YouTube for automatic language selection
- Edit translations in YouTube Studio if needed

## 🐛 Known Issues

### Subtitle Burning (Windows)
**Issue**: FFmpeg's `subtitles` filter in `filter_complex` fails with non-ASCII paths on Windows (even with workarounds).

**Workaround**: SRT files are generated but not burned into video. Upload them separately to YouTube.

**Future Fix**: Two-pass rendering approach planned.

### API Chunking Timeout
**Issue**: Very large stories (>100K characters) may timeout.

**Workaround**: Split story into smaller parts or use manual mode.

## 📊 Performance

| Operation | Time | Cost |
|-----------|------|------|
| API Chunking (60K chars) | 20-60s | ~$0.002 |
| Image Generation (4 images) | ~10 min | Free (ChatGPT) |
| Video Rendering (4 images, 20s) | 30-60s | Free |
| SRT Generation (60 min audio) | 30-90s | ~$0.36 |
| Multi-Language SRT (10 langs) | 60-120s | ~$0.002 |

## 🔄 Migration Guide

### From V2 to V3

V3 is a complete rewrite with clean architecture:

**What's the Same:**
- All features work identically
- Projects are compatible
- UI layout is similar

**What's Different:**
- Codebase is modular and clean
- Easier to understand and modify
- Better error handling
- More maintainable

**Migration:**
```bash
# Your existing projects and config work with V3
python story_illustrator_v3.py

# V2 still works if needed
python story_illustrator_v2.py
```

## 🛠️ Development

### Adding New Features

**Example: Add new TTS backend**

1. Update `story_illustrator/core/tts_generator.py`:
```python
def generate_with_new_backend(self, text, output_path):
    # Implementation
    pass
```

2. Update main app UI:
```python
ttk.Button(frame, text="Generate TTS",
           command=self.generate_tts).pack()
```

3. Connect in main app:
```python
from story_illustrator.core.tts_generator import TTSGenerator

tts = TTSGenerator(backend='kokoro')
tts.generate(section['text'], output_path)
```

### Code Style

- **Functions**: Descriptive names, single responsibility
- **Classes**: Clear interfaces, dependency injection
- **Comments**: Explain why, not what
- **Logging**: All operations logged with levels (INFO, SUCCESS, ERROR, DEBUG)

## 📝 Changelog

### V3.0.0 (2025-10-30)
- ✨ Complete modular rewrite
- ✨ API-based story chunking
- ✨ Project save/load system
- ✨ Improved error logging
- ✨ Multi-language SRT translation
- 🐛 Fixed FFmpeg bracket stripping bug
- 🐛 Fixed API timeout issues
- 📚 Comprehensive documentation

### V2.0.0 (Previous)
- Initial monolithic version
- All 4 phases implemented
- PyAutoGUI automation
- FFmpeg video rendering

## 🤝 Contributing

Contributions welcome! The modular structure makes it easy:

1. Choose a module to improve
2. Write clean, documented code
3. Test thoroughly
4. Submit with clear description

## 📄 License

This project is provided as-is for educational and creative purposes.

## 🙏 Credits

- **FFmpeg**: Video processing
- **OpenAI**: GPT-4o-mini for chunking/translation, Whisper for SRT
- **PyAutoGUI**: Browser automation

## 📞 Support

For issues or questions:
1. Check "Known Issues" section
2. Review log output for errors
3. Ensure all dependencies installed
4. Test with simple story first

---

**Built with clean code principles • Easy to understand • Easy to extend**
