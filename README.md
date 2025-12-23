# 🧠 Neural Swarm v2.0 - YouTube AI Agentic Production

Neural Swarm v2.0 is an advanced, multi-agent AI framework designed to automate the entire YouTube video production pipeline. Built on top of the Google Gemini 3.0 & 2.5 ecosystem, it orchestrates 15 specialized agents organized into 5 distinct departments to transform a simple niche or topic into a fully realized video script with professional visual prompts, native TTS audio, and SEO optimization.

![Neural Swarm v2.0 Footer](https://img.shields.io/badge/Neural_Swarm-v2.0-purple?style=for-the-badge)
![Aguntín Arellano](https://img.shields.io/badge/Created_by-Agust%C3%ADn_Arellano-blue?style=for-the-badge)

## 🏢 Departmental Architecture

The "Swarm" is organized into specialized departments, each responsible for a critical phase of production:

### 1. 🏢 Strategy & Direction
*   **📡 Trend Hunter**: Analyzes niches to find high-potential viral topics.
*   **👥 Audience Profiler**: Defines the target demographic and psychological triggers.
*   **📋 Project Manager**: Synthesizes strategy into a "Project Bible" that guides all agents.

### 2. 🔎 Intelligence & Research
*   **🧠 Deep Researcher**: Performs technical and historical research on the selected topic.
*   **📰 Investigative Journalist**: Finds compelling angles, stories, and data points.
*   **✅ Fact Checker**: Rigorously verifies all claims to ensure accuracy.

### 3. ✍️ Narrative & Scripting
*   **🏗️ Script Architect**: Designs the structural arc of the video (Hook, Body, CTA).
*   **📝 Lead Writer**: Crafts the final conversational script in the project's language.
*   **🪝 Hook Master**: Optimizes the first 15 seconds for maximum retention.
*   **🎭 Comedy Specialist**: Infuses wit and engaging humor into the narrative.

### 4. 🎨 Art & Visuals
*   **🎭 Art Director**: Establishes the visual style manual (colors, lighting, composition).
*   **🖼️ Prompt Engineer**: Generates technical prompts for the **Nano Banana** image engines.
*   **🎯 Thumbnail Strategist**: Concepts high-click-rate thumbnail designs.

### 5. 🔊 Post-Production & SEO
*   **🎤 Audio Director**: Configures the **Voice Studio** with native Gemini TTS.
*   **🏷️ SEO Optimizer**: Generates viral titles, optimized descriptions, and meta-tags.

---

## 🚀 Key Features

*   **⚡ Gemini 3.0 & 2.5 Integration**: Leverages the latest models like `gemini-3-flash-preview` for speed and `gemini-3-pro-preview` for deep reasoning.
*   **🍌 Advanced Image Engines**: Support for **Nano Banana** (`gemini-2.5-flash-image`) and **Nano Banana Pro** (`gemini-3-pro-image-preview`).
*   **🎙️ Voice Studio**: Access to 30+ native Gemini text-to-speech voices with fine-tuned emotional control.
*   **🌐 Internationalization (I18n)**: Fully translatable UI and agent prompts (currently supporting Spanish/English).
*   **⚙️ Live Agent Editor**: Modify agent instructions and names directly in the browser without restarting the server.
*   **🕵️ Audit Panel**: A specialized "Quality Control" panel that evaluates scripts before finalization.

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/monrroyag/Neural-Swarm-2.0-Youtube-Gemini.git
    cd Neural-Swarm-2.0-Youtube-Gemini
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    python run.py
    ```

4.  **Configuration**: Navigate to the **Settings** tab in the UI to enter your `GEMINI_API_KEY` and select your preferred models.

## 📁 Project Structure

```text
neural_swarm/
├── app/
│   ├── core/           # Infrastructure (Config, Settings, Database, AI)
│   ├── agents/         # The 15 Specialized Swarm Agents
│   ├── orchestrator/   # Swarm coordination logic
│   ├── models/         # Pydantic data models
│   ├── i18n/           # Language packs (es.json, etc.)
│   └── templates/      # High-end Alpine.js + Tailwind UI
├── studio_audio/       # Project audio exports
├── studio_images/      # AI generated visual assets
├── settings.json       # Persisted user configuration
└── run.py              # Application entry point
```

## 🤝 Contribution

Created with ❤️ by [Agustín Arellano](https://github.com/monrroyag).

If you have suggestions or want to improve the Swarm, feel free to open a PR or reach out!

---
**Neural Swarm v2.0** - *The future of AI-driven content creation.*
