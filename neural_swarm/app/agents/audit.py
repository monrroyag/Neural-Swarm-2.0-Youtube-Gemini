import asyncio
from typing import List, Dict
from datetime import datetime
from .base import AgentBase
from ..core.ai import client
from ..core.config import MODEL_FAST
from ..core.i18n import i18n
from ..core.utils import clean_and_parse_json, retry_with_backoff
from ..core.websocket import manager
from google.genai import types

class SpecialistAuditor(AgentBase):
    """Base class for specialized audit agents."""
    name: str = "Especialista"
    icon: str = "🔍"
    criteria: List[str] = []
    focus_prompt: str = ""
    
    def __init__(self, name, icon, criteria, focus_prompt):
        # We don't call super().__init__ because AgentBase uses class attributes
        self.name = f"{icon} {name}"
        self.agent_name = name
        self.agent_icon = icon
        self.criteria = criteria
        self.focus_prompt = focus_prompt
    
    async def evaluate(self, script_text: str, topic: str, niche: str, metadata: dict) -> dict:
        criteria_list = ", ".join(self.criteria)
        
        prompt = i18n.get_prompt("SpecialistAuditor", {
            "agent_name": self.agent_name,
            "focus_prompt": self.focus_prompt,
            "topic": topic,
            "niche": niche,
            "script_text": script_text[:12000],
            "criteria_list": criteria_list
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
            result["agent_name"] = self.agent_name
            result["agent_icon"] = self.agent_icon
            await self.log(f"Score: {result.get('overall_score', 0)}/10 - {result.get('verdict', 'N/A')}")
            self.name = f"{self.agent_icon} {self.agent_name}" # Reset name in case it was changed
            return result
        except Exception as e:
            await self.log(f"⚠️ Error: {e}")
            return {
                "agent_name": self.agent_name,
                "agent_icon": self.agent_icon,
                "overall_score": 0,
                "verdict": "ERROR",
                "criteria_scores": [],
                "top_issues": [str(e)],
                "quick_wins": []
            }

class AuditPanel:
    def __init__(self):
        self.agents = [
            SpecialistAuditor("Director Creativo", "🎬", ["Arco Narrativo", "Hook Inicial", "Transiciones", "Clímax", "Cierre Memorable"], "Evalúas la estructura narrativa..."),
            SpecialistAuditor("Estratega de Marketing", "📈", ["Potencial Viral", "Keywords/SEO", "Diferenciación", "CTA Efectivo", "Tendencias"], "Evalúas el potencial comercial..."),
            SpecialistAuditor("Experto YouTube", "🎯", ["Retención Predicha", "Watch Time", "CTR Thumbnail", "Algoritmo Friendly"], "Evalúas para el algoritmo..."),
            SpecialistAuditor("Psicólogo de Audiencias", "🧠", ["Gatillos Emocionales", "Persuasión", "Conexión Personal"], "Evalúas el impacto psicológico..."),
            SpecialistAuditor("Editor de Contenido", "✍️", ["Claridad", "Gramática/Estilo", "Ritmo/Cadencia"], "Evalúas la calidad técnica..."),
            SpecialistAuditor("Director Visual", "🎨", ["Coherencia Audio-Visual", "Prompts Detallados", "Estética"], "Evalúas los prompts visuales..."),
            SpecialistAuditor("Especialista en Retención", "🧲", ["Hook 5 Segundos", "Curiosity Gaps", "Pattern Interrupts"], "Evalúas técnicas de captación...")
        ]
    
    async def log(self, message: str, type: str = "info"):
        await manager.broadcast(f"[AuditPanel] {message}", type)

    async def execute(self, state: ProjectContext) -> ProjectContext:
        script_text = "\n".join([f"[{block.get('section', 'N/A')}] {block.get('audio_text', '')}" for block in state.final_script])
        
        await self.log("🎯 Convocando panel de 7 expertos...")
        
        tasks = [agent.evaluate(script_text, state.project_bible.get("selected_topic", {}).get("title", ""), state.niche, {}) for agent in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        agent_reports = []
        total_score = 0
        valid_count = 0
        all_issues = []
        all_quick_wins = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_reports.append({"agent_name": self.agents[i].agent_name, "agent_icon": self.agents[i].agent_icon, "overall_score": 0, "verdict": "ERROR"})
            else:
                agent_reports.append(result)
                score = result.get('overall_score', 0)
                if score > 0:
                    total_score += score
                    valid_count += 1
                all_issues.extend([(self.agents[i].agent_name, issue) for issue in result.get('top_issues', [])])
                all_quick_wins.extend(result.get('quick_wins', []))
        
        global_score = round(total_score / valid_count, 1) if valid_count > 0 else 0
        
        state.audit_report = {
            "panel_version": "2.2",
            "global_score": global_score,
            "global_verdict": "Aprobado" if global_score >= 7 else "Revisar",
            "agent_reports": agent_reports,
            "top_issues": all_issues[:5],
            "quick_wins": list(set(all_quick_wins))[:5],
            "timestamp": datetime.now().isoformat()
        }
        
        await self.log(f"✅ Panel completado. Score Global: {global_score}/10", "success")
        return state

audit_panel = AuditPanel()
