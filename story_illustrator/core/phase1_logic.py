"""Phase 1: Story chunking logic"""
import re
from pathlib import Path


class StoryChunker:
    """Handles story parsing and section extraction"""

    def __init__(self, output_folder=None, logger=None):
        """
        Args:
            output_folder: Base folder for section outputs
            logger: Callable that takes (message, level) for logging
        """
        self.output_folder = Path(output_folder) if output_folder else Path.cwd() / "story_images"
        self.output_folder.mkdir(exist_ok=True)
        self.logger = logger or self._default_logger

    @staticmethod
    def _default_logger(message, level='INFO'):
        """Default logger that prints to console"""
        print(f"[{level}] {message}")

    @staticmethod
    def sanitize_filename(name):
        """Remove invalid filename characters"""
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.replace(' ', '_')
        return name[:50]  # Limit length

    def parse_sections(self, text):
        """
        Parse sections from ChatGPT response

        Args:
            text: The ChatGPT response with sections

        Returns:
            List of section dictionaries with 'title', 'text', 'folder'
            Returns None if parsing failed
        """
        # Try primary format: === SECTION 1: Title ===
        pattern = r'(?:===\s*)?SECTION\s+\d+:\s*([^\n=]+?)(?:\s*===)?\s*\n(.*?)(?=(?:===\s*)?SECTION\s+\d+:|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        if not matches:
            # Try alternative format: # Section 1: Title
            pattern = r'(?:#+\s*)?Section\s+\d+[:\-]\s*([^\n]+)\s*\n(.*?)(?=(?:#+\s*)?Section\s+\d+[:\-]|$)'
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        if not matches:
            self.logger("Could not parse sections! Expected format: === SECTION 1: Title ===", "ERROR")
            return None

        sections = []
        for i, (title, content) in enumerate(matches, 1):
            # Create folder for this section
            folder_name = f"section_{i:02d}_{self.sanitize_filename(title.strip())}"
            section_folder = self.output_folder / folder_name
            section_folder.mkdir(exist_ok=True)

            sections.append({
                'title': title.strip(),
                'text': content.strip(),
                'folder': section_folder
            })

        self.logger(f"✓ Parsed {len(sections)} sections successfully!", "SUCCESS")
        return sections

    def generate_chunking_prompt(self, story):
        """
        Generate the prompt to send to ChatGPT for chunking

        Args:
            story: The full story text

        Returns:
            Formatted prompt string
        """
        prompt = f"""Please read this story and divide it into logical sections for illustration. For each section:
1. Give it a descriptive title (e.g., "Section 1: The Awakening")
2. Include the full text of that section
3. Format each section clearly so I can easily copy them

Here's the story:

{story}

Please divide this into sections and format your response like this:
=== SECTION 1: [Title] ===
[Full text of section 1]

=== SECTION 2: [Title] ===
[Full text of section 2]

And so on."""
        return prompt
