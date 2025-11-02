"""
API Key Management
Loads API keys from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

def get_api_key(key_name: str, required: bool = False) -> str:
    """
    Get API key from environment variables

    Args:
        key_name: Name of the environment variable
        required: If True, raise error if key not found

    Returns:
        API key value or empty string

    Raises:
        ValueError: If required=True and key not found
    """
    value = os.getenv(key_name, "")

    if required and not value:
        raise ValueError(
            f"Required API key '{key_name}' not found in .env file. "
            f"Please add it to {env_path}"
        )

    return value

# Convenience functions for common API keys
def get_perplexity_key(required: bool = False) -> str:
    """Get Perplexity API key"""
    return get_api_key('PERPLEXITY_API_KEY', required)

def get_openai_key(required: bool = False) -> str:
    """Get OpenAI API key"""
    return get_api_key('OPENAI_API_KEY', required)

def get_huggingface_token(required: bool = False) -> str:
    """Get Hugging Face token"""
    return get_api_key('HUGGINGFACE_TOKEN', required)

# Example usage:
if __name__ == "__main__":
    print("API Keys Status:")
    print(f"Perplexity: {'[OK]' if get_perplexity_key() else '[NOT SET]'}")
    print(f"OpenAI: {'[OK]' if get_openai_key() else '[NOT SET]'}")
    print(f"Hugging Face: {'[OK]' if get_huggingface_token() else '[NOT SET]'}")
