"""Configuration management"""
import json
from pathlib import Path


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_file=None):
        if config_file is None:
            config_file = Path.cwd() / "story_illustrator_v2_config.json"
        self.config_file = Path(config_file)
        self.config = {}
        self.load()

    def load(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
        else:
            self.config = {}

    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save()

    def update(self, updates):
        """Update multiple configuration values"""
        self.config.update(updates)
        self.save()
