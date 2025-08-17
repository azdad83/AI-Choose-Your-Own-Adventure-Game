"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Play, BookOpen, Users, Star } from "lucide-react";
import { useStories } from "@/hooks/use-game-api";
import { Story } from "@/types/game";

export default function StorySelectionPage() {
  const router = useRouter();
  const { stories, loading, error, refetch: fetchStories } = useStories();
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);

  const handleStorySelect = (story: Story) => {
    setSelectedStory(story);
  };

  const handleStartAdventure = () => {
    if (selectedStory) {
      // Navigate to character creation with the selected story
      router.push(`/game/character-creation?storyId=${selectedStory.id}`);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'bg-green-500/20 text-green-400';
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400';
      case 'hard':
        return 'bg-red-500/20 text-red-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStoryEmoji = (genre: string) => {
    switch (genre.toLowerCase()) {
      case 'fantasy':
        return '🧙‍♂️';
      case 'sci-fi':
        return '🚀';
      case 'mystery':
        return '🕵️';
      case 'horror':
        return '🧛';
      case 'romance':
        return '💕';
      case 'adventure':
        return '⚔️';
      default:
        return '📖';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading adventures...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">Failed to load stories: {error}</p>
          <Button onClick={() => fetchStories()} className="bg-purple-600 hover:bg-purple-700">
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
        <div className="flex items-center gap-4 mb-8">
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
            <h1 className="text-3xl font-bold text-white">Choose Your Adventure</h1>
            <p className="text-gray-400">Select a story to begin your journey</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Stories List */}
          <div className="lg:col-span-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {stories.map((story: Story) => (
                <Card
                  key={story.id}
                  className={`cursor-pointer transition-all duration-200 ${
                    selectedStory?.id === story.id
                      ? 'bg-purple-800/50 border-purple-500 ring-2 ring-purple-400'
                      : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800/70'
                  }`}
                  onClick={() => handleStorySelect(story)}
                >
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="text-3xl">{getStoryEmoji(story.genre)}</div>
                      <Badge className={getDifficultyColor(story.difficulty)}>
                        {story.difficulty}
                      </Badge>
                    </div>
                    <CardTitle className="text-white text-lg">
                      {story.name}
                    </CardTitle>
                    <CardDescription className="text-gray-400">
                      {story.setting}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                      {story.description}
                    </p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      <Badge variant="secondary" className="text-xs">
                        {story.genre}
                      </Badge>
                      {story.themes?.map((theme: string, index: number) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {theme}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <div className="flex items-center gap-1">
                        <BookOpen className="w-4 h-4" />
                        <span>{story.genre}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        <span>{story.difficulty}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4" />
                        <span>4.8</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Story Details Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              {selectedStory ? (
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="text-4xl">{getStoryEmoji(selectedStory.genre)}</div>
                      <div>
                        <CardTitle className="text-white text-xl">
                          {selectedStory.name}
                        </CardTitle>
                        <CardDescription className="text-gray-400">
                          {selectedStory.setting}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h3 className="text-white font-semibold mb-2">Description</h3>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {selectedStory.description}
                      </p>
                    </div>

                    <div>
                      <h3 className="text-white font-semibold mb-2">Details</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Genre:</span>
                          <Badge variant="secondary">{selectedStory.genre}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Difficulty:</span>
                          <Badge className={getDifficultyColor(selectedStory.difficulty)}>
                            {selectedStory.difficulty}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Setting:</span>
                          <span className="text-white text-sm">{selectedStory.setting}</span>
                        </div>
                      </div>
                    </div>

                    {selectedStory.themes && selectedStory.themes.length > 0 && (
                      <div>
                        <h3 className="text-white font-semibold mb-2">Themes</h3>
                        <div className="flex flex-wrap gap-2">
                          {selectedStory.themes.map((theme: string, index: number) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {theme}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <Button
                      onClick={handleStartAdventure}
                      className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                      size="lg"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Start This Adventure
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <Card className="bg-slate-800/50 border-slate-700">
                  <CardContent className="p-8 text-center">
                    <BookOpen className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <h3 className="text-white font-semibold mb-2">Select a Story</h3>
                    <p className="text-gray-400 text-sm">
                      Choose an adventure from the list to see more details and begin your journey.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
