from ..models.project import ProjectContext
from ..core.websocket import manager

class AgentBase:
    """Base para todos los agentes con capacidad de logueo."""
    name: str = "Generic Agent"
    
    async def log(self, message: str, type: str = "agent"):
        await manager.broadcast(f"[{self.name}] {message}", type=type)

class SwarmAgent(AgentBase):
    """Agente del enjambre con contexto compartido."""
    department: str = "General"
    
    async def execute(self, context: ProjectContext) -> ProjectContext:
        raise NotImplementedError

    def grounded_call(self, client, model_id: str, prompt: str, response_mime_type: str = "text/plain") -> str:
        """Realiza una llamada a Gemini con Búsqueda de Google (Grounding) habilitada."""
        from google.genai import types
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        
        # NOTE: Gemini API currently does not support tool use with response_mime_type="application/json"
        # We fallback to text/plain if tools are used, trusting the prompt to guide JSON output format.
        effective_mime_type = response_mime_type
        if response_mime_type == "application/json":
            effective_mime_type = "text/plain"

        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            response_mime_type=effective_mime_type
        )
        
        res = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )
        return res.text
