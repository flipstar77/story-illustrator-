"""
Ollama Prompt Enhancer - Lightweight alternative to full Prompt Quill

Uses local Ollama LLM to enhance prompts without requiring the full
Prompt Quill installation with vector databases.
"""

import requests
from typing import Dict, List, Optional


class OllamaPromptEnhancer:
    """Lightweight prompt enhancer using Ollama"""

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "llama3.2:3b",
        temperature: float = 0.7
    ):
        """
        Initialize Ollama prompt enhancer

        Args:
            ollama_url: URL of Ollama API
            model: Ollama model name
            temperature: Sampling temperature (0-1)
        """
        self.ollama_url = ollama_url
        self.model = model
        self.temperature = temperature
        self.is_available = False
        self.error_message = None

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]

                # Check if our model is available
                if self.model in model_names:
                    self.is_available = True
                else:
                    self.error_message = f"Model '{self.model}' not found. Available models: {', '.join(model_names)}"
                    self.is_available = False
            else:
                self.error_message = f"Ollama API returned status {response.status_code}"
                self.is_available = False
        except Exception as e:
            self.error_message = f"Cannot connect to Ollama: {str(e)}"
            self.is_available = False

    def enhance_image_prompt(
        self,
        simple_prompt: str,
        style: str = "cinematic",
        add_quality_tags: bool = True
    ) -> Dict:
        """
        Enhance a simple prompt into a detailed image generation prompt

        Args:
            simple_prompt: Basic description
            style: Visual style (cinematic, anime, photorealistic, artistic, etc.)
            add_quality_tags: Whether to add quality/technical tags

        Returns:
            Dictionary with enhanced prompt and metadata
        """
        if not self.is_available:
            return {
                "enhanced_prompt": simple_prompt,
                "original_prompt": simple_prompt,
                "success": False,
                "error": self.error_message
            }

        # Build system prompt for image prompt enhancement
        system_prompt = f"""You are an expert prompt engineer for AI image generation (Stable Diffusion, FLUX, etc).

Your task: Transform simple prompts into detailed, production-ready prompts that will generate high-quality images.

Guidelines:
- Expand the description with visual details (lighting, composition, mood, atmosphere)
- Add specific technical terms used in image generation
- Maintain the core concept while enriching it
- Use {style} style
- Keep it concise but detailed (2-3 sentences max)
- Focus on visual, tangible details
- DO NOT add phrases like "Create an image of" or "Generate"
- Just describe what should be in the image

Example transformations:
Input: "rocket man in space"
Output: "High-quality digital art, ultra-detailed cinematic photograph of an astronaut in a sleek space suit floating in the vastness of outer space, surrounded by distant stars and nebulae, dramatic rim lighting from a nearby planet, sense of isolation and wonder, sharp focus, bokeh background, professional photography composition"

Input: "medieval knight"
Output: "Detailed oil painting of a battle-worn medieval knight in ornate armor, standing in misty forest clearing, golden hour lighting filtering through trees, intricate metalwork on armor showing signs of combat, atmospheric perspective, painterly style, rich colors"

Now enhance this prompt: "{simple_prompt}"

Enhanced prompt:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": system_prompt,
                    "temperature": self.temperature,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                enhanced = result.get("response", "").strip()

                # Add quality tags if requested
                if add_quality_tags and enhanced:
                    quality_tags = ", masterpiece, best quality, highly detailed, 8k uhd, professional"
                    enhanced = f"{enhanced}{quality_tags}"

                return {
                    "enhanced_prompt": enhanced or simple_prompt,
                    "original_prompt": simple_prompt,
                    "success": True,
                    "style": style,
                    "model_used": self.model
                }
            else:
                return {
                    "enhanced_prompt": simple_prompt,
                    "original_prompt": simple_prompt,
                    "success": False,
                    "error": f"Ollama API error: {response.status_code}"
                }

        except Exception as e:
            return {
                "enhanced_prompt": simple_prompt,
                "original_prompt": simple_prompt,
                "success": False,
                "error": str(e)
            }

    def enhance_narration_scene(
        self,
        scene_description: str,
        focus_on: str = "visual atmosphere"
    ) -> Dict:
        """
        Enhance a narration scene for image generation

        Args:
            scene_description: Scene from narration script
            focus_on: What to focus on (visual atmosphere, characters, setting, etc.)

        Returns:
            Enhanced scene description optimized for visual generation
        """
        if not self.is_available:
            return {
                "enhanced_prompt": scene_description,
                "original_prompt": scene_description,
                "success": False,
                "error": self.error_message
            }

        system_prompt = f"""You are an expert at converting story narration into visual image prompts.

Your task: Extract and enhance the VISUAL elements from this narration scene to create an image generation prompt.

Guidelines:
- Focus on {focus_on}
- Describe what can be SEEN in the image
- Include lighting, mood, composition details
- Remove any dialogue or internal thoughts
- Convert narrative description to visual description
- Keep it concrete and visual

Scene: "{scene_description}"

Visual prompt for this scene:"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": system_prompt,
                    "temperature": self.temperature,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                enhanced = result.get("response", "").strip()

                return {
                    "enhanced_prompt": enhanced or scene_description,
                    "original_prompt": scene_description,
                    "success": True,
                    "model_used": self.model
                }
            else:
                return {
                    "enhanced_prompt": scene_description,
                    "original_prompt": scene_description,
                    "success": False,
                    "error": f"Ollama API error: {response.status_code}"
                }

        except Exception as e:
            return {
                "enhanced_prompt": scene_description,
                "original_prompt": scene_description,
                "success": False,
                "error": str(e)
            }

    def generate_negative_prompt(
        self,
        positive_prompt: str,
        quality_focus: bool = True
    ) -> str:
        """
        Generate appropriate negative prompt for image generation

        Args:
            positive_prompt: The positive prompt
            quality_focus: Whether to focus on quality issues

        Returns:
            Negative prompt string
        """
        # Basic negative prompt template
        if quality_focus:
            negative = "blurry, low quality, distorted, deformed, ugly, bad anatomy, poorly drawn, "
            negative += "low resolution, pixelated, artifacts, watermark, text, signature"
        else:
            negative = "blurry, distorted, low quality"

        # Could use LLM to generate custom negative prompts based on positive prompt
        # For now, return template
        return negative

    def batch_enhance(self, prompts: List[str], style: str = "cinematic") -> List[Dict]:
        """
        Enhance multiple prompts in batch

        Args:
            prompts: List of simple prompts
            style: Visual style to apply

        Returns:
            List of enhancement results
        """
        results = []
        for prompt in prompts:
            result = self.enhance_image_prompt(prompt, style=style)
            results.append(result)
        return results

    def get_status(self) -> Dict:
        """Get enhancer status"""
        return {
            "available": self.is_available,
            "backend": "Ollama",
            "model": self.model,
            "url": self.ollama_url,
            "error": self.error_message
        }


# Test and example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Testing Ollama Prompt Enhancer")
    print("=" * 70)

    # Create enhancer
    enhancer = OllamaPromptEnhancer()

    status = enhancer.get_status()
    print(f"\n[STATUS] Backend: {status['backend']}")
    print(f"[STATUS] Model: {status['model']}")
    print(f"[STATUS] Available: {status['available']}")

    if status['error']:
        print(f"[ERROR] {status['error']}")

    if enhancer.is_available:
        # Test basic prompt enhancement
        print("\n" + "=" * 70)
        print("[TEST 1] Simple Prompt Enhancement")
        print("=" * 70)

        result = enhancer.enhance_image_prompt("rocket man in space")

        print(f"\n[ORIGINAL]")
        print(f"  {result['original_prompt']}")

        print(f"\n[ENHANCED]")
        print(f"  {result['enhanced_prompt']}")

        # Test narration scene enhancement
        print("\n" + "=" * 70)
        print("[TEST 2] Narration Scene Enhancement")
        print("=" * 70)

        scene = "The lone astronaut floated silently through the void, stars twinkling in the distance. He wondered if anyone would ever find him out here."

        scene_result = enhancer.enhance_narration_scene(scene)

        print(f"\n[NARRATION]")
        print(f"  {scene}")

        print(f"\n[VISUAL PROMPT]")
        print(f"  {scene_result['enhanced_prompt']}")

        # Test negative prompt
        print("\n" + "=" * 70)
        print("[TEST 3] Negative Prompt Generation")
        print("=" * 70)

        negative = enhancer.generate_negative_prompt(result['enhanced_prompt'])
        print(f"\n[NEGATIVE PROMPT]")
        print(f"  {negative}")

    else:
        print("\n[INFO] Ollama not available. Make sure Ollama is running.")
        print("[INFO] Install: https://ollama.com")
        print(f"[INFO] Run: ollama pull {enhancer.model}")
