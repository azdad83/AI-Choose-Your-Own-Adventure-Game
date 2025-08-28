#!/usr/bin/env python3
"""
Setup script for the Choose Your Own Adventure Game (Local Ollama + Qdrant Version)
This script will help you set up the local environment for running the game.
"""

import os
import subprocess
import sys

def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_ollama():
    """Check if Ollama is installed"""
    try:
        # Try to check if Ollama service is running
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_ollama_llama3():
    """Check if Llama3 model is available in Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            return any('llama3' in model.get('name', '') for model in models.get('models', []))
        return False
    except:
        return False

def main():
    print("Choose Your Own Adventure Game Setup (Local Version)")
    print("=" * 55)
    print("This version uses:")
    print("- 🤖 Ollama with Llama3 (Local LLM)")
    print("- 🗄️  Qdrant (Local Vector Database)")
    print("- 🏠 No external APIs or costs!")
    print("=" * 55)
    
    # Check Docker
    if not check_docker():
        print("❌ Docker is not installed or not running")
        print("📦 Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/")
        return False
    else:
        print("✅ Docker is available")
    
    # Check Ollama
    if not check_ollama():
        print("❌ Ollama is not installed")
        print("🦙 Please install Ollama from: https://ollama.ai/")
        return False
    else:
        print("✅ Ollama is available")
    
    # Check Llama3 model
    if not check_ollama_llama3():
        print("⚠️  Llama3 model not found in Ollama")
        print("📥 Run: ollama pull llama3:latest")
        return False
    else:
        print("✅ Llama3 model is available")
    
    print("\n" + "=" * 55)
    print("🎉 Setup complete! You can now run the game:")
    print("   python scripts/start_game.py")
    print("   or")
    print("   python main.py")
    print("=" * 55)
    
    return True

if __name__ == "__main__":
    main()
