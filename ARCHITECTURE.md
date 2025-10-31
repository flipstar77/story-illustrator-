# Story Illustrator - Architecture Documentation

## Overview

Story Illustrator has evolved from a monolithic application (V2) to a clean, modular architecture (V3).

## Code Comparison

### V2 (Monolithic)
```
story_illustrator_v2.py - 1,466 lines
├── All UI code mixed with business logic
├── Hard to test individual components
├── Difficult to understand flow
└── Hard to extend or modify
```

### V3 (Modular)
```
story_illustrator_v3.py - 650 lines (UI only)
story_illustrator/
├── core/ - 860 lines total (business logic)
│   ├── project_manager.py - 130 lines
│   ├── phase1_logic.py - 90 lines
│   ├── phase2_logic.py - 160 lines
│   ├── phase3_logic.py - 280 lines
│   ├── phase4_logic.py - 150 lines
│   └── tts_generator.py - 180 lines
└── utils/ - 50 lines (helpers)
    └── config.py - 50 lines

Total: 1,560 lines (vs 1,466 in V2)
But: Clean separation, testable, maintainable
```

## Module Responsibilities

### `story_illustrator_v3.py` (Main App)
**Purpose**: UI orchestration only
- Creates Tkinter interface
- Handles user events
- Delegates logic to modules
- Manages threading for long operations

**What it DOESN'T do:**
- Parse stories
- Generate prompts
- Render videos
- Translate SRT files

### `core/project_manager.py`
**Purpose**: Project persistence
- Save/load project JSON files
- List available projects
- Generate project names
- Manage project metadata

**Interface:**
```python
manager = ProjectManager()
manager.save_project(name, sections)
project = manager.load_project(name)
projects = manager.list_projects()
```

### `core/phase1_logic.py`
**Purpose**: Story parsing and chunking
- Parse ChatGPT responses into sections
- Generate chunking prompts
- Create folder structure
- Sanitize filenames

**Interface:**
```python
chunker = StoryChunker(logger=log_func)
sections = chunker.parse_sections(text)
prompt = chunker.generate_chunking_prompt(story)
```

### `core/phase2_logic.py`
**Purpose**: Image generation automation
- Generate prompts for sections
- Send commands via PyAutoGUI
- Handle "go on" automation
- Track progress

**Interface:**
```python
generator = ImageGenerator(logger=log_func)
generator.automate_all_sections(
    sections,
    images_per_section=4,
    delay_after_prompt=150
)
```

### `core/phase3_logic.py`
**Purpose**: Video rendering with FFmpeg
- Build ffmpeg commands
- Render videos with transitions
- Mix audio (voiceover + music)
- Compress audio for Whisper API
- Monitor progress

**Interface:**
```python
renderer = VideoRenderer(logger=log_func)
success = renderer.render_video(
    image_files,
    output_file,
    voiceover=audio_path,
    music=music_path
)
```

### `core/phase4_logic.py`
**Purpose**: SRT translation
- Translate SRT to multiple languages
- Generate SRT from audio (Whisper API)
- Preserve timing and formatting

**Interface:**
```python
translator = SRTTranslator(api_key, logger=log_func)
results = translator.translate_srt(srt_path, ['de', 'es', 'fr'])

transcriber = WhisperTranscriber(api_key, logger=log_func)
srt_path = transcriber.transcribe_to_srt(audio_path)
```

### `core/tts_generator.py`
**Purpose**: Text-to-speech generation (future)
- Support multiple TTS backends
- Generate voiceovers for sections
- Handle different voice models

**Interface:**
```python
tts = TTSGenerator(backend='kokoro', logger=log_func)
audio_path = tts.generate(text, output_path, voice='af_bella')
```

### `utils/config.py`
**Purpose**: Configuration management
- Load/save config JSON
- Get/set individual values
- Auto-save on changes

**Interface:**
```python
config = ConfigManager()
api_key = config.get('openai_api_key', '')
config.set('openai_api_key', 'sk-...')
```

## Design Principles

### 1. Separation of Concerns
- **UI** (story_illustrator_v3.py): User interaction only
- **Logic** (core/): Business logic, no UI dependencies
- **Utilities** (utils/): Shared helpers

### 2. Dependency Injection
All modules accept a `logger` function:
```python
def logger(message, level='INFO'):
    # Can log to console, file, or UI widget
    pass

module = SomeModule(logger=logger)
```

This makes modules:
- Testable (inject mock logger)
- Flexible (log to different targets)
- Reusable (no UI coupling)

### 3. Single Responsibility
Each module does ONE thing well:
- `project_manager` = project persistence
- `phase1_logic` = story parsing
- `phase3_logic` = video rendering
- etc.

### 4. Clear Interfaces
All modules have simple, documented interfaces:
```python
class VideoRenderer:
    def __init__(self, logger=None):
        """Initialize renderer with optional logger"""

    def render_video(self, image_files, output_file, **options):
        """Render video - returns True/False"""
```

### 5. Error Handling
All operations:
- Log errors with context
- Return success/failure indicators
- Provide actionable error messages

## Data Flow

### Phase 1: Story → Sections
```
User Input (story text)
    ↓
StoryChunker.generate_chunking_prompt()
    ↓
OpenAI API (or manual ChatGPT)
    ↓
StoryChunker.parse_sections()
    ↓
ProjectManager.save_project()
    ↓
Sections ready for Phase 2
```

### Phase 2: Sections → Images
```
ProjectManager.load_project()
    ↓
ImageGenerator.automate_all_sections()
    ↓
For each section:
    - Generate prompt
    - Send via PyAutoGUI
    - Wait for images
    ↓
Manual image download
```

### Phase 3: Images → Video
```
Select section folder
    ↓
VideoRenderer.render_video()
    ↓
Build ffmpeg command:
    - Scale/pad images
    - Apply transitions
    - Mix audio
    ↓
Execute ffmpeg
    ↓
Video file created
```

### Phase 4: SRT → Multi-Language SRT
```
SRT file input
    ↓
SRTTranslator.translate_srt()
    ↓
For each target language:
    - Call GPT-4o-mini
    - Preserve formatting
    - Save translated SRT
    ↓
Multiple SRT files ready
```

## Threading Model

Long operations run in background threads:

```python
def start_long_operation(self):
    thread = threading.Thread(
        target=self._worker,
        args=(params,),
        daemon=True
    )
    thread.start()

def _worker(self, params):
    try:
        # Long operation
        result = module.do_work(params)

        # Update UI (thread-safe)
        self.log("Done!", "SUCCESS")
    except Exception as e:
        self.log(f"Error: {e}", "ERROR")
```

**Thread-safe operations:**
- Logging to UI widgets
- Showing messageboxes
- Updating progress

## Testing Strategy

### Unit Tests (modules)
Each module can be tested independently:

```python
def test_story_chunker():
    logger_calls = []
    def mock_logger(msg, level):
        logger_calls.append((msg, level))

    chunker = StoryChunker(logger=mock_logger)
    sections = chunker.parse_sections(sample_text)

    assert len(sections) == 5
    assert sections[0]['title'] == "The Awakening"
```

### Integration Tests (workflows)
Test complete workflows:

```python
def test_full_workflow():
    # Phase 1: Chunk story
    chunker = StoryChunker()
    sections = chunker.parse_sections(story)

    # Save project
    pm = ProjectManager()
    pm.save_project("test_project", sections)

    # Load project
    loaded = pm.load_project("test_project")
    assert len(loaded['sections']) == len(sections)
```

## Future Enhancements

### Easy to Add
Thanks to modular design, new features are easy:

**1. Local TTS Integration:**
- Update `tts_generator.py` with new backend
- Add UI button in Phase 3
- Call `tts.generate()` for each section

**2. Different Video Codecs:**
- Add codec parameter to `VideoRenderer`
- Update ffmpeg command builder
- No UI changes needed

**3. Cloud Storage:**
- Create `storage_manager.py`
- Implement upload/download methods
- Integrate in project manager

**4. Batch Processing:**
- Loop through multiple projects
- Reuse existing modules
- Add progress tracking

## Maintenance

### Adding Features
1. Identify which module(s) need changes
2. Update module logic
3. Add UI controls if needed
4. Test in isolation
5. Document changes

### Fixing Bugs
1. Check logs to identify module
2. Write test case that reproduces bug
3. Fix in module
4. Verify test passes
5. Deploy

### Code Review Checklist
- [ ] Logic in core/, not in main app
- [ ] Logger injected, not hardcoded
- [ ] Clear function/class names
- [ ] Docstrings for public methods
- [ ] Error handling with logging
- [ ] No duplicate code
- [ ] Constants not magic numbers

## Comparison: V2 vs V3

### Adding a Feature: "Export to PDF"

**V2 (Monolithic):**
1. Find relevant code (search 1466 lines)
2. Add PDF logic inline with UI
3. Test entire app
4. Risk breaking unrelated features

**V3 (Modular):**
1. Create `pdf_exporter.py` (50 lines)
2. Add button in main app (5 lines)
3. Test PDF module independently
4. No risk to existing features

### Fixing a Bug: "Video rendering fails"

**V2 (Monolithic):**
1. Search through 1466 lines
2. Find ffmpeg command building
3. Fix inline
4. Test entire workflow
5. Hope nothing else broke

**V3 (Modular):**
1. Check logs → error in `phase3_logic.py`
2. Open 280-line file
3. Find bug in `build_ffmpeg_command()`
4. Fix in isolation
5. Test just video rendering
6. Done!

## Conclusion

V3's modular architecture provides:

✅ **Clarity**: Each file has one purpose
✅ **Maintainability**: Easy to find and fix issues
✅ **Testability**: Modules test independently
✅ **Extensibility**: Add features without risk
✅ **Reusability**: Modules work in other projects

The slight increase in total lines (1560 vs 1466) is offset by massive improvements in code quality, understanding, and maintainability.

---

**"Clean code is not about the number of lines, it's about clarity and maintainability."**
