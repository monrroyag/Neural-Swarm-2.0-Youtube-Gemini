import time
import json
import re
import random
import logging

def retry_with_backoff(fn, max_retries=5, initial_delay=1):
    """Ejecuta una función con reintentos y backoff exponencial."""
    for i in range(max_retries):
        try:
            return fn()
        except Exception as e:
            if i == max_retries - 1:
                raise e
            delay = initial_delay * (2 ** i) + random.uniform(0, 1)
            time.sleep(delay)

def clean_and_parse_json(text: str) -> dict:
    """Limpia la respuesta del LLM y la convierte en un diccionario JSON."""
    try:
        # Intenta encontrar el bloque JSON si el modelo devolvió markdown
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            text = json_match.group(1)
        
        # Limpiezas comunes
        text = text.strip()
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        
        return json.loads(text)
    except Exception as e:
        print(f"Error parseando JSON: {e}")
        # Intenta parsing agresivo si falla el estándar
        try:
            # Elimina cualquier cosa que no esté entre las llaves exteriores
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
        except:
            pass
        return {}
