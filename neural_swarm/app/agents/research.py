from .base import SwarmAgent
from ..models.project import ProjectContext
from ..core.ai import client
from ..core.config import MODEL_FAST, MODEL_RESEARCH_ID
from ..core.utils import retry_with_backoff
from ..core.websocket import manager
from ..core.i18n import i18n

class DeepResearcherAgent(SwarmAgent):
    name: str = i18n.t("agents.DeepResearcher.name")
    department: str = "Investigación"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        topic = context.project_bible.get("selected_topic", {}).get("title", context.niche)
        await self.log(f"Investigación profunda: {topic}")
        
        prompt = i18n.get_prompt("DeepResearcher", {
            "topic": topic,
            "angle": context.project_bible.get("selected_topic", {}).get("angle", "")
        })
        
        def _call():
            return self.grounded_call(client, MODEL_RESEARCH_ID, prompt)
        
        try:
            context.deep_research = await retry_with_backoff(_call)
            await self.log(f"✅ Investigación completada ({len(context.deep_research)} chars)")
            await manager.broadcast("Deep Research finalizado", "data_update", {"step": "research_deep", "data": context.deep_research})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.deep_research = f"Investigación sobre {topic}"
        
        return context

class InvestigativeJournalistAgent(SwarmAgent):
    name: str = i18n.t("agents.InvestigativeJournalist.name")
    department: str = "Investigación"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        topic = context.project_bible.get("selected_topic", {}).get("title", context.niche)
        await self.log(f"Buscando historias ocultas: {topic}")
        
        prompt = i18n.get_prompt("InvestigativeJournalist", {
            "topic": topic
        })
        
        def _call():
            res = client.models.generate_content(model=MODEL_FAST, contents=prompt)
            return res.text
        
        try:
            context.human_stories = await retry_with_backoff(_call)
            await self.log(f"✅ Historias encontradas ({len(context.human_stories)} chars)")
            await manager.broadcast("Historias Humanas detectadas", "data_update", {"step": "research_human", "data": context.human_stories})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.human_stories = ""
        
        return context

class FactCheckerAgent(SwarmAgent):
    name: str = i18n.t("agents.FactChecker.name")
    department: str = "Investigación"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        await self.log("Verificando información y fusionando investigación...")
        
        prompt = i18n.get_prompt("FactChecker", {
            "deep_research": context.deep_research[:8000],
            "human_stories": context.human_stories[:4000]
        })
        
        def _call():
            res = client.models.generate_content(model=MODEL_FAST, contents=prompt)
            return res.text
        
        try:
            context.verified_research = await retry_with_backoff(_call)
            await self.log(f"✅ Investigación verificada ({len(context.verified_research)} chars)")
            await manager.broadcast("Dossier de Verdad compilado", "data_update", {"step": "research_verified", "data": context.verified_research})
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            context.verified_research = context.deep_research + "\n\n" + context.human_stories
        
        return context
