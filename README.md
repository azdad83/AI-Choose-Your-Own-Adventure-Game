# AI Choose Your Own Adventure Game

A RAG (Retrieval-Augmented Generation) powered interactive storytelling game using **Ollama** (local LLM) and **Qdrant** (local vector database) for persistent chat history. The game features dynamic character creation, story selection, and immersive gameplay with multiple branching narratives.

## Prerequisites

- Python 3.8+
- Docker Desktop (for Qdrant)
- Ollama with Gemma3:12b model installed

## Game Features

### Core Gameplay

- **Dynamic Story Selection**: Choose from 6 unique adventures (Fantasy, Noir Detective, Space Exploration, Medieval Court, Horror Mansion, Pirate Adventure)
- **Character Creation System**: 3-step character setup with predefined weapon, skill, and tool options
- **AI-Powered Storytelling**: Dynamic narrative generation focused on story progression and player choices
- **Intelligent Choice System**: Each turn offers 3 AI-generated choices plus custom action option
- **Session Persistence**: Continue previous adventures or start fresh with full context retention
- **Turn-Based Safety**: Minimum 10 turns before death scenarios become possible

### Game Flow

1. **Game Selection**: Continue existing adventure or start new
2. **Story Selection**: Choose from available story genres and difficulties
3. **Character Creation**:
   - Enter character name
   - Select starting weapon (4 predefined thematic options)
   - Select starting skill (4 predefined story-appropriate options)
   - Select starting tool (4 predefined adventure-specific options)
4. **Adventure Gameplay**: Interactive storytelling with choice-driven narrative
5. **Session Management**: Progress automatically saved after each turn

### Available Stories

- **Mystical Woods Adventure** (Fantasy, Easy) - Hunt for the Gem of Serenity
- **Noir Detective Mystery** (Noir, Medium) - 1940s NYC crime investigation
- **Deep Space Explorer** (Sci-Fi, Hard) - Command starship on alien frontier
- **Medieval Court Intrigue** (Historical, Medium) - Navigate royal politics
- **Haunted Mansion Mystery** (Horror, Hard) - Survive supernatural encounters
- **Caribbean Pirate Adventure** (Adventure, Medium) - Treasure hunting on high seas

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:

- `langchain` and `langchain-ollama` for LLM orchestration
- `qdrant-client` for vector database operations
- `sentence-transformers` for embeddings

### 2. Start Qdrant Database

**Option A: Using Docker Compose (Recommended)**

```bash
docker-compose up -d
```

**Option B: Manual Docker Command**

```bash
docker run -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

### 3. Install and Configure Ollama

Install Ollama and the required model:

```bash
# Install Ollama (visit https://ollama.com for platform-specific instructions)

# Pull the required model
ollama pull gemma3:12b
```

Verify Ollama is running:

```bash
ollama list
```

## Running the Game

### Quick Start

```bash
python scripts/start_game.py
```

This startup script will:

1. Check if Docker is running
2. Start Qdrant if not already running
3. Verify Ollama is accessible
4. Launch the main game

### Manual Start

```bash
# Ensure Qdrant is running
docker-compose up -d

# Run the game directly
python main.py
```

## How It Works

This RAG agent uses a **completely local setup**:

1. **Ollama with Gemma3:12b** - Local LLM for generating dynamic story content and character choices
2. **Qdrant Vector Database** - Local vector storage for conversation history with semantic search
3. **Sentence Transformers** - Local embeddings for semantic similarity
4. **LangChain** - Orchestrates the conversation flow and memory

### Architecture Benefits

- ✅ **Fully Local** - No external API calls or costs
- ✅ **Privacy** - All data stays on your machine
- ✅ **Fast** - Local processing with persistent memory
- ✅ **Semantic Memory** - Similar conversations can be recalled contextually

## Files in This Project

### Active Game Files

- `api_server.py` - FastAPI server providing REST API for the frontend
- `main.py` - Core game logic with session management and character creation
- `stories.json` - Story definitions and metadata for all available adventures
- `docker-compose.yml` - Qdrant database configuration
- `requirements.txt` - Python dependencies

### Utility Scripts (`scripts/`)

- `scripts/start_game.py` - Startup script that checks dependencies and launches main.py
- `scripts/setup.py` - Setup script for initial environment configuration
- `scripts/clear_game_data.py` - Script to clear/manage saved game data
- `scripts/test_ollama.py` - Test script to verify Ollama installation

### Legacy Files (`scripts/legacy/`)

- `scripts/legacy/main_qdrant.py` - Previous version using Qdrant + Ollama
- `scripts/legacy/main_backup.py` - Backup version for reference
- `scripts/legacy/main_simple.py` - Simple version without advanced features
- `test_ollama.py` - Ollama connection testing script

## Configuration

The game uses these default settings:

- **Ollama Model**: `gemma3:12b`
- **Qdrant Host**: `localhost:6333`
- **Embeddings**: `all-MiniLM-L6-v2` (384 dimensions)

You can modify these in `main.py` if needed.

## Troubleshooting

### Qdrant Issues

```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# View Qdrant logs
docker-compose logs qdrant

# Restart Qdrant
docker-compose restart
```

### Ollama Issues

```bash
# Check Ollama status
ollama list

# Test Ollama
ollama run gemma3:12b "Hello, world!"
```

### Python Package Issues

```bash
# Reinstall packages
pip install -r requirements.txt
```

## Character Creation Flow

The character creation system guides players through a 3-step process:

1. **Character Name**: Players enter a unique name for their character
2. **Weapon Selection**: Choose from 4 predefined thematic weapons specific to the story genre/setting
3. **Skill Selection**: Choose from 4 predefined skills appropriate for the chosen story
4. **Tool Selection**: Choose from 4 predefined useful tools that complement the adventure

Each selection is story-specific and defined in the JSON configuration, ensuring balanced and thematic character builds that influence gameplay mechanics.

## Managing Game Data

### Clear All Game Progress

To reset your adventure progress and clear all saved data:

**Windows:**

```cmd
.\clear_data.bat
```

**Or manually:**

```bash
python clear_game_data.py
```

The clear script provides options to:

- View all existing game sessions with details
- Clear specific sessions selectively
- Clear all game data completely
- Safe confirmation prompts to prevent accidental deletion

### Session Management

- Games automatically save progress after each turn
- Multiple characters can have separate adventures
- Session IDs are generated automatically with timestamps
- Character names and story selections are stored and retrieved with sessions
- Character equipment choices persist throughout the adventure

## Frontend Development

A Next.js frontend is included in the `frontend/` directory with ShadCN UI components pre-installed for future web interface development. See `FRONTEND_DEVELOPMENT_PLAN.md` for implementation details.
