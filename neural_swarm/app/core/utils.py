import time
import json
import re
import random
import logging

def retry_with_backoff(fn, max_retries=10, initial_delay=2):
    """Ejecuta una función con reintentos, backoff exponencial y manejo especial para 429."""
    for i in range(max_retries):
        try:
            return fn()
        except Exception as e:
            error_msg = str(e).upper()
            is_rate_limit = "429" in error_msg or "QUOTA" in error_msg or "LIMIT" in error_msg
            
            if i == max_retries - 1:
                raise e
            
            # Si es un error de cuota, esperamos más tiempo
            if is_rate_limit:
                delay = (initial_delay * 2) * (2 ** i) + random.uniform(0, 5)
            else:
                delay = initial_delay * (2 ** i) + random.uniform(0, 1)
                
            time.sleep(delay)

def clean_and_parse_json(text: str) -> any:
    """Limpia la respuesta del LLM y la convierte en un diccionario o lista JSON."""
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
        # Intenta parsing agresivo si falla el estándar
        try:
            # Busca el primer '[' o '{' y el último ']' o '}'
            start_bracket = text.find('[')
            start_brace = text.find('{')
            
            start = -1
            if start_bracket != -1 and (start_brace == -1 or start_bracket < start_brace):
                start = start_bracket
                end = text.rfind(']')
            elif start_brace != -1:
                start = start_brace
                end = text.rfind('}')
            
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
        except:
            pass
        return {}
