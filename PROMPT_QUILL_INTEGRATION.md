# Prompt Quill Vector Data Integration Guide

## Overview

Prompt Quill is a trained LoRA/embedding for FLUX models that enhances prompt understanding and enables consistent character generation across multiple images. This guide explains how to integrate it with Story Illustrator V3.

## What is Prompt Quill?

**Source**: https://civitai.com/models/330412/prompt-quill-vector-data

**Purpose**:
- Enhances FLUX model's understanding of detailed prompts
- Enables consistent character generation across frames
- Improves artistic style consistency
- Better understanding of cinematographic terminology

**Type**: LoRA or Embedding for FLUX models

## Installation

### Step 1: Download from CivitAI

You're already downloading the Prompt Quill vector data. Once complete:

1. Check the file extension:
   - `.safetensors` with "lora" in name → LoRA
   - `.safetensors` with "embedding" in name → Embedding
   - `.pt` or `.bin` → Embedding

### Step 2: Place in Correct Directory

**If it's a LoRA**:
```
C:\Users\Tobias\ComfyUI\models\loras\prompt_quill.safetensors
```

**If it's an Embedding**:
```
C:\Users\Tobias\ComfyUI\models\embeddings\prompt_quill.safetensors
```

### Step 3: Verify Installation

1. Restart ComfyUI (if running)
2. Check ComfyUI console for successful model loading
3. Verify the model appears in ComfyUI's model list

## Integration with Story Illustrator

### Option 1: Workflow-Level Integration

**Location**: ComfyUI workflow JSON files

**How to add**:

1. Open any workflow file in Story Illustrator's workflow directory:
   ```
   c:\Users\Tobias\story-illustrator\comfyui_workflows\
   ```

2. Add LoRA node to workflow (if it's a LoRA):
   ```json
   {
     "id": "lora_node_1",
     "type": "LoraLoader",
     "pos": [x, y],
     "size": [width, height],
     "properties": {},
     "widgets_values": [
       "prompt_quill.safetensors",  // Model name
       1.0,                          // Model strength
       1.0                           // Clip strength
     ]
   }
   ```

3. Connect to existing model chain:
   - Input: Base FLUX model
   - Output: To your existing prompt nodes

### Option 2: GUI Integration (Recommended)

**Add to Phase 2 (Image Generation)**:

**File**: `story_illustrator_v3.py`

**Add checkbox in Phase 2 tab**:
```python
# In create_phase2_tab method, add:
self.use_prompt_quill_var = tk.BooleanVar(value=True)
prompt_quill_cb = ttk.Checkbutton(
    settings_frame,
    text="Use Prompt Quill Enhancement",
    variable=self.use_prompt_quill_var
)
prompt_quill_cb.grid(row=X, column=0, sticky="w", padx=5, pady=2)
```

**Modify workflow loading**:

**File**: `story_illustrator/core/phase2_comfyui_logic.py` or workflow loader

```python
def inject_prompt_quill(workflow_json, enable=True):
    """
    Inject Prompt Quill LoRA into ComfyUI workflow

    Args:
        workflow_json: Workflow dictionary
        enable: Whether to enable Prompt Quill

    Returns:
        Modified workflow with Prompt Quill
    """
    if not enable:
        return workflow_json

    # Find the model loading node
    model_node_id = None
    for node_id, node in workflow_json.items():
        if node.get("class_type") == "CheckpointLoaderSimple":
            model_node_id = node_id
            break

    if not model_node_id:
        return workflow_json  # Can't find model loader

    # Create LoRA loader node
    lora_node_id = f"lora_prompt_quill_{model_node_id}"
    workflow_json[lora_node_id] = {
        "class_type": "LoraLoader",
        "inputs": {
            "model": [model_node_id, 0],
            "clip": [model_node_id, 1],
            "lora_name": "prompt_quill.safetensors",
            "strength_model": 1.0,
            "strength_clip": 1.0
        }
    }

    # Update all nodes that reference the model
    for node_id, node in workflow_json.items():
        if "inputs" in node:
            for input_name, input_value in node["inputs"].items():
                if isinstance(input_value, list) and len(input_value) == 2:
                    if input_value[0] == model_node_id:
                        # Redirect to LoRA node
                        node["inputs"][input_name] = [lora_node_id, input_value[1]]

    return workflow_json
```

**Usage in Phase 2**:
```python
# When generating images
workflow_data = load_workflow("flux_workflow.json")

if self.use_prompt_quill_var.get():
    workflow_data = inject_prompt_quill(workflow_data, enable=True)

# Send to ComfyUI
result = comfyui_client.queue_prompt(workflow_data)
```

### Option 3: Automatic Integration (Future)

**Create dedicated Prompt Quill module**:

**File**: `story_illustrator/utils/prompt_quill_enhancer.py`

```python
"""
Prompt Quill Enhancement Module

Automatically enhances prompts using Prompt Quill vector data.
"""

from pathlib import Path
import json


class PromptQuillEnhancer:
    """Enhances prompts using Prompt Quill LoRA/embedding"""

    def __init__(self, comfyui_models_dir=None):
        """
        Initialize Prompt Quill enhancer

        Args:
            comfyui_models_dir: Path to ComfyUI models directory
        """
        if comfyui_models_dir is None:
            comfyui_models_dir = Path("C:/Users/Tobias/ComfyUI/models")

        self.models_dir = Path(comfyui_models_dir)
        self.loras_dir = self.models_dir / "loras"
        self.embeddings_dir = self.models_dir / "embeddings"

        # Detect Prompt Quill type and location
        self.prompt_quill_path = self._find_prompt_quill()
        self.prompt_quill_type = self._detect_type()

    def _find_prompt_quill(self):
        """Find Prompt Quill file in models directory"""
        # Check LoRAs
        for lora_file in self.loras_dir.glob("*prompt*quill*.safetensors"):
            return lora_file

        # Check embeddings
        for emb_file in self.embeddings_dir.glob("*prompt*quill*.safetensors"):
            return emb_file

        return None

    def _detect_type(self):
        """Detect if Prompt Quill is a LoRA or embedding"""
        if not self.prompt_quill_path:
            return None

        if "lora" in self.prompt_quill_path.parent.name.lower():
            return "lora"
        elif "embedding" in self.prompt_quill_path.parent.name.lower():
            return "embedding"

        return "unknown"

    def is_available(self):
        """Check if Prompt Quill is available"""
        return self.prompt_quill_path is not None and self.prompt_quill_path.exists()

    def enhance_workflow(self, workflow_json):
        """
        Add Prompt Quill to ComfyUI workflow

        Args:
            workflow_json: Workflow dictionary

        Returns:
            Enhanced workflow with Prompt Quill
        """
        if not self.is_available():
            return workflow_json

        if self.prompt_quill_type == "lora":
            return self._inject_lora(workflow_json)
        elif self.prompt_quill_type == "embedding":
            return self._inject_embedding(workflow_json)

        return workflow_json

    def _inject_lora(self, workflow_json):
        """Inject Prompt Quill LoRA into workflow"""
        # Implementation from Option 2
        pass

    def _inject_embedding(self, workflow_json):
        """Inject Prompt Quill embedding into prompts"""
        # Find all prompt nodes
        for node_id, node in workflow_json.items():
            if node.get("class_type") in ["CLIPTextEncode", "CLIPTextEncodeFlux"]:
                if "inputs" in node and "text" in node["inputs"]:
                    # Prepend embedding trigger
                    original_prompt = node["inputs"]["text"]
                    node["inputs"]["text"] = f"prompt_quill {original_prompt}"

        return workflow_json
```

## Usage Examples

### Example 1: Enable for All Image Generation

```python
from story_illustrator.utils.prompt_quill_enhancer import PromptQuillEnhancer

enhancer = PromptQuillEnhancer()

if enhancer.is_available():
    print("Prompt Quill is available!")
    workflow = load_workflow("flux_workflow.json")
    workflow = enhancer.enhance_workflow(workflow)
    # Send to ComfyUI
```

### Example 2: Selective Enhancement

```python
# Only use Prompt Quill for character-focused scenes
if scene_type == "character" and enhancer.is_available():
    workflow = enhancer.enhance_workflow(workflow)
```

### Example 3: GUI Toggle

```python
# In Story Illustrator GUI
if self.use_prompt_quill_var.get() and enhancer.is_available():
    workflow = enhancer.enhance_workflow(workflow)
else:
    # Use base FLUX model
    pass
```

## Expected Benefits

### For Story Videos:
- **Character consistency**: Same character appears identically across frames
- **Style consistency**: Uniform artistic style throughout video
- **Better prompt understanding**: More accurate scene generation from text

### For Actor Videos:
- **Portrait quality**: Enhanced facial detail and likeness
- **Lighting consistency**: Uniform lighting across carousel
- **Professional polish**: Higher quality overall aesthetic

## Recommended Settings

### LoRA Strength:
- **Model strength**: 0.8-1.0 (higher = stronger effect)
- **CLIP strength**: 0.8-1.0 (affects prompt understanding)

### When to Use:
- ✓ Character-focused stories
- ✓ Consistent visual style needed
- ✓ Complex cinematographic prompts
- ✗ Abstract/experimental styles
- ✗ Simple scenes (may be overkill)

## Troubleshooting

### Prompt Quill Not Detected:
1. Check file name contains "prompt" and "quill"
2. Verify file is in correct directory
3. Restart ComfyUI
4. Check ComfyUI console for errors

### Poor Results:
1. Lower LoRA strength (try 0.6-0.7)
2. Adjust prompt formatting
3. Ensure FLUX model is compatible
4. Check if Prompt Quill version matches FLUX version

### Workflow Errors:
1. Verify LoRA node compatibility with ComfyUI version
2. Check workflow JSON structure
3. Test with simple workflow first
4. Review ComfyUI logs

## File Locations

```
ComfyUI Models:
C:\Users\Tobias\ComfyUI\models\loras\prompt_quill.safetensors
C:\Users\Tobias\ComfyUI\models\embeddings\prompt_quill.safetensors

Story Illustrator:
c:\Users\Tobias\story-illustrator\story_illustrator\utils\prompt_quill_enhancer.py
c:\Users\Tobias\story-illustrator\story_illustrator_v3.py (GUI integration)
```

## Next Steps

1. **Complete download** of Prompt Quill vector data
2. **Place file** in appropriate ComfyUI models directory
3. **Choose integration method** (Option 1, 2, or 3)
4. **Test with simple scene** to verify functionality
5. **Adjust settings** based on results
6. **Document learnings** for future reference

## Additional Resources

- **Prompt Quill on CivitAI**: https://civitai.com/models/330412/prompt-quill-vector-data
- **ComfyUI LoRA Guide**: ComfyUI documentation
- **FLUX Model Info**: Stability AI FLUX documentation

---

**Status**: Ready for implementation once download completes
**Priority**: Medium (enhances quality but not essential)
**Complexity**: Low (simple workflow modification)
