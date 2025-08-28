#!/usr/bin/env python3
"""
Clear Game Data Script
======================

This script clears all saved adventure data from the Qdrant vector database.
Use this to reset your game progress or clean up old sessions.

Note: Story definitions are now stored in stories.json and are not affected by this script.

Usage:
    python clear_game_data.py

Features:
- Connects to Qdrant database
- Lists existing game sessions (each stored in separate collections)
- Allows selective or complete data clearing
- Provides confirmation prompts for safety
- Stories remain safe in stories.json file
"""

import os
import sys
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "cyoa_chat_history"

def test_qdrant_connection(client: QdrantClient) -> bool:
    """Test if Qdrant is accessible."""
    try:
        client.get_collections()
        print("✓ Qdrant connection successful")
        return True
    except Exception as e:
        print(f"✗ Qdrant connection failed: {e}")
        return False

def get_all_sessions(client: QdrantClient) -> List[str]:
    """Get all unique session IDs by looking for session-specific collections."""
    try:
        # Get all collections
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        # Filter for chat history collections (format: chat_history_<session_id>)
        session_ids = []
        session_details = {}
        
        for name in collection_names:
            if name.startswith('chat_history_adventure_session_'):
                # Extract session ID from collection name
                session_id = name.replace('chat_history_', '')
                session_ids.append(session_id)
                
                # Get session details from the collection
                try:
                    search_result = client.scroll(
                        collection_name=name,
                        limit=1000,
                        with_payload=True
                    )
                    
                    session_details[session_id] = {
                        'messages': len(search_result[0]),
                        'character_name': 'Unknown',
                        'last_activity': 0,
                        'collection_name': name
                    }
                    
                    # Extract character name and last activity from messages
                    for point in search_result[0]:
                        if 'character_name' in point.payload:
                            session_details[session_id]['character_name'] = point.payload['character_name']
                        
                        if 'timestamp' in point.payload:
                            if point.payload['timestamp'] > session_details[session_id]['last_activity']:
                                session_details[session_id]['last_activity'] = point.payload['timestamp']
                
                except Exception as e:
                    print(f"Warning: Could not read details for session {session_id}: {e}")
                    session_details[session_id] = {
                        'messages': 0,
                        'character_name': 'Unknown',
                        'last_activity': 0,
                        'collection_name': name
                    }
        
        return session_ids, session_details
    
    except Exception as e:
        print(f"Error retrieving sessions: {e}")
        return [], {}

def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display."""
    if timestamp == 0:
        return "Unknown"
    
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def display_sessions(session_ids: List[str], session_details: dict) -> None:
    """Display all sessions with details."""
    if not session_ids:
        print("No game sessions found in the database.")
        return
    
    print(f"\nFound {len(session_ids)} game session(s):")
    print("=" * 80)
    
    for i, session_id in enumerate(session_ids, 1):
        details = session_details.get(session_id, {})
        short_id = session_id[-12:] if len(session_id) > 12 else session_id
        
        print(f"{i}. Session: {short_id}")
        print(f"   Character: {details.get('character_name', 'Unknown')}")
        print(f"   Messages: {details.get('messages', 0)}")
        print(f"   Last Activity: {format_timestamp(details.get('last_activity', 0))}")
        print("-" * 40)

def clear_specific_session(client: QdrantClient, session_id: str, session_details: dict) -> bool:
    """Clear a specific session by deleting its collection."""
    try:
        collection_name = session_details[session_id]['collection_name']
        # Delete the entire collection for this session
        client.delete_collection(collection_name=collection_name)
        print(f"✓ Successfully cleared session: {session_id[-12:]} (collection: {collection_name})")
        return True
    except Exception as e:
        print(f"✗ Error clearing session {session_id[-12:]}: {e}")
        return False

def clear_all_sessions(client: QdrantClient, session_details: dict) -> bool:
    """Clear all game sessions by deleting their collections."""
    try:
        deleted_count = 0
        for session_id, details in session_details.items():
            try:
                collection_name = details['collection_name']
                client.delete_collection(collection_name=collection_name)
                deleted_count += 1
                print(f"✓ Deleted collection: {collection_name}")
            except Exception as e:
                print(f"✗ Error deleting collection {details['collection_name']}: {e}")
        
        print(f"✓ Successfully deleted {deleted_count} session collection(s)")
        return deleted_count > 0
    except Exception as e:
        print(f"✗ Error clearing all sessions: {e}")
        return False

def get_user_confirmation(message: str) -> bool:
    """Get user confirmation for destructive operations."""
    while True:
        response = input(f"{message} (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        print("Please enter 'y' for yes or 'n' for no.")

def main():
    print("🧹 Choose Your Own Adventure - Game Data Cleaner")
    print("=" * 55)
    
    try:
        # Initialize Qdrant client
        print("Connecting to Qdrant...")
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Test connection
        if not test_qdrant_connection(qdrant_client):
            print("\nPlease ensure Qdrant is running:")
            print("Run: docker-compose up -d")
            return
        
        # Check if any session collections exist
        session_ids, session_details = get_all_sessions(qdrant_client)
        
        if not session_ids:
            print("No game sessions found. Database is already clean!")
            return
        
        if not session_ids:
            print("No game sessions found. Database is already clean!")
            return
        
        # Display sessions
        display_sessions(session_ids, session_details)
        
        # Present options
        print("\nClearing Options:")
        print("1. Clear specific session")
        print("2. Clear all sessions")
        print("3. Exit without clearing")
        
        while True:
            choice = input("\nChoose an option (1, 2, or 3): ").strip()
            
            if choice == '1':
                # Clear specific session
                if len(session_ids) == 1:
                    selected_session = session_ids[0]
                else:
                    print(f"\nSelect session to clear (1-{len(session_ids)}):")
                    while True:
                        try:
                            session_choice = int(input("Session number: ")) - 1
                            if 0 <= session_choice < len(session_ids):
                                selected_session = session_ids[session_choice]
                                break
                            print(f"Please enter a number between 1 and {len(session_ids)}")
                        except ValueError:
                            print("Please enter a valid number")
                
                # Confirm deletion
                short_id = selected_session[-12:]
                character = session_details[selected_session].get('character_name', 'Unknown')
                
                if get_user_confirmation(f"Clear session {short_id} (Character: {character})?"):
                    if clear_specific_session(qdrant_client, selected_session, session_details):
                        print("\n✓ Session cleared successfully!")
                    else:
                        print("\n✗ Failed to clear session.")
                else:
                    print("\n👍 Session preserved.")
                break
                
            elif choice == '2':
                # Clear all sessions
                total_messages = sum(details.get('messages', 0) for details in session_details.values())
                
                print(f"\n⚠️  WARNING: This will permanently delete:")
                print(f"   - {len(session_ids)} game session(s)")
                print(f"   - {total_messages} total message(s)")
                print("   - All character names and progress")
                
                if get_user_confirmation("Are you SURE you want to clear ALL game data?"):
                    if clear_all_sessions(qdrant_client, session_details):
                        print("\n✓ All game data cleared successfully!")
                    else:
                        print("\n✗ Failed to clear all data.")
                else:
                    print("\n👍 All data preserved.")
                break
                
            elif choice == '3':
                print("\n👋 Exiting without making changes.")
                break
                
            else:
                print("Please enter 1, 2, or 3.")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()