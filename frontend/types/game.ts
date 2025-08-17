export interface Story {
  id: string;
  name: string;
  description: string;
  genre: string;
  difficulty: 'easy' | 'medium' | 'hard';
  estimatedLength: string;
  setting: string;
  themes: string[];
  initialPrompt?: string;
  author?: string;
  createdDate?: string;
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
  createdAt: string;
}

export interface GameMessage {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: string;
  choices?: string[];
  turnNumber?: number;
}

export interface GameState {
  phase: 'lobby' | 'story-selection' | 'character-creation' | 'gameplay' | 'game-over';
  session?: GameSession;
  messages: GameMessage[];
  isLoading: boolean;
  error?: string;
}

export interface CharacterCreationStep {
  step: 'weapon' | 'skill' | 'tool';
  options: string[];
  prompt: string;
}

export interface CharacterChoice {
  type: 'weapon' | 'skill' | 'tool';
  choice: string;
  description: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface SessionSummary {
  sessionId: string;
  characterName: string;
  storyName: string;
  currentTurn: number;
  lastActivity: string;
  progress: number; // 0-100 percentage
}
