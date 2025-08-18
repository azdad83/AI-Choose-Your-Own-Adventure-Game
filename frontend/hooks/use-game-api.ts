"use client";

import { useState, useEffect } from 'react';
import { Story, GameSession, SessionSummary } from '@/types/game';
import { gameApi, devGameApi, isDevelopmentMode } from '@/lib/api-client';
import { useGame } from '@/lib/game-context';

// Hook for fetching stories
export function useStories() {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStories = async () => {
    try {
      setLoading(true);
      setError(null);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const fetchedStories = await client.getStories();
      setStories(fetchedStories);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stories');
      console.error('Error fetching stories:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStories();
  }, []);

  return { stories, loading, error, refetch: fetchStories };
}

// Hook for fetching sessions
export function useSessions() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const fetchedSessions = await client.getSessions();
      setSessions(fetchedSessions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  return { 
    sessions, 
    loading, 
    error, 
    refetch: fetchSessions,
    deleteSessions: async (sessionId: string) => {
      try {
        const client = isDevelopmentMode ? devGameApi : gameApi;
        await client.deleteSession(sessionId);
        await fetchSessions(); // Refresh the list
      } catch (err) {
        console.error('Error deleting session:', err);
        throw err;
      }
    }
  };
}

// Hook for game session management
export function useGameSession(sessionId?: string) {
  const { state, setSession, setMessages, setLoading, setError } = useGame();
  const [initializing, setInitializing] = useState(false);

  const createSession = async (storyId: string, characterName: string) => {
    try {
      setLoading(true);
      setError(undefined);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const session = await client.createSession(storyId, characterName);
      setSession(session);
      return session;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create session';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loadSession = async (id: string) => {
    try {
      setInitializing(true);
      setError(undefined);
      
      // Clear any existing session first to force fresh load
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const session = await client.getSession(id);
      const messages = await client.getMessages(id);
      setSession(session);
      setMessages(messages);
      return session;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session';
      setError(errorMessage);
      throw err;
    } finally {
      setInitializing(false);
    }
  };

  const sendMessage = async (message: string) => {
    if (!state.session) {
      throw new Error('No active session');
    }

    try {
      setLoading(true);
      setError(undefined);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const response = await client.sendMessage(state.session.sessionId, message);
      
      // Add user message
      const userMessage = {
        id: `user-${Date.now()}`,
        type: 'user' as const,
        content: message,
        timestamp: new Date().toISOString(),
      };
      
      // Add AI response
      const aiMessage = response.message;
      
      setMessages([...state.messages, userMessage, aiMessage]);
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Load session on component mount if sessionId is provided
  useEffect(() => {
    if (sessionId && sessionId !== state.session?.sessionId) {
      loadSession(sessionId).catch(console.error);
    }
  }, [sessionId]);

  return {
    session: state.session,
    messages: state.messages,
    loading: state.isLoading || initializing,
    error: state.error,
    createSession,
    loadSession,
    sendMessage,
  };
}

// Hook for character creation
export function useCharacterCreation() {
  const { state, updateCharacter, setLoading, setError } = useGame();
  const [currentStep, setCurrentStep] = useState<'weapon' | 'skill' | 'tool'>('weapon');
  const [stepData, setStepData] = useState<{
    weapon?: { options: string[]; prompt: string };
    skill?: { options: string[]; prompt: string };
    tool?: { options: string[]; prompt: string };
  }>({});

  const getCharacterCreationStep = async (
    sessionId: string,
    step: 'weapon' | 'skill' | 'tool',
    storyId: string,
    characterName: string,
    genre: string,
    setting: string
  ) => {
    try {
      setLoading(true);
      setError(undefined);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const stepResponse = await client.getCharacterCreationStep(
        sessionId,
        step,
        storyId,
        characterName,
        genre,
        setting
      );
      
      setStepData(prev => ({
        ...prev,
        [step]: {
          options: stepResponse.options,
          prompt: stepResponse.prompt,
        }
      }));
      
      return stepResponse;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get character creation step';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const submitCharacterChoice = async (
    sessionId: string,
    choiceType: 'weapon' | 'skill' | 'tool',
    choice: string
  ) => {
    try {
      setLoading(true);
      setError(undefined);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      await client.submitCharacterChoice(sessionId, choiceType, choice);
      
      // Update local character state
      updateCharacter({ [choiceType]: choice });
      
      // Move to next step
      const stepOrder: ('weapon' | 'skill' | 'tool')[] = ['weapon', 'skill', 'tool'];
      const currentIndex = stepOrder.indexOf(currentStep);
      if (currentIndex < stepOrder.length - 1) {
        setCurrentStep(stepOrder[currentIndex + 1]);
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit character choice';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const isCharacterCreationComplete = () => {
    if (!state.session) return false;
    const { character } = state.session;
    return character.weapon && character.skill && character.tool;
  };

  return {
    currentStep,
    setCurrentStep,
    stepData,
    character: state.session?.character,
    loading: state.isLoading,
    error: state.error,
    getCharacterCreationStep,
    submitCharacterChoice,
    isCharacterCreationComplete,
  };
}
