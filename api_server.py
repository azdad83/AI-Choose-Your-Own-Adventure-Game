#!/usr/bin/env python3
"""
FastAPI Web Server for the Choose Your Own Adventure Game
Provides REST API endpoints for the frontend to interact with the game logic.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import json
import os
from datetime import datetime

# Import the existing game logic and classes
from main import StoryManager, QdrantChatMessageHistory
from qdrant_client import QdrantClient
from langchain_core.messages import HumanMessage, AIMessage
from ai_config import get_llm, get_embeddings, test_ai_connection, get_provider_info, config

# Initialize FastAPI app
app = FastAPI(
    title="AI Choose Your Own Adventure API",
    description="REST API for the AI-powered choose your own adventure game",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class Skill(BaseModel):
    name: str
    description: str

class Weapon(BaseModel):
    name: str
    description: str
    image: Optional[str] = None

class Tool(BaseModel):
    name: str
    description: str

class Story(BaseModel):
    id: str
    name: str
    description: str
    genre: str
    difficulty: str
    estimatedLength: str
    setting: str
    themes: List[str]
    skills: List[Skill]
    weapons: List[Weapon]
    tools: List[Tool]
    image: Optional[str] = None
    author: Optional[str] = None
    createdDate: Optional[str] = None

class Character(BaseModel):
    name: str
    weapon: Optional[str] = None
    skill: Optional[str] = None
    tool: Optional[str] = None

class GameSession(BaseModel):
    sessionId: str
    character: Character
    story: Story
    currentTurn: int
    isActive: bool
    lastUpdated: str
    createdAt: str

class GameMessage(BaseModel):
    id: str
    type: str  # 'user', 'ai', 'system'
    content: str
    timestamp: str
    choices: Optional[List[str]] = None
    turnNumber: Optional[int] = None

class SessionSummary(BaseModel):
    sessionId: str
    characterName: str
    storyName: str
    currentTurn: int
    lastActivity: str
    progress: int  # 0-100 percentage

class CreateSessionRequest(BaseModel):
    storyId: str
    characterName: str
    weapon: Optional[str] = None
    skill: Optional[str] = None
    tool: Optional[str] = None

class SendMessageRequest(BaseModel):
    sessionId: str
    message: str

class SendMessageResponse(BaseModel):
    message: GameMessage

# Global instances
story_manager = None
qdrant_client = None
llm = None
embeddings = None
active_sessions: Dict[str, Dict] = {}  # In-memory session storage

# Configuration from ai_config
QDRANT_HOST = config.qdrant_host
QDRANT_PORT = config.qdrant_port

def initialize_components():
    """Initialize the game components."""
    global story_manager, qdrant_client, llm, embeddings
    
    print("🚀 Initializing AI Choose Your Own Adventure API...")
    
    # Initialize Qdrant client
    print("Connecting to Qdrant...")
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # Initialize Story Manager
    print("Loading story definitions...")
    story_manager = StoryManager("stories.json")
    
    # Initialize AI Language Model
    print("Initializing AI language model...")
    try:
        llm = get_llm()
        print("✓ AI language model initialized")
    except Exception as e:
        print(f"✗ Failed to initialize AI language model: {e}")
        raise
    
    # Test AI connection
    if not test_ai_connection():
        provider_info = get_provider_info()
        error_msg = f"Failed to connect to {provider_info['provider']} AI provider"
        print(f"✗ {error_msg}")
        raise Exception(error_msg)
    
    # Initialize embeddings
    print("Loading embedding model...")
    try:
        embeddings = get_embeddings()
        print(f"✅ Embedding model loaded successfully")
    except Exception as e:
        print(f"✗ Failed to initialize embedding model: {e}")
        raise
    
    print("✅ API server ready!")

@app.on_event("startup")
async def startup_event():
    """Initialize the game components on startup."""
    try:
        initialize_components()
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        print("Please ensure Qdrant is running and AI provider is properly configured")

@app.get("/")
async def root():
    """Health check endpoint."""
    provider_info = get_provider_info()
    return {
        "status": "running",
        "title": "AI Choose Your Own Adventure API",
        "ai_provider": provider_info['provider'],
        "ai_model": provider_info['model'],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/connection-status")
async def get_connection_status():
    """Get AI provider connection status."""
    provider_info = get_provider_info()
    
    try:
        # Test connection
        is_connected = test_ai_connection()
        
        return {
            "provider": provider_info['provider'],
            "model": provider_info['model'],
            "base_url": provider_info['base_url'],
            "connected": is_connected,
            "status": "connected" if is_connected else "disconnected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "provider": provider_info['provider'],
            "model": provider_info['model'],
            "base_url": provider_info['base_url'],
            "connected": False,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/stories", response_model=Dict[str, List[Story]])
async def get_stories():
    """Get all available stories."""
    try:
        stories_data = story_manager.get_all_stories()
        stories = []
        
        for story_data in stories_data:
            story = Story(
                id=story_data.get("id", ""),
                name=story_data.get("name", ""),
                description=story_data.get("description", ""),
                genre=story_data.get("genre", ""),
                difficulty=story_data.get("difficulty", "medium"),
                estimatedLength=story_data.get("estimated_length", "15-20 turns"),
                setting=story_data.get("setting", ""),
                themes=story_data.get("themes", []),
                skills=[Skill(name=skill["name"], description=skill["description"]) for skill in story_data.get("skills", [])],
                weapons=[Weapon(name=weapon["name"], description=weapon["description"], image=weapon.get("image")) for weapon in story_data.get("weapons", [])],
                tools=[Tool(name=tool["name"], description=tool["description"]) for tool in story_data.get("tools", [])],
                image=story_data.get("image"),
                author=story_data.get("author"),
                createdDate=story_data.get("created_date")
            )
            stories.append(story)
        
        return {"stories": stories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load stories: {str(e)}")

@app.get("/api/stories/{story_id}", response_model=Story)
async def get_story(story_id: str):
    """Get a specific story by ID."""
    try:
        story_data = story_manager.get_story_by_id(story_id)
        if not story_data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return Story(
            id=story_data.get("id", ""),
            name=story_data.get("name", ""),
            description=story_data.get("description", ""),
            genre=story_data.get("genre", ""),
            difficulty=story_data.get("difficulty", "medium"),
            estimatedLength=story_data.get("estimated_length", "15-20 turns"),
            setting=story_data.get("setting", ""),
            themes=story_data.get("themes", []),
            skills=[Skill(name=skill["name"], description=skill["description"]) for skill in story_data.get("skills", [])],
            weapons=[Weapon(name=weapon["name"], description=weapon["description"], image=weapon.get("image")) for weapon in story_data.get("weapons", [])],
            tools=[Tool(name=tool["name"], description=tool["description"]) for tool in story_data.get("tools", [])],
            image=story_data.get("image"),
            author=story_data.get("author"),
            createdDate=story_data.get("created_date")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load story: {str(e)}")

@app.post("/api/sessions", response_model=Dict[str, GameSession])
async def create_session(request: CreateSessionRequest):
    """Create a new game session."""
    try:
        # Get the story
        story_data = story_manager.get_story_by_id(request.storyId)
        if not story_data:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Create new session
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create session data
        session_data = {
            "sessionId": session_id,
            "character": {
                "name": request.characterName,
                "weapon": request.weapon,
                "skill": request.skill,
                "tool": request.tool
            },
            "story": story_data,
            "currentTurn": 1,
            "isActive": True,
            "lastUpdated": now,
            "createdAt": now,
            "chat_history": QdrantChatMessageHistory(
                session_id=session_id,
                qdrant_client=qdrant_client,
                embeddings_model=embeddings,
                collection_name="chat_histories"
            )
        }
        
        # Store in memory
        active_sessions[session_id] = session_data
        
        # Create engaging static opening message based on story data
        story_name = story_data.get('name', 'Adventure')
        description = story_data.get('description', '')
        setting = story_data.get('setting', '')
        genre = story_data.get('genre', '')
        
        # Create character introduction with equipment
        character_intro = f"You are {request.characterName}"
        equipment_parts = []
        if request.weapon:
            # Find weapon description
            weapon_desc = next((w['description'] for w in story_data.get('weapons', []) if w['name'] == request.weapon), request.weapon)
            equipment_parts.append(f"armed with {request.weapon} ({weapon_desc})")
        if request.skill:
            # Find skill description  
            skill_desc = next((s['description'] for s in story_data.get('skills', []) if s['name'] == request.skill), request.skill)
            equipment_parts.append(f"skilled in {request.skill} ({skill_desc})")
        if request.tool:
            # Find tool description
            tool_desc = next((t['description'] for t in story_data.get('tools', []) if t['name'] == request.tool), request.tool)
            equipment_parts.append(f"carrying {request.tool} ({tool_desc})")
        
        if equipment_parts:
            character_intro += ", " + ", ".join(equipment_parts)
        character_intro += "."
        
        # Create atmospheric opening based on genre
        if genre == "noir":
            scene_setting = f"The rain-slicked streets of {setting} gleam under the harsh glow of neon signs. Shadows dance between brick buildings, and the air is thick with cigarette smoke and secrets waiting to be uncovered."
        elif genre == "fantasy":
            scene_setting = f"The mystical realm of {setting} stretches before you, where ancient magic still flows through every leaf and stone. The air hums with possibility and danger."
        elif genre == "pirate":
            scene_setting = f"The salty sea air fills your lungs as {setting} comes into view. The sound of creaking ship timbers and distant seabirds creates an atmosphere of adventure and treachery."
        elif genre == "sci-fi":
            scene_setting = f"The gleaming corridors and pulsing lights of {setting} represent humanity's reach into the unknown. Technology and mystery intertwine in this futuristic landscape."
        else:
            scene_setting = f"You find yourself in {setting}, a place where adventure awaits around every corner."
        
        # Combine all elements
        opening_message = f"""**Welcome to {story_name}!**

{description}

{scene_setting}

{character_intro}

Your adventure begins now. The choices you make will shape your destiny in this world. What do you choose to do?

**1.** Look around and assess the situation
**2.** Call out to see if anyone is nearby  
**3.** Start moving forward cautiously"""
        
        # Store the static opening message - REMOVED: Let frontend trigger AI story generation
        # session_data["chat_history"].add_message(AIMessage(content=opening_message))
        
        # Convert to response format
        story = Story(
            id=story_data.get("id", ""),
            name=story_data.get("name", ""),
            description=story_data.get("description", ""),
            genre=story_data.get("genre", ""),
            difficulty=story_data.get("difficulty", "medium"),
            estimatedLength=story_data.get("estimated_length", "15-20 turns"),
            setting=story_data.get("setting", ""),
            themes=story_data.get("themes", []),
            skills=[Skill(name=skill["name"], description=skill["description"]) for skill in story_data.get("skills", [])],
            weapons=[Weapon(name=weapon["name"], description=weapon["description"]) for weapon in story_data.get("weapons", [])],
            tools=[Tool(name=tool["name"], description=tool["description"]) for tool in story_data.get("tools", [])],
            author=story_data.get("author"),
            createdDate=story_data.get("created_date")
        )
        
        session = GameSession(
            sessionId=session_id,
            character=Character(
                name=request.characterName,
                weapon=request.weapon,
                skill=request.skill,
                tool=request.tool
            ),
            story=story,
            currentTurn=1,
            isActive=True,
            lastUpdated=now,
            createdAt=now
        )
        
        return {"session": session}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/api/sessions", response_model=Dict[str, List[SessionSummary]])
async def get_sessions():
    """Get all active sessions."""
    try:
        sessions = []
        for session_id, session_data in active_sessions.items():
            summary = SessionSummary(
                sessionId=session_id,
                characterName=session_data["character"]["name"],
                storyName=session_data["story"]["name"],
                currentTurn=session_data["currentTurn"],
                lastActivity=session_data["lastUpdated"],
                progress=min(100, session_data["currentTurn"] * 5)  # Rough progress estimate
            )
            sessions.append(summary)
        
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sessions: {str(e)}")

@app.get("/api/sessions/{session_id}", response_model=GameSession)
async def get_session(session_id: str):
    """Get a specific session."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        story_data = session_data["story"]
        
        story = Story(
            id=story_data.get("id", ""),
            name=story_data.get("name", ""),
            description=story_data.get("description", ""),
            genre=story_data.get("genre", ""),
            difficulty=story_data.get("difficulty", "medium"),
            estimatedLength=story_data.get("estimated_length", "15-20 turns"),
            setting=story_data.get("setting", ""),
            themes=story_data.get("themes", []),
            skills=[Skill(name=skill["name"], description=skill["description"]) for skill in story_data.get("skills", [])],
            weapons=[Weapon(name=weapon["name"], description=weapon["description"]) for weapon in story_data.get("weapons", [])],
            tools=[Tool(name=tool["name"], description=tool["description"]) for tool in story_data.get("tools", [])],
            author=story_data.get("author"),
            createdDate=story_data.get("created_date")
        )
        
        character = Character(
            name=session_data["character"]["name"],
            weapon=session_data["character"].get("weapon"),
            skill=session_data["character"].get("skill"),
            tool=session_data["character"].get("tool")
        )
        
        return GameSession(
            sessionId=session_id,
            character=character,
            story=story,
            currentTurn=session_data["currentTurn"],
            isActive=session_data["isActive"],
            lastUpdated=session_data["lastUpdated"],
            createdAt=session_data["createdAt"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load session: {str(e)}")

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        del active_sessions[session_id]
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

def parse_choices_from_response(content: str) -> tuple[str, List[str]]:
    """Parse numbered choices from AI response and return content without choices and extracted choices."""
    import re
    
    # Find numbered choices pattern (1. 2. 3. etc.)
    choice_pattern = r'\n\d+\.\s*([^\n]+)'
    matches = re.findall(choice_pattern, content)
    
    if matches:
        # Extract choices
        choices = [match.strip() for match in matches]
        
        # Remove choices from content
        content_without_choices = re.sub(r'\n\d+\.\s*[^\n]+', '', content).strip()
        
        return content_without_choices, choices
    
    return content, []

@app.get("/api/sessions/{session_id}/messages", response_model=Dict[str, List[GameMessage]])
async def get_messages(session_id: str):
    """Get messages for a session."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        chat_history = session_data["chat_history"]
        
        messages = []
        for msg in chat_history.messages:
            if hasattr(msg, 'content'):
                message_type = 'ai' if isinstance(msg, AIMessage) else 'user'
                
                if message_type == 'ai':
                    # Parse choices from AI messages
                    content_without_choices, choices = parse_choices_from_response(msg.content)
                    message = GameMessage(
                        id=str(uuid.uuid4()),
                        type=message_type,
                        content=content_without_choices,
                        timestamp=datetime.now().isoformat(),
                        choices=choices if choices else None,
                        turnNumber=session_data["currentTurn"]
                    )
                else:
                    message = GameMessage(
                        id=str(uuid.uuid4()),
                        type=message_type,
                        content=msg.content,
                        timestamp=datetime.now().isoformat(),
                        turnNumber=session_data["currentTurn"]
                    )
                messages.append(message)
        
        # If still no messages, add enhanced fallback welcome message
        if not messages:
            story = session_data["story"]
            character = session_data["character"]
            
            # Create enhanced character introduction with equipment descriptions
            character_intro = f"You are {character['name']}"
            equipment_parts = []
            if character.get('weapon'):
                # Find weapon description
                weapon_desc = next((w['description'] for w in story.get('weapons', []) if w['name'] == character['weapon']), character['weapon'])
                equipment_parts.append(f"armed with {character['weapon']} ({weapon_desc})")
            if character.get('skill'):
                # Find skill description  
                skill_desc = next((s['description'] for s in story.get('skills', []) if s['name'] == character['skill']), character['skill'])
                equipment_parts.append(f"skilled in {character['skill']} ({skill_desc})")
            if character.get('tool'):
                # Find tool description
                tool_desc = next((t['description'] for t in story.get('tools', []) if t['name'] == character['tool']), character['tool'])
                equipment_parts.append(f"carrying {character['tool']} ({tool_desc})")
            
            if equipment_parts:
                character_intro += ", " + ", ".join(equipment_parts)
            character_intro += "."
            
            # Create atmospheric scene setting based on genre
            setting = story.get('setting', '')
            genre = story.get('genre', '')
            if genre == "noir":
                scene_setting = f"The rain-slicked streets of {setting} gleam under the harsh glow of neon signs. Shadows dance between brick buildings, and the air is thick with cigarette smoke and secrets waiting to be uncovered."
            elif genre == "fantasy":
                scene_setting = f"The mystical realm of {setting} stretches before you, where ancient magic still flows through every leaf and stone. The air hums with possibility and danger."
            elif genre == "pirate":
                scene_setting = f"The salty sea air fills your lungs as {setting} comes into view. The sound of creaking ship timbers and distant seabirds creates an atmosphere of adventure and treachery."
            elif genre == "sci-fi":
                scene_setting = f"The gleaming corridors and pulsing lights of {setting} represent humanity's reach into the unknown. Technology and mystery intertwine in this futuristic landscape."
            else:
                scene_setting = f"You find yourself in {setting}, a place where adventure awaits around every corner."
            
            welcome_content = f"""**Welcome to {story['name']}!**

{story['description']}

{scene_setting}

{character_intro}

Your adventure begins now. The choices you make will shape your destiny in this world. What do you choose to do?"""
            
        # Don't add static welcome content - let frontend trigger AI story generation
        # if len(messages) == 0:
        #     [removed static content generation]
        
        return {"messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load messages: {str(e)}")

@app.post("/api/messages", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    """Send a message and get AI response."""
    try:
        if request.sessionId not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[request.sessionId]
        story_data = session_data["story"]
        character_data = session_data["character"]
        chat_history = session_data["chat_history"]
        
        # Add user message to history
        chat_history.add_message(HumanMessage(content=request.message))
        
        # Create a rich, immersive prompt for the AI with JSON format requirement
        is_first_message = len([msg for msg in chat_history.messages if isinstance(msg, HumanMessage)]) == 1
        
        if is_first_message:
            # First message - create an immersive story opening
            story_context = f"""
{story_data['initial_prompt'].format(character_name=character_data['name'])}

STORY SETTING: {story_data['setting']}
GENRE: {story_data['genre'].title()}
THEMES: {', '.join(story_data['themes'])}

CHARACTER PROFILE:
- Name: {character_data['name']}
- Weapon: {character_data['weapon']}
- Special Skill: {character_data['skill']}
- Equipment: {character_data['tool']}

STORYTELLING INSTRUCTIONS:
1. Begin with a rich, atmospheric introduction that establishes the setting, mood, and immediate situation
2. Seamlessly integrate the character's name, weapon, skill, and equipment into the opening scene
3. Create an immersive scenario that reflects the {story_data['genre']} genre and {story_data['setting']} setting
4. The opening should be 3-4 paragraphs long and highly descriptive
5. End with the character facing their first meaningful decision
6. Provide exactly 4 distinct, meaningful choices that reflect different approaches (combat, stealth, social, creative)

CRITICAL: You MUST respond in the following JSON format:
{{
  "story": "The main story text here",
  "choices": [
    {{"name": "Action Name", "description": "Detailed description of what this action entails"}},
    {{"name": "Action Name", "description": "Detailed description of what this action entails"}},
    {{"name": "Action Name", "description": "Detailed description of what this action entails"}},
    {{"name": "Action Name", "description": "Detailed description of what this action entails"}}
  ]
}}

PLAYER'S OPENING ACTION: {request.message}

Respond ONLY with valid JSON in the exact format specified above.
"""
        else:
            # Continuing story - shorter context
            story_context = f"""
You are the game master continuing an adventure story called "{story_data['name']}".
Setting: {story_data['setting']} | Genre: {story_data['genre']} | Themes: {', '.join(story_data['themes'])}

The player is {character_data['name']} (equipped with {character_data['weapon']}, skilled in {character_data['skill']}, carrying {character_data['tool']}).

Player's action: {request.message}

Continue the story based on the player's action. Be engaging, descriptive, and true to the {story_data['genre']} genre.
Keep responses to 2-3 paragraphs.

CRITICAL: You MUST respond in the following JSON format:
{{
  "story": "The main story text here",
  "choices": [
    {{"name": "Action Name", "description": "Detailed description of what this action entails"}},
    {{"name": "Action Name", "description": "Detailed description of what this action entails"}},
    {{"name": "Action Name", "description": "Detailed description of what this action entails"}},
    {{"name": "Action Name", "description": "Detailed description of what this action entails"}}
  ]
}}

Respond ONLY with valid JSON in the exact format specified above.
"""
        
        print(f"DEBUG: Prompt length: {len(story_context)}")
        print(f"DEBUG: First 200 chars of prompt: {story_context[:200]}")
        
        # Get AI response
        response = llm.invoke(story_context)
        print(f"DEBUG: AI response type: {type(response)}")
        
        # Extract content from AIMessage if needed
        if hasattr(response, 'content'):
            response_content = response.content
        else:
            response_content = str(response)
        
        print(f"DEBUG: Response content length: {len(response_content) if response_content else 0}")
        print(f"DEBUG: Raw response: {response_content[:500]}")
        
        # Parse JSON response
        try:
            # Clean up the response content first
            response_content = response_content.strip()
            
            # Try to extract JSON from response if it's wrapped in markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*\n?({.*?})\s*\n?```', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print(f"DEBUG: Found JSON in code blocks: {json_str[:200]}...")
            else:
                # Try to find JSON object directly - look for balanced braces
                brace_count = 0
                start_idx = -1
                end_idx = -1
                
                for i, char in enumerate(response_content):
                    if char == '{':
                        if brace_count == 0:
                            start_idx = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and start_idx != -1:
                            end_idx = i + 1
                            break
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_content[start_idx:end_idx]
                    print(f"DEBUG: Found JSON object: {json_str[:200]}...")
                else:
                    print(f"DEBUG: No JSON found, using fallback parsing")
                    # Fallback to old parsing method
                    story_content, choices = parse_choices_from_response(response_content)
                    print(f"DEBUG: Fallback - story: {len(story_content)} chars, choices: {len(choices)}")
                    
                    # Add AI response to history (store the story content only)
                    chat_history.add_message(AIMessage(content=story_content))
                    
                    # Update session
                    session_data["currentTurn"] += 1
                    session_data["lastUpdated"] = datetime.now().isoformat()
                    
                    # Create AI message
                    ai_message = GameMessage(
                        id=str(uuid.uuid4()),
                        type='ai',
                        content=story_content,
                        timestamp=datetime.now().isoformat(),
                        choices=choices if choices else None,
                        turnNumber=session_data["currentTurn"]
                    )
                    
                    return SendMessageResponse(message=ai_message)
            
            # Parse the JSON
            print(f"DEBUG: Attempting to parse JSON: {json_str[:100]}...")
            parsed_response = json.loads(json_str)
            
            story_content = parsed_response.get('story', '')
            choices_data = parsed_response.get('choices', [])
            
            print(f"DEBUG: Successfully parsed JSON - story: {len(story_content)} chars, choices: {len(choices_data)}")
            
            # Format choices as expected by frontend
            choices = []
            for choice_obj in choices_data:
                if isinstance(choice_obj, dict) and 'name' in choice_obj and 'description' in choice_obj:
                    choices.append(f"**{choice_obj['name']}** {choice_obj['description']}")
                else:
                    # Fallback if structure is unexpected
                    choices.append(str(choice_obj))
            
            print(f"DEBUG: Formatted choices: {[c[:50] + '...' if len(c) > 50 else c for c in choices]}")
            
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            print(f"DEBUG: Raw response content: {response_content[:500]}")
            print(f"DEBUG: Falling back to old parsing method")
            # Fallback to old parsing method if JSON parsing fails
            story_content, choices = parse_choices_from_response(response_content)
            print(f"DEBUG: Fallback result - story: {len(story_content)} chars, choices: {len(choices)}")
        
        # Add AI response to history (store the story content only)
        chat_history.add_message(AIMessage(content=story_content))
        
        # Update session
        session_data["currentTurn"] += 1
        session_data["lastUpdated"] = datetime.now().isoformat()
        
        # Create AI message
        ai_message = GameMessage(
            id=str(uuid.uuid4()),
            type='ai',
            content=story_content,
            timestamp=datetime.now().isoformat(),
            choices=choices if choices else None,
            turnNumber=session_data["currentTurn"]
        )
        
        return SendMessageResponse(message=ai_message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
