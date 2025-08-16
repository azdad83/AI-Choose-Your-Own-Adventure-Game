#!/usr/bin/env python3
"""
Clear Game Data Script
======================

This script clears all saved adventure data from the Qdrant vector database.
Use this to reset your game progress or clean up old sessions.

Usage:
    python clear_game_data.py

Features:
- Connects to Qdrant database
- Lists existing game sessions
- Allows selective or complete data clearing
- Provides confirmation prompts for safety
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
    """Get all unique session IDs from the database."""
    try:
        # Get all points from the collection
        search_result = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10000,  # Large limit to get all sessions
            with_payload=True
        )
        
        session_ids = set()
        session_details = {}
        
        for point in search_result[0]:
            if 'session_id' in point.payload:
                session_id = point.payload['session_id']
                session_ids.add(session_id)
                
                # Collect session details
                if session_id not in session_details:
                    session_details[session_id] = {
                        'messages': 0,
                        'character_name': 'Unknown',
                        'last_activity': 0
                    }
                
                session_details[session_id]['messages'] += 1
                
                # Get character name if available
                if 'character_name' in point.payload:
                    session_details[session_id]['character_name'] = point.payload['character_name']
                
                # Track latest timestamp
                if 'timestamp' in point.payload:
                    if point.payload['timestamp'] > session_details[session_id]['last_activity']:
                        session_details[session_id]['last_activity'] = point.payload['timestamp']
        
        return list(session_ids), session_details
    
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

def clear_specific_session(client: QdrantClient, session_id: str) -> bool:
    """Clear a specific session from the database."""
    try:
        # Delete all points for this session
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="session_id",
                        match=MatchValue(value=session_id)
                    )
                ]
            )
        )
        print(f"✓ Successfully cleared session: {session_id[-12:]}")
        return True
    except Exception as e:
        print(f"✗ Error clearing session {session_id[-12:]}: {e}")
        return False

def clear_all_sessions(client: QdrantClient) -> bool:
    """Clear the entire collection."""
    try:
        # Delete the entire collection
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"✓ Successfully deleted collection: {COLLECTION_NAME}")
        
        # Recreate the collection
        from qdrant_client.models import VectorParams, Distance
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"✓ Recreated empty collection: {COLLECTION_NAME}")
        return True
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
        
        # Check if collection exists
        try:
            collections = qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if COLLECTION_NAME not in collection_names:
                print(f"Collection '{COLLECTION_NAME}' does not exist.")
                print("No game data to clear.")
                return
        except Exception as e:
            print(f"Error checking collections: {e}")
            return
        
        # Get all sessions
        session_ids, session_details = get_all_sessions(qdrant_client)
        
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
                    if clear_specific_session(qdrant_client, selected_session):
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
                    if clear_all_sessions(qdrant_client):
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