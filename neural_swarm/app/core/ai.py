from google import genai
from .config import get_api_key

_client_cache = {"key": None, "instance": None}

def get_client():
    """Returns a GenAI client, re-initializing if the API key has changed."""
    current_key = get_api_key()
    if not current_key:
        return None
        
    if _client_cache["key"] != current_key:
        try:
            _client_cache["key"] = current_key
            _client_cache["instance"] = genai.Client(api_key=current_key)
        except Exception as e:
            print(f"⚠️ Error initializing GenAI Client: {e}")
            return None
    return _client_cache["instance"]

class ClientProxy:
    """Proxy object that always uses the latest initialized client."""
    def __getattr__(self, name):
        c = get_client()
        if c is None:
            raise AttributeError(f"Gemini Client not initialized. Please check your API Key in Settings (trying to access '{name}').")
        return getattr(c, name)

# This proxy object can be imported and will always proxy to the real client
client = ClientProxy()
