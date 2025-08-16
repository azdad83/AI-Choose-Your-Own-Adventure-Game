import os
import time
import json
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain_ollama import OllamaLLM
import requests

class SimpleGameMemory:
    """Simple memory class for the game without complex LangChain dependencies."""
    
    def __init__(self, session_id: str, qdrant_client: QdrantClient):
        self.session_id = session_id
        self.client = qdrant_client
        self.collection_name = "cyoa_chat_history"
        self._ensure_collection()
        self.conversation_history = []
        
    def _ensure_collection(self):
        """Ensure the collection exists in Qdrant."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1, distance=Distance.COSINE)  # Minimal vector for simple storage
                )
                print(f"Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection: {e}")
    
    def add_interaction(self, human_input: str, ai_response: str):
        """Add a human-AI interaction to memory."""
        try:
            # Store in local memory
            self.conversation_history.append({
                "human": human_input,
                "ai": ai_response,
                "timestamp": time.time()
            })
            
            # Store in Qdrant (simplified)
            point = PointStruct(
                id=str(len(self.conversation_history)),
                vector=[0.0],  # Dummy vector for simple storage
                payload={
                    "session_id": self.session_id,
                    "human": human_input,
                    "ai": ai_response,
                    "timestamp": time.time()
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        except Exception as e:
            print(f"Error adding interaction: {e}")
    
    def get_context(self, last_n: int = 5) -> str:
        """Get recent conversation context."""
        if not self.conversation_history:
            return ""
        
        recent = self.conversation_history[-last_n:] if len(self.conversation_history) > last_n else self.conversation_history
        context = []
        
        for interaction in recent:
            context.append(f"Human: {interaction['human']}")
            context.append(f"AI: {interaction['ai']}")
        
        return "\n".join(context)
    
    def clear(self):
        """Clear conversation history."""
        self.conversation_history = []
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector={
                    "filter": {
                        "must": [
                            {"key": "session_id", "match": {"value": self.session_id}}
                        ]
                    }
                }
            )
            print(f"Cleared chat history for session: {self.session_id}")
        except Exception as e:
            print(f"Error clearing history: {e}")

def test_connections():
    """Test if all services are running."""
    print("Testing connections...")
    
    # Test Qdrant
    try:
        qdrant_client = QdrantClient(host="localhost", port=6333)
        qdrant_client.get_collections()
        print("✅ Qdrant connection successful")
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False, None
    
    # Test Ollama
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama connection successful")
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False, None
    
    return True, qdrant_client

def create_prompt(chat_history: str, human_input: str) -> str:
    """Create the prompt for the LLM."""
    return f"""You are the guide of a mystical journey in the Whispering Woods. 
A traveler named Elara seeks the lost Gem of Serenity. 
You must navigate her through challenges, choices, and consequences, 
dynamically adapting the tale based on the traveler's decisions. 

Rules:
1. Start by asking the player to choose weapons that will be used later
2. Have paths that lead to success and others to death
3. If the user dies, end with "The End."
4. Keep responses engaging but concise (2-3 paragraphs)
5. Always end with clear choices

Recent conversation:
{chat_history}