# Utility Scripts

This directory contains utility scripts for the AI Choose Your Own Adventure Game.

## Scripts

### `setup.py`
Initial setup script that:
- Checks for Docker installation
- Verifies Ollama is running
- Ensures required models are available
- Sets up the development environment

**Usage:**
```bash
python scripts/setup.py
```

### `start_game.py`
Game launcher that:
- Checks all dependencies
- Starts Qdrant database if needed
- Launches the main game
- Handles error recovery

**Usage:**
```bash
python scripts/start_game.py
```

### `clear_game_data.py`
Data management script that:
- Clears saved game sessions
- Resets the Qdrant database
- Preserves story definitions
- Provides data cleanup options

**Usage:**
```bash
python scripts/clear_game_data.py
```

### `test_ollama.py`
Testing script that:
- Verifies Ollama service is running
- Tests model availability
- Checks API connectivity
- Validates AI model responses

**Usage:**
```bash
python scripts/test_ollama.py
```

## Legacy Directory

The `legacy/` subdirectory contains previous versions of the main game script:

- `main_backup.py` - Backup version for reference
- `main_qdrant.py` - Previous Qdrant-focused implementation  
- `main_simple.py` - Simplified version without advanced features

These are kept for historical reference and rollback purposes if needed.