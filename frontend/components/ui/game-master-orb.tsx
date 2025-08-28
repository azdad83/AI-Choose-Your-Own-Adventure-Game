"use client";

import { Bot } from "lucide-react";

interface GameMasterOrbProps {
    isThinking?: boolean;
    size?: 'sm' | 'md' | 'lg';
}

export function GameMasterOrb({ isThinking = false, size = 'md' }: GameMasterOrbProps) {
    const sizeClasses = {
        sm: 'w-8 h-8',
        md: 'w-12 h-12',
        lg: 'w-16 h-16'
    };

    const glowSizeClasses = {
        sm: 'w-16 h-16',
        md: 'w-24 h-24',
        lg: 'w-32 h-32'
    };

    const iconSizeClasses = {
        sm: 'w-4 h-4',
        md: 'w-6 h-6',
        lg: 'w-8 h-8'
    };

    return (
        <div className="relative flex items-center justify-center">
            {/* Animated glow rings - only when thinking */}
            {isThinking && (
                <>
                    {/* Outer glow ring */}
                    <div
                        className={`absolute ${glowSizeClasses[size]} rounded-full animate-ping opacity-60`}
                        style={{
                            background: 'radial-gradient(circle, rgba(147, 51, 234, 0.3) 0%, rgba(147, 51, 234, 0.08) 70%, transparent 100%)',
                            animationDuration: '2.5s'
                        }}
                    />

                    {/* Middle glow ring */}
                    <div
                        className={`absolute ${sizeClasses[size]} rounded-full animate-ping opacity-70`}
                        style={{
                            background: 'radial-gradient(circle, rgba(168, 85, 247, 0.4) 0%, rgba(168, 85, 247, 0.15) 70%, transparent 100%)',
                            animationDuration: '2s',
                            animationDelay: '0.4s'
                        }}
                    />

                    {/* Inner glow ring */}
                    <div
                        className={`absolute w-10 h-10 rounded-full animate-ping opacity-85`}
                        style={{
                            background: 'radial-gradient(circle, rgba(196, 181, 253, 0.6) 0%, rgba(196, 181, 253, 0.2) 70%, transparent 100%)',
                            animationDuration: '1.5s',
                            animationDelay: '0.8s'
                        }}
                    />
                </>
            )}

            {/* Static glow background - always present */}
            <div
                className={`absolute ${sizeClasses[size]} rounded-full`}
                style={{
                    background: 'radial-gradient(circle, rgba(147, 51, 234, 0.3) 0%, rgba(147, 51, 234, 0.1) 70%, transparent 100%)',
                    filter: 'blur(1px)'
                }}
            />

            {/* Main orb with icon */}
            <div
                className={`relative ${sizeClasses[size]} rounded-full flex items-center justify-center transition-all duration-300`}
                style={{
                    background: isThinking
                        ? 'linear-gradient(135deg, rgba(147, 51, 234, 0.9) 0%, rgba(168, 85, 247, 0.8) 50%, rgba(196, 181, 253, 0.7) 100%)'
                        : 'linear-gradient(135deg, rgba(147, 51, 234, 0.7) 0%, rgba(168, 85, 247, 0.6) 50%, rgba(196, 181, 253, 0.5) 100%)',
                    boxShadow: isThinking
                        ? '0 0 20px rgba(147, 51, 234, 0.6), inset 0 1px 3px rgba(255, 255, 255, 0.3)'
                        : '0 0 10px rgba(147, 51, 234, 0.4), inset 0 1px 3px rgba(255, 255, 255, 0.2)',
                }}
            >
                <Bot
                    className={`${iconSizeClasses[size]} text-white drop-shadow-sm`}
                />
            </div>
        </div>
    );
}