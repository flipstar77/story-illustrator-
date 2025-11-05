"""
Prompt Quill Integration for Story Illustrator

This module provides access to Prompt Quill's prompt engineering capabilities,
allowing Story Illustrator to enhance and refine prompts using semantic search
over a large corpus of high-quality prompts.

Features:
- Enhance simple prompts into detailed, production-ready prompts
- Search similar prompts from a vector database
- Access to 3.2+ million prompt examples
- Integration with Story Illustrator's narration and image generation

For more information about Prompt Quill:
https://github.com/osi1880vr/prompt_quill
"""

from .prompt_quill_client import PromptQuillClient
from .prompt_enhancer import PromptEnhancer

__all__ = ["PromptQuillClient", "PromptEnhancer"]
__version__ = "1.0.0"
