from .base import AgentBase
from ..core.ai import client
from ..core.config import MODEL_FAST
from ..core.utils import retry_with_backoff
from google.genai import types
from ..core.i18n import i18n

class EditorAgent(AgentBase):
    """Agente especializado en edición, refinamiento y manipulación de texto."""
    name: str = i18n.t("agents.Editor.name")
    
    async def refine_text(self, text: str, critique: str) -> str:
        prompt = i18n.get_prompt("Editor.refine_prompt", {
            "text": text,
            "critique": critique
        })
        def _call():
            return client.models.generate_content(model=MODEL_FAST, contents=prompt).text
        return retry_with_backoff(_call)

    async def expand_text(self, text: str, context: str = "") -> str:
        prompt = i18n.get_prompt("Editor.expand_prompt", {
            "text": text,
            "context": context
        })
        def _call():
            return client.models.generate_content(model=MODEL_FAST, contents=prompt).text
        return retry_with_backoff(_call)

    async def shorten_text(self, text: str) -> str:
        prompt = i18n.get_prompt("Editor.shorten_prompt", {
            "text": text
        })
        def _call():
            return client.models.generate_content(model=MODEL_FAST, contents=prompt).text
        return retry_with_backoff(_call)

    async def regenerate_visual_prompt(self, text: str, topic: str) -> str:
        prompt = i18n.get_prompt("Editor.visual_regen_prompt", {
            "text": text,
            "topic": topic
        })
        def _call():
             return client.models.generate_content(model=MODEL_FAST, contents=prompt).text
        return await retry_with_backoff(_call)
