# Story Management System

## Overview
The game now uses a **simplified JSON-based story management system** instead of storing stories in Qdrant. This makes story management much easier and eliminates duplication issues.

## How It Works

### Story Storage
- **Stories are stored in**: `stories.json`
- **Chat history is stored in**: Qdrant (session-specific collections)
- **No more story database imports needed**

### Adding New Stories
1. Open `stories.json`
2. Add your story following the existing format:
```json
{
    "id": "unique_story_id",
    "name": "Story Display Name",
    "description": "Brief description shown in selector",
    "genre": "fantasy|noir|sci-fi|historical|horror|adventure",
    "difficulty": "easy|medium|hard",
    "estimated_length": "X-Y turns",
    "initial_prompt": "Your story prompt with {character_name} placeholder",
    "setting": "Where the story takes place",
    "themes": ["list", "of", "themes"],
    "author": "Your Name",
    "created_date": "YYYY-MM-DD"
}
```
3. Save the file - changes take effect immediately

### Editing Stories
- Simply edit `stories.json` and save
- No need to restart the game or reimport anything
- Changes are picked up on next game start

### Story Structure
Each story should include:
- **`id`**: Unique identifier (no spaces, use underscores)
- **`name`**: Display name shown in story selector
- **`description`**: Brief description for story selection
- **`genre`**: Used by AI to adapt storytelling style
- **`initial_prompt`**: The specific story setup for the AI
- **`setting`**: Where/when the story takes place
- **`difficulty`**: Affects story complexity
- **`themes`**: Optional tags for categorization

### Benefits of JSON-Based System
✅ **No duplicate imports** - stories can't be accidentally loaded multiple times  
✅ **Easy editing** - just edit the JSON file  
✅ **Version control friendly** - JSON files work great with Git  
✅ **No database management** - no need to clear/reload story collections  
✅ **Immediate updates** - changes take effect on next game start  
✅ **Simpler architecture** - fewer moving parts  

### Migration Notes
- Old `story_loader.py` is no longer needed
- Story collections in Qdrant can be safely deleted
- Chat history collections remain untouched
- All existing game saves continue to work

### File Organization
```
├── stories.json              # All story definitions
├── main.py                  # Main game engine
├── clear_game_data.py       # Clear chat history only
└── README_STORY_MANAGEMENT.md  # This file
```