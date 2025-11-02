# ComfyUI Integration Status

## Installation Summary

### ✅ ComfyUI - INSTALLED
- **Location:** `C:\Users\Tobias\ComfyUI\`
- **Virtual Environment:** `C:\Users\Tobias\ComfyUI_venv\`
- **Status:** Fully installed and ready to use

### ✅ ComfyUI Extensions Installed

1. **ComfyUI-Manager** - Package management for custom nodes
2. **ComfyUI-Copilot** - AI workflow assistant
   - Workflow generation from text
   - Automated debugging
   - Parameter tuning
   - Node recommendations
3. **ComfyUI-Lora-Manager** - LoRA model management
   - Download from CivitAI
   - Recipe system for favorite combinations
   - Web interface at `http://localhost:8188/loras`
4. **ComfyUI-VideoHelperSuite** - Video processing utilities
5. **ComfyUI-WanVideoWrapper** - WAN video generation support

### ✅ Story Illustrator Integration - COMPLETE

#### Created Files:
1. **story_illustrator/utils/comfyui_client.py** - ComfyUI API client
2. **story_illustrator/utils/slideshow_image_generator.py** - Flux image generator
3. **workflows/flux_wan_slideshow.json** - Flux WAN 2.2 workflow template
4. **slideshow_generator.py** - Complete slideshow pipeline
5. **test_comfyui_slideshow.py** - Integration test script
6. **examples/sample_slideshow.csv** - Sample slideshow data

#### Features:
- ✅ ComfyUI API integration
- ✅ Flux WAN 2.2 workflow support
- ✅ Professional text overlays
- ✅ Chatterbox TTS narration
- ✅ FFmpeg video assembly
- ✅ Background music support
- ✅ Resume capability
- ✅ CSV data loading

### ⚠️ Models Needed

To use Flux WAN 2.2, download these models to ComfyUI:

1. **flux1-dev.safetensors** (~23 GB)
   - Download: https://huggingface.co/black-forest-labs/FLUX.1-dev
   - Location: `C:\Users\Tobias\ComfyUI\models\diffusion_models\`

2. **ae.safetensors** (VAE) (~335 MB)
   - Download: https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/ae.safetensors
   - Location: `C:\Users\Tobias\ComfyUI\models\vae\`

3. **clip_l.safetensors** (~246 MB)
   - Download: https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/clip_l.safetensors
   - Location: `C:\Users\Tobias\ComfyUI\models\clip\`

4. **t5xxl_fp8_e4m3fn.safetensors** (~4.9 GB)
   - Download: https://huggingface.co/comfyanonymous/flux_text_encoders/blob/main/t5xxl_fp8_e4m3fn.safetensors
   - Location: `C:\Users\Tobias\ComfyUI\models\text_encoders\`

### ✅ Chatterbox TTS - INTEGRATED
- **Module:** story_illustrator/core/tts_generator.py
- **Status:** Fully integrated in slideshow generator
- **Features:** Auto-device detection (CUDA/MPS/CPU)

### ⚠️ PyTorch - DLL Issue
- **Status:** Installed but has DLL initialization error
- **Impact:** Doesn't affect ComfyUI (uses own venv)
- **Fix:** May need Visual C++ Redistributable update

---

## How to Use

### 1. Start ComfyUI
```bash
cd C:\Users\Tobias\ComfyUI
# Activate venv and start server
python main.py
```

### 2. Access ComfyUI
- Main UI: http://localhost:8188
- LoRA Manager: http://localhost:8188/loras

### 3. Generate Slideshow Video
```bash
# From story-illustrator directory
py slideshow_generator.py examples/sample_slideshow.csv
```

### 4. Advanced Options
```bash
# With background music
py slideshow_generator.py data.csv --music background.mp3

# Custom output directory
py slideshow_generator.py data.csv --output my_slideshow

# Resume from slide 5
py slideshow_generator.py data.csv --start 5

# Skip image generation (use existing)
py slideshow_generator.py data.csv --skip-images

# Skip audio generation (use existing)
py slideshow_generator.py data.csv --skip-audio
```

---

## CSV Data Format

```csv
slide_number,title,data_point,narration_text,image_prompt
1,Title Here,Key Data,"Narration text for TTS",image generation prompt for Flux
2,Another Slide,$1M Revenue,"More narration",cinematic scene description
```

### Fields:
- **slide_number**: Sequential number
- **title**: Displayed at top of image
- **data_point**: Key metric/data displayed at bottom (e.g., "$1M", "100%", "Year 2020")
- **narration_text**: Text read by Chatterbox TTS
- **image_prompt**: Detailed description for Flux image generation

---

## ComfyUI-Copilot Usage

### Activate Copilot
1. Open ComfyUI web interface
2. Click Copilot icon in left panel
3. Generate API key with your email
4. Paste key to activate

### Features:
- **Generate Workflow**: Describe what you want in text
- **Debug**: Auto-fix errors in workflows
- **Tune Parameters**: Batch test different settings
- **Get Recommendations**: Node and model suggestions

---

## LoRA Manager Usage

### Access Interface
- Open http://localhost:8188/loras
- Browse installed LoRAs
- Download new LoRAs from CivitAI
- Create recipes (favorite combinations)

### Download from CivitAI:
1. Browse models at https://civitai.com
2. Copy model URL or ID
3. Paste in LoRA Manager
4. Download with metadata and previews

---

## Next Steps

1. **Download Flux Models** (see Models Needed section above)
2. **Start ComfyUI** server
3. **Test Integration** with sample slideshow:
   ```bash
   py test_comfyui_slideshow.py
   ```
4. **Create Custom Slideshows** with your own CSV data
5. **Use Copilot** to create custom workflows
6. **Manage LoRAs** for different visual styles

---

## Troubleshooting

### ComfyUI Won't Start
- Check if port 8188 is available
- Activate virtual environment first
- Check for Python version compatibility

### No Images Generated
- Verify Flux models are downloaded
- Check ComfyUI console for errors
- Ensure workflow JSON is valid

### TTS Fails
- Check Chatterbox installation
- Verify audio permissions
- Check available disk space

### Video Creation Fails
- Ensure FFmpeg is accessible
- Check output directory permissions
- Verify image/audio files exist

---

## Project Structure

```
story-illustrator/
├── story_illustrator/
│   ├── utils/
│   │   ├── comfyui_client.py          # ComfyUI API client
│   │   └── slideshow_image_generator.py # Flux image generator
│   └── core/
│       └── tts_generator.py            # Chatterbox TTS
├── workflows/
│   └── flux_wan_slideshow.json         # Flux workflow template
├── slideshow_generator.py              # Main slideshow script
├── test_comfyui_slideshow.py          # Test script
└── examples/
    └── sample_slideshow.csv            # Sample data
```

---

## Resources

- **ComfyUI Docs:** https://github.com/comfyanonymous/ComfyUI
- **Flux WAN 2.2:** https://huggingface.co/black-forest-labs/FLUX.1-dev
- **Copilot:** https://github.com/AIDC-AI/ComfyUI-Copilot
- **LoRA Manager:** https://github.com/willmiao/ComfyUI-Lora-Manager
- **Chatterbox TTS:** (included in story-illustrator)

---

**Status:** Ready to use once Flux models are downloaded!
