#!/usr/bin/env python3
"""
🔱 FOCUSED OMNIPOTENT SYSTEM Test Suite 🔱
Testing specific endpoints as requested in the review
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusedOmnipotentTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
            
        self.test_results[test_name] = {
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"{test_name}: {status} - {details}")

    async def test_health_check(self):
        """Test basic health check endpoint"""
        test_name = "Health Check Endpoint"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get("status", "unknown")
                        components = data.get("components", {})
                        
                        self.log_test_result(
                            test_name, True,
                            f"Backend running, status: {status}, components: {len(components)}",
                            {"status": status, "component_count": len(components)}
                        )
                    else:
                        self.log_test_result(test_name, False, f"HTTP {response.status}", await response.text())
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_omnipotent_status(self):
        """Test omnipotent system status endpoint"""
        test_name = "Omnipotent System Status"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/omnipotent/status", timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get("status", "unknown")
                        omnipotent_mode = data.get("omnipotent_mode", False)
                        unrestricted_models = data.get("unrestricted_models", False)
                        
                        self.log_test_result(
                            test_name, True,
                            f"Status: {status}, omnipotent: {omnipotent_mode}, unrestricted: {unrestricted_models}",
                            data
                        )
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_omnipotent_capabilities(self):
        """Test omnipotent capabilities endpoint"""
        test_name = "Omnipotent Capabilities"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/omnipotent/capabilities", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        capabilities = data.get("capabilities", {})
                        capability_count = len(capabilities) if isinstance(capabilities, dict) else 0
                        unrestricted = data.get("unrestricted", False)
                        
                        self.log_test_result(
                            test_name, True,
                            f"Found {capability_count} capabilities, unrestricted: {unrestricted}",
                            {"capability_count": capability_count, "unrestricted": unrestricted}
                        )
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_simple_text_generation(self):
        """Test unrestricted text generation with simple educational request"""
        test_name = "Simple Text Generation"
        try:
            # Simple educational prompt to avoid balance issues
            test_prompt = "Explain the basic structure of a cell for biology students"
            
            form_data = aiohttp.FormData()
            form_data.add_field('prompt', test_prompt)
            form_data.add_field('request_type', 'educational')
            form_data.add_field('user_id', 'test_student')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/omnipotent/generate",
                    data=form_data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success":
                            content = data.get("content", data.get("response", ""))
                            model_used = data.get("model_used", "unknown")
                            
                            self.log_test_result(
                                test_name, True,
                                f"Generated {len(content)} chars using {model_used}",
                                {"content_length": len(content), "model_used": model_used}
                            )
                        else:
                            error_msg = data.get("error", "Unknown error")
                            if "balance" in error_msg.lower() or "exhausted" in error_msg.lower():
                                self.log_test_result(test_name, False, f"FAL.ai balance issue: {error_msg}", data)
                            else:
                                self.log_test_result(test_name, False, f"Generation failed: {error_msg}", data)
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_computer_control(self):
        """Test computer control with safe command"""
        test_name = "Computer Control"
        try:
            # Safe system command as requested
            test_command = "ls -la"
            
            form_data = aiohttp.FormData()
            form_data.add_field('command', test_command)
            form_data.add_field('working_directory', '/app')
            form_data.add_field('timeout', '10')
            form_data.add_field('user_id', 'system_tester')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/omnipotent/computer",
                    data=form_data,
                    timeout=15
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success":
                            output = data.get("output", "")
                            exit_code = data.get("exit_code", -1)
                            execution_time = data.get("execution_time", 0)
                            
                            self.log_test_result(
                                test_name, True,
                                f"Command executed in {execution_time:.2f}s, exit code: {exit_code}, output: {len(output)} chars",
                                {"exit_code": exit_code, "execution_time": execution_time, "output_length": len(output)}
                            )
                        else:
                            self.log_test_result(test_name, False, f"Command failed: {data.get('error', 'Unknown error')}", data)
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_api_keys_status(self):
        """Test API keys verification through status endpoint"""
        test_name = "API Keys Status"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/omnipotent/status", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Look for API key information in the response
                        system_status = data.get("system_status", {})
                        api_keys_info = system_status.get("api_keys", {})
                        
                        if api_keys_info:
                            configured_keys = sum(1 for v in api_keys_info.values() if v and v != "not_configured")
                            total_keys = len(api_keys_info)
                            
                            self.log_test_result(
                                test_name, configured_keys > 0,
                                f"API keys: {configured_keys}/{total_keys} configured",
                                {"configured_keys": configured_keys, "total_keys": total_keys}
                            )
                        else:
                            # Check if environment variables are loaded
                            env_check = {
                                "OPENROUTER_API_KEY": bool(data.get("openrouter_available")),
                                "FAL_KEY": bool(data.get("fal_available")),
                                "TOGETHER_API_KEY": bool(data.get("together_available"))
                            }
                            configured_count = sum(env_check.values())
                            
                            self.log_test_result(
                                test_name, configured_count > 0,
                                f"Environment API keys detected: {configured_count}/3",
                                env_check
                            )
                    else:
                        self.log_test_result(test_name, False, f"Could not check API keys: HTTP {response.status}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"API keys check error: {str(e)}")

    async def run_focused_tests(self):
        """Run the focused test suite"""
        print("🔱 JAI MAHAKAAL! Starting Focused OMNIPOTENT Test Suite 🔱")
        print("=" * 60)
        print(f"Testing server at: {self.base_url}")
        print("Focus: Basic health, omnipotent status, capabilities, simple text gen, computer control")
        print("=" * 60)
        
        # Run focused tests
        test_functions = [
            self.test_health_check,
            self.test_omnipotent_status,
            self.test_omnipotent_capabilities,
            self.test_simple_text_generation,
            self.test_computer_control,
            self.test_api_keys_status
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
            except Exception as e:
                logger.error(f"Test function {test_func.__name__} failed: {e}")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Print summary
        self.print_test_summary()
        
        return self.passed_tests, self.total_tests

    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🌟 FOCUSED OMNIPOTENT TEST RESULTS")
        print("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = result["status"]
            details = result["details"]
            print(f"{test_name:30} {status}")
            if details:
                print(f"{'':32} └─ {details}")
        
        print("-" * 60)
        print(f"📊 RESULTS: {self.passed_tests}/{self.total_tests} tests passed")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        if success_rate == 100:
            print("🔱 JAI MAHAKAAL! All focused tests passed! 🔱")
        elif success_rate >= 80:
            print("⚡ Most functionality working with minor issues")
        else:
            print("❌ Significant issues found requiring attention")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    # Test the omnipotent server on port 8001
    tester = FocusedOmnipotentTester("http://localhost:8001")
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/health", timeout=5) as response:
                if response.status == 200:
                    print("✅ Found server running on port 8001")
                else:
                    print("❌ Server not responding properly on port 8001")
                    return False
    except Exception as e:
        print(f"❌ Cannot connect to server on port 8001: {e}")
        return False
    
    # Run focused tests
    passed, total = await tester.run_focused_tests()
    
    print(f"\n🎯 Focused test completed: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)