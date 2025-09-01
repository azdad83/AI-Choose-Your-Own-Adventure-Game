#!/usr/bin/env python3
"""
Clear all Qdrant collections to fix vector dimension mismatch
"""

from qdrant_client import QdrantClient
from ai_config import config

def clear_collections():
    """Delete all collections in Qdrant"""
    client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
    
    try:
        collections = client.get_collections().collections
        print(f"Found {len(collections)} collections:")
        
        for collection in collections:
            print(f"  - {collection.name}")
            client.delete_collection(collection.name)
            print(f"    ✓ Deleted {collection.name}")
        
        print("✅ All collections cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing collections: {e}")

if __name__ == "__main__":
    clear_collections()