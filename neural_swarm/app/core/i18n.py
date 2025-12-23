import json
import os
from typing import Dict, Any, Optional
from .settings import settings_manager
from .config import BASE_DIR

class I18nManager:
    """Manages translations and localized prompts."""
    
    def __init__(self, i18n_dir: str):
        self.i18n_dir = i18n_dir
        self.translations: Dict[str, Dict[str, Any]] = {}
        self._load_available()

    def _load_available(self):
        os.makedirs(self.i18n_dir, exist_ok=True)
        for filename in os.listdir(self.i18n_dir):
            if filename.endswith(".json"):
                lang = filename[:-5]
                try:
                    with open(os.path.join(self.i18n_dir, filename), 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                except Exception:
                    pass
        
        # Ensure at least 'es' exists with defaults if empty
        if 'es' not in self.translations:
            self.translations['es'] = self.get_defaults('es')
            self.save_translation('es', self.translations['es'])

    def get_defaults(self, lang: str) -> Dict[str, Any]:
        # This will be populated with all UI and Prompt strings
        return {
            "ui": {
                "dashboard": "Dashboard",
                "library": "Librería",
                "settings": "Configuración",
                "ignite": "ENCENDER ENJAMBRE",
                "niche_placeholder": "Ingresa Nicho / Tópico...",
                "save": "GUARDAR",
                "delete": "ELIMINAR"
            },
            "agents": {
                "TrendHunter": {
                    "name": "📡 Trend Hunter",
                    "prompt": "Eres el Trend Hunter..."
                },
                # ... all other agents ...
            }
        }

    def t(self, path: str, lang: Optional[str] = None) -> str:
        """Translates a string based on a dot-separated path."""
        lang = lang or settings_manager.get("language", "es")
        data = self.translations.get(lang, self.translations.get('es', {}))
        
        parts = path.split('.')
        for part in parts:
            if isinstance(data, dict):
                data = data.get(part, path)
            else:
                return path
        return str(data)

    def get_prompt(self, agent_id: str, context: Dict[str, Any] = None, lang: str = None) -> str:
        prompt_tmpl = self.t(f"agents.{agent_id}.prompt", lang)
        if context:
            try:
                return prompt_tmpl.format(**context)
            except Exception:
                return prompt_tmpl
        return prompt_tmpl

    def save_translation(self, lang: str, data: Dict[str, Any]):
        self.translations[lang] = data
        filepath = os.path.join(self.i18n_dir, f"{lang}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

# Singleton instance
I18N_DIR = os.path.join(BASE_DIR, "neural_swarm", "app", "i18n")
i18n = I18nManager(I18N_DIR)
