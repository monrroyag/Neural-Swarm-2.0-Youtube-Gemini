import json
from google.genai import types
from .base import SwarmAgent
from ..models.project import ProjectContext
from ..core.ai import client
from ..core.config import MODEL_FAST
from ..core.utils import clean_and_parse_json, retry_with_backoff
from ..core.websocket import manager
from ..core.i18n import i18n

class ScriptArchitectAgent(SwarmAgent):
    name: str = i18n.t("agents.ScriptArchitect.name")
    department: str = "Narrativa"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Diseñando arquitectura del guion...")
        strategy = context.project_bible.get("content_strategy", {})
        technique = strategy.get("storytelling_technique", "Problem-Solution")
        target_length = strategy.get("target_length_minutes", 10)
        
        prompt = i18n.get_prompt("ScriptArchitect", {
            "title": context.project_bible.get("selected_topic", {}).get("title", ""),
            "angle": context.project_bible.get("selected_topic", {}).get("angle", ""),
            "technique": technique,
            "target_length": target_length,
            "tone": strategy.get("tone", "Épico y revelador"),
            "audience_psychographics": json.dumps(context.audience_profile.get("psychographics", {}), indent=2, ensure_ascii=False),
            "verified_research": context.verified_research[:6000]
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            result = await retry_with_backoff(_call)
            context.script_outline = result.get("outline", [])
            await self.log(f"✅ Escaleta creada: {len(context.script_outline)} bloques")
            await manager.broadcast("Escaleta Narrativa definida", "data_update", {"step": "script_outline", "data": context.script_outline})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.script_outline = [{"block_number": i+1, "section": s, "content_brief": ""} 
                                       for i, s in enumerate(["HOOK", "INTRO", "PROBLEMA", "DESARROLLO", "CLÍMAX", "SOLUCIÓN", "CTA"])]
        
        return context

class LeadWriterAgent(SwarmAgent):
    name: str = i18n.t("agents.LeadWriter.name")
    department: str = "Narrativa"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Escribiendo el guion completo...")
        tone = context.project_bible.get("content_strategy", {}).get("tone", "Épico y revelador")
        audience = context.audience_profile.get("messaging_guide", {})
        
        prompt = i18n.get_prompt("LeadWriter", {
            "script_outline": json.dumps(context.script_outline, indent=2, ensure_ascii=False),
            "verified_research": context.verified_research[:10000],
            "tone": tone,
            "speak_to": audience.get("speak_to", "Una persona curiosa")
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            result = await retry_with_backoff(_call)
            context.raw_script = result.get("script", [])
            await self.log(f"✅ Guion escrito: {len(context.raw_script)} bloques")
            await manager.broadcast("Borrador del Guion completado", "data_update", {"step": "script_raw", "data": context.raw_script})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
        
        return context

class HookMasterAgent(SwarmAgent):
    name: str = i18n.t("agents.HookMaster.name")
    department: str = "Narrativa"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Perfeccionando el Hook inicial...")
        current_hook = context.raw_script[0].get("audio_text", "") if context.raw_script else ""
        
        prompt = i18n.get_prompt("HookMaster", {
            "current_hook": current_hook,
            "title": context.project_bible.get("selected_topic", {}).get("title", ""),
            "fears": context.audience_profile.get("psychographics", {}).get("primary_fears", [])
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            result = await retry_with_backoff(_call)
            selected = result.get("selected_hook", {})
            context.hooked_intro = selected.get("text", current_hook)
            if context.raw_script:
                context.raw_script[0]["audio_text"] = context.hooked_intro
            await self.log(f"✅ Hook optimizado")
            await manager.broadcast("Hook Viral optimizado", "data_update", {"step": "script_hook", "data": context.hooked_intro})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
        
        return context

class ComedySpecialistAgent(SwarmAgent):
    name: str = i18n.t("agents.ComedySpecialist.name")
    department: str = "Narrativa"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Agregando punch-ups y analogías...")
        script_text = json.dumps(context.raw_script, ensure_ascii=False)
        
        prompt = i18n.get_prompt("ComedySpecialist", {
            "script_text": script_text[:12000]
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            result = await retry_with_backoff(_call)
            context.final_script = result.get("enhanced_script", context.raw_script)
            await self.log(f"✅ Guion mejorado")
            await manager.broadcast("Guion Final pulido (Comedia + Punch-ups)", "data_update", {"step": "script_final", "data": context.final_script})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.final_script = context.raw_script
        
        return context
