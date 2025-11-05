"""
Prompt Enhancer - High-level interface for Story Illustrator

Provides easy-to-use methods for enhancing narration scripts and image prompts.
"""

from typing import List, Dict, Optional
from .prompt_quill_client import PromptQuillClient


class PromptEnhancer:
    """High-level interface for prompt enhancement"""

    def __init__(self, client: Optional[PromptQuillClient] = None):
        """
        Initialize prompt enhancer

        Args:
            client: PromptQuillClient instance (creates new one if None)
        """
        self.client = client or PromptQuillClient()

    def is_available(self) -> bool:
        """Check if Prompt Quill is available"""
        return self.client.is_available

    def get_status_message(self) -> str:
        """Get human-readable status message"""
        status = self.client.get_status()

        if status["available"]:
            mode = "API" if status["mode"] == "API" else "Direct"
            return f"Prompt Quill connected ({mode} mode)"
        else:
            return f"Prompt Quill unavailable: {status.get('error', 'Unknown error')}"

    def enhance_image_prompt(self, simple_prompt: str) -> Dict:
        """
        Enhance a simple image prompt into a detailed, production-ready prompt

        Args:
            simple_prompt: Basic description (e.g., "rocket man in space")

        Returns:
            Dictionary with:
                - enhanced_prompt: Detailed prompt
                - original_prompt: Original input
                - success: Whether enhancement succeeded
                - similar_prompts: List of similar prompts (if available)
        """
        result = self.client.enhance_prompt(simple_prompt)

        return {
            "enhanced_prompt": result.get("enhanced_prompt", simple_prompt),
            "original_prompt": simple_prompt,
            "success": result.get("success", False),
            "similar_prompts": result.get("similar_prompts", []),
            "error": result.get("error")
        }

    def enhance_batch_prompts(self, prompts: List[str]) -> List[Dict]:
        """
        Enhance multiple prompts in batch

        Args:
            prompts: List of simple prompts

        Returns:
            List of enhancement results
        """
        results = []
        for prompt in prompts:
            results.append(self.enhance_image_prompt(prompt))
        return results

    def enhance_narration_scene(self, scene_description: str) -> Dict:
        """
        Enhance a narration scene description for better visual generation

        Args:
            scene_description: Scene from narration script

        Returns:
            Enhanced scene description with visual details
        """
        # Extract key visual elements from scene description
        # For now, just enhance the full description
        return self.enhance_image_prompt(scene_description)

    def get_style_suggestions(self, prompt: str) -> List[str]:
        """
        Get style suggestions for a prompt

        Args:
            prompt: Base prompt

        Returns:
            List of style variations
        """
        # This would use similar_prompts to suggest different styles
        result = self.client.enhance_prompt(prompt)
        return result.get("similar_prompts", [])

    def get_negative_prompt_suggestions(self, prompt: str) -> str:
        """
        Get negative prompt suggestions for image generation

        Args:
            prompt: Positive prompt

        Returns:
            Suggested negative prompt
        """
        # This would query Prompt Quill's negative prompt database
        # For now, return a default
        return "blurry, low quality, distorted, deformed, ugly, bad anatomy"


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("Testing Prompt Enhancer")
    print("=" * 70)

    # Create enhancer
    enhancer = PromptEnhancer()

    print(f"\n[STATUS] {enhancer.get_status_message()}")

    if enhancer.is_available():
        # Test basic enhancement
        print("\n[TEST] Enhancing simple prompt...")
        result = enhancer.enhance_image_prompt("rocket man in space")

        print(f"\n[ORIGINAL]")
        print(f"  {result['original_prompt']}")

        print(f"\n[ENHANCED]")
        print(f"  {result['enhanced_prompt']}")

        if result['similar_prompts']:
            print(f"\n[SIMILAR PROMPTS]")
            for i, p in enumerate(result['similar_prompts'][:3], 1):
                print(f"  {i}. {p}")

        # Test narration enhancement
        print("\n[TEST] Enhancing narration scene...")
        scene = "A lone astronaut floats in deep space, surrounded by stars"
        scene_result = enhancer.enhance_narration_scene(scene)

        print(f"\n[SCENE]")
        print(f"  {scene_result['enhanced_prompt']}")

    else:
        print("\n[INFO] Prompt Quill not available for testing")
        print("[INFO] Install Prompt Quill to enable prompt enhancement features")
