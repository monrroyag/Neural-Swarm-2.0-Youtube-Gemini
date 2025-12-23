import json
import os
from typing import Dict, Any

class SettingsManager:
    """Manages application settings and persistence."""
    
    def __init__(self, settings_file: str):
        self.settings_file = settings_file
        self.settings: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return self.get_defaults()

    def get_defaults(self) -> Dict[str, Any]:
        return {
            "api_key": "", 
            "language": "es",
            "models": {
                "fast": "gemini-3-flash-preview",
                "research": "gemini-2.5-pro",
                "image": "gemini-2.5-flash-image",
                "audio": "gemini-2.5-flash-preview-tts"
            },
            "voice_name": "Fenrir"
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def update(self, new_settings: Dict[str, Any]):
        self.settings.update(new_settings)
        self._save()

    def _save(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

# Singleton instance
from .constants import SETTINGS_FILE
settings_manager = SettingsManager(SETTINGS_FILE)
