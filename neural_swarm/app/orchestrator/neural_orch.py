import time
import asyncio
from datetime import datetime

from ..models.project import ProjectContext
from ..core.database import Database
from ..core.websocket import manager

# Import Agents
from ..agents.strategy import TrendHunterAgent, AudienceProfilerAgent, ProjectManagerAgent
from ..agents.research import DeepResearcherAgent, InvestigativeJournalistAgent, FactCheckerAgent
from ..agents.narrative import ScriptArchitectAgent, LeadWriterAgent, HookMasterAgent, ComedySpecialistAgent
from ..agents.art import ArtDirectorAgent, PromptEngineerAgent, ThumbnailStrategistAgent
from ..agents.post_production import AudioDirectorAgent, SEOOptimizerAgent
from ..agents.helpers import VoiceAgent, ImageAgent
from ..agents.audit import audit_panel
from ..agents.editor import EditorAgent

class NeuralSwarmOrchestrator:
    """Orquestador del Enjambre Neural v2.0 - 15 agentes, 4 fases."""
    
    def __init__(self):
        # Dept 1: Strategy
        self.trend_hunter = TrendHunterAgent()
        self.audience_profiler = AudienceProfilerAgent()
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
    
    async def log(self, message: str, phase: str = ""):
        prefix = f"[🧠 NeuralSwarm{' | ' + phase if phase else ''}]"
        print(f"{prefix} {message}")
        await manager.broadcast(f"{prefix} {message}", "info")
    
    async def run_phase_1_strategy(self, context: ProjectContext) -> ProjectContext:
        await self.log("═══════════════════════════════════════════", "FASE 1")
        await self.log("🏢 FASE 1: ESTRATEGIA Y DIRECCIÓN", "FASE 1")
        
        # Parallel: Trend Hunter + Audience Profiler
        await asyncio.gather(
            self.trend_hunter.execute(context),
            self.audience_profiler.execute(context)
        )
        
        # Sequential: Project Manager
        context = await self.project_manager.execute(context)
        
        await self.log("✅ FASE 1 COMPLETADA", "FASE 1")
        return context
    
    async def run_phase_2_research(self, context: ProjectContext) -> ProjectContext:
        await self.log("═══════════════════════════════════════════", "FASE 2")
        await self.log("🔎 FASE 2: INTELIGENCIA E INVESTIGACIÓN", "FASE 2")
        
        # Parallel: Deep Researcher + Investigative Journalist
        await asyncio.gather(
            self.deep_researcher.execute(context),
            self.investigative_journalist.execute(context)
        )
        
        # Sequential: Fact Checker
        context = await self.fact_checker.execute(context)
        
        await self.log("✅ FASE 2 COMPLETADA", "FASE 2")
        return context
    
    async def run_phase_3_scripting(self, context: ProjectContext) -> ProjectContext:
        await self.log("═══════════════════════════════════════════", "FASE 3")
        await self.log("✍️ FASE 3: NARRATIVA Y GUION", "FASE 3")
        
        # Sequential pipeline
        context = await self.script_architect.execute(context)
        context = await self.lead_writer.execute(context)
        context = await self.hook_master.execute(context)
        context = await self.comedy_specialist.execute(context)
        
        await self.log("✅ FASE 3 COMPLETADA", "FASE 3")
        return context
    
    async def run_phase_4_assets(self, context: ProjectContext) -> ProjectContext:
        await self.log("═══════════════════════════════════════════", "FASE 4")
        await self.log("🎨 FASE 4: PRODUCCIÓN DE ACTIVOS", "FASE 4")
        
        async def visual_track():
            await self.art_director.execute(context)
            await self.prompt_engineer.execute(context)
            await self.thumbnail_strategist.execute(context)
        
        await asyncio.gather(
            visual_track(),
            self.audio_director.execute(context),
            self.seo_optimizer.execute(context)
        )
        
        await self.log("✅ FASE 4 COMPLETADA", "FASE 4")
        return context
    
    async def generate_media(self, context: ProjectContext, project_id: str) -> ProjectContext:
        await self.log("🎬 GENERACIÓN DE MEDIA", "MEDIA")
        
        # Generate images
        for i, prompt_data in enumerate(context.visual_prompts):
            filename = await self.image_agent.generate_image(prompt_data.get("prompt", ""), project_id, f"block_{i}")
            if filename: context.generated_images.append(filename)
        
        # Thumbnail
        thumb_prompt = context.thumbnail_concept.get("technical_prompt", "")
        if thumb_prompt:
            thumb_file = await self.image_agent.generate_image(thumb_prompt, project_id, "thumbnail")
            if thumb_file: context.thumbnail_concept["generated_file"] = thumb_file
        
        # Audio
        for i, block in enumerate(context.final_script):
            audio_text = block.get("audio_text", "")
            audio_file = await self.voice_agent.synthesize([block], project_id, i) # Pass list and offset
            if audio_file: context.audio_files.append(audio_file[0])
        
        await self.log(f"✅ Media generada", "MEDIA")
        return context
    
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
            "status": "Neural Swarm v2.0 - Completed",
            "script": script_blocks,
            "metadata": metadata,
            "project_bible": context.project_bible,
            "audience_profile": context.audience_profile,
            "art_direction": context.art_direction,
            "audio_instructions": context.audio_instructions,
            "neural_swarm_version": "2.0"
        }
    
    async def run_full_pipeline(self, niche: str) -> dict:
        project_id = f"proj_{int(time.time())}"
        await self.log("🚀 ENJAMBRE NEURAL v2.0 - INICIANDO", "SYSTEM")
        
        context = ProjectContext(project_id=project_id, niche=niche)
        try:
            context = await self.run_phase_1_strategy(context)
            context = await self.run_phase_2_research(context)
            context = await self.run_phase_3_scripting(context)
            context = await self.run_phase_4_assets(context)
            context = await self.generate_media(context, project_id)
            
            project = self.compile_project(context)
            Database.add_project(project)
            
            await self.log(f"✅ PRODUCCIÓN COMPLETADA: {project.get('topic')[:50]}...", "SYSTEM")
            return project
        except Exception as e:
            await self.log(f"❌ ERROR CRÍTICO: {e}", "SYSTEM")
            raise e
