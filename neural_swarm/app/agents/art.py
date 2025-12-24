import json
from google.genai import types
from .base import SwarmAgent
from ..models.project import ProjectContext
from ..core.ai import client
from ..core.config import MODEL_FAST
from ..core.utils import clean_and_parse_json, retry_with_backoff
from ..core.websocket import manager
from ..core.i18n import i18n

class ArtDirectorAgent(SwarmAgent):
    name: str = i18n.t("agents.ArtDirector.name")
    department: str = "Arte"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Diseñando manual de estilo visual...")
        topic = context.project_bible.get("selected_topic", {}).get("title", "")
        tone = context.project_bible.get("content_strategy", {}).get("tone", "")
        
        prompt = i18n.get_prompt("ArtDirector", {
            "topic": topic,
            "tone": tone
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            context.art_direction = await retry_with_backoff(_call)
            await self.log(f"✅ Estilo definido")
            await manager.broadcast("Dirección de Arte definida", "data_update", {"step": "art_direction", "data": context.art_direction})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.art_direction = {"visual_style": {"aesthetic": "Cinematográfico moderno"}}
        
        return context

class PromptEngineerAgent(SwarmAgent):
    name: str = i18n.t("agents.PromptEngineer.name")
    department: str = "Arte"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Generando prompts técnicos para cada bloque...")
        art_style = json.dumps(context.art_direction, indent=2, ensure_ascii=False)
        prompts_list = []
        
        for block in context.final_script:
            visual_suggestion = block.get("visual_suggestion", block.get("audio_text", "")[:100])
            section = block.get("section", "")
            
            prompt = i18n.get_prompt("PromptEngineer", {
                "art_style": art_style[:3000],
                "section": section,
                "visual_suggestion": visual_suggestion,
                "audio_text": block.get("audio_text", "")[:300]
            })
            
            def _call():
                res = client.models.generate_content(model=MODEL_FAST, contents=prompt)
                return res.text.strip()
            
            try:
                visual_prompt = await retry_with_backoff(_call)
                prompts_list.append({
                    "block": block.get("block", len(prompts_list)+1),
                    "section": section,
                    "prompt": visual_prompt
                })
            except Exception as e:
                prompts_list.append({"block": block.get("block", len(prompts_list)+1), "section": section, "prompt": "Cinematic shot"})
        
        context.visual_prompts = prompts_list
        await self.log(f"✅ {len(prompts_list)} prompts técnicos generados")
        await manager.broadcast("Prompts de Ingeniería Visual generados", "data_update", {"step": "art_prompts", "data": context.visual_prompts})
        return context

class ThumbnailStrategistAgent(SwarmAgent):
    name: str = i18n.t("agents.ThumbnailStrategist.name")
    department: str = "Arte"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Diseñando estrategia de thumbnail...")
        topic = context.project_bible.get("selected_topic", {}).get("title", "")
        fears = context.audience_profile.get("psychographics", {}).get("primary_fears", [])
        
        prompt = i18n.get_prompt("ThumbnailStrategist", {
            "topic": topic,
            "fears": fears,
            "aesthetic": context.art_direction.get("visual_style", {}).get("aesthetic", "")
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            context.thumbnail_concept = await retry_with_backoff(_call)
            await self.log(f"✅ Concepto de thumbnail definido")
            await manager.broadcast("Estrategia de Thumbnail definida", "data_update", {"step": "art_thumbnail", "data": context.thumbnail_concept})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.thumbnail_concept = {"technical_prompt": f"Cinematic thumbnail for {topic}"}
        
        return context
