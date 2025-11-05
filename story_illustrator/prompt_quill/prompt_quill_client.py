"""
Prompt Quill Client - API Interface

Provides a simple interface to Prompt Quill's REST API or direct Python integration.
"""

import os
import sys
import requests
from typing import Optional, Dict, List
from pathlib import Path


class PromptQuillClient:
    """Client for interfacing with Prompt Quill"""

    def __init__(
        self,
        api_url: str = "http://localhost:64738",
        prompt_quill_path: Optional[str] = None,
        use_api: bool = True
    ):
        """
        Initialize Prompt Quill client

        Args:
            api_url: URL of Prompt Quill API server
            prompt_quill_path: Path to Prompt Quill installation (for direct import)
            use_api: Whether to use API (True) or direct import (False)
        """
        self.api_url = api_url
        self.use_api = use_api
        self.prompt_quill_path = prompt_quill_path
        self.is_available = False
        self.error_message = None

        # Try to connect or import
        self._initialize()

    def _initialize(self):
        """Initialize connection to Prompt Quill"""
        if self.use_api:
            self._initialize_api()
        else:
            self._initialize_direct()

    def _initialize_api(self):
        """Initialize API connection"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=2)
            self.is_available = True
        except Exception as e:
            self.error_message = f"Prompt Quill API not available at {self.api_url}"
            self.is_available = False

    def _initialize_direct(self):
        """Initialize direct Python import"""
        try:
            # Add Prompt Quill to Python path
            if self.prompt_quill_path:
                pq_path = Path(self.prompt_quill_path)
                if pq_path.exists():
                    sys.path.insert(0, str(pq_path / "llama_index_pq"))
                    self.is_available = True
                else:
                    self.error_message = f"Prompt Quill path not found: {self.prompt_quill_path}"
                    self.is_available = False
            else:
                # Try to find Prompt Quill in common locations
                possible_paths = [
                    Path.cwd() / "prompt_quill",
                    Path.cwd().parent / "prompt_quill",
                    Path.home() / "prompt_quill"
                ]

                for path in possible_paths:
                    if (path / "llama_index_pq").exists():
                        sys.path.insert(0, str(path / "llama_index_pq"))
                        self.prompt_quill_path = str(path)
                        self.is_available = True
                        break

                if not self.is_available:
                    self.error_message = "Prompt Quill installation not found"
        except Exception as e:
            self.error_message = f"Error initializing Prompt Quill: {str(e)}"
            self.is_available = False

    def enhance_prompt(self, prompt: str, **kwargs) -> Dict:
        """
        Enhance a prompt using Prompt Quill

        Args:
            prompt: The input prompt to enhance
            **kwargs: Additional parameters for prompt enhancement

        Returns:
            Dictionary with 'enhanced_prompt' and optional 'similar_prompts'
        """
        if not self.is_available:
            return {
                "enhanced_prompt": prompt,
                "error": self.error_message,
                "similar_prompts": []
            }

        if self.use_api:
            return self._enhance_prompt_api(prompt, **kwargs)
        else:
            return self._enhance_prompt_direct(prompt, **kwargs)

    def _enhance_prompt_api(self, prompt: str, **kwargs) -> Dict:
        """Enhance prompt via API"""
        try:
            response = requests.post(
                f"{self.api_url}/get_prompt",
                json={"query": prompt},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "enhanced_prompt": result.get("enhanced_prompt", prompt),
                    "similar_prompts": result.get("similar_prompts", []),
                    "success": True
                }
            else:
                return {
                    "enhanced_prompt": prompt,
                    "error": f"API error: {response.status_code}",
                    "success": False
                }
        except Exception as e:
            return {
                "enhanced_prompt": prompt,
                "error": str(e),
                "success": False
            }

    def _enhance_prompt_direct(self, prompt: str, **kwargs) -> Dict:
        """Enhance prompt via direct import"""
        try:
            # This would require importing the actual Prompt Quill modules
            # For now, return the original prompt with a note
            return {
                "enhanced_prompt": prompt,
                "error": "Direct import not yet implemented",
                "similar_prompts": [],
                "success": False
            }
        except Exception as e:
            return {
                "enhanced_prompt": prompt,
                "error": str(e),
                "success": False
            }

    def search_similar_prompts(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search for similar prompts in the vector database

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of similar prompts
        """
        if not self.is_available:
            return []

        # API implementation would go here
        return []

    def get_status(self) -> Dict:
        """Get Prompt Quill status"""
        return {
            "available": self.is_available,
            "mode": "API" if self.use_api else "Direct",
            "api_url": self.api_url if self.use_api else None,
            "path": self.prompt_quill_path,
            "error": self.error_message
        }


# Example usage
if __name__ == "__main__":
    # Try API connection first
    client = PromptQuillClient(use_api=True)

    if not client.is_available:
        print("[INFO] API not available, trying direct import...")
        client = PromptQuillClient(
            use_api=False,
            prompt_quill_path="c:/Users/Tobias/story-illustrator/prompt_quill"
        )

    print(f"[STATUS] {client.get_status()}")

    if client.is_available:
        # Test prompt enhancement
        result = client.enhance_prompt("a rocket man in space")
        print(f"[RESULT] {result}")
    else:
        print(f"[ERROR] Prompt Quill not available: {client.error_message}")
