"""Phase 2: Image generation automation logic"""
import pyautogui
import pyperclip
import time


class ImageGenerator:
    """Handles automated image generation prompts"""

    def __init__(self, logger=None):
        """
        Args:
            logger: Callable that takes (message, level) for logging
        """
        self.logger = logger or self._default_logger
        self.is_running = False

    @staticmethod
    def _default_logger(message, level='INFO'):
        """Default logger that prints to console"""
        print(f"[{level}] {message}")

    def stop(self):
        """Stop the automation"""
        self.is_running = False
        self.logger("Stopping automation...", "INFO")

    def generate_image_prompt(self, section_title, section_text, section_number, total_sections):
        """
        Generate prompt for image generation

        Args:
            section_title: Title of the section
            section_text: Full text of the section
            section_number: Current section number
            total_sections: Total number of sections

        Returns:
            Formatted prompt string for ChatGPT
        """
        prompt = f"""Create 4 detailed, cinematic images for this section of the story:

SECTION {section_number}/{total_sections}: {section_title}

{section_text}

Please create 4 high-quality, detailed images that capture the key moments and atmosphere of this section. Make them cinematic and visually striking."""
        return prompt

    def send_prompt_to_chatgpt(self, prompt, delay_after=3):
        """
        Send a prompt to ChatGPT using clipboard paste

        Args:
            prompt: The prompt text to send
            delay_after: Seconds to wait after sending

        Returns:
            True if successful, False if stopped
        """
        if not self.is_running:
            return False

        try:
            # Copy to clipboard
            pyperclip.copy(prompt)
            time.sleep(0.3)

            # Paste and send
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)
            pyautogui.press('enter')

            self.logger(f"✓ Prompt sent, waiting {delay_after}s...", "INFO")
            time.sleep(delay_after)

            return True

        except Exception as e:
            self.logger(f"❌ Error sending prompt: {e}", "ERROR")
            return False

    def send_go_on(self, count=1, delay_between=150):
        """
        Send 'go on' commands to ChatGPT

        Args:
            count: Number of times to send 'go on'
            delay_between: Seconds to wait between sends

        Returns:
            True if all successful, False if stopped
        """
        for i in range(count):
            if not self.is_running:
                return False

            try:
                pyautogui.write('go on')
                time.sleep(0.5)
                pyautogui.press('enter')

                self.logger(f"✓ 'go on' sent ({i+1}/{count})", "INFO")

                if i < count - 1:  # Don't wait after last one
                    self.logger(f"Waiting {delay_between}s...", "INFO")
                    time.sleep(delay_between)

            except Exception as e:
                self.logger(f"❌ Error sending 'go on': {e}", "ERROR")
                return False

        return True

    def automate_section(self, section, section_number, total_sections,
                        images_per_section=4, delay_after_prompt=150,
                        delay_between_go_on=150):
        """
        Automate image generation for a single section

        Args:
            section: Section dict with 'title' and 'text'
            section_number: Current section number (1-indexed)
            total_sections: Total number of sections
            images_per_section: Number of images to request
            delay_after_prompt: Seconds to wait after sending prompt
            delay_between_go_on: Seconds to wait between 'go on' commands

        Returns:
            True if successful, False if stopped or failed
        """
        self.logger(f"📝 Starting Section {section_number}: {section['title']}", "INFO")

        # Generate and send prompt
        prompt = self.generate_image_prompt(
            section['title'],
            section['text'],
            section_number,
            total_sections
        )

        if not self.send_prompt_to_chatgpt(prompt, delay_after_prompt):
            return False

        # Send 'go on' commands for additional images
        # First prompt generates first image, need (images_per_section - 1) more
        go_on_count = images_per_section - 1

        if go_on_count > 0:
            if not self.send_go_on(go_on_count, delay_between_go_on):
                return False

        self.logger(f"✅ Section {section_number} complete!", "SUCCESS")
        return True

    def automate_all_sections(self, sections, start_from=0, images_per_section=4,
                              delay_after_prompt=150, delay_between_go_on=150):
        """
        Automate image generation for all sections

        Args:
            sections: List of section dicts
            start_from: Section index to start from (0-indexed)
            images_per_section: Number of images per section
            delay_after_prompt: Seconds to wait after prompt
            delay_between_go_on: Seconds to wait between 'go on'

        Returns:
            True if all successful, False if stopped
        """
        self.is_running = True
        total_sections = len(sections)

        for i in range(start_from, total_sections):
            if not self.is_running:
                self.logger("⏹️ Automation stopped by user", "INFO")
                return False

            section = sections[i]
            success = self.automate_section(
                section, i + 1, total_sections,
                images_per_section, delay_after_prompt, delay_between_go_on
            )

            if not success:
                return False

        self.is_running = False
        self.logger("🎉 All sections complete!", "SUCCESS")
        return True
