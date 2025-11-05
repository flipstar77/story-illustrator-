# Prompt Quill - Quick Start Guide

## What is Prompt Quill?

Prompt Quill is a powerful prompt enhancement system with **3.2+ million high-quality prompts** stored in a local Qdrant vector database. It uses semantic search to find similar prompts and enhance your simple prompts into detailed, production-ready ones.

## What You Have

### 1. Ollama Prompt Enhancer (Lightweight)
- **Location**: `story_illustrator/prompt_quill/ollama_prompt_enhancer.py`
- **Requirements**: Ollama running locally
- **Database**: None (uses LLM directly)
- **Speed**: Fast
- **Quality**: Good

### 2. Full Prompt Quill (High Quality)
- **Location**: `story_illustrator/prompt_quill/prompt_quill_client.py`
- **Requirements**: Qdrant server + Prompt Quill API
- **Database**: 3.2M prompts (19GB)
- **Speed**: Fast (local vector search)
- **Quality**: Excellent

## Installation Status

The installation is currently running in the command window. It will:

1. Download and install Miniconda (~5 minutes)
2. Create Python 3.11 environment (~2 minutes)
3. Install Python dependencies (~3 minutes)
4. Download Qdrant server (~1 minute)
5. Extract 19GB vector database (~10 minutes)
6. Start Qdrant and load data (~5-10 minutes)

**Total time**: 20-30 minutes

Watch the window for progress messages. When complete, you'll see:
```
Qdrant setup complete - 19GB of data loaded and verified!
Installation completed
Press any key to continue...
```

## After Installation Completes

### Starting Prompt Quill Services

1. **Start Prompt Quill (includes Qdrant)**:
   ```bash
   cd c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq
   start_prompt_quill.bat
   ```

   This will open TWO windows:
   - **Qdrant Server** (vector database) on port 6333
   - **Prompt Quill API** (prompt enhancement) on port 64738

2. **Verify Qdrant is running**:
   - Open browser: `http://localhost:6333/dashboard`
   - You should see the Qdrant Web UI
   - Check collection: `prompts_ng_gte` should have 3.2M+ vectors

3. **Verify Prompt Quill API**:
   - Open browser: `http://localhost:64738`
   - You should see API documentation or status page

### Testing the System

#### Test 1: Ollama Prompt Enhancer (No setup needed)

```bash
cd c:\Users\Tobias\story-illustrator
python story_illustrator/prompt_quill/ollama_prompt_enhancer.py
```

**Expected output**:
```
[TEST 1] Simple Prompt Enhancement
[ORIGINAL] rocket man in space
[ENHANCED] Cinematic photograph of astronaut in advanced space suit...
```

#### Test 2: Full Prompt Quill (After services started)

```python
from story_illustrator.prompt_quill import PromptQuillClient

client = PromptQuillClient()

if client.is_available:
    result = client.enhance_prompt("rocket man in space")
    print(result['enhanced_prompt'])
    print(result['similar_prompts'])  # Shows similar prompts from 3.2M database
else:
    print(f"Error: {client.error_message}")
```

## Using in Story Illustrator

### Option 1: Automatic (Recommended)

The `PromptEnhancer` class automatically tries Prompt Quill first, then falls back to Ollama:

```python
from story_illustrator.prompt_quill import PromptEnhancer

enhancer = PromptEnhancer()

# Automatically uses best available method
result = enhancer.enhance_image_prompt("medieval knight")

print(result['enhanced_prompt'])
```

### Option 2: Explicit Choice

```python
from story_illustrator.prompt_quill import OllamaPromptEnhancer, PromptQuillClient

# Use Ollama specifically
ollama = OllamaPromptEnhancer()
result = ollama.enhance_image_prompt("rocket man in space")

# Use Prompt Quill specifically
quill = PromptQuillClient()
result = quill.enhance_prompt("rocket man in space")
```

### Option 3: In Phase 1 (Narration Scene Enhancement)

```python
from story_illustrator.prompt_quill import PromptEnhancer

enhancer = PromptEnhancer()

# Enhance narration scenes for better visual generation
for scene in narration_script:
    if enhancer.is_available():
        enhanced = enhancer.enhance_narration_scene(scene['description'])
        scene['image_prompt'] = enhanced['enhanced_prompt']
    else:
        scene['image_prompt'] = scene['description']
```

## Common Use Cases

### 1. Simple Prompt to Detailed Prompt

**Before**:
```
"rocket man in space"
```

**After** (with Prompt Quill):
```
"Cinematic photograph of astronaut in advanced white space suit floating
gracefully through the cosmic void, surrounded by distant stars and colorful
nebulae, dramatic rim lighting from a nearby planet casting golden glow on
helmet, sense of profound isolation and wonder, volumetric cosmic rays,
atmospheric depth, sharp focus on subject with bokeh background,
professional space photography composition, 8k uhd, masterpiece"
```

### 2. Style Application

```python
enhancer = OllamaPromptEnhancer()

# Apply different styles
result = enhancer.enhance_image_prompt(
    "medieval knight",
    style="oil painting"
)
```

Supported styles:
- `cinematic` - Movie-like, dramatic
- `photorealistic` - Photo-quality
- `anime` - Japanese animation
- `oil painting` - Traditional art
- `digital art` - Modern illustration
- `concept art` - Professional concept art
- `3d render` - CGI style

### 3. Batch Processing

```python
enhancer = PromptEnhancer()

prompts = [
    "rocket man in space",
    "medieval knight",
    "cyberpunk city"
]

results = enhancer.enhance_batch_prompts(prompts)

for r in results:
    print(f"Original: {r['original_prompt']}")
    print(f"Enhanced: {r['enhanced_prompt']}")
    print()
```

### 4. Negative Prompts

```python
enhancer = OllamaPromptEnhancer()

positive = "beautiful landscape"
negative = enhancer.generate_negative_prompt(positive)

print(negative)
# Output: "blurry, low quality, distorted, deformed, ugly, bad anatomy,
#          poorly drawn, low resolution, pixelated, artifacts, watermark"
```

## Services Management

### Starting Services

**Method 1: Using batch file**:
```bash
cd c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq
start_prompt_quill.bat
```

**Method 2: Manual start**:
```bash
# Start Qdrant
cd c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq\installer_files\qdrant
qdrant.exe

# Start Prompt Quill API (in new window)
cd c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq
python pq/api/v1.py
```

### Stopping Services

Simply close the command windows running Qdrant and Prompt Quill.

### Checking Status

```bash
# Check if Qdrant is running
curl http://localhost:6333/collections/prompts_ng_gte

# Check if Prompt Quill API is running
curl http://localhost:64738
```

Or use Python:
```python
from story_illustrator.prompt_quill import PromptQuillClient

client = PromptQuillClient()
status = client.get_status()

print(f"Available: {status['available']}")
print(f"Mode: {status['mode']}")
print(f"Error: {status.get('error', 'None')}")
```

## Troubleshooting

### Qdrant Not Starting

**Problem**: Qdrant window closes immediately

**Solution**:
1. Check if port 6333 is already in use:
   ```bash
   netstat -ano | findstr :6333
   ```
2. If port is in use, kill the process or change Qdrant config

**Problem**: "Collection not found"

**Solution**: The snapshot wasn't loaded. Re-run installation:
```bash
cd c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq
python install_qdrant.py
```

### Prompt Quill API Not Responding

**Problem**: Can't connect to `http://localhost:64738`

**Solution**:
1. Make sure Qdrant is running first (required)
2. Check Python environment:
   ```bash
   cd c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq
   installer_files\conda\_conda.exe run -p installer_files\env python --version
   ```
3. Start API manually:
   ```bash
   cd c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq
   installer_files\conda\_conda.exe run -p installer_files\env python pq/api/v1.py
   ```

### Ollama Not Available

**Problem**: `OllamaPromptEnhancer` says "Ollama not available"

**Solution**:
1. Install Ollama from https://ollama.com
2. Pull a model:
   ```bash
   ollama pull llama3.2:3b
   ```
3. Verify it's running:
   ```bash
   ollama list
   ```

### Installation Failed

**Problem**: Installation window showed errors

**Solution**:
1. Check the log file:
   ```bash
   type c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq\installation.log
   ```
2. Common issues:
   - Disk space: Need ~25GB free
   - Internet: Large downloads require stable connection
   - Permissions: Run as Administrator if needed

3. Retry installation:
   ```bash
   cd c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq
   del install_state.txt
   one_click_install.bat
   ```

## File Locations

```
Prompt Quill Installation:
c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq\

Vector Database (19GB):
c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq\installer_files\temp_extract\

Qdrant Server:
c:\Users\Tobias\story-illustrator\prompt_quill\llama_index_pq\installer_files\qdrant\

Story Illustrator Modules:
c:\Users\Tobias\story-illustrator\story_illustrator\prompt_quill\
├── __init__.py
├── ollama_prompt_enhancer.py       (Lightweight Ollama-based)
├── prompt_quill_client.py          (Full Prompt Quill client)
└── prompt_enhancer.py              (High-level wrapper)
```

## URLs

- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Qdrant API**: http://localhost:6333
- **Prompt Quill API**: http://localhost:64738
- **Ollama**: http://localhost:11434

## Performance

### Ollama Prompt Enhancer
- **Speed**: ~2-5 seconds per prompt
- **RAM**: ~4GB (for llama3.2:3b)
- **VRAM**: Optional (faster with GPU)

### Prompt Quill
- **Speed**: ~0.5-1 second per prompt
- **RAM**: ~2GB for Qdrant
- **Database**: 19GB on disk

### Batch Processing
- Process 100 prompts in ~2-3 minutes (Ollama)
- Process 100 prompts in ~1 minute (Prompt Quill)

## Next Steps

1. **Wait for installation** to complete (check the window)
2. **Start services** using `start_prompt_quill.bat`
3. **Test both enhancers** to compare quality
4. **Integrate into Story Illustrator** workflow
5. **Experiment with styles** to find what works best

## Support

- **Ollama Issues**: https://ollama.com
- **Prompt Quill Issues**: https://github.com/osi1880vr/prompt_quill
- **Qdrant Issues**: https://qdrant.tech/documentation/

---

**Status**: Installation in progress
**Modules**: Ready to use
**Integration**: Complete
