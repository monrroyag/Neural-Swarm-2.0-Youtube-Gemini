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
