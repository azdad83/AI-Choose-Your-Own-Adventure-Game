"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft, ArrowRight, Sword, Wrench, Star, User } from "lucide-react";
import { useStories } from "@/hooks/use-game-api";
import { Character, Story } from "@/types/game";
import { gameApi, devGameApi, isDevelopmentMode } from "@/lib/api-client";

interface CharacterOption {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
}

const weaponOptions: CharacterOption[] = [
  {
    id: "sword",
    name: "Sword",
    description: "A trusty blade for close combat",
    icon: <Sword className="w-6 h-6" />
  },
  {
    id: "bow",
    name: "Bow",
    description: "Strike from a distance with precision",
    icon: <span className="text-xl">🏹</span>
  },
  {
    id: "staff",
    name: "Staff",
    description: "Channel magical energies",
    icon: <span className="text-xl">🔮</span>
  },
  {
    id: "daggers",
    name: "Daggers",
    description: "Swift and stealthy attacks",
    icon: <span className="text-xl">🗡️</span>
  }
];

const skillOptions: CharacterOption[] = [
  {
    id: "stealth",
    name: "Stealth",
    description: "Move unseen and strike from shadows",
    icon: <span className="text-xl">🥷</span>
  },
  {
    id: "persuasion",
    name: "Persuasion",
    description: "Win others over with words",
    icon: <span className="text-xl">💬</span>
  },
  {
    id: "healing",
    name: "Healing",
    description: "Restore health and vitality",
    icon: <span className="text-xl">🩹</span>
  },
  {
    id: "athletics",
    name: "Athletics",
    description: "Physical prowess and endurance",
    icon: <span className="text-xl">💪</span>
  }
];

const toolOptions: CharacterOption[] = [
  {
    id: "lockpicks",
    name: "Lockpicks",
    description: "Open doors and chests",
    icon: <span className="text-xl">🔓</span>
  },
  {
    id: "rope",
    name: "Rope",
    description: "Climb and secure pathways",
    icon: <span className="text-xl">🪢</span>
  },
  {
    id: "compass",
    name: "Compass",
    description: "Never lose your way",
    icon: <span className="text-xl">🧭</span>
  },
  {
    id: "spellbook",
    name: "Spellbook",
    description: "Contains ancient knowledge",
    icon: <span className="text-xl">📚</span>
  }
];

export default function CharacterCreationPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading character creation...</p>
        </div>
      </div>
    }>
      <CharacterCreationContent />
    </Suspense>
  );
}

function CharacterCreationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const storyId = searchParams.get('storyId');
  
  const { stories } = useStories();
  
  const [story, setStory] = useState<Story | null>(null);
  const [step, setStep] = useState<'name' | 'weapon' | 'skill' | 'tool' | 'review'>('name');
  const [character, setCharacter] = useState<Character>({
    name: '',
    weapon: '',
    skill: '',
    tool: ''
  });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (storyId && stories.length > 0) {
      const foundStory = stories.find(s => s.id === storyId);
      setStory(foundStory || null);
    }
  }, [storyId, stories]);

  const handleNext = () => {
    switch (step) {
      case 'name':
        setStep('weapon');
        break;
      case 'weapon':
        setStep('skill');
        break;
      case 'skill':
        setStep('tool');
        break;
      case 'tool':
        setStep('review');
        break;
    }
  };

  const handleBack = () => {
    switch (step) {
      case 'weapon':
        setStep('name');
        break;
      case 'skill':
        setStep('weapon');
        break;
      case 'tool':
        setStep('skill');
        break;
      case 'review':
        setStep('tool');
        break;
      case 'name':
        router.back();
        break;
    }
  };

  const handleSelectOption = (optionId: string) => {
    switch (step) {
      case 'weapon':
        setCharacter(prev => ({ ...prev, weapon: optionId }));
        break;
      case 'skill':
        setCharacter(prev => ({ ...prev, skill: optionId }));
        break;
      case 'tool':
        setCharacter(prev => ({ ...prev, tool: optionId }));
        break;
    }
  };

  const handleStartGame = async () => {
    if (!story || !character.name) return;

    try {
      setCreating(true);
      const client = isDevelopmentMode ? devGameApi : gameApi;
      const session = await client.createSession(
        story.id, 
        character.name,
        character.weapon,
        character.skill,
        character.tool
      );
      // Navigate to the main game interface
      router.push(`/game/play/${session.sessionId}`);
    } catch (error) {
      console.error('Failed to create session:', error);
    } finally {
      setCreating(false);
    }
  };

  const isNextDisabled = () => {
    switch (step) {
      case 'name':
        return !character.name.trim();
      case 'weapon':
        return !character.weapon;
      case 'skill':
        return !character.skill;
      case 'tool':
        return !character.tool;
      default:
        return false;
    }
  };

  const renderStepContent = () => {
    switch (step) {
      case 'name':
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <User className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Name Your Character</h2>
              <p className="text-gray-400">What shall we call your hero?</p>
            </div>
            
            <div className="max-w-md mx-auto">
              <Label htmlFor="characterName" className="text-white text-lg mb-3 block">
                Character Name
              </Label>
              <Input
                id="characterName"
                type="text"
                placeholder="Enter your character's name..."
                value={character.name}
                onChange={(e) => setCharacter(prev => ({ ...prev, name: e.target.value }))}
                className="bg-slate-800 border-slate-600 text-white text-lg p-4"
                autoFocus
              />
            </div>
          </div>
        );

      case 'weapon':
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Sword className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Choose Your Weapon</h2>
              <p className="text-gray-400">What will be your primary tool in battle?</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              {weaponOptions.map((option) => (
                <Card
                  key={option.id}
                  className={`cursor-pointer transition-all duration-200 ${
                    character.weapon === option.id
                      ? 'bg-purple-800/50 border-purple-500 ring-2 ring-purple-400'
                      : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800/70'
                  }`}
                  onClick={() => handleSelectOption(option.id)}
                >
                  <CardContent className="p-6 text-center">
                    <div className="mb-3">{option.icon}</div>
                    <h3 className="text-white font-semibold mb-2">{option.name}</h3>
                    <p className="text-gray-400 text-sm">{option.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'skill':
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Star className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Choose Your Skill</h2>
              <p className="text-gray-400">What special ability do you possess?</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              {skillOptions.map((option) => (
                <Card
                  key={option.id}
                  className={`cursor-pointer transition-all duration-200 ${
                    character.skill === option.id
                      ? 'bg-purple-800/50 border-purple-500 ring-2 ring-purple-400'
                      : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800/70'
                  }`}
                  onClick={() => handleSelectOption(option.id)}
                >
                  <CardContent className="p-6 text-center">
                    <div className="mb-3">{option.icon}</div>
                    <h3 className="text-white font-semibold mb-2">{option.name}</h3>
                    <p className="text-gray-400 text-sm">{option.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'tool':
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Wrench className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Choose Your Tool</h2>
              <p className="text-gray-400">What item will aid you on your journey?</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              {toolOptions.map((option) => (
                <Card
                  key={option.id}
                  className={`cursor-pointer transition-all duration-200 ${
                    character.tool === option.id
                      ? 'bg-purple-800/50 border-purple-500 ring-2 ring-purple-400'
                      : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800/70'
                  }`}
                  onClick={() => handleSelectOption(option.id)}
                >
                  <CardContent className="p-6 text-center">
                    <div className="mb-3">{option.icon}</div>
                    <h3 className="text-white font-semibold mb-2">{option.name}</h3>
                    <p className="text-gray-400 text-sm">{option.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'review':
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="w-8 h-8 text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Review Your Character</h2>
              <p className="text-gray-400">Ready to begin your adventure?</p>
            </div>
            
            <Card className="bg-slate-800/50 border-slate-700 max-w-md mx-auto">
              <CardHeader>
                <CardTitle className="text-white text-center text-xl">
                  {character.name}
                </CardTitle>
                <CardDescription className="text-center text-gray-400">
                  Your Adventure Awaits
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Weapon:</span>
                  <Badge variant="secondary">
                    {weaponOptions.find(w => w.id === character.weapon)?.name}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Skill:</span>
                  <Badge variant="secondary">
                    {skillOptions.find(s => s.id === character.skill)?.name}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Tool:</span>
                  <Badge variant="secondary">
                    {toolOptions.find(t => t.id === character.tool)?.name}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  if (!story) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading story...</p>
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
            onClick={handleBack}
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-white">Create Your Character</h1>
            <p className="text-gray-400">For {story.name}</p>
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span className={step === 'name' ? 'text-purple-400 font-semibold' : ''}>Name</span>
            <span className={step === 'weapon' ? 'text-purple-400 font-semibold' : ''}>Weapon</span>
            <span className={step === 'skill' ? 'text-purple-400 font-semibold' : ''}>Skill</span>
            <span className={step === 'tool' ? 'text-purple-400 font-semibold' : ''}>Tool</span>
            <span className={step === 'review' ? 'text-purple-400 font-semibold' : ''}>Review</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2 mt-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: step === 'name' ? '20%' : 
                       step === 'weapon' ? '40%' : 
                       step === 'skill' ? '60%' : 
                       step === 'tool' ? '80%' : '100%'
              }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="max-w-4xl mx-auto">
          {renderStepContent()}
        </div>

        {/* Navigation */}
        <div className="max-w-2xl mx-auto mt-12 flex justify-between">
          <div /> {/* Spacer for alignment */}
          
          {step !== 'review' ? (
            <Button
              onClick={handleNext}
              disabled={isNextDisabled()}
              className="bg-purple-600 hover:bg-purple-700 text-white px-8"
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleStartGame}
              disabled={creating}
              className="bg-green-600 hover:bg-green-700 text-white px-8"
              size="lg"
            >
              {creating ? 'Starting...' : 'Begin Adventure'}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
