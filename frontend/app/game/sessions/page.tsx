"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Play, Trash2, Calendar, User, BookOpen, Plus } from "lucide-react";
import { useSessions } from "@/hooks/use-game-api";
import { SessionSummary } from "@/types/game";
import { gameApi, devGameApi, isDevelopmentMode } from "@/lib/api-client";

export default function SessionsPage() {
  const router = useRouter();
  const { sessions, loading, error, refetch } = useSessions();
  const [deleting, setDeleting] = useState<string | null>(null);

  const handleContinueSession = (sessionId: string) => {
    router.push(`/game/play/${sessionId}`);
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      setDeleting(sessionId);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      await client.deleteSession(sessionId);
      await refetch(); // Refresh the sessions list
    } catch (error) {
      console.error('Failed to delete session:', error);
    } finally {
      setDeleting(null);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Unknown date';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading your adventures...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">Failed to load sessions: {error}</p>
          <Button onClick={refetch} className="bg-purple-600 hover:bg-purple-700">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              onClick={() => router.back()}
              variant="ghost"
              size="sm"
              className="text-gray-400 hover:text-white"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-white">Your Adventures</h1>
              <p className="text-gray-400">Continue where you left off or start a new journey</p>
            </div>
          </div>
          
          <Button
            onClick={() => router.push('/game/story-selection')}
            className="bg-purple-600 hover:bg-purple-700 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Adventure
          </Button>
        </div>

        {sessions.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="w-24 h-24 text-gray-500 mx-auto mb-6" />
            <h2 className="text-2xl font-bold text-white mb-4">No Adventures Yet</h2>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              You haven&apos;t started any adventures yet. Create your first character and begin an epic journey!
            </p>
            <Button
              onClick={() => router.push('/game/story-selection')}
              className="bg-purple-600 hover:bg-purple-700 text-white"
              size="lg"
            >
              <Plus className="w-5 h-5 mr-2" />
              Start Your First Adventure
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session: SessionSummary) => (
              <Card
                key={session.sessionId}
                className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors group"
              >
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-2xl">📖</div>
                    <Badge className="bg-blue-500/20 text-blue-400">
                      {session.progress}% Complete
                    </Badge>
                  </div>
                  <CardTitle className="text-white text-lg">
                    {session.storyName}
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    Adventure in Progress
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  {/* Character Info */}
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <User className="w-4 h-4" />
                    <span className="font-medium">{session.characterName}</span>
                  </div>

                  {/* Session Details */}
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(session.lastActivity)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span>Turn {session.currentTurn}</span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-400">
                      <span>Progress</span>
                      <span>{session.progress}%</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${session.progress}%` }}
                      />
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      onClick={() => handleContinueSession(session.sessionId)}
                      className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
                      size="sm"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Continue
                    </Button>
                    
                    <Button
                      onClick={() => handleDeleteSession(session.sessionId)}
                      disabled={deleting === session.sessionId}
                      variant="outline"
                      size="sm"
                      className="border-red-500 text-red-400 hover:bg-red-500 hover:text-white"
                    >
                      {deleting === session.sessionId ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
