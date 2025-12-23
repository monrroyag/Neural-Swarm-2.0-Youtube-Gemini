import json
from datetime import datetime
from google.genai import types
from .base import SwarmAgent
from ..models.project import ProjectContext
from ..core.ai import client
from ..core.config import MODEL_FAST
from ..core.utils import clean_and_parse_json, retry_with_backoff
from ..core.websocket import manager

from ..core.i18n import i18n

class TrendHunterAgent(SwarmAgent):
    name: str = i18n.t("agents.TrendHunter.name")
    department: str = "Strategy"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log(f"Escaneando tendencias en: {context.niche}")
        
        prompt = i18n.get_prompt("TrendHunter", {
            "niche": context.niche,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            result = retry_with_backoff(_call)
            context.trend_opportunities = result.get("opportunities", [])
            await self.log(f"✅ Encontradas {len(context.trend_opportunities)} oportunidades")
            await manager.broadcast("Tendencias detectadas", "data_update", {"step": "trends", "data": context.trend_opportunities})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.trend_opportunities = [{"topic": context.niche, "angle": "Análisis profundo", "traffic_potential": 7}]
        
        return context

class AudienceProfilerAgent(SwarmAgent):
    name: str = i18n.t("agents.AudienceProfiler.name")
    department: str = "Strategy"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Construyendo perfil psicológico de la audiencia...")
        topics = [t.get("topic", "") for t in context.trend_opportunities[:3]]
        
        prompt = i18n.get_prompt("AudienceProfiler", {
            "niche": context.niche,
            "topics": ', '.join(topics)
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            context.audience_profile = retry_with_backoff(_call)
            await self.log("✅ Perfil de audiencia construido")
            await manager.broadcast("Perfil de Audiencia creado", "data_update", {"step": "audience", "data": context.audience_profile})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.audience_profile = {"psychographics": {"primary_fears": ["Quedarse atrás"], "deep_desires": ["Entender el tema"]}}
        
        return context

class ProjectManagerAgent(SwarmAgent):
    name: str = i18n.t("agents.ProjectManager.name")
    department: str = "Strategy"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Analizando datos y creando la Biblia del Proyecto...")
        
        prompt = i18n.get_prompt("ProjectManager", {
            "opportunities": json.dumps(context.trend_opportunities, indent=2, ensure_ascii=False),
            "audience_profile": json.dumps(context.audience_profile, indent=2, ensure_ascii=False)
        })
        
        def _call():
            res = client.models.generate_content(
                model=MODEL_FAST,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return clean_and_parse_json(res.text)
        
        try:
            context.project_bible = retry_with_backoff(_call)
            topic = context.project_bible.get("selected_topic", {}).get("title", "Sin título")
            await self.log(f"✅ Biblia creada: {topic}")
            await manager.broadcast("Biblia del Proyecto completada", "data_update", {"step": "bible", "data": context.project_bible})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.project_bible = {"selected_topic": {"title": context.niche, "angle": "Análisis", "hook": "Descubre la verdad"}}
        
        return context
