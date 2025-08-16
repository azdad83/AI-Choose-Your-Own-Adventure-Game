# AI Choose Your Own Adventure Game

A RAG (Retrieval-Augmented Generation) powered interactive storytelling game using **Ollama** (local LLM) and **Qdrant** (local vector database) for persistent chat history.

## Prerequisites

- Python 3.8+
- Docker Desktop (for Qdrant)
- Ollama with Llama3 model installed

## Setup Instructions

### 1. Virtual Environment (✅ Already Done)
You've already created and activated the virtual environment.

### 2. Install Dependencies (✅ Already Done)
The required packages have been installed:
- `langchain` and `langchain-ollama` for LLM orchestration
- `qdrant-client` and `langchain-qdrant` for vector database
- `sentence-transformers` for embeddings

### 3. Start Qdrant Database

**Option A: Using Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option B: Manual Docker Command**
```bash
docker run -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

### 4. Verify Ollama is Running

Check if Ollama is running and has Llama3:
```bash
ollama list
```

If Llama3 is not installed:
```bash
ollama pull llama3:latest
```

## Running the Game

### Quick Start
```bash
python start_game.py
```

This script will:
1. Check if Docker is running
2. Start Qdrant if not already running
3. Verify Ollama is accessible
4. Launch the game

### Manual Start
```bash
# Ensure Qdrant is running
docker-compose up -d

# Run the game
python main_qdrant.py
```

## How It Works

This RAG agent now uses a **completely local setup**:

1. **Ollama with Llama3** - Local LLM for generating dynamic story content
2. **Qdrant Vector Database** - Local vector storage for conversation history with semantic search
3. **Sentence Transformers** - Local embeddings for semantic similarity
4. **LangChain** - Orchestrates the conversation flow and memory

### Architecture Benefits:
- ✅ **Fully Local** - No external API calls or costs
- ✅ **Privacy** - All data stays on your machine
- ✅ **Fast** - Local processing with persistent memory
- ✅ **Semantic Memory** - Similar conversations can be recalled contextually

## Files in This Project

### Active Game Files
- `main.py` - Main game script with session management and mixed response types
- `start_game.py` - Startup script that checks dependencies and launches main.py
- `clear_game_data.py` - Script to clear/manage saved game data
- `clear_data.bat` - Windows batch script for easy data clearing
- `docker-compose.yml` - Qdrant database configuration
- `requirements.txt` - Python dependencies

### Legacy Files (Old Versions)
- `main_qdrant.py` - Previous version using Qdrant + Ollama
- `main_improved.py` - Improved Cassandra version (legacy)
- `main_simple.py` - Simple Cassandra version (legacy)
- `main_ollama.py` - Test Ollama version (legacy)
- `/legacy/` - Folder containing old Cassandra/OpenAI versions

## Configuration

The game uses these default settings:
- **Ollama Model**: `llama3:latest`
- **Qdrant Host**: `localhost:6333`
- **Embeddings**: `all-MiniLM-L6-v2` (384 dimensions)

You can modify these in `main_qdrant.py` if needed.

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
ollama run llama3:latest "Hello, world!"
```

### Python Package Issues
```bash
# Reinstall packages
pip install -r requirements.txt
```

## Game Features

- Dynamic storytelling with local AI (Llama3)
- Persistent conversation history with semantic search
- Multiple branching paths leading to success or failure
- Weapon selection system affecting gameplay
- Death scenarios with proper game endings
- Session-based memory that persists across restarts
- **Continue existing adventures or start new ones**
- **Character name input and persistence**
- **Mixed response types**: 3 AI-suggested choices + 1 custom action option
- **Turn tracking**: Minimum 10 turns before death is possible

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
- Session IDs are generated automatically
- Character names are stored and retrieved with sessions
