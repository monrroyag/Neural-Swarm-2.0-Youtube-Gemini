import os
import wave
from typing import List, Dict
from google.genai import types
from .base import AgentBase
from ..core.ai import client
from ..core.config import AUDIO_DIR, IMAGE_DIR, get_model_tts, get_model_image, settings_manager
from ..core.utils import retry_with_backoff

class VoiceAgent(AgentBase):
    name: str = "Voice Studio"
    
    async def synthesize(self, script_blocks: List[Dict], project_id: str, index_offset=0):
        await self.log("Iniciando sesión de grabación neuronal...")
        files = []
        
        for i, block in enumerate(script_blocks):
            filename = f"{project_id}_{i + index_offset}.wav"
            filepath = os.path.join(AUDIO_DIR, filename)
            text = block.get('audio_text', '')
            
            if not text: continue

            await self.log(f"Grabando bloque {i + 1}/{len(script_blocks)}: {block.get('section', 'N/A')}")
            
            def _call():
                return client.models.generate_content(
                    model=get_model_tts(), 
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=settings_manager.get('voice_name', 'Fenrir')
                                )
                            )
                        )
                    )
                )

            try:
                res = await retry_with_backoff(_call)
                if not res.candidates or not res.candidates[0].content.parts or not res.candidates[0].content.parts[0].inline_data:
                    raise Exception("No audio data received from API")
                
                audio_data = res.candidates[0].content.parts[0].inline_data.data
                with wave.open(filepath, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(audio_data)
                    
                    # Calculate duration
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
                    block['duration_seconds'] = duration
                
                block['audio_file'] = filename
                files.append(filename)
            except Exception as e:
                await self.log(f"⚠️ Error generando audio para bloque {i+1}: {e}")
                block['audio_file'] = None
        
        await self.log("Producción de audio finalizada.")
        return files

class ImageAgent(AgentBase):
    name: str = "Nano Banana Art"
    
    async def generate_image(self, prompt: str, project_id: str, suffix: str):
        filename = f"{project_id}_{suffix}.png"
        filepath = os.path.join(IMAGE_DIR, filename)

        def _call():
            return client.models.generate_content(
                model=get_model_image(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"]
                )
            )

        try:
            res = await retry_with_backoff(_call)
            if not res.candidates or not res.candidates[0].content.parts:
                raise Exception("No image data received")
            
            part = res.candidates[0].content.parts[0]
            if part.inline_data:
                image_data = part.inline_data.data
                with open(filepath, "wb") as f:
                    f.write(image_data)
                return filename
            else:
                raise Exception("Image part has no inline data")
        except Exception as e:
            await self.log(f"⚠️ Error generando imagen ({suffix}): {e}")
            return None
