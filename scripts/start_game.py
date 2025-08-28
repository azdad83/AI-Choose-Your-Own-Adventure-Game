#!/usr/bin/env python3
"""
Startup script for the Choose Your Own Adventure Game with Qdrant
"""

import subprocess
import time
import sys
import requests
import os

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(['docker', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_qdrant():
    """Check if Qdrant is running and accessible"""
    try:
        response = requests.get('http://localhost:6333/', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_qdrant():
    """Start Qdrant using Docker Compose"""
    print("Starting Qdrant with Docker Compose...")
    try:
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        print("Qdrant container started successfully!")
        
        # Wait for Qdrant to be ready
        print("Waiting for Qdrant to be ready...")
        for i in range(30):  # Wait up to 30 seconds
            if check_qdrant():
                print("Qdrant is ready!")
                return True
            time.sleep(1)
            print(f"Waiting... ({i+1}/30)")
        
        print("Qdrant took too long to start")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Qdrant: {e}")
        return False

def main():
    print("Choose Your Own Adventure Game - Startup Check")
    print("=" * 50)
    
    # Check Docker
    if not check_docker():
        print("❌ Docker is not running or not installed")
        print("Please install and start Docker Desktop")
        return False
    else:
        print("✅ Docker is running")
    
    # Check Qdrant
    if not check_qdrant():
        print("⚠️  Qdrant is not running")
        if not start_qdrant():
            return False
    else:
        print("✅ Qdrant is running")
    
    # Check Ollama
    if not check_ollama():
        print("❌ Ollama is not running")
        print("Please start Ollama service")
        return False
    else:
        print("✅ Ollama is running")
    
    print("\n" + "=" * 50)
    print("All systems ready! Starting the game...")
    print("=" * 50)
    
    # Start the game
    try:
        import sys
        import os
        # Add parent directory to path to import main
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from main import main as game_main
        game_main()
    except ImportError:
        print("Running game directly...")
        # Navigate to parent directory and run main.py
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run([sys.executable, 'main.py'], cwd=parent_dir)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nSetup incomplete. Please fix the issues above and try again.")
        sys.exit(1)
