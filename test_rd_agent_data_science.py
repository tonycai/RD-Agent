#!/usr/bin/env python3
"""
Comprehensive test script for rd-agent-data-science model
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_gateway_health():
    """Test gateway health endpoint"""
    print("🔍 Testing Gateway Health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gateway Health: {data['status']}")
            print(f"   Default Scenario: {data['details']['default_scenario']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_models_endpoint():
    """Test models listing endpoint"""
    print("\n🔍 Testing Models Endpoint...")
    try:
        response = requests.get("http://localhost:8000/v1/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model['id'] for model in data['data']]
            print(f"✅ Available Models: {', '.join(models)}")
            
            # Check if rd-agent-data-science is available
            if 'rd-agent-data-science' in models:
                print("✅ rd-agent-data-science model found")
                return True
            else:
                print("❌ rd-agent-data-science model not found")
                return False
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False

def test_chat_completion_simple():
    """Test simple chat completion without competition specifics"""
    print("\n🔍 Testing Simple Chat Completion...")
    
    # Simple test that should work without datasets
    payload = {
        "model": "rd-agent-data-science",
        "messages": [
            {"role": "user", "content": "What is machine learning?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"✅ Response received: {content[:100]}...")
                return True
            else:
                print(f"❌ Unexpected response format: {data}")
                return False
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
        return False

def test_openai_client():
    """Test with OpenAI Python client"""
    print("\n🔍 Testing OpenAI Python Client...")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key="test-key",  # Not needed since auth is disabled
            base_url="http://localhost:8000/v1"
        )
        
        response = client.chat.completions.create(
            model="rd-agent-data-science",
            messages=[
                {"role": "user", "content": "What are the main steps in a data science project?"}
            ],
            max_tokens=100
        )
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"✅ OpenAI Client Response: {content[:100]}...")
            return True
        else:
            print("❌ No response from OpenAI client")
            return False
            
    except ImportError:
        print("⚠️  OpenAI client not available (pip install openai)")
        return None
    except Exception as e:
        print(f"❌ OpenAI client error: {e}")
        return False

def test_data_science_capabilities():
    """Test data science specific capabilities"""
    print("\n🔍 Testing Data Science Capabilities...")
    
    capabilities_query = """
    List the main capabilities of the RD-Agent data science model:
    1. What types of machine learning problems can it solve?
    2. What are its key features for automated ML?
    """
    
    payload = {
        "model": "rd-agent-data-science",
        "messages": [{"role": "user", "content": capabilities_query}],
        "max_tokens": 200
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data:
                content = data['choices'][0]['message']['content']
                print(f"✅ Capabilities Response: {content[:150]}...")
                return True
        
        print(f"❌ Capabilities test failed: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Capabilities test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing rd-agent-data-science Model")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Gateway Health", test_gateway_health),
        ("Models Endpoint", test_models_endpoint),
        ("Simple Chat Completion", test_chat_completion_simple),
        ("OpenAI Client", test_openai_client),
        ("Data Science Capabilities", test_data_science_capabilities),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        result = test_func()
        results[test_name] = result
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    for test_name, result in results.items():
        if result is True:
            print(f"✅ {test_name}: PASSED")
            passed += 1
            total += 1
        elif result is False:
            print(f"❌ {test_name}: FAILED")
            total += 1
        else:  # None means skipped
            print(f"⚠️  {test_name}: SKIPPED")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! rd-agent-data-science model is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())