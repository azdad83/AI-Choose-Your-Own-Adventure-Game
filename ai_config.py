"""
Configuration module for AI Choose Your Own Adventure Game
Handles switching between Ollama and OpenAI providers
"""

import os
from typing import Union, Optional
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models import BaseLanguageModel
from langchain_core.embeddings import Embeddings

# Load environment variables from .env file
load_dotenv()

class AIConfig:
    """Configuration class for AI provider settings"""
    
    def __init__(self):
        self.ai_provider = os.getenv('AI_PROVIDER', 'ollama').lower()
        
        # OpenAI settings
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.openai_embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        
        # Ollama settings
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'gemma3:12b')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_embedding_model = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
        
        # Embedding provider - can be different from LLM provider
        self.embedding_provider = os.getenv('EMBEDDING_PROVIDER', 'ollama').lower()
        
        # Qdrant settings
        self.qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        self.qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
        
        # Environment
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        print(f"🔧 AI Provider: {self.ai_provider}")
        print(f"🔧 Embedding Provider: {self.embedding_provider}")
        if self.ai_provider == 'openai':
            print(f"🔧 OpenAI Model: {self.openai_model}")
        else:
            print(f"🔧 Ollama Model: {self.ollama_model}")
        
        if self.embedding_provider == 'openai':
            print(f"🔧 OpenAI Embedding Model: {self.openai_embedding_model}")
        else:
            print(f"🔧 Ollama Embedding Model: {self.ollama_embedding_model}")
    
    def get_llm(self) -> BaseLanguageModel:
        """Get the configured language model based on AI_PROVIDER setting"""
        
        if self.ai_provider == 'openai':
            return self._get_openai_llm()
        elif self.ai_provider == 'ollama':
            return self._get_ollama_llm()
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}. Use 'openai' or 'ollama'")
    
    def _get_openai_llm(self) -> ChatOpenAI:
        """Initialize OpenAI language model"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required when using OpenAI provider. Set OPENAI_API_KEY environment variable.")
        
        print(f"🤖 Initializing OpenAI with model: {self.openai_model}")
        
        return ChatOpenAI(
            api_key=self.openai_api_key,
            model=self.openai_model,
            base_url=self.openai_base_url,
            temperature=0.7,  # Good balance for creative storytelling
            max_tokens=1000,  # Reasonable response length
        )
    
    def _get_ollama_llm(self) -> OllamaLLM:
        """Initialize Ollama language model"""
        print(f"🤖 Initializing Ollama with model: {self.ollama_model}")
        
        return OllamaLLM(
            model=self.ollama_model,
            base_url=self.ollama_base_url,
            temperature=0.7,  # Good balance for creative storytelling
        )
    
    def get_embeddings(self) -> Embeddings:
        """Get the configured embedding model based on EMBEDDING_PROVIDER setting"""
        
        if self.embedding_provider == 'openai':
            return self._get_openai_embeddings()
        elif self.embedding_provider == 'ollama':
            return self._get_ollama_embeddings()
        else:
            raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}. Use 'openai' or 'ollama'")
    
    def _get_openai_embeddings(self) -> OpenAIEmbeddings:
        """Initialize OpenAI embedding model"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required when using OpenAI embeddings. Set OPENAI_API_KEY environment variable.")
        
        print(f"🔗 Initializing OpenAI embeddings with model: {self.openai_embedding_model}")
        
        return OpenAIEmbeddings(
            api_key=self.openai_api_key,
            model=self.openai_embedding_model,
            base_url=self.openai_base_url,
        )
    
    def _get_ollama_embeddings(self) -> OllamaEmbeddings:
        """Initialize Ollama embedding model"""
        print(f"🔗 Initializing Ollama embeddings with model: {self.ollama_embedding_model}")
        
        return OllamaEmbeddings(
            model=self.ollama_embedding_model,
            base_url=self.ollama_base_url,
        )
    
    def test_connection(self) -> bool:
        """Test connection to the configured AI provider"""
        try:
            llm = self.get_llm()
            
            # Test with a simple prompt
            test_prompt = "Hello, respond with just 'Connection successful!'"
            
            if self.ai_provider == 'openai':
                # For ChatOpenAI, we need to use the chat interface
                from langchain_core.messages import HumanMessage
                response = llm.invoke([HumanMessage(content=test_prompt)])
                result = response.content if hasattr(response, 'content') else str(response)
            else:
                # For OllamaLLM, use direct invoke
                result = llm.invoke(test_prompt)
            
            print(f"✓ {self.ai_provider.title()} connection successful")
            print(f"  Test response: {result[:100]}...")
            return True
            
        except Exception as e:
            print(f"✗ {self.ai_provider.title()} connection failed: {e}")
            return False
    
    def get_provider_info(self) -> dict:
        """Get information about the current AI provider configuration"""
        return {
            'provider': self.ai_provider,
            'model': self.openai_model if self.ai_provider == 'openai' else self.ollama_model,
            'base_url': self.openai_base_url if self.ai_provider == 'openai' else self.ollama_base_url,
            'embedding_provider': self.embedding_provider,
            'embedding_model': self.openai_embedding_model if self.embedding_provider == 'openai' else self.ollama_embedding_model,
            'environment': self.environment
        }

# Global configuration instance
config = AIConfig()

def get_llm() -> BaseLanguageModel:
    """Convenience function to get the configured language model"""
    return config.get_llm()

def get_embeddings() -> Embeddings:
    """Convenience function to get the configured embedding model"""
    return config.get_embeddings()

def test_ai_connection() -> bool:
    """Convenience function to test AI provider connection"""
    return config.test_connection()

def get_provider_info() -> dict:
    """Convenience function to get provider information"""
    return config.get_provider_info()

def print_config_info():
    """Print current configuration information"""
    info = get_provider_info()
    print("\n" + "=" * 50)
    print("🔧 AI CONFIGURATION")
    print("=" * 50)
    print(f"LLM Provider: {info['provider'].title()}")
    print(f"LLM Model: {info['model']}")
    print(f"LLM Base URL: {info['base_url']}")
    print(f"Embedding Provider: {info['embedding_provider'].title()}")
    print(f"Embedding Model: {info['embedding_model']}")
    print(f"Environment: {info['environment']}")
    print("=" * 50)