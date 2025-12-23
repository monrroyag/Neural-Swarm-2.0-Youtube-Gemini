# Neural Swarm v2.0 - Modular Architecture

## Overview
Neural Swarm is a professional video production orchestration system powered by Google Gemini. It uses 15 specialized agents divided into 5 departments to handle everything from trend hunting to SEO optimization.

## Directory Structure
-   `app/main.py`: Entry point for the FastAPI application.
-   `app/core/`: Infrastructure components (config, database, websockets, utils).
-   `app/agents/`: Specialized AI agents grouped by department.
-   `app/models/`: Shared data models (`ProjectContext`).
-   `app/orchestrator/`: The 4-phase pipeline coordination logic.
-   `app/templates/`: UI components.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your API key in `app/core/config.py`.
3. Run the application:
   ```bash
   uvicorn neural_swarm.app.main:app --reload
   ```

## Usage
-   Access the dashboard at `http://localhost:8000`.
-   Real-time logs and agent data updates are broadcasted via WebSockets.
-   Generated media is stored in `studio_audio/` and `studio_images/`.
