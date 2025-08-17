"use client";

import { useState, useEffect } from 'react';

// Hook for managing localStorage
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  const removeValue = () => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue, removeValue] as const;
}

// Hook for managing sessionStorage
export function useSessionStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting sessionStorage key "${key}":`, error);
    }
  };

  const removeValue = () => {
    try {
      window.sessionStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing sessionStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue, removeValue] as const;
}

// Hook for game preferences
interface GamePreferences {
  theme: 'light' | 'dark' | 'system';
  fontSize: 'small' | 'medium' | 'large';
  animationsEnabled: boolean;
  soundEnabled: boolean;
  autoSave: boolean;
}

const defaultPreferences: GamePreferences = {
  theme: 'dark',
  fontSize: 'medium',
  animationsEnabled: true,
  soundEnabled: true,
  autoSave: true,
};

export function useGamePreferences() {
  const [preferences, setPreferences, removePreferences] = useLocalStorage(
    'game-preferences',
    defaultPreferences
  );

  const updatePreference = <K extends keyof GamePreferences>(
    key: K,
    value: GamePreferences[K]
  ) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  const resetPreferences = () => {
    setPreferences(defaultPreferences);
  };

  return {
    preferences,
    updatePreference,
    resetPreferences,
    removePreferences,
  };
}

// Hook for recent sessions
export function useRecentSessions() {
  const [recentSessions, setRecentSessions] = useLocalStorage<string[]>('recent-sessions', []);

  const addRecentSession = (sessionId: string) => {
    setRecentSessions(prev => {
      const filtered = prev.filter(id => id !== sessionId);
      return [sessionId, ...filtered].slice(0, 5); // Keep only 5 most recent
    });
  };

  const removeRecentSession = (sessionId: string) => {
    setRecentSessions(prev => prev.filter(id => id !== sessionId));
  };

  const clearRecentSessions = () => {
    setRecentSessions([]);
  };

  return {
    recentSessions,
    addRecentSession,
    removeRecentSession,
    clearRecentSessions,
  };
}
