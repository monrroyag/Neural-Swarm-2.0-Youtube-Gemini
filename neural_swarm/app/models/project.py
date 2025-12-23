from dataclasses import dataclass, field
from typing import List

@dataclass
class ProjectContext:
    """Estado compartido entre todos los agentes del enjambre."""
    project_id: str
    niche: str
    
    # Phase 1: Strategy outputs
    trend_opportunities: List[dict] = field(default_factory=list)
    audience_profile: dict = field(default_factory=dict)
    project_bible: dict = field(default_factory=dict)
    
    # Phase 2: Research outputs
    deep_research: str = ""
    human_stories: str = ""
    verified_research: str = ""
    
    # Phase 3: Scripting outputs
    script_outline: List[dict] = field(default_factory=list)
    raw_script: List[dict] = field(default_factory=list)
    hooked_intro: str = ""
    final_script: List[dict] = field(default_factory=list)
    
    # Phase 4: Assets outputs
    art_direction: dict = field(default_factory=dict)
    visual_prompts: List[str] = field(default_factory=list)
    thumbnail_concept: dict = field(default_factory=dict)
    audio_instructions: dict = field(default_factory=dict)
    seo_package: dict = field(default_factory=dict)
    generated_images: List[str] = field(default_factory=list)
    audio_files: List[str] = field(default_factory=list)
