import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from .core.config import AUDIO_DIR, IMAGE_DIR
from .core.websocket import manager
from .core.database import Database
from .orchestrator.neural_orch import NeuralSwarmOrchestrator
from .core.settings import settings_manager
from .core.i18n import i18n

app = FastAPI(title="Neural Swarm v2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Orchestrator
neural_swarm = NeuralSwarmOrchestrator()

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

@app.get('/')
async def serve_ui():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "frontend.html")
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content='<h1>frontend.html not found</h1>', status_code=404)

@app.post("/api/start")
async def start_generation(data: dict, background_tasks: BackgroundTasks):
    niche = data.get("niche", "Tech & AI")
    background_tasks.add_task(neural_swarm.run_full_pipeline, niche)
    return {"status": "started", "message": f"🧠 Neural Swarm v2.0 iniciado para: {niche}"}

@app.get("/api/projects")
def get_projects():
    return Database.load()["projects"]

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    Database.delete_project(project_id)
    return {"status": "deleted"}

@app.get("/audio/{filename}")
def get_audio(filename: str):
    path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path)

@app.get("/images/{filename}")
def get_image(filename: str):
    path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)

# --- Settings & I18n Endpoints ---

@app.get("/api/settings")
def get_settings():
    return settings_manager.settings

@app.post("/api/settings")
def update_settings(new_settings: dict):
    settings_manager.update_settings(new_settings)
    return {"status": "ok", "settings": settings_manager.settings}

@app.get("/api/i18n/{lang}")
def get_translations(lang: str):
    # This ensures the language is loaded
    i18n.load_language(lang)
    return i18n.translations

import shutil
import time
from typing import Optional, List
from fastapi import UploadFile, File

# --- Models for granular API requests ---

class RetryRequest(BaseModel):
    project_id: str
    block_index: int

class EditorRequest(BaseModel):
    text: str
    context: str = ""

class AutoFixRequest(BaseModel):
    instruction: Optional[str] = None

@app.post("/api/retry_audio")
async def retry_audio(req: RetryRequest):
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == req.project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        block = project["script"][req.block_index]
        # Re-synthesize this block
        new_files = await neural_swarm.voice_agent.synthesize([block], project["id"], offset=req.block_index)
        
        # VoiceAgent.synthesize already handles file naming if offset is provided
        if new_files:
            block['audio_file'] = new_files[0]
            
        Database.update_project(project)
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects/{project_id}/audit_panel")
async def audit_panel_endpoint(project_id: str):
    db = Database.load()
    project_dict = next((p for p in db["projects"] if p["id"] == project_id), None)
    if not project_dict:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Convert dict to ProjectContext for the auditor
    from .models.project import ProjectContext
    # Basic conversion (this is a bit manual but safe)
    context = ProjectContext(project_id=project_id, niche=project_dict.get("niche", ""))
    context.final_script = project_dict.get("script", [])
    context.project_bible = project_dict.get("project_bible", {})
    
    context = await neural_swarm.audit_panel.execute(context)
    panel_report = context.audit_report
    
    project_dict["audit_report"] = {
        "type": "panel",
        "global_score": panel_report["global_score"],
        "global_verdict": panel_report["global_verdict"],
        "critique": panel_report["global_verdict"],
        "suggestions": [f"[{report.get('agent_name')}] {report.get('top_issues', ['N/A'])[0] if report.get('top_issues') else 'N/A'}" for report in panel_report["agent_reports"]],
        "panel": panel_report
    }
    Database.update_project(project_dict)
    return project_dict

@app.post("/api/editor/expand")
async def editor_expand(req: EditorRequest):
    expanded = await neural_swarm.editor.expand_text(req.text, req.context)
    return {"text": expanded}

@app.post("/api/editor/shorten")
async def editor_shorten(req: EditorRequest):
    shortened = await neural_swarm.editor.shorten_text(req.text)
    return {"text": shortened}

@app.put("/api/projects/{project_id}")
async def update_project_endpoint(project_id: str, project_data: dict):
    if project_data.get('id') != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    Database.update_project(project_data)
    return project_data

@app.post("/api/projects/{project_id}/images/thumbnail")
async def regen_thumbnail(project_id: str):
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == project_id), None)
    if not project: raise HTTPException(404, "Project not found")
    
    prompt = project.get("metadata", {}).get("thumbnail_prompt")
    if not prompt: raise HTTPException(400, "No thumbnail prompt found")
    
    await neural_swarm.log("🔄 Regenerando Thumbnail manualmente...")
    filename = await neural_swarm.image_agent.generate_image(prompt, project_id, f"thumbnail_{int(time.time())}")
    
    if filename:
        project["metadata"]["thumbnail_file"] = filename
        Database.update_project(project)
        return {"file": filename}
    else:
        raise HTTPException(500, "Failed to generate thumbnail")

@app.post("/api/projects/{project_id}/autofix")
async def autofix_project(project_id: str, req: AutoFixRequest):
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == project_id), None)
    if not project: raise HTTPException(404, "Project not found")
    
    instruction = req.instruction
    if not instruction:
        report = project.get("audit_report")
        if report:
            instruction = f"{report.get('critique', '')}\nSuggestions: {', '.join(report.get('suggestions', []))}"
        else:
            raise HTTPException(400, "No instruction or audit report found")
    
    await neural_swarm.log(f"🪄 Iniciando Auto-Fix para: {project['topic']}")
    
    for block in project.get("script", []):
        refined = await neural_swarm.editor.refine_text(block['audio_text'], instruction)
        block['audio_text'] = refined
    
    project['status'] = 'Auto-Fixed'
    Database.update_project(project)
    await neural_swarm.log("✅ Auto-Fix completado.")
    return project

@app.post("/api/projects/{project_id}/upload/thumbnail")
async def upload_thumbnail(project_id: str, file: UploadFile = File(...)):
    filename = f"{project_id}_thumb_custom_{int(time.time())}_{file.filename}"
    filepath = os.path.join(IMAGE_DIR, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == project_id), None)
    if project:
        project["metadata"]["thumbnail_file"] = filename
        Database.update_project(project)
    return {"file": filename}
@app.post("/api/projects/{project_id}/images/block/{block_index}")
async def regen_block_images(project_id: str, block_index: int):
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == project_id), None)
    if not project: raise HTTPException(404, "Project not found")
    
    try:
        block = project["script"][block_index]
    except IndexError:
        raise HTTPException(404, "Block not found")

    prompts = block.get("visual_prompts", [])
    if isinstance(prompts, str): prompts = [prompts]
    if not prompts and block.get("visual_prompt"): prompts = [block.get("visual_prompt")]
    
    if not prompts: raise HTTPException(400, "No visual prompts in block")
    
    await neural_swarm.log(f"🔄 Regenerando imágenes para bloque {block_index}...")
    new_images = []
    for i, p in enumerate(prompts[:3]):
        img = await neural_swarm.image_agent.generate_image(p, project_id, f"block_{block_index}_img_{i}_{int(time.time())}")
        if img: new_images.append(img)
        
    block["generated_images"] = new_images
    Database.update_project(project)
    return {"images": new_images}

@app.post("/api/projects/{project_id}/images/all")
async def regen_all_images(project_id: str, background_tasks: BackgroundTasks):
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == project_id), None)
    if not project: raise HTTPException(404, "Project not found")

    async def _process_all_images():
        await neural_swarm.log(f"🚀 Iniciando generación masiva para: {project.get('topic')}")
        # Thumbnail
        meta = project.get("metadata", {})
        if meta.get("thumbnail_prompt"):
             thm = await neural_swarm.image_agent.generate_image(meta["thumbnail_prompt"], project_id, f"thumb_all_{int(time.time())}")
             if thm: meta["thumbnail_file"] = thm
        # Blocks
        for i, block in enumerate(project.get("script", [])):
            prompt = block.get("visual_prompt") or (block.get("visual_prompts")[0] if block.get("visual_prompts") else None)
            if prompt:
                img = await neural_swarm.image_agent.generate_image(prompt, project_id, f"block_{i}_all_{int(time.time())}")
                if img: block["generated_images"] = [img]
        Database.update_project(project)
        await manager.broadcast("Imágenes actualizadas", "project_update", project)

    background_tasks.add_task(_process_all_images)
    return {"status": "started"}

@app.post("/api/projects/{project_id}/block/{block_index}/refine")
async def refine_block_endpoint(project_id: str, block_index: int, req: AutoFixRequest):
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == project_id), None)
    if not project: raise HTTPException(404, "Project not found")
    try:
        block = project["script"][block_index]
    except IndexError: raise HTTPException(404, "Block not found")
        
    refined_text = await neural_swarm.editor.refine_text(block['audio_text'], req.instruction or "Mejorar redacción.")
    block['audio_text'] = refined_text
    Database.update_project(project)
    return {"text": refined_text}

@app.post("/api/projects/{project_id}/block/{block_index}/regen_prompt")
async def regen_visual_prompt_endpoint(project_id: str, block_index: int):
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == project_id), None)
    if not project: raise HTTPException(404, "Project not found")
    try:
        block = project["script"][block_index]
    except IndexError: raise HTTPException(404, "Block not found")

    new_prompt = await neural_swarm.editor.regenerate_visual_prompt(block['audio_text'], project.get('topic', ''))
    block['visual_prompt'] = new_prompt
    Database.update_project(project)
    return {"visual_prompt": new_prompt}

@app.post("/api/projects/{project_id}/upload/block/{block_index}")
async def upload_block_image(project_id: str, block_index: int, file: UploadFile = File(...)):
    filename = f"{project_id}_block{block_index}_custom_{int(time.time())}_{file.filename}"
    filepath = os.path.join(IMAGE_DIR, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    db = Database.load()
    project = next((p for p in db["projects"] if p["id"] == project_id), None)
    if project:
        try:
            block = project["script"][block_index]
            if "generated_images" not in block: block["generated_images"] = []
            block["generated_images"].insert(0, filename)
            Database.update_project(project)
        except IndexError: raise HTTPException(404, "Block not found")
    return {"file": filename}
