import os

# Base directory of the project (parent of neural_swarm)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data paths
DB_FILE = os.path.join(BASE_DIR, "studio_db.json")
AUDIO_DIR = os.path.join(BASE_DIR, "studio_audio")
IMAGE_DIR = os.path.join(BASE_DIR, "studio_images")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
