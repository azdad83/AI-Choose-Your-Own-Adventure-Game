#!/usr/bin/env python3
"""
Test script for AI provider switching functionality
Tests both Ollama and OpenAI configurations
"""

import os
import sys
from ai_config import AIConfig, get_llm, test_ai_connection, get_provider_info, print_config_info

def test_provider_switching():
    """Test switching between AI providers"""
    
    print("🧪 Testing AI Provider Switching")
    print("=" * 50)
    
    # Test current configuration
    print("\n1. Testing current configuration:")
    print_config_info()
    
    # Test connection
    print("\n2. Testing connection:")
    if test_ai_connection():
        print("✓ Connection test passed!")
    else:
        print("✗ Connection test failed!")
        return False
    
    return True

def test_ollama_config():
    """Test Ollama configuration specifically"""
    print("\n🦙 Testing Ollama Configuration")
    print("-" * 30)
    
    # Temporarily set environment for Ollama
    original_provider = os.environ.get('AI_PROVIDER')
    os.environ['AI_PROVIDER'] = 'ollama'
    
    try:
        config = AIConfig()
        info = config.get_provider_info()
        print(f"Provider: {info['provider']}")
        print(f"Model: {info['model']}")
        print(f"Base URL: {info['base_url']}")
        
        # Test connection
        if config.test_connection():
            print("✓ Ollama test passed!")
            return True
        else:
            print("✗ Ollama test failed!")
            return False
    except Exception as e:
        print(f"✗ Ollama configuration error: {e}")
        return False
    finally:
        # Restore original provider
        if original_provider:
            os.environ['AI_PROVIDER'] = original_provider
        elif 'AI_PROVIDER' in os.environ:
            del os.environ['AI_PROVIDER']

def test_openai_config():
    """Test OpenAI configuration specifically"""
    print("\n🤖 Testing OpenAI Configuration")
    print("-" * 30)
    
    # Check if OpenAI API key is available
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set - skipping OpenAI test")
        print("   To test OpenAI, set OPENAI_API_KEY environment variable")
        return True
    
    # Temporarily set environment for OpenAI
    original_provider = os.environ.get('AI_PROVIDER')
    os.environ['AI_PROVIDER'] = 'openai'
    
    try:
        config = AIConfig()
        info = config.get_provider_info()
        print(f"Provider: {info['provider']}")
        print(f"Model: {info['model']}")
        print(f"Base URL: {info['base_url']}")
        print(f"API Key: {api_key[:8]}..." + "*" * 20)
        
        # Test connection
        if config.test_connection():
            print("✓ OpenAI test passed!")
            return True
        else:
            print("✗ OpenAI test failed!")
            return False
    except Exception as e:
        print(f"✗ OpenAI configuration error: {e}")
        return False
    finally:
        # Restore original provider
        if original_provider:
            os.environ['AI_PROVIDER'] = original_provider
        elif 'AI_PROVIDER' in os.environ:
            del os.environ['AI_PROVIDER']

def test_invalid_provider():
    """Test handling of invalid provider configuration"""
    print("\n❌ Testing Invalid Provider Handling")
    print("-" * 35)
    
    original_provider = os.environ.get('AI_PROVIDER')
    os.environ['AI_PROVIDER'] = 'invalid_provider'
    
    try:
        config = AIConfig()
        config.get_llm()
        print("✗ Should have failed with invalid provider!")
        return False
    except ValueError as e:
        print(f"✓ Correctly caught invalid provider: {e}")
        return True
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        # Restore original provider
        if original_provider:
            os.environ['AI_PROVIDER'] = original_provider
        elif 'AI_PROVIDER' in os.environ:
            del os.environ['AI_PROVIDER']

def main():
    """Run all tests"""
    print("🚀 AI Choose Your Own Adventure - Configuration Test")
    print("=" * 60)
    
    tests = [
        ("Current Configuration", test_provider_switching),
        ("Ollama Configuration", test_ollama_config),
        ("OpenAI Configuration", test_openai_config),
        ("Invalid Provider Handling", test_invalid_provider),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())