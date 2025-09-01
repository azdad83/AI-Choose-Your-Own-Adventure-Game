#!/usr/bin/env python3
"""
Setup script for AI Choose Your Own Adventure Game
Helps configure the AI provider and environment variables
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    env_example_path = Path(".env.example")
    env_path = Path(".env")
    
    if not env_example_path.exists():
        print("❌ .env.example file not found!")
        return False
    
    if env_path.exists():
        response = input("📄 .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("📄 Keeping existing .env file")
            return True
    
    try:
        shutil.copy(env_example_path, env_path)
        print("✅ Created .env file from template")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def configure_ai_provider():
    """Help user configure AI provider"""
    print("\n🤖 AI Provider Configuration")
    print("=" * 40)
    print("1. Ollama (Local AI - Free, requires Ollama installation)")
    print("2. OpenAI (Cloud AI - Requires API key)")
    print()
    
    while True:
        choice = input("Choose AI provider (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found. Run create_env_file() first.")
        return False
    
    # Read current .env content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update AI_PROVIDER setting
    provider = "ollama" if choice == "1" else "openai"
    
    updated_lines = []
    for line in lines:
        if line.startswith('AI_PROVIDER='):
            updated_lines.append(f'AI_PROVIDER={provider}\n')
        else:
            updated_lines.append(line)
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"✅ Set AI provider to: {provider}")
    
    if provider == "openai":
        print("\n⚠️  OpenAI Configuration Required:")
        print("   1. Get your API key from: https://platform.openai.com/api-keys")
        print("   2. Edit .env file and set OPENAI_API_KEY=your_actual_api_key")
        print("   3. Optionally change OPENAI_MODEL if desired")
    else:
        print("\n🦙 Ollama Configuration:")
        print("   1. Install Ollama from: https://ollama.com")
        print("   2. Run: ollama pull gemma3:12b")
        print("   3. Ensure Ollama is running before starting the game")
    
    return True

def install_dependencies():
    """Guide user to install dependencies"""
    print("\n📦 Installing Dependencies")
    print("=" * 30)
    print("Run the following command to install required packages:")
    print()
    print("    pip install -r requirements.txt")
    print()
    print("Or if you prefer using conda:")
    print("    conda install --file requirements.txt")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking Dependencies")
    print("=" * 25)
    
    required_packages = [
        'langchain',
        'langchain_core',
        'langchain_ollama',
        'langchain_openai',
        'qdrant_client',
        'sentence_transformers',
        'python_dotenv',
        'openai',
        'requests',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('_', '-'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n🎉 All dependencies are installed!")
        return True

def setup_qdrant():
    """Guide user to set up Qdrant"""
    print("\n🗄️  Qdrant Database Setup")
    print("=" * 25)
    print("Qdrant is required for storing game sessions and chat history.")
    print()
    print("To start Qdrant:")
    print("    docker-compose up -d")
    print()
    print("To check if Qdrant is running:")
    print("    curl http://localhost:6333/health")
    print()
    print("If you don't have Docker, install it from: https://docker.com")

def main():
    """Main setup function"""
    print("🎮 AI Choose Your Own Adventure - Setup")
    print("=" * 45)
    
    steps = [
        ("Create .env file", create_env_file),
        ("Configure AI provider", configure_ai_provider),
        ("Check dependencies", check_dependencies),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return 1
    
    install_dependencies()
    setup_qdrant()
    
    print("\n" + "=" * 45)
    print("🎉 Setup Complete!")
    print("=" * 45)
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start Qdrant: docker-compose up -d")
    print("3. Test configuration: python test_ai_config.py")
    print("4. Start game: python main.py")
    print("5. Or start API server: python api_server.py")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())