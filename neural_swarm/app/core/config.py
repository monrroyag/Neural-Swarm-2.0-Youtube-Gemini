import os

# API Keys & Models (Dynamic)
from .settings import settings_manager

def get_api_key():
    return settings_manager.get("api_key")

def get_model(type_name):
    # Mapping based on user request details
    models = settings_manager.get("models", {})
    return models.get(type_name, "gemini-2.0-flash-lite")

# Transition helpers (Now dynamic)
def get_model_fast(): return get_model("fast")
def get_model_research(): return get_model("research")
def get_model_tts(): return get_model("audio")
def get_model_image(): return get_model("image")

def __getattr__(name):
    if name == "MODEL_FAST": return get_model_fast()
    if name in ["MODEL_RESEARCH", "MODEL_RESEARCH_ID"]: return get_model_research()
    if name == "MODEL_TTS": return get_model_tts()
    if name == "MODEL_IMAGE": return get_model_image()
    if name == "API_KEY": return get_api_key()
    raise AttributeError(f"module {__name__} has no attribute {name}")

from .constants import BASE_DIR, DB_FILE, AUDIO_DIR, IMAGE_DIR

# Ensure directories exist
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
