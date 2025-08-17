# Frontend Development Plan
## AI Choose Your Own Adventure Game - Next.js Interface

This document outlines the development plan for creating a web-based frontend that replicates the Python game's functionality using Next.js and ShadCN UI components with a ChatGPT-inspired interface.

## Project Overview

**Current State**: Next.js 15.4.5 project with ShadCN UI components pre-installed
**Target**: Full-featured web interface matching the Python game's functionality
**UI/UX Inspiration**: ChatGPT-style conversational interface with modern design

## Tech Stack

- **Framework**: Next.js 15.4.5 (App Router)
- **UI Library**: ShadCN UI (Radix UI primitives)
- **Styling**: Tailwind CSS v4
- **Language**: TypeScript
- **State Management**: React hooks + Context API
- **Backend Integration**: REST API endpoints (to be created)

## Architecture Overview

### Frontend Structure
```
frontend/
├── app/
│   ├── api/                    # API routes for backend integration
│   ├── game/                   # Game interface pages
│   ├── layout.tsx              # Root layout with providers
│   └── page.tsx                # Landing/lobby page
├── components/
│   ├── game/                   # Game-specific components
│   ├── ui/                     # ShadCN components (already installed)
│   └── layout/                 # Layout components
├── hooks/                      # Custom React hooks
├── lib/                        # Utilities and configurations
└── types/                      # TypeScript type definitions
```

### Backend Integration
```
backend-api/                    # New Python API service
├── main.py                     # FastAPI application
├── models/                     # Pydantic models
├── routes/                     # API route handlers
└── services/                   # Business logic (wraps existing game logic)
```

## Phase 1: Foundation Setup (Week 1)

### 1.1 Project Structure & Types

**File**: `types/game.ts`
```typescript
export interface Story {
  id: string;
  name: string;
  description: string;
  genre: string;
  difficulty: 'easy' | 'medium' | 'hard';
  estimatedLength: string;
  setting: string;
  themes: string[];
}

export interface Character {
  name: string;
  weapon?: string;
  skill?: string;
  tool?: string;
}

export interface GameSession {
  sessionId: string;
  character: Character;
  story: Story;
  currentTurn: number;
  isActive: boolean;
  lastUpdated: string;
}

export interface GameMessage {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: string;
  choices?: string[];
}

export interface GameState {
  phase: 'lobby' | 'story-selection' | 'character-creation' | 'gameplay' | 'game-over';
  session?: GameSession;
  messages: GameMessage[];
  isLoading: boolean;
}
```

**File**: `lib/game-context.tsx`
```typescript
"use client";

import { createContext, useContext, useReducer, ReactNode } from 'react';
import { GameState, GameMessage } from '@/types/game';

// Context for game state management
```

### 1.2 Landing Page Redesign

**File**: `app/page.tsx`
```typescript
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sword, Users, BookOpen, Settings } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero section with game stats and quick start */}
    </div>
  );
}
```

**Features**:
- Hero section with animated background
- Game statistics (sessions played, stories available)
- Quick start buttons (Continue/New Game)
- Story showcase carousel
- Recent sessions preview

### 1.3 Layout Components

**File**: `components/layout/game-header.tsx`
```typescript
// Header with game title, session info, and controls
// - Session indicator
// - Character name display
// - Settings dropdown
// - Exit game confirmation
```

**File**: `components/layout/sidebar.tsx`
```typescript
// Collapsible sidebar for game navigation
// - Session list
// - Character summary
// - Story progress
// - Game settings
```

## Phase 2: Game Flow Implementation (Week 2-3)

### 2.1 Story Selection Interface

**File**: `app/game/story-selection/page.tsx`
```typescript
// Grid layout of story cards with filtering
// - Genre filters (Fantasy, Sci-Fi, Horror, etc.)
// - Difficulty filters
// - Search functionality
// - Story preview modals
```

**Components**:
- `components/game/story-card.tsx` - Individual story display
- `components/game/story-filter.tsx` - Filter controls
- `components/game/story-preview-modal.tsx` - Detailed story preview

### 2.2 Character Creation Flow

**File**: `app/game/character-creation/page.tsx`
```typescript
// Multi-step character creation wizard
// - Name input with validation
// - Weapon selection (3 AI-generated choices)
// - Skill selection (3 AI-generated choices)  
// - Tool selection (3 AI-generated choices)
// - Character summary confirmation
```

**Components**:
- `components/game/character-name-form.tsx`
- `components/game/equipment-selection.tsx`
- `components/game/character-summary.tsx`
- `components/ui/progress-steps.tsx` - Custom step progress indicator

### 2.3 Main Game Interface

**File**: `app/game/[sessionId]/page.tsx`
```typescript
// ChatGPT-inspired conversation interface
// - Message history with proper formatting
// - AI story responses with rich formatting
// - Choice buttons (1, 2, 3) + custom input
// - Turn counter and progress indicators
```

**Components**:
- `components/game/message-bubble.tsx` - Story text and user choices
- `components/game/choice-buttons.tsx` - Interactive choice selection
- `components/game/custom-action-input.tsx` - Free text input for option 4
- `components/game/game-controls.tsx` - Save, settings, exit controls

## Phase 3: Advanced Features (Week 4)

### 3.1 Session Management

**Components**:
- `components/game/session-browser.tsx` - Browse existing sessions
- `components/game/session-card.tsx` - Session preview with continue option
- `components/game/session-details-modal.tsx` - Detailed session information

### 3.2 Enhanced UI Elements

**Custom Components** (extending ShadCN):
- `components/game/typing-animation.tsx` - Typewriter effect for AI responses
- `components/game/character-avatar.tsx` - Dynamic character representation
- `components/game/story-progress.tsx` - Visual progress through story
- `components/game/inventory-display.tsx` - Show character equipment

### 3.3 Responsive Design & Accessibility

- Mobile-optimized layouts
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Font size adjustments

## Phase 4: Backend Integration (Week 5)

### 4.1 API Development

**File**: `backend-api/main.py`
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add the parent directory to path to import existing game logic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import StoryManager, QdrantChatMessageHistory, main as game_main

app = FastAPI()

# API endpoints wrapping existing game functionality
```

**API Endpoints**:
- `GET /api/stories` - Get available stories
- `POST /api/sessions` - Create new game session
- `GET /api/sessions` - List user sessions
- `GET /api/sessions/{id}` - Get session details
- `POST /api/sessions/{id}/messages` - Send player choice
- `POST /api/character-creation/{step}` - Handle character creation steps
- `DELETE /api/sessions/{id}` - Clear session data

### 4.2 Frontend API Integration

**File**: `lib/api-client.ts`
```typescript
// API client with error handling and type safety
class GameApiClient {
  async getStories(): Promise<Story[]> { }
  async createSession(storyId: string): Promise<GameSession> { }
  async sendMessage(sessionId: string, message: string): Promise<GameMessage> { }
  // ... other methods
}
```

### 4.3 Real-time Features

- WebSocket connection for real-time updates
- Typing indicators during AI response generation
- Auto-save functionality
- Session heartbeat to prevent timeouts

## Phase 5: Polish & Optimization (Week 6)

### 5.1 Performance Optimization

- Code splitting and lazy loading
- Image optimization for story thumbnails
- Memoization of expensive components
- Bundle size optimization

### 5.2 User Experience Enhancements

- Loading states and skeletons
- Error boundaries and fallbacks
- Offline mode indicators
- Toast notifications for actions

### 5.3 Testing & Documentation

- Unit tests for components
- Integration tests for game flow
- API endpoint testing
- User documentation

## Implementation Priorities

### Must-Have Features (MVP)
1. ✅ Story selection interface
2. ✅ Character creation flow
3. ✅ Basic game conversation interface
4. ✅ Session persistence
5. ✅ Backend API integration

### Should-Have Features
1. 🔄 Advanced UI animations
2. 🔄 Session browser with filters
3. 🔄 Character equipment visualization
4. 🔄 Mobile responsive design
5. 🔄 Accessibility features

### Could-Have Features
1. ⏳ Multiplayer sessions
2. ⏳ Story creation tools
3. ⏳ Achievement system
4. ⏳ Share adventure summaries
5. ⏳ Theme customization

## Design System

### Color Palette (ChatGPT-inspired)
```css
:root {
  --background: 212 12% 4%;           /* Dark background */
  --foreground: 213 31% 91%;         /* Light text */
  --primary: 210 40% 98%;            /* Primary buttons */
  --primary-foreground: 222.2 84% 4.9%; 
  --secondary: 217.2 32.6% 17.5%;    /* Secondary elements */
  --accent: 217.2 32.6% 17.5%;       /* Accent colors */
  --muted: 217.2 32.6% 17.5%;        /* Muted text */
  --border: 217.2 32.6% 17.5%;       /* Borders */
}
```

### Typography
- **Headings**: Inter font family, various weights
- **Body Text**: System font stack for readability
- **Monospace**: For code/technical elements

### Component Styling Guidelines
- Consistent spacing using Tailwind's scale
- Rounded corners (rounded-lg, rounded-xl)
- Subtle shadows and gradients
- Smooth transitions (duration-200, duration-300)

## File Structure Implementation

```
frontend/
├── app/
│   ├── api/                          # Next.js API routes
│   │   └── proxy/                    # Proxy to Python backend
│   ├── game/
│   │   ├── [sessionId]/
│   │   │   └── page.tsx              # Main game interface
│   │   ├── character-creation/
│   │   │   └── page.tsx              # Character creation wizard
│   │   ├── story-selection/
│   │   │   └── page.tsx              # Story selection grid
│   │   └── sessions/
│   │       └── page.tsx              # Session browser
│   ├── globals.css                   # Global styles
│   ├── layout.tsx                    # Root layout
│   └── page.tsx                      # Landing page
├── components/
│   ├── game/
│   │   ├── character-creation/
│   │   │   ├── character-name-form.tsx
│   │   │   ├── equipment-selection.tsx
│   │   │   └── character-summary.tsx
│   │   ├── conversation/
│   │   │   ├── message-bubble.tsx
│   │   │   ├── choice-buttons.tsx
│   │   │   └── custom-action-input.tsx
│   │   ├── session/
│   │   │   ├── session-browser.tsx
│   │   │   ├── session-card.tsx
│   │   │   └── session-details-modal.tsx
│   │   └── story/
│   │       ├── story-card.tsx
│   │       ├── story-filter.tsx
│   │       └── story-preview-modal.tsx
│   ├── layout/
│   │   ├── game-header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   └── ui/                           # ShadCN components (existing)
├── hooks/
│   ├── use-game-state.ts             # Game state management
│   ├── use-api.ts                    # API interaction
│   └── use-session-storage.ts        # Local storage helpers
├── lib/
│   ├── api-client.ts                 # API client
│   ├── game-context.tsx              # React context
│   ├── utils.ts                      # Utility functions
│   └── validations.ts                # Form validations
└── types/
    ├── game.ts                       # Game-related types
    ├── api.ts                        # API response types
    └── ui.ts                         # UI component types
```

## Development Commands

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npx tsc --noEmit
```

## Environment Configuration

**File**: `.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Deployment Considerations

### Frontend Deployment
- **Platform**: Vercel (recommended for Next.js)
- **Build Command**: `npm run build`
- **Environment Variables**: API URLs, feature flags

### Backend API Deployment
- **Platform**: Railway, DigitalOcean, or AWS
- **Requirements**: Docker support for Qdrant
- **Environment**: Python 3.8+, sufficient RAM for Ollama model

### Full-Stack Deployment
- Docker Compose setup for local development
- Separate containers for frontend, backend API, and Qdrant
- Nginx reverse proxy for production

This plan provides a comprehensive roadmap for creating a modern, ChatGPT-inspired web interface that fully replicates the Python game's functionality while providing an enhanced user experience through responsive design and intuitive interactions.
