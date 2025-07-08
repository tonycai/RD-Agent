#!/usr/bin/env python3
"""
RD-Agent Gateway Python Client Examples

This script demonstrates how to interact with the RD-Agent OpenAI-compatible gateway
using the OpenAI Python client library.

Requirements:
    pip install openai requests

Usage:
    python python_examples.py [function_name]
    
Examples:
    python python_examples.py health_check
    python python_examples.py list_models
    python python_examples.py data_science_example
"""

import sys
import json
import requests
from typing import Optional, Dict, Any

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI library not available. Install with: pip install openai")

# Configuration
GATEWAY_URL = "http://localhost:8001"
API_KEY = None  # Set this if authentication is enabled

class RDAgentClient:
    """Simple client for RD-Agent Gateway"""
    
    def __init__(self, base_url: str = GATEWAY_URL, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def health_check(self) -> Dict[str, Any]:
        """Check gateway health"""
        response = requests.get(f"{self.base_url}/health", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_models(self) -> Dict[str, Any]:
        """List available models"""
        response = requests.get(f"{self.base_url}/v1/models", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def chat_completion(self, 
                       model: str, 
                       messages: list, 
                       rd_agent_config: Optional[Dict] = None,
                       **kwargs) -> Dict[str, Any]:
        """Create a chat completion"""
        data = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        if rd_agent_config:
            data["rd_agent"] = rd_agent_config
        
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*50}")
    print(f"🔹 {title}")
    print('='*50)

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def health_check():
    """Test gateway health"""
    print_header("Gateway Health Check")
    
    try:
        client = RDAgentClient()
        health = client.health_check()
        
        print_success("Gateway is healthy!")
        print(f"Status: {health['status']}")
        print(f"Default Scenario: {health['details']['default_scenario']}")
        print(f"Auth Enabled: {health['details']['auth_enabled']}")
        
    except Exception as e:
        print_error(f"Health check failed: {e}")

def list_models():
    """List available models"""
    print_header("Available Models")
    
    try:
        client = RDAgentClient()
        models = client.list_models()
        
        print_success(f"Found {len(models['data'])} models:")
        for model in models['data']:
            print(f"  • {model['id']} ({model['root']})")
            
    except Exception as e:
        print_error(f"Failed to list models: {e}")

def data_science_example():
    """Data science scenario example"""
    print_header("Data Science Example")
    
    try:
        client = RDAgentClient()
        
        response = client.chat_completion(
            model="rd-agent-data-science",
            messages=[
                {"role": "user", "content": "Explain the key steps in a machine learning competition workflow."}
            ],
            rd_agent_config={
                "competition": "sf-crime",
                "steps": 1
            },
            max_tokens=500,
            temperature=0.7
        )
        
        if 'choices' in response and response['choices']:
            content = response['choices'][0]['message']['content']
            print_success("Data science response received:")
            print(f"\n{content[:300]}{'...' if len(content) > 300 else ''}")
        else:
            print_error(f"Unexpected response format: {response}")
            
    except Exception as e:
        print_error(f"Data science example failed: {e}")

def quantitative_finance_example():
    """Quantitative finance scenario example"""
    print_header("Quantitative Finance Example")
    
    try:
        client = RDAgentClient()
        
        response = client.chat_completion(
            model="rd-agent-quantitative-finance",
            messages=[
                {"role": "user", "content": "Describe the process of developing a momentum factor for stock selection."}
            ],
            rd_agent_config={
                "mode": "factor",
                "steps": 1
            },
            max_tokens=500,
            temperature=0.5
        )
        
        if 'choices' in response and response['choices']:
            content = response['choices'][0]['message']['content']
            print_success("Quantitative finance response received:")
            print(f"\n{content[:300]}{'...' if len(content) > 300 else ''}")
        else:
            print_error(f"Unexpected response format: {response}")
            
    except Exception as e:
        print_error(f"Quantitative finance example failed: {e}")

def openai_client_example():
    """Example using OpenAI Python client"""
    print_header("OpenAI Client Example")
    
    if not OPENAI_AVAILABLE:
        print_error("OpenAI library not available. Install with: pip install openai")
        return
    
    try:
        # Initialize OpenAI client
        client = OpenAI(
            api_key=API_KEY or "dummy-key",  # API key might not be required
            base_url=f"{GATEWAY_URL}/v1"
        )
        
        # Test with data science model
        response = client.chat.completions.create(
            model="rd-agent-data-science",
            messages=[
                {"role": "user", "content": "What are the main challenges in machine learning competitions?"}
            ],
            max_tokens=300,
            extra_body={
                "rd_agent": {
                    "steps": 1
                }
            }
        )
        
        print_success("OpenAI client response received:")
        print(f"\n{response.choices[0].message.content}")
        
    except Exception as e:
        print_error(f"OpenAI client example failed: {e}")

def streaming_example():
    """Example of streaming response"""
    print_header("Streaming Example")
    
    if not OPENAI_AVAILABLE:
        print_error("OpenAI library not available. Install with: pip install openai")
        return
    
    try:
        client = OpenAI(
            api_key=API_KEY or "dummy-key",
            base_url=f"{GATEWAY_URL}/v1"
        )
        
        print_success("Starting streaming response...")
        print("Response: ", end="", flush=True)
        
        stream = client.chat.completions.create(
            model="rd-agent-data-science",
            messages=[
                {"role": "user", "content": "Briefly explain feature engineering."}
            ],
            max_tokens=200,
            stream=True,
            extra_body={
                "rd_agent": {
                    "steps": 1
                }
            }
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        
        print("\n")
        print_success("Streaming completed!")
        
    except Exception as e:
        print_error(f"Streaming example failed: {e}")

def run_all_examples():
    """Run all examples"""
    print_header("Running All Examples")
    
    examples = [
        health_check,
        list_models,
        data_science_example,
        openai_client_example,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print_error(f"Example {example.__name__} failed: {e}")
        print()  # Add spacing between examples

def show_usage():
    """Show usage information"""
    print_header("RD-Agent Gateway Python Examples")
    
    print("Available functions:")
    print("  health_check              - Test gateway health")
    print("  list_models               - List available models")
    print("  data_science_example      - Test data science scenario")
    print("  quantitative_finance_example - Test quant finance scenario")
    print("  openai_client_example     - Use OpenAI Python client")
    print("  streaming_example         - Test streaming responses")
    print("  run_all_examples          - Run all examples")
    print("  show_usage                - Show this help")
    print("\nUsage:")
    print(f"  python {sys.argv[0]} [function_name]")
    print(f"  python {sys.argv[0]} health_check")
    print(f"  python {sys.argv[0]} run_all_examples")
    
    print("\nConfiguration:")
    print(f"  Gateway URL: {GATEWAY_URL}")
    print(f"  API Key: {'Set' if API_KEY else 'Not set'}")
    print(f"  OpenAI Library: {'Available' if OPENAI_AVAILABLE else 'Not available'}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    function_name = sys.argv[1]
    
    # Map of available functions
    functions = {
        'health_check': health_check,
        'list_models': list_models,
        'data_science_example': data_science_example,
        'quantitative_finance_example': quantitative_finance_example,
        'openai_client_example': openai_client_example,
        'streaming_example': streaming_example,
        'run_all_examples': run_all_examples,
        'show_usage': show_usage,
        'help': show_usage,
    }
    
    if function_name in functions:
        functions[function_name]()
    else:
        print_error(f"Unknown function: {function_name}")
        show_usage()

if __name__ == "__main__":
    main()