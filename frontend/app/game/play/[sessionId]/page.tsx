"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  ArrowLeft, 
  Send, 
  User, 
  Bot, 
  Settings,
  Volume2,
  VolumeX 
} from "lucide-react";
import { useGameSession } from "@/hooks/use-game-api";
import { GameMessage } from "@/types/game";

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
  
  // Look for bold text at the beginning (either at start or after **)
  const boldMatch = trimmed.match(/^\*\*(.*?)\*\*\s*(.*)$/);
  if (boldMatch) {
    return {
      header: boldMatch[1].trim(),
      content: boldMatch[2].trim()
    };
  }
  
  // Look for bold text anywhere in the string
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
  
  // Try to split on first period or sentence
  const sentences = trimmed.split(/\.\s+/);
  if (sentences.length > 1) {
    return {
      header: sentences[0] + '.',
      content: sentences.slice(1).join('. ')
    };
  }
  
  // Fallback: treat entire text as header
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
  const [newMessage, setNewMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const latestAiMessageRef = useRef<HTMLDivElement>(null);

  const scrollToLatestMessage = useCallback(() => {
    // If there are messages, try to scroll to the latest AI message
    if (messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      if (latestMessage.type === 'ai' && latestAiMessageRef.current) {
        // Scroll to the top of the latest AI message
        latestAiMessageRef.current.scrollIntoView({ 
          behavior: "smooth",
          block: "start",
          inline: "nearest"
        });
      } else {
        // Fall back to scrolling to bottom for user messages
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [messages]);

  useEffect(() => {
    scrollToLatestMessage();
  }, [messages, scrollToLatestMessage]);

  const handleSendMessage = async () => {
    if (!newMessage.trim() || isSending || !session) return;

    try {
      setIsSending(true);
      await sendMessage(newMessage.trim());
      setNewMessage("");
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
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

  if (loading) {
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
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
              
              <div>
                <h1 className="text-xl font-bold text-white">{session.story.name}</h1>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <User className="w-4 h-4" />
                  <span>{session.character.name}</span>
                  <span>•</span>
                  <span>Turn {session.currentTurn}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                onClick={() => setSoundEnabled(!soundEnabled)}
                variant="ghost"
                size="sm"
                className="text-gray-400 hover:text-white"
              >
                {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              </Button>
              
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

      <div className="container mx-auto px-4 py-6 h-[calc(100vh-88px)] flex flex-col lg:flex-row gap-6">
        {/* Sidebar - Character & Story Info */}
        <div className="lg:w-80 space-y-4">
          {/* Character Card */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <User className="w-5 h-5" />
                {session.character.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {session.character.weapon && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Weapon:</span>
                  <Badge variant="secondary">⚔️ {session.character.weapon}</Badge>
                </div>
              )}
              {session.character.skill && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Skill:</span>
                  <Badge variant="secondary">⭐ {session.character.skill}</Badge>
                </div>
              )}
              {session.character.tool && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Tool:</span>
                  <Badge variant="secondary">🔧 {session.character.tool}</Badge>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Story Info */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white text-lg">{session.story.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Genre:</span>
                <Badge variant="secondary">{session.story.genre}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Setting:</span>
                <span className="text-white text-sm">{session.story.setting}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Difficulty:</span>
                <Badge className={
                  session.story.difficulty === 'easy' ? 'bg-green-500/20 text-green-400' :
                  session.story.difficulty === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-red-500/20 text-red-400'
                }>
                  {session.story.difficulty}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-h-0">
          {/* Messages */}
          <ScrollArea className="flex-1 pr-4 mb-4 max-h-[calc(100vh-240px)]">
            <div className="space-y-4">
              {messages.map((message: GameMessage, index: number) => {
                const isLatestAiMessage = message.type === 'ai' && index === messages.length - 1;
                return (
                  <div
                    key={message.id}
                    ref={isLatestAiMessage ? latestAiMessageRef : null}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                  <div className={`${message.type === 'user' ? 'max-w-[80%]' : 'w-full'} ${
                    message.type === 'user' 
                      ? 'bg-purple-600 text-white' 
                      : message.type === 'ai'
                      ? 'bg-slate-700 text-gray-100'
                      : 'bg-slate-600 text-gray-300'
                  } rounded-lg p-4 shadow-lg`}>
                    <div className="flex items-center gap-2 mb-2">
                      {message.type === 'user' ? (
                        <User className="w-4 h-4" />
                      ) : (
                        <Bot className="w-4 h-4" />
                      )}
                      <span className="text-sm font-medium">
                        {message.type === 'user' ? session.character.name : 'Game Master'}
                      </span>
                      <span className="text-xs opacity-75 ml-auto">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                    <div className="leading-relaxed">
                      {message.type === 'ai' ? parseMarkdown(message.content) : (
                        <div className="whitespace-pre-wrap">{message.content}</div>
                      )}
                    </div>
                    
                    {/* Choice cards for AI messages */}
                    {message.type === 'ai' && message.choices && message.choices.length > 0 && (
                      <div className="mt-4 grid gap-3" style={{ gridTemplateColumns: `repeat(${message.choices.length}, 1fr)` }}>
                        {message.choices.map((choice, index) => {
                          const parsedChoice = parseChoice(choice);
                          return (
                            <div
                              key={index}
                              role="button"
                              tabIndex={0}
                              onClick={async (e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                
                                if (isSending || !session) {
                                  console.log('Choice blocked:', { isSending, session: !!session });
                                  return;
                                }
                                
                                console.log('Choice clicked:', choice);
                                console.log('Current loading state:', loading);
                                console.log('Current isSending state:', isSending);
                                
                                // Send only the clean header text without markdown or punctuation
                                const cleanAction = parsedChoice.header.replace(/\*\*/g, '').replace(/\*/g, '').replace(/:$/, '').trim();
                                
                                try {
                                  setIsSending(true);
                                  console.log('About to send message:', cleanAction);
                                  await sendMessage(cleanAction);
                                  console.log('Message sent successfully');
                                } catch (error) {
                                  console.error('Failed to send choice:', error);
                                } finally {
                                  setIsSending(false);
                                  console.log('isSending set to false');
                                }
                              }}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault();
                                  e.currentTarget.click();
                                }
                              }}
                              className={`cursor-pointer transition-all duration-200 bg-slate-800 border border-slate-600 rounded-lg p-4 hover:bg-slate-700 hover:border-slate-500 ${
                                isSending ? 'opacity-50 cursor-not-allowed' : ''
                              }`}
                            >
                              <div className="text-gray-100 font-medium text-sm mb-2">
                                {parsedChoice.header}
                              </div>
                              {parsedChoice.content && (
                                <div className="text-gray-300 text-xs leading-relaxed">
                                  {parsedChoice.content}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
              
              {isSending && (
                <div className="flex justify-start">
                  <div className="bg-slate-700 text-gray-100 rounded-lg p-4 shadow-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Bot className="w-4 h-4" />
                      <span className="text-sm font-medium">Game Master</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="animate-bounce w-2 h-2 bg-gray-400 rounded-full"></div>
                      <div className="animate-bounce w-2 h-2 bg-gray-400 rounded-full delay-100"></div>
                      <div className="animate-bounce w-2 h-2 bg-gray-400 rounded-full delay-200"></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Message Input */}
          <div className="flex gap-2">
            <Textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="What do you do next?"
              className="flex-1 bg-slate-800 border-slate-600 text-white resize-none"
              rows={3}
              disabled={isSending}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!newMessage.trim() || isSending}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6"
            >
              {isSending ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
