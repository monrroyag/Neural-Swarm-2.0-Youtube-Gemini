from .base import SwarmAgent
from ..models.project import ProjectContext
from ..core.ai import client
from ..core.config import MODEL_FAST
from ..core.utils import clean_and_parse_json, retry_with_backoff
from ..core.websocket import manager
from ..core.i18n import i18n
from google.genai import types

class SEOOptimizerAgent(SwarmAgent):
    name: str = i18n.t("agents.SEOOptimizer.name")
    department: str = "Post-Producción"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Optimizando metadatos para YouTube...")
        topic = context.project_bible.get("selected_topic", {}).get("title", "")
        niche = context.niche
        
        prompt = i18n.get_prompt("SEOOptimizer", {
            "topic": topic,
            "niche": niche
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            context.seo_package = await retry_with_backoff(_call)
            await self.log(f"✅ SEO optimizado")
            await manager.broadcast("Paquete SEO Generado", "data_update", {"step": "post_seo", "data": context.seo_package})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.seo_package = {"titles": {"primary": topic}, "tags": [niche]}
        
        return context

class AudioDirectorAgent(SwarmAgent):
    name: str = i18n.t("agents.AudioDirector.name")
    department: str = "Post-Producción"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Marcando instrucciones de audio...")
        import json
        script_text = json.dumps(context.final_script, ensure_ascii=False)
        
        prompt = i18n.get_prompt("AudioDirector", {
            "script_text": script_text[:10000]
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            context.audio_instructions = await retry_with_backoff(_call)
            await self.log("✅ Instrucciones de audio completas")
            await manager.broadcast("Instrucciones de Audio (Director) listas", "data_update", {"step": "post_audio", "data": context.audio_instructions})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.audio_instructions = {"audio_notes": [], "global_notes": {}}
        
        return context
