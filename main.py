import os
import time
import uuid
import warnings
import json
from typing import List, Dict, Any, Optional
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

# Suppress LaChain deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")

class StoryManager:
    """Manage story definitions from local JSON file."""
    
    def __init__(self, stories_file: str = "stories.json"):
        self.stories_file = stories_file
        self._stories_cache = None
    
    def _load_stories(self) -> List[Dict[str, Any]]:
        """Load stories from JSON file with caching."""
        if self._stories_cache is None:
            try:
                if os.path.exists(self.stories_file):
                    with open(self.stories_file, 'r', encoding='utf-8') as f:
                        self._stories_cache = json.load(f)
                        print(f"✓ Loaded {len(self._stories_cache)} stories from {self.stories_file}")
                else:
                    print(f"⚠️  Stories file {self.stories_file} not found. Using default story.")
                    self._stories_cache = []
            except Exception as e:
                print(f"❌ Error loading stories from {self.stories_file}: {e}")
                self._stories_cache = []
        
        return self._stories_cache
    
    def get_all_stories(self) -> List[Dict[str, Any]]:
        """Get all available stories from the JSON file."""
        stories = self._load_stories()
        return sorted(stories, key=lambda x: x.get('name', ''))
    
    def get_story_by_id(self, story_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific story by ID from the JSON file."""
        stories = self._load_stories()
        for story in stories:
            if story.get('id') == story_id:
                return story
        return None
    
    def get_default_story(self) -> Dict[str, Any]:
        """Get a default story if no others are available."""
        return {
            'id': 'default_adventure',
            'name': 'Classic Adventure',
            'description': 'A classic adventure story',
            'initial_prompt': 'You are now the guide of a mystical journey. A traveler named {character_name} seeks adventure in an unknown land. You must navigate {character_name} through challenges, choices, and consequences, dynamically adapting the tale based on the traveler\'s decisions.',
            'genre': 'adventure',
            'difficulty': 'medium',
            'setting': 'Fantasy World'
        }
    
    def reload_stories(self) -> None:
        """Reload stories from file (clears cache)."""
        self._stories_cache = None
        print("🔄 Story cache cleared. Stories will be reloaded on next access.")

class QdrantChatMessageHistory(BaseChatMessageHistory):
    """Custom chat message history using Qdrant vector database with session-specific collections."""
    
    def __init__(self, session_id: str, qdrant_client: QdrantClient, collection_name: str = None):
        self.session_id = session_id
        self.client = qdrant_client
        # Create a unique collection name for this session if none provided
        self.collection_name = collection_name or f"chat_history_{session_id}"
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.turn_count = 0
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
    
    def store_story_selection(self, story_id: str, story_name: str) -> None:
        """Store the selected story for this session."""
        try:
            embedding = self.encoder.encode(f"Story selection: {story_name}").tolist()
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "session_id": self.session_id,
                    "message": f"Selected story: {story_name}",
                    "type": "story_metadata",
                    "story_id": story_id,
                    "story_name": story_name,
                    "timestamp": time.time()
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        except Exception as e:
            print(f"Error storing story selection: {e}")
    
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
    
    def get_story_selection(self) -> str:
        """Retrieve the selected story ID from the session metadata."""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            # Search for story selection metadata
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
                            match=MatchValue(value="story_metadata")
                        )
                    ]
                ),
                limit=10,
                with_payload=True
            )
            
            for point in search_result[0]:
                if "story_id" in point.payload:
                    return point.payload["story_id"]
            
            return None  # No story selected
        except Exception:
            return None  # No story selected

    def store_character_choice(self, choice_type: str, choice: str) -> None:
        """Store character creation choices (weapon, skill, tool)."""
        try:
            embedding = self.encoder.encode(f"Character {choice_type}: {choice}").tolist()
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "session_id": self.session_id,
                    "message": f"Selected {choice_type}: {choice}",
                    "type": "character_choice",
                    "choice_type": choice_type,  # "weapon", "skill", "tool"
                    "choice": choice,
                    "timestamp": time.time()
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        except Exception as e:
            print(f"Error storing character choice: {e}")

    def get_character_choices(self) -> Dict[str, str]:
        """Retrieve all character creation choices."""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            # Search for character choices
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
                            match=MatchValue(value="character_choice")
                        )
                    ]
                ),
                limit=10,
                with_payload=True
            )
            
            choices = {}
            for point in search_result[0]:
                payload = point.payload
                if "choice_type" in payload and "choice" in payload:
                    choices[payload["choice_type"]] = payload["choice"]
            
            return choices
        except Exception:
            return {}

    def get_character_creation_state(self) -> str:
        """Get the current character creation state (weapon, skill, tool, or complete)."""
        choices = self.get_character_choices()
        
        if "weapon" not in choices:
            return "weapon"
        elif "skill" not in choices:
            return "skill"
        elif "tool" not in choices:
            return "tool"
        else:
            return "complete"

    def is_character_creation_complete(self) -> bool:
        """Check if character creation is complete."""
        return self.get_character_creation_state() == "complete"
    
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
    
    def get_turn_count(self) -> int:
        """Get the current turn count for this session."""
        # Count human messages (player turns)
        human_messages = [msg for msg in self.messages if isinstance(msg, HumanMessage)]
        self.turn_count = len(human_messages)
        return self.turn_count
    
    def increment_turn(self) -> None:
        """Increment the turn counter."""
        self.turn_count += 1

def test_qdrant_connection(client: QdrantClient) -> bool:
    """Test if Qdrant is accessible."""
    try:
        client.get_collections()
        print("✓ Qdrant connection successful")
        return True
    except Exception as e:
        print(f"✗ Qdrant connection failed: {e}")
        return False

def check_for_existing_games(qdrant_client: QdrantClient) -> List[str]:
    """Check for existing game sessions by looking for session-specific collections."""
    try:
        # Get all collections
        collections = qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        # Filter for chat history collections (format: chat_history_<session_id>)
        session_ids = []
        for name in collection_names:
            if name.startswith('chat_history_adventure_session_'):
                # Extract session ID from collection name
                session_id = name.replace('chat_history_', '')
                session_ids.append(session_id)
        
        return session_ids
    except Exception as e:
        print(f"Error checking for existing games: {e}")
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

def format_game_response(response: str) -> None:
    """Display the AI response with consistent 3+1 choice formatting."""
    print("\n" + "═" * 60)
    print("📖 YOUR ADVENTURE CONTINUES")
    print("═" * 60)
    print(response.strip())
    print("═" * 60)
    print("💡 Choose 1-3 for suggested actions, or 4 for your own action")
    print("4. Your own action (describe what you want to do)")
    print("═" * 60)
    print()

def display_story_selector(story_manager: StoryManager) -> str:
    """Display story selection menu and get user choice."""
    stories = story_manager.get_all_stories()
    
    if not stories:
        print("No stories found in stories.json. Please check that stories.json exists and contains valid story definitions.")
        return None
    
    print("\n" + "=" * 70)
    print("🏰 STORY SELECTION")
    print("=" * 70)
    print("Choose your adventure:")
    print()
    
    for i, story in enumerate(stories, 1):
        difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(story.get('difficulty', 'medium'), "🟡")
        genre_emoji = {
            "fantasy": "🧙‍♂️", "noir": "🕵️", "sci-fi": "🚀", 
            "historical": "🏰", "horror": "👻", "adventure": "⚔️"
        }.get(story.get('genre', 'fantasy'), "📖")
        
        print(f"{i}. {genre_emoji} {story['name']}")
        print(f"   {story['description']}")
        print(f"   {difficulty_emoji} Difficulty: {story.get('difficulty', 'medium').title()} | Length: {story.get('estimated_length', 'Unknown')}")
        print(f"   Setting: {story.get('setting', 'Unknown')}")
        print()
    
    print("=" * 70)
    
    while True:
        try:
            choice = input(f"\nSelect a story (1-{len(stories)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(stories):
                selected_story = stories[choice_num - 1]
                print(f"\n✓ Selected: {selected_story['name']}")
                return selected_story['id']
            else:
                print(f"Please enter a number between 1 and {len(stories)}.")
        except ValueError:
            print("Please enter a valid number.")

# Add character creation display functions
def display_character_creation_step(step: str, character_name: str, genre: str, setting: str) -> str:
    """Display character creation step and get AI to generate choices."""
    templates = {
        "weapon": f"""You are helping {character_name} choose their starting weapon for a {genre} adventure set in {setting}.

Generate exactly 3 weapon options appropriate for this genre and setting. Present them as:

1. [Weapon name]: [Brief description]
2. [Weapon name]: [Brief description] 
3. [Weapon name]: [Brief description]

Make each weapon distinct and interesting, fitting the {genre} genre in a {setting} setting.""",

        "skill": f"""You are helping {character_name} choose their starting skill for a {genre} adventure set in {setting}.

Generate exactly 3 skill options appropriate for this genre and setting. Present them as:

1. [Skill name]: [Brief description]
2. [Skill name]: [Brief description]
3. [Skill name]: [Brief description]

Make each skill distinct and useful, fitting the {genre} genre in a {setting} setting.""",

        "tool": f"""You are helping {character_name} choose their starting tool for a {genre} adventure set in {setting}.

Generate exactly 3 tool options appropriate for this genre and setting. Present them as:

1. [Tool name]: [Brief description]
2. [Tool name]: [Brief description]
3. [Tool name]: [Brief description]

Make each tool distinct and useful, fitting the {genre} genre in a {setting} setting."""
    }
    
    return templates[step]

def handle_character_creation(message_history: 'QdrantChatMessageHistory', llm: OllamaLLM, character_name: str, story_data: dict) -> bool:
    """Handle the character creation process using predefined story skills and weapons. Returns True when complete."""
    current_state = message_history.get_character_creation_state()
    
    if current_state == "complete":
        return True
    
    step_names = {
        "weapon": "⚔️ CHOOSE YOUR WEAPON",
        "skill": "🎯 CHOOSE YOUR SKILL", 
        "tool": "🔧 CHOOSE YOUR TOOL"
    }
    
    print(f"\n" + "═" * 60)
    print(f"{step_names[current_state]}")
    print("═" * 60)
    
    # Use predefined options from story data for weapons and skills
    if current_state == "weapon":
        options = story_data.get('weapons', [])
        print("Choose your weapon:")
        for i, weapon in enumerate(options, 1):
            print(f"{i}. {weapon['name']}: {weapon['description']}")
    elif current_state == "skill":
        options = story_data.get('skills', [])
        print("Choose your skill:")
        for i, skill in enumerate(options, 1):
            print(f"{i}. {skill['name']}: {skill['description']}")
    else:  # tool - still use AI generation since tools aren't story-specific
        prompt = display_character_creation_step(current_state, character_name, story_data.get('genre', ''), story_data.get('setting', ''))
        response = llm.invoke(prompt)
        print(response.strip())
        options = None  # Will parse from AI response
    
    print("═" * 60)
    
    # Get user choice
    while True:
        if current_state in ["weapon", "skill"] and options:
            max_choice = len(options)
            choice = input(f"\n🎯 Choose your {current_state} (1-{max_choice}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= max_choice:
                chosen_option = options[int(choice) - 1]
                chosen_text = f"{chosen_option['name']}: {chosen_option['description']}"
                # Store the choice
                message_history.store_character_choice(current_state, chosen_text)
                print(f"\n✓ Selected: {chosen_text}")
                return False  # Not complete yet, need to check next step
            else:
                print(f"Please enter a number between 1 and {max_choice}.")
        else:  # tool case with AI generation
            choice = input(f"\n🎯 Choose your {current_state} (1, 2, or 3): ").strip()
            if choice in ['1', '2', '3']:
                # Extract the chosen option from AI response
                lines = response.strip().split('\n')
                choice_lines = [line for line in lines if line.strip().startswith(f"{choice}.")]
                if choice_lines:
                    chosen_option = choice_lines[0].strip()
                    # Store the choice
                    message_history.store_character_choice(current_state, chosen_option)
                    print(f"\n✓ Selected: {chosen_option}")
                    return False  # Not complete yet, need to check next step
                else:
                    print("Error parsing choice. Please try again.")
            else:
                print("Please enter 1, 2, or 3.")

def display_character_summary(message_history: 'QdrantChatMessageHistory', character_name: str) -> str:
    """Display the character's final loadout and return it as a string for the story."""
    choices = message_history.get_character_choices()
    
    print(f"\n" + "═" * 60)
    print(f"🎭 {character_name.upper()}'S LOADOUT")
    print("═" * 60)
    print(f"⚔️ Weapon: {choices.get('weapon', 'None')}")
    print(f"🎯 Skill: {choices.get('skill', 'None')}")
    print(f"🔧 Tool: {choices.get('tool', 'None')}")
    print("═" * 60)
    print("\nYour adventure begins now!")
    
    # Return formatted string for AI context
    return f"Character {character_name} has chosen:\n- Weapon: {choices.get('weapon', 'None')}\n- Skill: {choices.get('skill', 'None')}\n- Tool: {choices.get('tool', 'None')}"

def select_existing_session(session_ids: List[str], qdrant_client: QdrantClient, story_manager: StoryManager) -> str:
    """Let user select from existing sessions."""
    if len(session_ids) == 1:
        return session_ids[0]
    
    print("\nFound multiple previous adventures:")
    print("-" * 40)
    
    for i, session_id in enumerate(session_ids, 1):
        # Create a temporary message history to get summary
        temp_history = QdrantChatMessageHistory(
            session_id=session_id,
            qdrant_client=qdrant_client
        )
        summary = temp_history.get_last_session_summary()
        character_name = temp_history.get_character_name()
        story_id = temp_history.get_story_selection()
        
        # Get story name if available
        story_name = "Unknown Story"
        if story_id:
            story_data = story_manager.get_story_by_id(story_id)
            if story_data:
                story_name = story_data['name']
        
        print(f"{i}. Character: {character_name} | Story: {story_name}")
        print(f"   Session: {session_id[-8:]}...")
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
        
        # Initialize Story Manager (JSON-based)
        print("Loading story definitions from JSON...")
        story_manager = StoryManager("stories.json")
        
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
        selected_story_id = None
        
        if existing_sessions:
            choice = get_game_choice()
            
            if choice == '1':  # Continue existing adventure
                SESSION_ID = select_existing_session(existing_sessions, qdrant_client, story_manager)
                should_clear_history = False
                print(f"\n✓ Continuing adventure: {SESSION_ID[-12:]}...")
            else:  # Start new adventure
                SESSION_ID = f"adventure_session_{int(time.time())}"
                should_clear_history = True
                character_name = get_character_name()  # Get character name for new game
                selected_story_id = display_story_selector(story_manager)  # Select story
                print(f"\n✓ Starting new adventure: {SESSION_ID[-12:]}...")
        else:
            # No existing sessions, start new
            SESSION_ID = f"adventure_session_{int(time.time())}"
            character_name = get_character_name()  # Get character name for new game
            selected_story_id = display_story_selector(story_manager)  # Select story
            print("\n✓ No previous adventures found. Starting new adventure...")
        
        # Initialize chat history with Qdrant (uses session-specific collection)
        message_history = QdrantChatMessageHistory(
            session_id=SESSION_ID,
            qdrant_client=qdrant_client
        )
        
        # Clear previous session only if starting new
        if should_clear_history:
            message_history.clear()
            message_history.store_character_name(character_name)  # Store character name
            if selected_story_id:
                story_data = story_manager.get_story_by_id(selected_story_id)
                if story_data:
                    message_history.store_story_selection(selected_story_id, story_data['name'])
                else:
                    story_data = story_manager.get_default_story()
            else:
                story_data = story_manager.get_default_story()
            print("✓ Started fresh adventure")
        else:
            print("✓ Loaded previous adventure")
            # Get character name and story from existing session
            character_name = message_history.get_character_name()
            selected_story_id = message_history.get_story_selection()
            
            if selected_story_id:
                story_data = story_manager.get_story_by_id(selected_story_id)
                if not story_data:
                    story_data = story_manager.get_default_story()
            else:
                # For old sessions without story data
                story_data = story_manager.get_default_story()
            
            print(f"✓ Welcome back, {character_name}!")
            print(f"✓ Continuing: {story_data['name']}")
            
            # Show previous context
            previous_messages = message_history.messages
            if previous_messages:
                print("\n📖 Previous adventure context:")
                print("-" * 40)
                summary = message_history.get_last_session_summary()
                print(summary)
                print("-" * 40)
        
        # Create prompt template with turn tracking and dynamic story integration
        turn_count = message_history.get_turn_count()
        
        # Get story details for dynamic prompt  
        story_prompt = story_data.get('initial_prompt', 'You are the guide of an epic adventure.')
        genre = story_data.get('genre', 'adventure')
        setting = story_data.get('setting', 'Unknown Land')
        difficulty = story_data.get('difficulty', 'medium')
        
        # Get character choices for context
        character_choices = message_history.get_character_choices()
        equipment_context = ""
        if character_choices:
            equipment_context = f"""
CHARACTER EQUIPMENT:
- Weapon: {character_choices.get('weapon', 'None chosen')}
- Skill: {character_choices.get('skill', 'None chosen')}
- Tool: {character_choices.get('tool', 'None chosen')}

Use these equipment choices naturally in the story. The character has these items/abilities available.
"""
        
        template = f"""You are our guide on this adventure. You are the narrator and game master for this interactive story experience.

STORY CONTEXT:
- Genre: {genre}
- Setting: {setting}
- Difficulty: {difficulty}
- Character: {{character_name}}
{equipment_context}
STORY PROMPT:
{story_prompt}

CURRENT TURN: {turn_count + 1}

GAME RULES:
1. The player has already chosen their equipment and is ready to begin the adventure
2. Create multiple paths that can lead to success
3. CRITICAL: DO NOT allow the player to die until after turn 10. Before turn 10, if the player makes dangerous choices, have them face consequences but survive (injured, lost, setbacks, etc.)
4. After turn 10, some paths may lead to failure or death depending on the story type. If the user fails/dies, generate a response that explains the outcome and ends with the text: "The End."
5. Keep responses engaging but concise (2-3 paragraphs max)
6. Create a rich, layered story with character development and meaningful choices that fit the {genre} genre
7. Adapt your storytelling style to match the {genre} genre and {setting} setting

IMPORTANT FORMAT REQUIREMENT:
ALWAYS end your response with exactly 3 numbered choices for the player:
1. [First suggested action]
2. [Second suggested action] 
3. [Third suggested action]

Make these choices varied and interesting - include options appropriate to the {genre} genre such as combat, dialogue, exploration, problem-solving, etc.
The player will also have the option to choose "4" for their own custom action.

Here is the chat history: {{chat_history}}
Human: {{human_input}}
AI:"""






        prompt = PromptTemplate(
            input_variables=["character_name", "chat_history", "human_input"],
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
                "character_name": lambda x: character_name,
                "chat_history": lambda x: format_chat_history(),
                "human_input": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        print(f"\nSession ID: {SESSION_ID[-12:]}...")
        print("=" * 55)
        print(f"Welcome, {character_name}, you're going on an adventure!")
        print("Type 'quit' to exit the game.")
        print("=" * 55)
        
        # Determine starting choice based on whether continuing or starting new
        if should_clear_history or not message_history.messages:
            # Handle character creation for new games
            if not message_history.is_character_creation_complete():
                print("\nStarting character creation...")
                
                # Get story details for character creation context
                story_data = story_manager.get_story_by_id(selected_story_id) if selected_story_id else story_manager.get_default_story()
                
                # Handle character creation steps
                while not message_history.is_character_creation_complete():
                    handle_character_creation(message_history, llm, character_name, story_data)
                
                # Display final character summary
                character_summary = display_character_summary(message_history, character_name)
                choice = f"start with character setup: {character_summary}"
            else:
                choice = "start"
        else:
            choice = "continue"  # Continue from where they left off

        while True:
            try:
                # Add user input to message history
                if choice != "start" and choice != "continue":
                    message_history.add_message(HumanMessage(content=choice))
                
                # Get AI response
                response = chain.invoke(choice)
                
                # Format and display response with 3+1 choices
                format_game_response(response)
                
                # Add AI response to message history
                message_history.add_message(AIMessage(content=response))

                if "The End." in response:
                    print("\n" + "🎭" + "=" * 58)
                    print("GAME OVER! Thanks for playing!")
                    print("Your adventure has been saved for future reference.")
                    print("=" * 60)
                    break

                # Get user input - handle both numbered choices and custom actions
                while True:
                    choice = input("\n🎯 Your choice (1, 2, 3, or 4 for custom action): ").strip()
                    
                    if choice in ['1', '2', '3']:
                        # Player chose one of the suggested options
                        break
                    elif choice == '4':
                        # Player wants to enter custom action
                        custom_action = input("\n✨ Describe your action: ").strip()
                        if custom_action:
                            choice = custom_action
                            break
                        else:
                            print("Please enter an action or choose 1, 2, or 3.")
                    elif choice.lower() in ['quit', 'exit', 'q']:
                        current_turn = message_history.get_turn_count()
                        print(f"\n👋 Thanks for playing! You completed {current_turn} turns. Your progress has been saved.")
                        break
                    else:
                        print("Please enter 1, 2, 3, or 4.")
                    
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
