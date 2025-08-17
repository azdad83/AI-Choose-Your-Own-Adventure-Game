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
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage
from sentence_transformers import SentenceTransformer

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
class Story(BaseModel):
    id: str
    name: str
    description: str
    genre: str
    difficulty: str
    estimatedLength: str
    setting: str
    themes: List[str]
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

# Configuration constants
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
OLLAMA_MODEL = "gemma3:12b"

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
    
    # Initialize Ollama
    print(f"Initializing Ollama with model: {OLLAMA_MODEL}")
    llm = OllamaLLM(model=OLLAMA_MODEL, base_url="http://localhost:11434")
    
    # Initialize embeddings
    print("Loading embedding model...")
    embeddings = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("✅ API server ready!")

@app.on_event("startup")
async def startup_event():
    """Initialize the game components on startup."""
    try:
        initialize_components()
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        print("Please ensure Qdrant and Ollama are running")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "title": "AI Choose Your Own Adventure API",
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
            "character": {"name": request.characterName},
            "story": story_data,
            "currentTurn": 1,
            "isActive": True,
            "lastUpdated": now,
            "createdAt": now,
            "chat_history": QdrantChatMessageHistory(
                session_id=session_id,
                qdrant_client=qdrant_client,
                collection_name="chat_histories"
            )
        }
        
        # Store in memory
        active_sessions[session_id] = session_data
        
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
            author=story_data.get("author"),
            createdDate=story_data.get("created_date")
        )
        
        session = GameSession(
            sessionId=session_id,
            character=Character(name=request.characterName),
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
                message_type = 'ai' if hasattr(msg, 'response_metadata') else 'user'
                message = GameMessage(
                    id=str(uuid.uuid4()),
                    type=message_type,
                    content=msg.content,
                    timestamp=datetime.now().isoformat(),
                    turnNumber=session_data["currentTurn"]
                )
                messages.append(message)
        
        # If no messages, add welcome message
        if not messages:
            story = session_data["story"]
            welcome_message = GameMessage(
                id=str(uuid.uuid4()),
                type='ai',
                content=f"Welcome to {story['name']}! {story['description']} You are {session_data['character']['name']}. Let's begin your adventure!",
                timestamp=datetime.now().isoformat(),
                choices=[
                    "Look around and assess the situation",
                    "Call out to see if anyone is nearby", 
                    "Start moving forward cautiously",
                    "Wait and listen carefully"
                ],
                turnNumber=1
            )
            messages.append(welcome_message)
        
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
        
        # Create a simple prompt for the AI
        story_context = f"""
You are the game master for an adventure story called "{story_data['name']}".
Setting: {story_data['setting']}
Genre: {story_data['genre']}
Description: {story_data['description']}

The player is {character_data['name']}.
Player's action: {request.message}

Continue the story based on the player's action. Be engaging and descriptive.
At the end, provide 3-4 numbered choices for what the player can do next.
Keep responses to 2-3 paragraphs maximum.
"""
        
        # Get AI response
        response = llm.invoke(story_context)
        
        # Add AI response to history
        chat_history.add_message(AIMessage(content=response))
        
        # Update session
        session_data["currentTurn"] += 1
        session_data["lastUpdated"] = datetime.now().isoformat()
        
        # Parse response for choices (simple implementation)
        choices = []
        if "1." in response and "2." in response:
            # Extract numbered choices from response
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith(('1.', '2.', '3.', '4.')):
                    choice = line[2:].strip()
                    if choice:
                        choices.append(choice)
        
        # Create AI message
        ai_message = GameMessage(
            id=str(uuid.uuid4()),
            type='ai',
            content=response,
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
