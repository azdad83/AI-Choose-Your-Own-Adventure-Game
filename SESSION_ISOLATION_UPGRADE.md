# Session Isolation Upgrade

## Problem Addressed
Previously, all game sessions shared the same Qdrant collection (`cyoa_chat_history`), which caused potential crossover between different games when users loaded "existing" games.

## Solution Implemented
**Session-Specific Collections**: Each game session now gets its own dedicated Qdrant collection, providing complete isolation between games.

## Changes Made

### 1. Updated QdrantChatMessageHistory Class
- **Location**: `main.py` - `QdrantChatMessageHistory.__init__()`
- **Change**: Modified constructor to create unique collection names per session
- **New Behavior**: 
  - If no `collection_name` provided, automatically creates: `chat_history_{session_id}`
  - Example: `chat_history_adventure_session_1693123456`

### 2. Updated Session Discovery
- **Location**: `main.py` - `check_for_existing_games()`
- **Change**: Now searches for collections starting with `chat_history_adventure_session_`
- **New Behavior**: 
  - Scans all Qdrant collections instead of scanning within one collection
  - Extracts session IDs from collection names
  - Returns list of actual session IDs found

### 3. Updated Clear Game Data Script
- **Location**: `clear_game_data.py`
- **Changes**: 
  - `get_all_sessions()`: Now finds sessions by scanning collection names
  - `clear_specific_session()`: Deletes entire collection instead of filtering points
  - `clear_all_sessions()`: Deletes multiple collections instead of one
- **New Behavior**: Complete session isolation and cleanup

### 4. Updated Session Instantiation
- **Location**: `main.py` - Game initialization
- **Change**: Removed hardcoded collection names
- **New Behavior**: 
  - `QdrantChatMessageHistory(session_id, qdrant_client)` - Uses default session-specific naming
  - No more `collection_name="cyoa_chat_history"` parameter

## Benefits

### ✅ Complete Session Isolation
- Each game session is completely independent
- No risk of message crossover between games
- Clean separation of game data

### ✅ Better Session Management
- Easy to identify and manage individual game sessions
- Clear mapping between session ID and storage
- Simplified backup/restore of specific games

### ✅ Enhanced Performance
- Smaller collections per session = faster queries
- No need for complex filtering by session_id
- Improved scalability for many concurrent sessions

### ✅ Cleaner Data Model
- One session = One collection
- Intuitive data organization
- Easier debugging and maintenance

## Collection Naming Convention

```
Stories Collection:     story_definitions
Session Collections:    chat_history_adventure_session_{timestamp}
```

**Example Session Collections:**
- `chat_history_adventure_session_1693123456`
- `chat_history_adventure_session_1693124567`
- `chat_history_adventure_session_1693125678`

## Backward Compatibility

⚠️ **Breaking Change**: This update is NOT backward compatible with existing games stored in the old `cyoa_chat_history` collection.

**Migration Path:**
1. Use the old clear script to backup existing games if needed
2. Clear old data using: `python clear_game_data.py`
3. Start fresh with the new session isolation system

## Testing the Changes

### Test Session Creation:
1. Start a new game - should create `chat_history_adventure_session_{timestamp}`
2. Start another new game - should create a different collection
3. Verify collections exist independently in Qdrant

### Test Session Loading:
1. Create multiple game sessions
2. Exit and restart the game
3. Should see list of available sessions
4. Loading a session should access only that session's data

### Test Data Clearing:
1. Run `python clear_game_data.py`
2. Should list all session collections
3. Can clear individual sessions or all sessions
4. Story definitions should remain untouched

## Impact on Performance

### Positive Impacts:
- **Faster Queries**: Smaller collections = faster searches
- **Better Concurrency**: Independent collections = less locking
- **Cleaner Scaling**: Linear growth with sessions

### Considerations:
- **More Collections**: Each session creates a new collection
- **Collection Overhead**: Minimal metadata overhead per collection
- **Qdrant Limits**: Check Qdrant documentation for collection limits

## Summary

This upgrade provides **complete session isolation** ensuring that each game session is entirely independent. Users can now safely play multiple games without any risk of data crossover, and the system provides better performance and easier management of game sessions.

The new system is more robust, scalable, and provides a cleaner separation of concerns between different game sessions while maintaining the existing user experience.