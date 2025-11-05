# Ollama Prompt Enhancer - Quick Start Guide

## Overview

Story Illustrator now includes an **Ollama-based Prompt Enhancer** - a lightweight AI system that transforms simple prompts into detailed, production-ready prompts for image generation.

This is a standalone module that works with your **local Ollama LLM** - no internet required, no vector databases needed!

## Quick Example

```python
from story_illustrator.prompt_quill import OllamaPromptEnhancer

enhancer = OllamaPromptEnhancer()

# Transform simple prompt into detailed one
result = enhancer.enhance_image_prompt("rocket man in space")

print(result['enhanced_prompt'])
# Output: "Cinematic photograph of astronaut in advanced space suit floating...
#          surrounded by distant stars and nebulae, dramatic rim lighting..."
```

## Setup (5 Minutes)

### 1. Install Ollama

Download from: **https://ollama.com**

### 2. Pull a Model

```bash
# Recommended for speed (4GB VRAM):
ollama pull llama3.2:3b

# OR for better quality (8GB VRAM):
ollama pull llama3.1:8b
```

### 3. Verify It's Running

```bash
ollama list
```

That's it! You're ready to use it.

## Testing

```bash
cd c:\Users\Tobias\story-illustrator
python story_illustrator/prompt_quill/ollama_prompt_enhancer.py
```

## Module Location

```
story_illustrator/prompt_quill/
├── __init__.py
├── ollama_prompt_enhancer.py  ← Main module
├── prompt_quill_client.py      (optional - for full Prompt Quill)
└── prompt_enhancer.py          (optional - high-level wrapper)
```

## Usage in Your Code

### Basic Enhancement

```python
from story_illustrator.prompt_quill import OllamaPromptEnhancer

enhancer = OllamaPromptEnhancer()

if enhancer.is_available:
    result = enhancer.enhance_image_prompt("medieval knight")
    print(result['enhanced_prompt'])
```

### With Style

```python
result = enhancer.enhance_image_prompt(
    "medieval knight",
    style="oil painting",
    add_quality_tags=True
)
```

### Narration Scene Enhancement

```python
scene = "The astronaut floated silently through space"
result = enhancer.enhance_narration_scene(scene)
```

### Batch Processing

```python
prompts = ["rocket man", "medieval knight", "cyberpunk city"]
results = enhancer.batch_enhance(prompts, style="cinematic")

for r in results:
    print(r['enhanced_prompt'])
```

## Supported Styles

- `"cinematic"` - Movie-like, dramatic
- `"photorealistic"` - Photo-quality
- `"anime"` - Japanese animation
- `"oil painting"` - Traditional art
- `"digital art"` - Modern illustration
- `"concept art"` - Professional concept art
- `"3d render"` - CGI style

## Configuration

Change model or settings:

```python
enhancer = OllamaPromptEnhancer(
    model="llama3.1:8b",     # Different model
    temperature=0.5           # Less creative, more consistent
)
```

## Integration with Story Illustrator

### Example: Enhance All Scenes

```python
from story_illustrator.prompt_quill import OllamaPromptEnhancer

enhancer = OllamaPromptEnhancer()

# In your narration generation loop:
for scene in narration_script:
    if enhancer.is_available:
        enhanced = enhancer.enhance_narration_scene(scene['description'])
        scene['image_prompt'] = enhanced['enhanced_prompt']
    else:
        # Fallback to original
        scene['image_prompt'] = scene['description']
```

## Troubleshooting

### "Ollama not available"

**Check if installed:**
```bash
ollama --version
```

**Start Ollama (Windows):**
Search for "Ollama" in Start menu and run it

**Verify running:**
```bash
ollama list
```

### "Model not found"

```bash
# Pull the model first
ollama pull llama3.2:3b
```

### Slow Performance

- Use smaller model: `llama3.2:3b` (faster)
- Lower temperature: `temperature=0.5`
- Ensure enough VRAM/RAM

## Why Use This?

**Before:**
```
"rocket man in space"
```

**After:**
```
"Cinematic photograph of astronaut in advanced white space suit floating
gracefully through the cosmic void, surrounded by distant stars and colorful
nebulae, dramatic rim lighting from a nearby planet casting golden glow on
helmet, sense of profound isolation and wonder, volumetric cosmic rays,
atmospheric depth, sharp focus on subject with bokeh background,
professional space photography composition, 8k uhd, masterpiece"
```

Better image quality, more consistent results, automatic quality tags!

## Next Steps

1. Test the module (see Testing section above)
2. Try enhancing some of your existing prompts
3. Integrate into your Story Illustrator workflow
4. Experiment with different styles and models

## Support

- **Ollama Issues**: https://ollama.com
- **Module Issues**: Story Illustrator repository
- **Model Recommendations**: See Ollama model library

---

**Quick Links:**
- Module: `story_illustrator/prompt_quill/ollama_prompt_enhancer.py`
- Test Script: Same file (run with Python)
- Ollama: https://ollama.com
- Models: https://ollama.com/library

**Status:** ✓ Ready to use
**Requirements:** Ollama + any LLM model
**Complexity:** Low (just 2 setup steps)
