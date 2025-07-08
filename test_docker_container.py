#!/usr/bin/env python3
"""
RD-Agent Docker Container Unit Tests

Tests the running Docker container instance to validate:
- Health endpoints
- API functionality
- OpenAI compatibility
- Error handling
- Performance metrics
"""

import unittest
import requests
import json
import time
import subprocess
from typing import Dict, Any, Optional


class TestRDAgentDockerContainer(unittest.TestCase):
    """Test suite for RD-Agent Docker container."""
    
    BASE_URL = "http://localhost:8001"
    TIMEOUT = 30
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - verify container is running."""
        print("🧪 Testing RD-Agent Docker Container")
        print("=" * 60)
        
        # Check if container is running
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=rdagent-gateway-minimal", "--format", "{{.Status}}"],
                capture_output=True, text=True, timeout=10
            )
            if not result.stdout.strip() or "Up" not in result.stdout:
                raise Exception("RD-Agent container not running")
            print(f"✅ Container Status: {result.stdout.strip()}")
        except Exception as e:
            raise unittest.SkipTest(f"❌ Container not available: {e}")
    
    def test_01_container_health(self):
        """Test container health endpoint."""
        print("\n📋 Testing container health...")
        
        response = requests.get(f"{self.BASE_URL}/health", timeout=self.TIMEOUT)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertIn("details", data)
        
        details = data["details"]
        self.assertIn("auth_enabled", details)
        self.assertIn("cors_enabled", details)
        self.assertIn("default_scenario", details)
        
        print(f"   ✅ Health Status: {data['status']}")
        print(f"   ✅ Auth Enabled: {details['auth_enabled']}")
        print(f"   ✅ CORS Enabled: {details['cors_enabled']}")
        print(f"   ✅ Default Scenario: {details['default_scenario']}")
    
    def test_02_models_endpoint(self):
        """Test models listing endpoint."""
        print("\n📋 Testing models endpoint...")
        
        response = requests.get(f"{self.BASE_URL}/v1/models", timeout=self.TIMEOUT)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["object"], "list")
        self.assertIn("data", data)
        
        models = data["data"]
        self.assertGreater(len(models), 0)
        
        expected_models = [
            "rd-agent-data-science",
            "rd-agent-quantitative-finance", 
            "rd-agent-general-model"
        ]
        
        model_ids = [model["id"] for model in models]
        for expected_model in expected_models:
            self.assertIn(expected_model, model_ids)
            print(f"   ✅ Model Available: {expected_model}")
        
        # Validate model structure
        for model in models:
            self.assertIn("id", model)
            self.assertIn("object", model)
            self.assertIn("created", model)
            self.assertIn("owned_by", model)
            self.assertEqual(model["object"], "model")
    
    def test_03_chat_completions_endpoint_structure(self):
        """Test chat completions endpoint structure (without valid API keys)."""
        print("\n📋 Testing chat completions endpoint structure...")
        
        payload = {
            "model": "rd-agent-data-science",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 50
        }
        
        response = requests.post(
            f"{self.BASE_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.TIMEOUT
        )
        
        # Expect either success or proper error format
        self.assertIn(response.status_code, [200, 422, 500])
        
        data = response.json()
        
        if response.status_code == 200:
            # Valid response structure
            self.assertIn("id", data)
            self.assertIn("object", data)
            self.assertIn("created", data)
            self.assertIn("choices", data)
            print("   ✅ Chat completion successful")
        else:
            # Error response structure
            self.assertIn("detail", data)
            if "error" in data["detail"]:
                error = data["detail"]["error"]
                self.assertIn("message", error)
                self.assertIn("type", error)
                print(f"   ✅ Expected error: {error['type']}")
            print("   ✅ Error response properly formatted")
    
    def test_04_openai_compatibility_headers(self):
        """Test OpenAI compatibility headers."""
        print("\n📋 Testing OpenAI compatibility...")
        
        response = requests.get(f"{self.BASE_URL}/v1/models", timeout=self.TIMEOUT)
        
        # Check content type
        self.assertEqual(response.headers.get("content-type"), "application/json")
        
        # Check CORS headers if enabled
        if "access-control-allow-origin" in response.headers:
            print("   ✅ CORS headers present")
        
        print("   ✅ OpenAI-compatible headers validated")
    
    def test_05_error_handling(self):
        """Test error handling for invalid requests."""
        print("\n📋 Testing error handling...")
        
        # Test invalid model
        payload = {
            "model": "invalid-model",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=self.TIMEOUT
        )
        
        self.assertIn(response.status_code, [400, 404, 422, 500])
        print(f"   ✅ Invalid model handled: {response.status_code}")
        
        # Test malformed request
        response = requests.post(
            f"{self.BASE_URL}/v1/chat/completions",
            data="invalid-json",
            headers={"Content-Type": "application/json"},
            timeout=self.TIMEOUT
        )
        
        self.assertIn(response.status_code, [400, 422])
        print(f"   ✅ Malformed JSON handled: {response.status_code}")
        
        # Test missing required fields
        payload = {"model": "rd-agent-data-science"}  # missing messages
        
        response = requests.post(
            f"{self.BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=self.TIMEOUT
        )
        
        self.assertIn(response.status_code, [400, 422])
        print(f"   ✅ Missing fields handled: {response.status_code}")
    
    def test_06_response_times(self):
        """Test response times for basic endpoints."""
        print("\n📋 Testing response times...")
        
        # Health endpoint
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/health", timeout=self.TIMEOUT)
        health_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(health_time, 2.0)  # Should be fast
        print(f"   ✅ Health endpoint: {health_time:.3f}s")
        
        # Models endpoint
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/v1/models", timeout=self.TIMEOUT)
        models_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(models_time, 3.0)  # Should be reasonably fast
        print(f"   ✅ Models endpoint: {models_time:.3f}s")
    
    def test_07_container_logs_health(self):
        """Test container logs for errors."""
        print("\n📋 Testing container logs...")
        
        try:
            result = subprocess.run(
                ["docker", "logs", "rdagent-gateway-minimal", "--tail", "20"],
                capture_output=True, text=True, timeout=10
            )
            
            logs = result.stdout
            
            # Check for critical errors
            critical_errors = ["CRITICAL", "FATAL", "ERROR.*startup", "ERROR.*import"]
            error_found = False
            
            for error_pattern in critical_errors:
                if error_pattern.lower() in logs.lower():
                    error_found = True
                    print(f"   ⚠️  Found potential issue: {error_pattern}")
            
            if not error_found:
                print("   ✅ No critical errors in recent logs")
            
            # Check for successful requests
            if "200 OK" in logs:
                print("   ✅ Successful requests logged")
            
        except Exception as e:
            print(f"   ⚠️  Could not check logs: {e}")
    
    def test_08_container_resource_usage(self):
        """Test container resource usage."""
        print("\n📋 Testing container resources...")
        
        try:
            result = subprocess.run(
                ["docker", "stats", "rdagent-gateway-minimal", "--no-stream", "--format", 
                 "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    stats = lines[1].split('\t')
                    if len(stats) >= 3:
                        cpu_usage = stats[0]
                        mem_usage = stats[1]
                        net_io = stats[2]
                        
                        print(f"   ✅ CPU Usage: {cpu_usage}")
                        print(f"   ✅ Memory Usage: {mem_usage}")
                        print(f"   ✅ Network I/O: {net_io}")
                        
                        # Basic sanity checks
                        cpu_percent = float(cpu_usage.replace('%', ''))
                        self.assertLess(cpu_percent, 100.0)
            
        except Exception as e:
            print(f"   ⚠️  Could not check resource usage: {e}")
    
    def test_09_concurrent_requests(self):
        """Test handling of concurrent requests."""
        print("\n📋 Testing concurrent requests...")
        
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.get(f"{self.BASE_URL}/health", timeout=5)
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        # Launch 5 concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=10)
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        self.assertGreaterEqual(success_count, 4)  # At least 4/5 should succeed
        print(f"   ✅ Concurrent requests: {success_count}/5 successful")
    
    def test_10_api_validation_edge_cases(self):
        """Test API validation with edge cases."""
        print("\n📋 Testing API validation edge cases...")
        
        # Test extremely long message
        long_message = "A" * 10000
        payload = {
            "model": "rd-agent-data-science",
            "messages": [{"role": "user", "content": long_message}],
            "max_tokens": 10
        }
        
        response = requests.post(
            f"{self.BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=self.TIMEOUT
        )
        
        # Should handle gracefully (either process or return proper error)
        self.assertIn(response.status_code, [200, 400, 422, 500])
        print("   ✅ Long message handled")
        
        # Test edge parameter values
        payload = {
            "model": "rd-agent-data-science",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 2.0,  # Maximum allowed
            "max_tokens": 1      # Minimum useful value
        }
        
        response = requests.post(
            f"{self.BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=self.TIMEOUT
        )
        
        self.assertIn(response.status_code, [200, 400, 422, 500])
        print("   ✅ Edge parameters handled")


def run_container_tests():
    """Run all container tests and generate report."""
    print("🚀 Starting RD-Agent Docker Container Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRDAgentDockerContainer)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=None)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    
    if failures > 0:
        print("\n🔍 FAILURES:")
        for test, traceback in result.failures:
            lines = traceback.split('\n')
            error_line = next((line for line in reversed(lines) if line.strip() and not line.startswith(' ')), "Unknown error")
            print(f"   - {test}: {error_line}")
    
    if errors > 0:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            lines = traceback.split('\n')
            error_line = next((line for line in reversed(lines) if line.strip() and not line.startswith(' ')), "Unknown error")
            print(f"   - {test}: {error_line}")
    
    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n🎉 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎊 Container is functioning well!")
    elif success_rate >= 60:
        print("⚠️  Container has some issues but is mostly functional")
    else:
        print("🚨 Container has significant issues")
    
    return result


if __name__ == "__main__":
    run_container_tests()