"""
Example client usage for RD-Agent OpenAI-compatible Gateway.

This module demonstrates various ways to interact with the RD-Agent Gateway
using different clients and libraries.
"""

import os
import asyncio
import json
from typing import Dict, Any
import requests
from openai import OpenAI


class RDAgentClient:
    """Example client for RD-Agent Gateway."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("RD_AGENT_API_KEY")
        self.headers = {}
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(
            api_key=self.api_key or "dummy-key",
            base_url=f"{self.base_url}/v1"
        )
    
    def list_models(self) -> Dict[str, Any]:
        """List available models."""
        response = requests.get(
            f"{self.base_url}/v1/models",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check gateway health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def chat_completion(
        self,
        model: str,
        messages: list,
        rd_agent_config: Dict[str, Any] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a chat completion using requests."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        if rd_agent_config:
            payload["rd_agent"] = rd_agent_config
        
        if stream:
            return self._stream_completion(payload)
        else:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    def _stream_completion(self, payload: Dict[str, Any]):
        """Handle streaming completion."""
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data == '[DONE]':
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue
    
    def openai_chat_completion(
        self,
        model: str,
        messages: list,
        rd_agent_config: Dict[str, Any] = None,
        stream: bool = False,
        **kwargs
    ):
        """Create a chat completion using OpenAI client."""
        extra_body = {}
        if rd_agent_config:
            extra_body["rd_agent"] = rd_agent_config
        
        return self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            extra_body=extra_body,
            **kwargs
        )


def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    client = RDAgentClient()
    
    # Health check
    print("Health check:", client.health_check())
    
    # List models
    models = client.list_models()
    print("Available models:", [model["id"] for model in models["data"]])
    
    # Simple chat completion
    response = client.chat_completion(
        model="rd-agent-data-science",
        messages=[
            {"role": "user", "content": "Start a data science project for sf-crime"}
        ],
        rd_agent_config={
            "competition": "sf-crime",
            "steps": 2
        }
    )
    
    print("Response:", response["choices"][0]["message"]["content"][:200] + "...")


def example_streaming():
    """Streaming response example."""
    print("\n=== Streaming Example ===")
    
    client = RDAgentClient()
    
    messages = [
        {"role": "user", "content": "Start a data science project with detailed steps"}
    ]
    
    rd_agent_config = {
        "competition": "sf-crime",
        "steps": 3,
        "log_level": "INFO"
    }
    
    print("Streaming response:")
    for chunk in client.chat_completion(
        model="rd-agent-data-science",
        messages=messages,
        rd_agent_config=rd_agent_config,
        stream=True
    ):
        if "choices" in chunk and chunk["choices"]:
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content:
                print(content, end="", flush=True)
    
    print("\n[Stream completed]")


def example_openai_client():
    """OpenAI client example."""
    print("\n=== OpenAI Client Example ===")
    
    client = RDAgentClient()
    
    response = client.openai_chat_completion(
        model="rd-agent-quantitative-finance",
        messages=[
            {"role": "user", "content": "Start quantitative finance factor discovery"}
        ],
        rd_agent_config={
            "steps": 2
        }
    )
    
    print("OpenAI client response:", response.choices[0].message.content[:200] + "...")


def example_different_scenarios():
    """Examples for different RD-Agent scenarios."""
    print("\n=== Different Scenarios Examples ===")
    
    client = RDAgentClient()
    
    scenarios = [
        {
            "name": "Data Science",
            "model": "rd-agent-data-science",
            "messages": [{"role": "user", "content": "Analyze the titanic dataset"}],
            "config": {"competition": "spaceship-titanic", "steps": 1}
        },
        {
            "name": "Quantitative Finance",
            "model": "rd-agent-quantitative-finance", 
            "messages": [{"role": "user", "content": "Develop trading factors"}],
            "config": {"steps": 1}
        },
        {
            "name": "General Model",
            "model": "rd-agent-general-model",
            "messages": [{"role": "user", "content": "Implement a transformer model"}],
            "config": {"steps": 1}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']} Scenario:")
        try:
            response = client.chat_completion(
                model=scenario["model"],
                messages=scenario["messages"],
                rd_agent_config=scenario["config"]
            )
            content = response["choices"][0]["message"]["content"]
            print(f"Response: {content[:150]}...")
        except Exception as e:
            print(f"Error: {e}")


def example_error_handling():
    """Error handling examples."""
    print("\n=== Error Handling Examples ===")
    
    client = RDAgentClient()
    
    # Invalid model
    try:
        client.chat_completion(
            model="invalid-model",
            messages=[{"role": "user", "content": "test"}]
        )
    except requests.exceptions.HTTPError as e:
        print(f"Invalid model error: {e.response.status_code} - {e.response.json()}")
    
    # Invalid parameters
    try:
        client.chat_completion(
            model="rd-agent-data-science",
            messages=[{"role": "user", "content": "test"}],
            rd_agent_config={"steps": 1000}  # Exceeds max_steps
        )
    except requests.exceptions.HTTPError as e:
        print(f"Invalid parameters error: {e.response.status_code} - {e.response.json()}")


async def example_async_usage():
    """Async usage example with aiohttp."""
    print("\n=== Async Usage Example ===")
    
    try:
        import aiohttp
    except ImportError:
        print("aiohttp not installed, skipping async example")
        return
    
    async with aiohttp.ClientSession() as session:
        # Health check
        async with session.get("http://localhost:8000/health") as response:
            health = await response.json()
            print("Async health check:", health)
        
        # Chat completion
        payload = {
            "model": "rd-agent-data-science",
            "messages": [{"role": "user", "content": "Quick test"}],
            "rd_agent": {"steps": 1}
        }
        
        headers = {"Content-Type": "application/json"}
        api_key = os.getenv("RD_AGENT_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        async with session.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            headers=headers
        ) as response:
            result = await response.json()
            print("Async response:", result["choices"][0]["message"]["content"][:100] + "...")


def main():
    """Run all examples."""
    print("RD-Agent Gateway Client Examples")
    print("=" * 40)
    
    try:
        example_basic_usage()
        example_streaming()
        example_openai_client()
        example_different_scenarios()
        example_error_handling()
        
        # Run async example
        asyncio.run(example_async_usage())
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to RD-Agent Gateway.")
        print("Make sure the gateway is running at http://localhost:8000")
        print("Start it with: uvicorn rdagent.app.gateway.main_new:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()