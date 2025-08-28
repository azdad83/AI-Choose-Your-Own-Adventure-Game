import os
import time
import uuid
import warnings
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from langchain_ollama import OllamaLLM
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import SentenceTransformer
import json

# Suppress LangChain deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")

class QdrantChatMessageHistory(BaseChatMessageHistory):
    """Custom chat message history using Qdrant vector database."""
    
    def __init__(self, session_id: str, qdrant_client: QdrantClient, collection_name: str = "chat_history"):
        self.session_id = session_id
        self.client = qdrant_client
        self.collection_name = collection_name
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self._ensure_collection()
        
    def _ensure_collection(self):
        """Ensure the collection exists in Qdrant."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection: {e}")
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the history."""
        try:
            message_text = message.content
            message_type = "human" if isinstance(message, HumanMessage) else "ai"
            
            # Create embedding
            embedding = self.encoder.encode(message_text).tolist()
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "session_id": self.session_id,
                    "message": message_text,
                    "type": message_type,
                    "timestamp": time.time()
                }
            )
            
            # Upsert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        except Exception as e:
            print(f"Error adding message: {e}")
    
    def store_character_name(self, character_name: str) -> None:
        """Store the character name as metadata in the session."""
        try:
            # Create a special metadata point for character name
            embedding = self.encoder.encode(f"Character name: {character_name}").tolist()
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "session_id": self.session_id,
                    "message": f"Character name: {character_name}",
                    "type": "metadata",
                    "character_name": character_name,
                    "timestamp": time.time()
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        except Exception as e:
            print(f"Error storing character name: {e}")
    
    def get_character_name(self) -> str:
        """Retrieve the character name from the session metadata."""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            # Search for character name metadata
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=self.session_id)
                        ),
                        FieldCondition(
                            key="type",
                            match=MatchValue(value="metadata")
                        )
                    ]
                ),
                limit=10,
                with_payload=True
            )
            
            for point in search_result[0]:
                if "character_name" in point.payload:
                    return point.payload["character_name"]
            
            return "Elara"  # Default fallback
        except Exception:
            return "Elara"  # Default fallback
    
    def clear(self) -> None:
        """Clear all messages for this session."""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            # Delete all points for this session using proper filter format
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=self.session_id)
                        )
                    ]
                )
            )
            print(f"Cleared chat history for session: {self.session_id}")
        except Exception as e:
            print(f"Error clearing messages: {e}")
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve all messages for this session."""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            # Search for all messages in this session
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=self.session_id)
                        )
                    ]
                ),
                limit=1000,
                with_payload=True
            )
            
            # Sort by timestamp and convert to BaseMessage objects
            points = sorted(search_result[0], key=lambda x: x.payload["timestamp"])
            messages = []
            
            for point in points:
                payload = point.payload
                if payload["type"] == "human":
                    messages.append(HumanMessage(content=payload["message"]))
                else:
                    messages.append(AIMessage(content=payload["message"]))
            
            return messages
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []
    
    def has_existing_messages(self) -> bool:
        """Check if there are any existing messages in the chat history."""
        try:
            messages = self.messages
            return len(messages) > 0
        except Exception:
            return False
    
    def get_last_session_summary(self) -> str:
        """Get a summary of the last session for display to user."""
        try:
            messages = self.messages
            if not messages:
                return "No previous adventure found."
            
            # Get the last few messages to show context
            recent_messages = messages[-3:] if len(messages) >= 3 else messages
            summary_parts = []
            
            for msg in recent_messages:
                if isinstance(msg, HumanMessage):
                    summary_parts.append(f"You: {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}")
                else:
                    summary_parts.append(f"Game: {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}")
            
            return "\n".join(summary_parts)
        except Exception:
            return "Unable to load previous adventure summary."

def test_qdrant_connection(client: QdrantClient) -> bool:
    """Test if Qdrant is accessible."""
    try:
        client.get_collections()
        print("✓ Qdrant connection successful")
        return True
    except Exception as e:
        print(f"✗ Qdrant connection failed: {e}")
        return False

def check_for_existing_games(qdrant_client: QdrantClient, collection_name: str = "cyoa_chat_history") -> List[str]:
    """Check for existing game sessions in the database."""
    try:
        # Get all unique session IDs from the collection
        search_result = qdrant_client.scroll(
            collection_name=collection_name,
            limit=1000,
            with_payload=True
        )
        
        session_ids = set()
        for point in search_result[0]:
            if 'session_id' in point.payload:
                session_ids.add(point.payload['session_id'])
        
        return list(session_ids)
    except Exception:
        return []

def get_game_choice() -> str:
    """Get user's choice between continuing existing game or starting new."""
    print("\n" + "=" * 55)
    print("GAME OPTIONS")
    print("=" * 55)
    print("1. Continue existing adventure")
    print("2. Start new adventure")
    print("=" * 55)
    
    while True:
        choice = input("\nChoose an option (1 or 2): ").strip()
        if choice in ['1', '2']:
            return choice
        print("Please enter 1 or 2.")

def get_character_name() -> str:
    """Get the character name from the user for new adventures."""
    print("\n" + "=" * 55)
    print("CHARACTER CREATION")
    print("=" * 55)
    
    while True:
        name = input("Enter your character's name: ").strip()
        if name and len(name) >= 2:
            # Capitalize first letter for consistency
            name = name[0].upper() + name[1:]
            print(f"\n✓ Welcome, {name}, to your adventure!")
            return name
        print("Please enter a name with at least 2 characters.")

def select_existing_session(session_ids: List[str], qdrant_client: QdrantClient) -> str:
    """Let user select from existing sessions."""
    if len(session_ids) == 1:
        return session_ids[0]
    
    print("\nFound multiple previous adventures:")
    print("-" * 40)
    
    for i, session_id in enumerate(session_ids, 1):
        # Create a temporary message history to get summary
        temp_history = QdrantChatMessageHistory(
            session_id=session_id,
            qdrant_client=qdrant_client,
            collection_name="cyoa_chat_history"
        )
        summary = temp_history.get_last_session_summary()
        print(f"{i}. Session: {session_id[-8:]}...")
        print(f"   Last activity: {summary.split(chr(10))[0] if summary else 'No summary available'}")
        print()
    
    while True:
        try:
            choice = int(input(f"Select adventure (1-{len(session_ids)}): "))
            if 1 <= choice <= len(session_ids):
                return session_ids[choice - 1]
            print(f"Please enter a number between 1 and {len(session_ids)}.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    print("Choose Your Own Adventure Game with Ollama & Qdrant!")
    print("=" * 55)
    
    # Configuration
    OLLAMA_MODEL = "gemma3:12b"
    QDRANT_HOST = "localhost"
    QDRANT_PORT = 6333
    
    try:
        # Initialize Qdrant client
        print("Connecting to Qdrant...")
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Test connection
        if not test_qdrant_connection(qdrant_client):
            print("\nPlease ensure Qdrant is running:")
            print("Run: docker-compose up -d")
            return
        
        # Initialize Ollama
        print(f"Initializing Ollama with model: {OLLAMA_MODEL}")
        llm = OllamaLLM(model=OLLAMA_MODEL, base_url="http://localhost:11434")
        
        # Test Ollama connection
        try:
            test_response = llm.invoke("Hello")
            print("✓ Ollama connection successful")
        except Exception as e:
            print(f"✗ Ollama connection failed: {e}")
            print("Please ensure Ollama is running and the llama3:latest model is available")
            return
        
        # Check for existing games
        existing_sessions = check_for_existing_games(qdrant_client)
        SESSION_ID = None
        should_clear_history = True
        character_name = "Elara"  # Default name
        
        if existing_sessions:
            choice = get_game_choice()
            
            if choice == '1':  # Continue existing adventure
                SESSION_ID = select_existing_session(existing_sessions, qdrant_client)
                should_clear_history = False
                print(f"\n✓ Continuing adventure: {SESSION_ID[-12:]}...")
            else:  # Start new adventure
                SESSION_ID = f"adventure_session_{int(time.time())}"
                should_clear_history = True
                character_name = get_character_name()  # Get character name for new game
                print(f"\n✓ Starting new adventure: {SESSION_ID[-12:]}...")
        else:
            # No existing sessions, start new
            SESSION_ID = f"adventure_session_{int(time.time())}"
            character_name = get_character_name()  # Get character name for new game
            print("\n✓ No previous adventures found. Starting new adventure...")
        
        # Initialize chat history with Qdrant
        message_history = QdrantChatMessageHistory(
            session_id=SESSION_ID,
            qdrant_client=qdrant_client,
            collection_name="cyoa_chat_history"
        )
        
        # Clear previous session only if starting new
        if should_clear_history:
            message_history.clear()
            message_history.store_character_name(character_name)  # Store character name
            print("✓ Started fresh adventure")
        else:
            print("✓ Loaded previous adventure")
            # Get character name from existing session
            character_name = message_history.get_character_name()
            print(f"✓ Welcome back, {character_name}!")
            # Show previous context
            previous_messages = message_history.messages
            if previous_messages:
                print("\n📖 Previous adventure context:")
                print("-" * 40)
                summary = message_history.get_last_session_summary()
                print(summary)
                print("-" * 40)
        
        # Create prompt template
        template = f"""You are now the guide of a mystical journey in the Whispering Woods. 
A traveler named {character_name} seeks the lost Gem of Serenity. 
You must navigate {character_name} through challenges, choices, and consequences, 
dynamically adapting the tale based on the traveler's decisions. 
Your goal is to create a branching narrative experience where each choice 
leads to a new path, ultimately determining {character_name}'s fate. 

Here are some rules to follow:
1. Start by asking the player to choose some kind of weapons that will be used later in the game
2. Have a few paths that lead to success
3. Have some paths that lead to death. If the user dies generate a response that explains the death and ends in the text: "The End.", I will search for this text to end the game
4. Keep responses engaging but concise (2-3 paragraphs max)

RESPONSE TYPES - Use these strategically throughout the game:

**STRUCTURED CHOICES** (Use for major decisions, combat, or pivotal moments):
Format: End with exactly 3 numbered choices like:
1. [Action/choice 1]
2. [Action/choice 2] 
3. [Action/choice 3]

**OPEN-ENDED QUESTIONS** (Use for creative moments, dialogue, exploration):
Format: End with an open question like:
- "What do you say to the mysterious figure?"
- "How do you approach this challenge?"
- "What creative solution do you try?"

**DIALOGUE PROMPTS** (Use for character interactions):
Format: End with dialogue setup like:
- "The wizard awaits your response..."
- "You may ask one question..."

**EXPLORATION PROMPTS** (Use for environmental discovery):
Format: End with exploration setup like:
- "You notice several interesting things. What draws your attention?"
- "The room holds many secrets. What do you investigate first?"

Mix these response types to create variety. Use structured choices for 60% of responses, open-ended for 30%, and dialogue/exploration for 10%.

Here is the chat history: {{chat_history}}
Human: {{human_input}}
AI:"""

        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"],
            template=template
        )

        # Create modern LangChain chain using RunnableSequence
        def format_chat_history():
            messages = message_history.messages
            if not messages:
                return "No previous conversation."
            
            history_text = []
            for msg in messages[-10:]:  # Last 10 messages to keep context manageable
                if isinstance(msg, HumanMessage):
                    history_text.append(f"Human: {msg.content}")
                else:
                    history_text.append(f"AI: {msg.content}")
            return "\n".join(history_text)
        
        # Create the chain
        chain = (
            {
                "chat_history": lambda x: format_chat_history(),
                "human_input": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        print(f"\nSession ID: {SESSION_ID[-12:]}...")
        print("=" * 55)
        print(f"Welcome, {character_name}, to the mystical journey in the Whispering Woods!")
        print("Type 'quit' to exit the game.")
        print("=" * 55)
        
        # Determine starting choice based on whether continuing or starting new
        if should_clear_history or not message_history.messages:
            choice = "start"
        else:
            choice = "continue"  # Continue from where they left off

        while True:
            try:
                # Add user input to message history
                if choice != "start":
                    message_history.add_message(HumanMessage(content=choice))
                
                # Get AI response
                response = chain.invoke(choice)
                print(f"\n{response.strip()}")
                
                # Add AI response to message history
                message_history.add_message(AIMessage(content=response))

                if "The End." in response:
                    print("\n" + "=" * 55)
                    print("Game Over! Thanks for playing!")
                    break

                choice = input("\nYour reply: ")
                
                if choice.lower() in ['quit', 'exit', 'q']:
                    print("\nThanks for playing! Your progress has been saved.")
                    break
                    
            except KeyboardInterrupt:
                print("\n\nGame interrupted. Your progress has been saved.")
                break
            except Exception as e:
                print(f"\nError during game: {e}")
                break
                
    except Exception as e:
        print(f"Failed to initialize game: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Qdrant is running: docker-compose up -d")
        print("2. Ensure Ollama is running with llama3:latest model")
        print("3. Check that all Python packages are installed")

if __name__ == "__main__":
    main()
