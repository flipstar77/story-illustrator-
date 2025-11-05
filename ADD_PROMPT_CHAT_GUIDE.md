# Adding Prompt Enhancer Chat Tab to Story Illustrator

## Quick Integration (2 Steps)

### Step 1: Add Import

Add this line near the top of `story_illustrator_v3.py` (around line 28):

```python
from story_illustrator.ui import PromptEnhancerTab
```

### Step 2: Create Tab

Add this line in the `create_ui()` method (around line 104):

```python
def create_ui(self):
    """Create the main user interface"""
    # ... existing code ...

    # Create main tabs
    self.create_settings_tab()
    self.create_sleep_videos_notebook()
    self.create_actor_filmography_tab()
    self.create_dengeai_prompt_builder_tab()

    # ADD THIS LINE:
    PromptEnhancerTab(self.notebook, self.root)
```

That's it! The tab will appear automatically.

## Full Integration Code

If you want to see the complete code, here's the patch:

**File: `story_illustrator_v3.py`**

```python
# Add at top (line 28, after other imports):
from story_illustrator.ui import PromptEnhancerTab

# In create_ui() method (around line 104):
def create_ui(self):
    """Create the main user interface"""
    # Style
    style = ttk.Style()
    style.theme_use('clam')

    # Main notebook
    self.notebook = ttk.Notebook(self.root)
    self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create main tabs
    self.create_settings_tab()
    self.create_sleep_videos_notebook()
    self.create_actor_filmography_tab()
    self.create_dengeai_prompt_builder_tab()

    # Add Prompt Enhancer Chat tab
    PromptEnhancerTab(self.notebook, self.root)
```

## Testing

1. Make the changes above
2. Run: `python story_illustrator_v3.py`
3. Look for the "💬 Prompt Enhancer" tab
4. Enter a prompt and click "Enhance" or press Ctrl+Enter

## Features

The chat interface includes:

- **Chat-style UI** with colored messages (user, AI, system)
- **Backend Selection**:
  - Auto (tries Prompt Quill first, falls back to Ollama)
  - Prompt Quill (3.2M prompt database)
  - Ollama (local LLM)

- **Style Selection**: cinematic, photorealistic, anime, oil painting, etc.
- **Quality Tags**: Optional quality/technical tags
- **Example Prompts**: Click-to-use examples
- **Service Status**: Check Qdrant/Ollama/Prompt Quill status
- **Copy Last**: Copy enhanced prompt to clipboard
- **Keyboard Shortcut**: Ctrl+Enter to enhance

## Troubleshooting

### Tab Not Showing

Make sure you:
1. Added the import at the top
2. Called `PromptEnhancerTab(self.notebook, self.root)`
3. Restarted the app

### Import Error

If you get `ModuleNotFoundError: No module named 'story_illustrator.ui'`:

1. Check that `story_illustrator/ui/__init__.py` exists
2. Check that `story_illustrator/ui/prompt_enhancer_tab.py` exists

### "No Backends Available"

This means:
- Ollama is not running (install from https://ollama.com)
- Prompt Quill is not running (run `start_prompt_quill.bat`)

The tab will still work, just won't be able to enhance prompts until you start one of the services.

## File Locations

```
story_illustrator/
├── ui/
│   ├── __init__.py                      ← Created
│   └── prompt_enhancer_tab.py           ← Created
├── prompt_quill/
│   ├── __init__.py
│   ├── ollama_prompt_enhancer.py
│   ├── prompt_quill_client.py
│   └── prompt_enhancer.py
└── story_illustrator_v3.py              ← Modify this
```

## What It Looks Like

```
┌────────────────────────────────────────────────────────┐
│ Story Illustrator V3                                  │
├────────────────────────────────────────────────────────┤
│ ⚙️ Settings | 🎬 Sleep Videos | ... | 💬 Prompt Enhancer│
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─── Chat ────────────────────┐ ┌─── Settings ──┐   │
│  │ [12:34:56] You: rocket man  │ │ Backend:       │   │
│  │                              │ │ ○ Auto        │   │
│  │ [12:34:58] Enhanced:         │ │ ● Prompt Quill│   │
│  │ Cinematic photograph of...   │ │ ○ Ollama      │   │
│  │                              │ │               │   │
│  │ [12:34:59] Used: Prompt Quill│ │ Style:        │   │
│  │                              │ │ [cinematic ▼] │   │
│  ├──────────────────────────────┤ │               │   │
│  │ Your Prompt:                 │ │ ☑ Quality Tags│   │
│  │ ┌────────────────────────┐   │ └───────────────┘   │
│  │ │                        │   │                     │
│  │ └────────────────────────┘   │ ┌─── Actions ───┐   │
│  │ [✨ Enhance] [📋 Copy] [Clear]│ │ [📚 Examples] │   │
│  └──────────────────────────────┘ │ [ℹ️ Status]   │   │
│                                    └───────────────┘   │
└────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Add the tab** using the instructions above
2. **Start Ollama** if you have it installed
3. **Start Prompt Quill** after installation completes
4. **Try enhancing** some prompts!

## Advanced: Customization

You can customize the tab by editing `story_illustrator/ui/prompt_enhancer_tab.py`:

- Change default backend/style
- Add more example prompts
- Customize colors/fonts
- Add new features

The tab is completely self-contained and won't affect other parts of the app.

---

**Status**: ✅ Ready to integrate
**Difficulty**: Easy (2 lines of code)
**Time**: 1 minute
