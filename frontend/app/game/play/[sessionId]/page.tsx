"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  ArrowLeft,
  User,
  Settings
} from "lucide-react";
import { useGameSession } from "@/hooks/use-game-api";
import { GameMessage } from "@/types/game";
import { GameMasterOrb } from "@/components/ui/game-master-orb";

// Utility function to parse simple markdown
const parseMarkdown = (text: string) => {
  // Split by paragraphs
  const paragraphs = text.split('\n\n');

  return paragraphs.map((paragraph, pIndex) => {
    const lines = paragraph.split('\n');

    return (
      <div key={pIndex} className={pIndex > 0 ? 'mt-4' : ''}>
        {lines.map((line, lIndex) => {
          // Check if this is likely a question - more flexible detection
          const trimmedLine = line.trim();
          const isQuestion = trimmedLine.endsWith('?') && (
            trimmedLine.toLowerCase().includes('what do you') ||
            trimmedLine.toLowerCase().includes('what will you') ||
            trimmedLine.toLowerCase().includes('how do you') ||
            trimmedLine.toLowerCase().includes('where do you') ||
            trimmedLine.toLowerCase().includes('do you do') ||
            trimmedLine.toLowerCase().includes('do next') ||
            trimmedLine.toLowerCase().includes('your next move') ||
            trimmedLine.toLowerCase().includes('your decision') ||
            (trimmedLine.toLowerCase().startsWith('what') && trimmedLine.includes('you'))
          );

          // Parse both single and double asterisk formatting
          const parts = line.split(/(\*\*.*?\*\*|\*.*?\*)/g);
          const renderedLine = parts.map((part, index) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              // Double asterisk - header/strong emphasis
              const boldText = part.slice(2, -2);
              return <strong key={index} className="font-bold text-gray-100">{boldText}</strong>;
            } else if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
              // Single asterisk - italic/emphasis (but we'll make it bold for game text)
              const italicText = part.slice(1, -1);
              return <strong key={index} className="font-semibold text-purple-200">{italicText}</strong>;
            }
            return part;
          });

          return (
            <div
              key={lIndex}
              className={`${isQuestion ? 'font-bold text-purple-100 mt-6 text-2xl border-l-4 border-purple-400 pl-4 py-3 bg-purple-900/20 rounded-r-lg' : ''} ${lIndex > 0 ? 'mt-1' : ''}`}
            >
              {renderedLine}
            </div>
          );
        })}
      </div>
    );
  });
};

// Utility function to parse choice text into header and content
const parseChoice = (choice: string) => {
  // Remove leading/trailing whitespace
  const trimmed = choice.trim();

  // Check if this is already in the format from JSON parsing: **Action Name** Description
  const jsonFormatMatch = trimmed.match(/^\*\*(.*?)\*\*\s*(.*)$/);
  if (jsonFormatMatch) {
    return {
      header: jsonFormatMatch[1].trim(),
      content: jsonFormatMatch[2].trim()
    };
  }

  // Try to parse as raw JSON if it looks like it (for debugging)
  try {
    const parsed = JSON.parse(trimmed);
    if (parsed.name && parsed.description) {
      return {
        header: parsed.name,
        content: parsed.description
      };
    }
  } catch (e) {
    // Not JSON, continue with other parsing methods
  }

  // Pattern 2: Action Name: Description
  const colonMatch = trimmed.match(/^([^:]+):\s*(.*)$/);
  if (colonMatch) {
    return {
      header: colonMatch[1].trim(),
      content: colonMatch[2].trim()
    };
  }

  // Pattern 3: Action Name - Description
  const dashMatch = trimmed.match(/^([^-]+)-\s*(.*)$/);
  if (dashMatch) {
    return {
      header: dashMatch[1].trim(),
      content: dashMatch[2].trim()
    };
  }

  // Pattern 4: Look for bold text anywhere in the string
  const anyBoldMatch = trimmed.match(/^(.*?)\*\*(.*?)\*\*(.*)$/);
  if (anyBoldMatch) {
    const beforeBold = anyBoldMatch[1].trim();
    const boldText = anyBoldMatch[2].trim();
    const afterBold = anyBoldMatch[3].trim();

    return {
      header: boldText,
      content: [beforeBold, afterBold].filter(text => text.length > 0).join(' ')
    };
  }

  // Pattern 5: Try to split on first period if it creates reasonable parts
  const sentences = trimmed.split(/\.\s+/);
  if (sentences.length > 1 && sentences[0].length > 0 && sentences[0].length < 50) {
    return {
      header: sentences[0].trim(),
      content: sentences.slice(1).join('. ').trim()
    };
  }

  // Fallback: If choice is too long, try to extract first meaningful phrase
  if (trimmed.length > 50) {
    const words = trimmed.split(' ');
    const firstPart = words.slice(0, 4).join(' '); // Take first 4 words as header
    const secondPart = words.slice(4).join(' '); // Rest as content

    if (secondPart.length > 0) {
      return {
        header: firstPart,
        content: secondPart
      };
    }
  }

  // Final fallback: treat entire text as header
  return {
    header: trimmed,
    content: ''
  };
};

export default function GamePlayPage() {
  const router = useRouter();
  const params = useParams();
  const sessionId = params.sessionId as string;

  const { session, messages, loading, error, sendMessage } = useGameSession(sessionId);
  const [isSending, setIsSending] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);
  const [currentChoices, setCurrentChoices] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const latestAiMessageRef = useRef<HTMLDivElement>(null);

  const scrollToLatestMessage = useCallback(() => {
    // If there are messages, try to scroll to the latest AI message
    if (messages && messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      if (latestMessage.type === 'ai' && latestAiMessageRef.current) {
        // Scroll to the top of the latest AI message with offset for action bar
        setTimeout(() => {
          latestAiMessageRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
            inline: "nearest"
          });
        }, 100);
      } else {
        // Fall back to scrolling to bottom for user messages, accounting for action bar
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end"
          });
        }, 100);
      }
    }
  }, [messages]);

  useEffect(() => {
    scrollToLatestMessage();
  }, [messages, scrollToLatestMessage]);

  // Auto-generate opening story when session is loaded but has no messages
  useEffect(() => {
    if (session && messages && messages.length === 0 && !loading && !isSending && !isInitializing) {
      // This is a new session with no messages - trigger AI to generate opening scene
      const initializeStory = async () => {
        try {
          setIsInitializing(true);
          await sendMessage("Begin the adventure and set the scene. Respond in JSON format with story content and exactly 4 action choices formatted as name and description pairs.");
        } catch (error) {
          console.error('Failed to initialize story:', error);
        } finally {
          setIsInitializing(false);
        }
      }; initializeStory();
    }
  }, [session, messages, loading, isSending, isInitializing, sendMessage]);

  // Update current choices when messages change
  useEffect(() => {
    if (messages && messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      if (latestMessage.type === 'ai' && latestMessage.choices && latestMessage.choices.length > 0) {
        setCurrentChoices(latestMessage.choices);
      }
    }
  }, [messages]);

  const handleChoiceSelect = async (choice: string) => {
    if (isSending || !session) {
      console.log('Choice blocked:', { isSending, session: !!session });
      return;
    }

    console.log('Choice clicked:', choice);
    const parsedChoice = parseChoice(choice);
    const cleanAction = parsedChoice.header.replace(/\*\*/g, '').replace(/\*/g, '').replace(/:$/, '').trim();

    try {
      setIsSending(true);
      console.log('About to send message:', cleanAction);
      await sendMessage(cleanAction);
      console.log('Message sent successfully');
      // Clear choices after sending
      setCurrentChoices([]);
    } catch (error) {
      console.error('Failed to send choice:', error);
    } finally {
      setIsSending(false);
      console.log('isSending set to false');
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };

  const handleReturnToMenu = () => {
    router.push('/');
  };

  const handleSessionSettings = () => {
    // Future: Open session settings modal
    console.log('Session settings clicked');
  };

  if (loading || isInitializing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading your adventure...</p>
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">
            {error || 'Session not found'}
          </p>
          <Button
            onClick={handleReturnToMenu}
            className="bg-purple-600 hover:bg-purple-700"
          >
            Return to Menu
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col overflow-hidden">
      {/* Auto-hiding Header */}
      <div className="fixed top-0 left-0 right-0 z-50 group">
        {/* Invisible hover trigger area */}
        <div className="h-4 w-full bg-transparent"></div>

        {/* Actual header - minimal by default, expands on hover */}
        <div className="border-b border-slate-700 bg-slate-900/80 backdrop-blur-sm transform transition-all duration-300 ease-in-out -translate-y-full group-hover:translate-y-0 opacity-0 group-hover:opacity-100">
          <div className="container mx-auto px-4 transition-all duration-300 ease-in-out py-3 group-hover:py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  onClick={handleReturnToMenu}
                  variant="ghost"
                  size="sm"
                  className="text-gray-400 hover:text-white"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Menu
                </Button>

                {/* Minimal state - just adventure name */}
                <div className="group-hover:hidden">
                  <h1 className="text-xl font-bold text-white">{session.story.name}</h1>
                </div>

                {/* Expanded state - full info */}
                <div className="hidden group-hover:block">
                  <h1 className="text-xl font-bold text-white">{session.story.name}</h1>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <User className="w-4 h-4" />
                    <span>{session.character.name}</span>
                    <span>•</span>
                    <span>Turn {session.currentTurn}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="secondary">{session.story.genre}</Badge>
                    <Badge variant="secondary">{session.story.setting}</Badge>
                    <Badge className={
                      session.story.difficulty === 'easy' ? 'bg-green-500/20 text-green-400' :
                        session.story.difficulty === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                    }>
                      {session.story.difficulty}
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="flex items-center">
                <Button
                  onClick={handleSessionSettings}
                  variant="ghost"
                  size="sm"
                  className="text-gray-400 hover:text-white"
                >
                  <Settings className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col pt-16 pb-0">
        <div className="container mx-auto px-4 flex-1 flex flex-col min-h-0">
          {/* Messages Container - Fixed height with internal scroll */}
          <div className="flex-1 overflow-hidden" style={{ maxHeight: 'calc(100vh - 10rem)' }}>
            <ScrollArea className="h-full">
              <div className="space-y-4 pr-4 pb-40 px-2">
                {messages && messages.length > 0 ? messages
                  .filter(message =>
                    message.content !== 'Begin the adventure and set the scene' &&
                    message.content !== 'Begin the adventure and set the scene. Respond in JSON format with story content and exactly 4 action choices formatted as name and description pairs.' &&
                    !message.content.startsWith('```json')
                  )
                  .map((message: GameMessage, index: number) => {
                    const isLatestAiMessage = message.type === 'ai' && index === messages.length - 1;
                    return (
                      <div
                        key={message.id}
                        ref={isLatestAiMessage ? latestAiMessageRef : null}
                      >
                        {message.type === 'user' ? (
                          // Ornamental separator line instead of user message card
                          <div className="flex justify-center py-6">
                            <div className="flex items-center justify-center w-1/2 max-w-md">
                              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-100 to-transparent opacity-30"></div>
                              <div className="mx-4">
                                <div className="w-2 h-2 bg-gray-100 rounded-full opacity-40"></div>
                              </div>
                              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-100 to-transparent opacity-30"></div>
                            </div>
                          </div>
                        ) : (
                          // AI messages with orb on the left with proper spacing
                          <div className="flex justify-start items-start gap-4 px-6">
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <div className="mt-2 ml-16">
                                    <GameMasterOrb size="md" />
                                  </div>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Game Master</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>

                            <div className="flex-1 space-y-4">
                              <div className="text-gray-100 leading-relaxed">
                                {parseMarkdown(message.content)}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  }) : (
                  <div className="text-center text-gray-400 py-8">
                    <p>No messages yet. Start your adventure!</p>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
          </div>

          {/* Hidden - Text input removed in favor of choice grid */}
        </div>
      </div>

      {/* Sticky Action Bar - Fixed to bottom of viewport */}
      {currentChoices.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 z-40 p-2 bg-slate-900/95 backdrop-blur-sm border-t border-slate-700">
          <div className="container mx-auto">
            <div className="grid grid-cols-2 gap-2 max-w-4xl mx-auto">
              {currentChoices.slice(0, 4).map((choice, index) => {
                const parsedChoice = parseChoice(choice);
                return (
                  <TooltipProvider key={index}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Card
                          role="button"
                          tabIndex={0}
                          onClick={() => handleChoiceSelect(choice)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              handleChoiceSelect(choice);
                            }
                          }}
                          className={`cursor-pointer transition-all duration-200 border-2 bg-gradient-to-r from-slate-700 to-slate-600 border-slate-500 hover:from-purple-600 hover:to-purple-500 hover:border-purple-400 hover:shadow-lg hover:shadow-purple-500/25 min-h-[60px] ${isSending ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'
                            }`}
                          style={{ pointerEvents: isSending ? 'none' : 'auto' }}
                        >
                          <CardContent className="p-2 h-full flex items-center justify-center">
                            <div className="text-white font-semibold text-sm text-center">
                              {parsedChoice.header}
                            </div>
                          </CardContent>
                        </Card>
                      </TooltipTrigger>
                      {parsedChoice.content && (
                        <TooltipContent side="top" className="max-w-xs p-3 bg-slate-800 text-white border-slate-600">
                          <p className="text-sm leading-relaxed">{parsedChoice.content}</p>
                        </TooltipContent>
                      )}
                    </Tooltip>
                  </TooltipProvider>
                );
              })}

              {/* Fill empty slots if less than 4 choices */}
              {currentChoices.length < 4 && Array.from({ length: 4 - currentChoices.length }).map((_, index) => (
                <div key={`empty-${index}`} className="min-h-[60px]" />
              ))}
            </div>

            {isSending && (
              <div className="text-center mt-2">
                <div className="text-gray-400 text-sm">Game Master is thinking...</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
