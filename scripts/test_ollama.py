#!/usr/bin/env python3
"""
Test script to verify Ollama is working with Llama3
"""

import sys
import subprocess

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama service is running")
            return True
        else:
            print("❌ Ollama service is not responding correctly")
            return False
    except Exception as e:
        print(f"❌ Ollama service is not running: {e}")
        print("💡 Start Ollama with: ollama serve")
        return False

def check_ollama_models():
    """Check available Ollama models"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Available Ollama models:")
            print(result.stdout)
            if 'llama3' in result.stdout:
                print("✓ Llama3 model is available")
                return True
            else:
                print("❌ Llama3 model not found")
                print("💡 Install it with: ollama pull llama3:latest")
                return False
        else:
            print(f"❌ Error checking models: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running ollama command: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection with langchain"""
    try:
        from langchain_ollama import OllamaLLM
        
        llm = OllamaLLM(
            model="llama3:latest",
            base_url="http://localhost:11434",
            temperature=0.7
        )
        
        print("🧪 Testing Ollama with a simple prompt...")
        response = llm.invoke("Say hello and confirm you are Llama3!")
        print(f"✓ Ollama response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Ollama connection: {e}")
        return False

def main():
    print("Ollama + Llama3 Test Script")
    print("=" * 40)
    
    # Check if Ollama service is running
    if not check_ollama_service():
        return False
    
    # Check available models
    if not check_ollama_models():
        return False
    
    # Test connection with langchain
    if not test_ollama_connection():
        return False
    
    print("\n🎉 All tests passed! Ollama with Llama3 is ready to use!")
    print("You can now run: python main_ollama.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
