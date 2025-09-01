# AI Choose Your Own Adventure Game

A RAG (Retrieval-Augmented Generation) powered interactive storytelling game supporting both **Ollama** (local LLM) and **OpenAI** (cloud LLM) with **Qdrant** (local vector database) for persistent chat history. The game features dynamic character creation, story selection, and immersive gameplay with multiple branching narratives.

## Prerequisites

- Python 3.8+
- Docker Desktop (for Qdrant)
- **AI Provider** (choose one):
  - **Ollama**: Free local AI - Install from [ollama.com](https://ollama.com)
  - **OpenAI**: Cloud AI - Requires API key from [platform.openai.com](https://platform.openai.com)

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd AI-Choose-Your-Own-Adventure-Game

# Run setup script
python setup_ai_config.py
```

### 2. Configure AI Provider
Copy `.env.example` to `.env` and configure your preferred AI provider:

**For Ollama (Local AI):**
```bash
AI_PROVIDER=ollama
OLLAMA_MODEL=gemma3:12b
OLLAMA_BASE_URL=http://localhost:11434
```

**For OpenAI (Cloud AI):**
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Database
```bash
docker-compose up -d
```

### 5. Test Configuration
```bash
python test_ai_config.py
```

### 6. Start Game
```bash
# Command line interface
python main.py

# Or web API server
python api_server.py
```

## AI Provider Configuration

The game supports two AI providers that can be switched via environment variables:

### Ollama (Local AI) - Recommended for Privacy
- **Pros**: Free, private, runs offline, no API costs
- **Cons**: Requires local installation, uses system resources
- **Setup**: 
  1. Install Ollama from [ollama.com](https://ollama.com)
  2. Run `ollama pull gemma3:12b`
  3. Set `AI_PROVIDER=ollama` in `.env`

### OpenAI (Cloud AI) - Recommended for Performance  
- **Pros**: Fast responses, high quality, no local resources needed
- **Cons**: Requires API key, costs money, sends data to OpenAI
- **Setup**:
  1. Get API key from [platform.openai.com](https://platform.openai.com)
  2. Set `AI_PROVIDER=openai` and `OPENAI_API_KEY=your_key` in `.env`

### Switching Providers
Change the `AI_PROVIDER` variable in your `.env` file:
```bash
# Use Ollama
AI_PROVIDER=ollama

# Use OpenAI  
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

Restart the game after changing providers.

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

## Manual Setup Instructions (Alternative)

If you prefer to set up manually instead of using the setup script:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `langchain` and `langchain-ollama` for Ollama LLM integration  
- `langchain-openai` for OpenAI integration
- `qdrant-client` for vector database operations
- `sentence-transformers` for embeddings
- `python-dotenv` for environment configuration

### 2. Start Qdrant Database

```bash
docker-compose up -d
```

### 3. Configure AI Provider

**For Ollama:**
```bash
# Install Ollama from https://ollama.com
ollama pull gemma3:12b
ollama list  # Verify installation
```

**For OpenAI:**
- Get API key from [platform.openai.com](https://platform.openai.com)
- Set `OPENAI_API_KEY` in your `.env` file

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

This RAG-powered adventure game supports flexible AI provider configuration:

### AI Provider Options
1. **Ollama** (Local) - Gemma3:12b for private, offline AI storytelling
2. **OpenAI** (Cloud) - GPT-4 models for high-performance AI storytelling

### Core Components
1. **AI Language Model** - Either Ollama or OpenAI for dynamic story generation
2. **Qdrant Vector Database** - Local vector storage for conversation history with semantic search
3. **Sentence Transformers** - Local embeddings for semantic similarity
4. **LangChain** - Orchestrates the conversation flow and memory

### Architecture Benefits

#### Ollama Configuration:
- ✅ **Fully Local** - No external API calls or costs
- ✅ **Privacy** - All data stays on your machine  
- ✅ **Offline** - Works without internet connection
- ✅ **Free** - No API costs

#### OpenAI Configuration:
- ✅ **High Performance** - Fast, high-quality responses
- ✅ **Reliable** - Cloud-based availability
- ✅ **Advanced** - Access to latest GPT models
- ✅ **Scalable** - No local resource requirements

#### Both Configurations:
- ✅ **Semantic Memory** - Similar conversations can be recalled contextually
- ✅ **Session Persistence** - Continue adventures across sessions

## Files in This Project

### Active Game Files

- `ai_config.py` - AI provider configuration and switching logic
- `api_server.py` - FastAPI server providing REST API for the frontend
- `main.py` - Core game logic with session management and character creation
- `stories.json` - Story definitions and metadata for all available adventures
- `docker-compose.yml` - Qdrant database configuration
- `requirements.txt` - Python dependencies with both Ollama and OpenAI support
- `.env` / `.env.example` - Environment configuration for AI provider switching

### Configuration & Testing Scripts

- `setup_ai_config.py` - Interactive setup script for AI provider configuration
- `test_ai_config.py` - Test script to verify AI provider connections
- `scripts/start_game.py` - Startup script that checks dependencies and launches main.py
- `scripts/setup.py` - Setup script for initial environment configuration
- `scripts/clear_game_data.py` - Script to clear/manage saved game data

### Utility Scripts (`scripts/`)

- `scripts/test_ollama.py` - Test script to verify Ollama installation

### Legacy Files (`scripts/legacy/`)

- `scripts/legacy/main_qdrant.py` - Previous version using Qdrant + Ollama
- `scripts/legacy/main_backup.py` - Backup version for reference
- `scripts/legacy/main_simple.py` - Simple version without advanced features

## Configuration

The game uses environment variables for configuration. Create a `.env` file or set these variables:

### AI Provider Settings
```bash
# Choose your AI provider
AI_PROVIDER=ollama  # or "openai"

# Ollama settings (if using Ollama)
OLLAMA_MODEL=gemma3:12b
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI settings (if using OpenAI)  
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Database Settings
```bash
# Qdrant configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

You can modify these in your `.env` file as needed.

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
