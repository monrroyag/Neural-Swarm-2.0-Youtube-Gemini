import time
import asyncio
from datetime import datetime
from typing import Dict, TypedDict, Annotated, List, Any

from langgraph.graph import StateGraph, END

from ..models.project import ProjectContext
from ..core.database import Database
from ..core.websocket import manager

# Import Agents
from ..agents.strategy import TrendHunterAgent, AudienceProfilerAgent, ProjectManagerAgent, CompetitorAnalystAgent
from ..agents.research import DeepResearcherAgent, InvestigativeJournalistAgent, FactCheckerAgent
from ..agents.narrative import ScriptArchitectAgent, LeadWriterAgent, HookMasterAgent, ComedySpecialistAgent
from ..agents.art import ArtDirectorAgent, PromptEngineerAgent, ThumbnailStrategistAgent
from ..agents.post_production import AudioDirectorAgent, SEOOptimizerAgent
from ..agents.helpers import VoiceAgent, ImageAgent
from ..agents.audit import audit_panel
from ..agents.editor import EditorAgent

class NeuralSwarmOrchestrator:
    """Orquestador del Enjambre Neural v2.2 - LangGraph Powered."""
    
    def __init__(self):
        # Dept 1: Strategy
        self.trend_hunter = TrendHunterAgent()
        self.audience_profiler = AudienceProfilerAgent()
        self.competitor_analyst = CompetitorAnalystAgent()
        self.project_manager = ProjectManagerAgent()
        
        # Dept 2: Research
        self.deep_researcher = DeepResearcherAgent()
        self.investigative_journalist = InvestigativeJournalistAgent()
        self.fact_checker = FactCheckerAgent()
        
        # Dept 3: Narrative
        self.script_architect = ScriptArchitectAgent()
        self.lead_writer = LeadWriterAgent()
        self.hook_master = HookMasterAgent()
        self.comedy_specialist = ComedySpecialistAgent()
        
        # Dept 4: Art
        self.art_director = ArtDirectorAgent()
        self.prompt_engineer = PromptEngineerAgent()
        self.thumbnail_strategist = ThumbnailStrategistAgent()
        
        # Dept 5: Post-Production
        self.audio_director = AudioDirectorAgent()
        self.seo_optimizer = SEOOptimizerAgent()
        
        # Helper agents
        self.voice_agent = VoiceAgent()
        self.image_agent = ImageAgent()
        
        # New Departments (Audit & Editor)
        self.audit_panel = audit_panel
        self.editor = EditorAgent()

        self.stop_requested = False

        # Build Graph
        self.graph = self._build_graph()
    
    async def log(self, message: str, phase: str = ""):
        prefix = f"[🧠 NeuralSwarm{' | ' + phase if phase else ''}]"
        print(f"{prefix} {message}")
        await manager.broadcast(f"{prefix} {message}", "info")

    async def check_stop(self):
        if self.stop_requested:
            await self.log("🛑 DETENCIÓN SOLICITADA POR EL USUARIO. Abortando misión...", "SYSTEM")
            raise Exception("Swarm stopped by user")

    def stop(self):
        """Signals the orchestrator to stop at the next checkpoint."""
        self.stop_requested = True
        print("🛑 Orchestrator Stop Signal Received.")

    def _build_graph(self):
        workflow = StateGraph(ProjectContext)

        # Nodes
        workflow.add_node("strategy", self.run_phase_1_strategy)
        workflow.add_node("research", self.run_phase_2_research)
        workflow.add_node("scripting", self.run_phase_3_scripting)
        workflow.add_node("quality_check", self.run_quality_audit)
        workflow.add_node("refine", self.run_script_refinement) # NEW
        workflow.add_node("assets", self.run_phase_4_assets)
        workflow.add_node("media", self.generate_media_node)

        # Edges
        workflow.set_entry_point("strategy")
        workflow.add_edge("strategy", "research")
        workflow.add_edge("research", "scripting")
        workflow.add_edge("scripting", "quality_check")
        
        # Conditional Edge: Feedback Loop
        workflow.add_conditional_edges(
            "quality_check",
            self.should_refine_script,
            {
                "refine": "refine", # Goes to refinement first
                "proceed": "assets"
            }
        )
        
        workflow.add_edge("refine", "quality_check") # Re-audit after refinement
        workflow.add_edge("assets", "media")
        workflow.add_edge("media", END)

        return workflow.compile()

    # --- LangGraph Node Methods ---

    async def run_phase_1_strategy(self, state: ProjectContext):
        await self.check_stop()
        await self.log("🏢 FASE 1: ESTRATEGIA Y DIRECCIÓN", "FASE 1")
        await asyncio.gather(
            self.trend_hunter.execute(state),
            self.audience_profiler.execute(state),
            self.competitor_analyst.execute(state)
        )
        await self.project_manager.execute(state)
        return state

    async def run_phase_2_research(self, state: ProjectContext):
        await self.check_stop()
        await self.log("🔎 FASE 2: INTELIGENCIA E INVESTIGACIÓN", "FASE 2")
        await asyncio.gather(
            self.deep_researcher.execute(state),
            self.investigative_journalist.execute(state)
        )
        await self.fact_checker.execute(state)
        return state

    async def run_phase_3_scripting(self, state: ProjectContext):
        await self.check_stop()
        await self.log("✍️ FASE 3: NARRATIVA Y GUION", "FASE 3")
        await self.script_architect.execute(state)
        await self.lead_writer.execute(state)
        await self.hook_master.execute(state)
        await self.comedy_specialist.execute(state)
        return state

    async def run_quality_audit(self, state: ProjectContext):
        await self.check_stop()
        await self.log("🔍 CONTROL DE CALIDAD: AUDITORÍA", "AUDIT")
        await self.audit_panel.execute(state)
        return state

    async def run_script_refinement(self, state: ProjectContext):
        await self.check_stop()
        await self.log("✍️ REFINANDO GUIÓN SEGÚN AUDITORÍA...", "REFINE")
        issues = "\n".join([f"- {i[0]}: {i[1]}" for i in state.audit_report.get("top_issues", [])])
        
        # Refine each block
        for block in state.final_script:
            original = block.get("audio_text", "")
            refined = await self.editor.refine_text(original, issues)
            block["audio_text"] = refined
            
        await self.log("✅ Guion refinado por el Editor en Jefe")
        return state

    def should_refine_script(self, state: ProjectContext):
        score = state.audit_report.get("overall_score", 10)
        if score < 7:
            print(f"⚠️ Calidad insuficiente ({score}/10). Re-escritura iniciada.")
            return "refine"
        return "proceed"

    async def run_phase_4_assets(self, state: ProjectContext):
        await self.check_stop()
        await self.log("🎨 FASE 4: PRODUCCIÓN DE ACTIVOS", "FASE 4")
        async def visual_track():
            await self.art_director.execute(state)
            await self.prompt_engineer.execute(state)
            await self.thumbnail_strategist.execute(state)
        
        await asyncio.gather(
            visual_track(),
            self.audio_director.execute(state),
            self.seo_optimizer.execute(state)
        )
        return state

    async def generate_media_node(self, state: ProjectContext):
        await self.check_stop()
        await self.log("🎬 GENERACIÓN DE MEDIA", "MEDIA")
        # Generate images
        for i, prompt_data in enumerate(state.visual_prompts):
            filename = await self.image_agent.generate_image(prompt_data.get("prompt", ""), state.project_id, f"block_{i}")
            if filename: state.generated_images.append(filename)
        
        # Thumbnail
        thumb_prompt = state.thumbnail_concept.get("technical_prompt", "")
        if thumb_prompt:
            thumb_file = await self.image_agent.generate_image(thumb_prompt, state.project_id, "thumbnail")
            if thumb_file: state.thumbnail_concept["generated_file"] = thumb_file
        
        # Audio
        for i, block in enumerate(state.final_script):
            audio_file = await self.voice_agent.synthesize([block], state.project_id, i)
            if audio_file: state.audio_files.append(audio_file[0])
        
        return state

    def compile_project(self, context: ProjectContext) -> dict:
        script_blocks = []
        for i, block in enumerate(context.final_script):
            script_blocks.append({
                "section": block.get("section", f"BLOQUE_{i+1}"),
                "audio_text": block.get("audio_text", ""),
                "visual_prompt": context.visual_prompts[i]["prompt"] if i < len(context.visual_prompts) else "",
                "word_count": block.get("word_count", len(block.get("audio_text", "").split())),
                "duration_seconds": block.get("duration_seconds", 30),
                "audio_file": block.get("audio_file", ""),
                "generated_images": [context.generated_images[i]] if i < len(context.generated_images) else []
            })
        
        seo = context.seo_package
        metadata = {
            "title": seo.get("titles", {}).get("primary", context.project_bible.get("selected_topic", {}).get("title", "")),
            "description": seo.get("description", {}).get("full_description", ""),
            "tags": ", ".join(seo.get("tags", [])),
            "thumbnail_prompt": context.thumbnail_concept.get("technical_prompt", ""),
            "thumbnail_file": context.thumbnail_concept.get("generated_file", "")
        }
        
        return {
            "id": context.project_id,
            "niche": context.niche,
            "topic": context.project_bible.get("selected_topic", {}).get("title", context.niche),
            "date": datetime.now().isoformat(),
            "status": "Neural Swarm v2.2 - LangGraph Completed",
            "script": script_blocks,
            "metadata": metadata,
            "project_bible": context.project_bible,
            "audience_profile": context.audience_profile,
            "competitor_analysis": context.competitor_analysis,
            "audit_report": context.audit_report,
            "art_direction": context.art_direction,
            "audio_instructions": context.audio_instructions,
            "neural_swarm_version": "2.2"
        }
    
    async def run_full_pipeline(self, niche: str) -> dict:
        self.stop_requested = False
        project_id = f"proj_{int(time.time())}"
        await self.log("🚀 ENJAMBRE NEURAL v2.2 - INICIANDO (LANGGRAPH)", "SYSTEM")
        
        initial_state = ProjectContext(project_id=project_id, niche=niche)
        try:
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            project = self.compile_project(final_state)
            Database.add_project(project)
            
            await self.log(f"✅ PRODUCCIÓN COMPLETADA: {project.get('topic')[:50]}...", "SYSTEM")
            return project
        except Exception as e:
            await self.log(f"❌ ERROR CRÍTICO EN EL GRAFO: {e}", "SYSTEM")
            raise e
