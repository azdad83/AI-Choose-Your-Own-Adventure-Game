// API request/response types
export interface CreateSessionRequest {
  storyId: string;
  characterName: string;
  weapon?: string;
  skill?: string;
  tool?: string;
}

export interface CreateSessionResponse {
  sessionId: string;
  session: import('./game').GameSession;
}

export interface SendMessageRequest {
  sessionId: string;
  message: string;
  choice?: string;
}

export interface SendMessageResponse {
  message: import('./game').GameMessage;
  choices?: string[];
  gameEnded?: boolean;
}

export interface CharacterCreationRequest {
  sessionId: string;
  step: 'weapon' | 'skill' | 'tool';
  storyId: string;
  characterName: string;
  genre: string;
  setting: string;
}

export interface CharacterCreationResponse {
  step: 'weapon' | 'skill' | 'tool';
  options: string[];
  prompt: string;
}

export interface CharacterChoiceRequest {
  sessionId: string;
  choiceType: 'weapon' | 'skill' | 'tool';
  choice: string;
}

export interface SessionListResponse {
  sessions: import('./game').SessionSummary[];
}

export interface StoryListResponse {
  stories: import('./game').Story[];
}

// Error types
export interface ApiError {
  code: string;
  message: string;
  details?: any;
}
