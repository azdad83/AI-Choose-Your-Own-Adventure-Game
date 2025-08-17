"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sword, Users, BookOpen, Play, RotateCcw, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

export default function HomePage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleNewGame = () => {
    router.push('/game/story-selection');
  };

  const handleContinueGame = () => {
    router.push('/game/sessions');
  };

  if (!mounted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20 animate-pulse"></div>
        <div className="relative container mx-auto px-4 py-16 sm:py-24">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-purple-600/20 rounded-full">
                <Sparkles className="w-12 h-12 text-purple-400" />
              </div>
            </div>
            <h1 className="text-4xl sm:text-6xl font-bold text-white mb-6">
              AI Choose Your Own
              <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent block">
                Adventure
              </span>
            </h1>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Embark on dynamic storytelling adventures powered by AI. Create unique characters, 
              make meaningful choices, and shape your own epic tales.
            </p>
            
            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                onClick={handleNewGame}
                size="lg"
                className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 text-lg"
              >
                <Play className="w-5 h-5 mr-2" />
                Start New Adventure
              </Button>
              
              <Button
                onClick={handleContinueGame}
                variant="outline"
                size="lg"
                className="border-purple-400 text-purple-400 hover:bg-purple-400 hover:text-white px-8 py-3 text-lg"
              >
                <RotateCcw className="w-5 h-5 mr-2" />
                Continue Adventure
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-6 text-center">
              <BookOpen className="w-8 h-8 text-blue-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">6</div>
              <div className="text-gray-400">Stories Available</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-6 text-center">
              <Users className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">0</div>
              <div className="text-gray-400">Your Adventures</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-6 text-center">
              <Sword className="w-8 h-8 text-red-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">∞</div>
              <div className="text-gray-400">Possibilities</div>
            </CardContent>
          </Card>
        </div>

        {/* Featured Stories Preview */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-white mb-6 text-center">Featured Adventures</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors cursor-pointer group">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="text-2xl">🧙‍♂️</div>
                  <Badge className="bg-green-500/20 text-green-400">easy</Badge>
                </div>
                <CardTitle className="text-white group-hover:text-purple-400 transition-colors">
                  Mystical Woods Adventure
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Enchanted Forest
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 text-sm mb-4">
                  Journey through the enchanted Whispering Woods in search of the legendary Gem of Serenity.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" className="text-xs">magic</Badge>
                  <Badge variant="secondary" className="text-xs">nature</Badge>
                  <Badge variant="secondary" className="text-xs">quest</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors cursor-pointer group">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="text-2xl">🕵️</div>
                  <Badge className="bg-yellow-500/20 text-yellow-400">medium</Badge>
                </div>
                <CardTitle className="text-white group-hover:text-purple-400 transition-colors">
                  Noir Detective Mystery
                </CardTitle>
                <CardDescription className="text-gray-400">
                  1940s New York City
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 text-sm mb-4">
                  A gritty detective story in New York City. Solve crimes and uncover corruption.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" className="text-xs">mystery</Badge>
                  <Badge variant="secondary" className="text-xs">crime</Badge>
                  <Badge variant="secondary" className="text-xs">urban</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors cursor-pointer group">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="text-2xl">🚀</div>
                  <Badge className="bg-red-500/20 text-red-400">hard</Badge>
                </div>
                <CardTitle className="text-white group-hover:text-purple-400 transition-colors">
                  Deep Space Explorer
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Deep Space, 2387 CE
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 text-sm mb-4">
                  Command a starship on the edge of known space and discover alien civilizations.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" className="text-xs">exploration</Badge>
                  <Badge variant="secondary" className="text-xs">aliens</Badge>
                  <Badge variant="secondary" className="text-xs">leadership</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
