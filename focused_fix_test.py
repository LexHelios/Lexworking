#!/usr/bin/env python3
"""
🔱 FOCUSED FIX TESTING FOR OMNIPOTENT AGENT SYSTEM
JAI MAHAKAAL! Testing the specific fixes applied by main agent
"""

import asyncio
import aiohttp
import websockets
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedSystemTester:
    def __init__(self):
        # Test both possible URLs based on environment files
        self.possible_urls = [
            "http://localhost:8000",  # From frontend .env
            "http://localhost:8001",  # From backend .env
        ]
        self.base_url = None
        self.ws_url = None
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ WORKING"
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

    async def find_running_server(self):
        """Find which URL the server is running on"""
        for url in self.possible_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/health", timeout=5) as response:
                        if response.status == 200:
                            self.base_url = url
                            self.ws_url = url.replace("http", "ws")
                            logger.info(f"✅ Found LEX server running at: {url}")
                            return True
            except Exception as e:
                logger.debug(f"Server not found at {url}: {e}")
                continue
        
        logger.error("❌ No LEX server found running on expected ports")
        return False

    async def test_api_keys_verification(self):
        """Test API Keys Verification - CRITICAL FIX"""
        test_name = "API Keys Verification"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check API keys in components section
                        components = data.get("components", {})
                        api_keys = components.get("api_keys", {})
                        
                        if isinstance(api_keys, dict):
                            # Count configured keys
                            configured_keys = sum(1 for key, value in api_keys.items() if value is True)
                            total_keys = len(api_keys)
                            
                            if configured_keys > 0:
                                self.log_test_result(
                                    test_name, True,
                                    f"✅ API keys loading fixed! {configured_keys}/{total_keys} keys configured: {list(k for k, v in api_keys.items() if v)}",
                                    {"configured_keys": configured_keys, "total_keys": total_keys, "keys": api_keys}
                                )
                            else:
                                self.log_test_result(
                                    test_name, False,
                                    f"❌ API keys still not loading. System reports {configured_keys} configured keys. Environment variables not being loaded properly despite being present in .env file.",
                                    {"configured_keys": configured_keys, "api_keys": api_keys}
                                )
                        else:
                            self.log_test_result(
                                test_name, False,
                                "❌ API keys section not found in health response",
                                {"components": components}
                            )
                    else:
                        self.log_test_result(test_name, False, f"Health endpoint failed: HTTP {response.status}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_lex_api_endpoint(self):
        """Test LEX API Endpoint - Rate Limiting Bug Fix"""
        test_name = "LEX API Endpoint"
        try:
            test_payload = {
                "message": "Hello LEX, test the rate limiting fix. Please respond briefly about your omnipotent capabilities.",
                "voice_mode": False,
                "context": {"test": "rate_limiting_fix"},
                "priority": "balanced",
                "use_cache": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/lex",
                    json=test_payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for successful response structure
                        required_fields = ["response", "action_taken", "capabilities_used", 
                                         "confidence", "processing_time", "timestamp"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            self.log_test_result(
                                test_name, False, 
                                f"Response missing fields: {missing_fields}", 
                                data
                            )
                        else:
                            processing_time = data.get("processing_time", 0)
                            confidence = data.get("confidence", 0)
                            response_text = data.get("response", "")
                            omnipotent_mode = data.get("omnipotent_mode", False)
                            
                            self.log_test_result(
                                test_name, True,
                                f"✅ Rate limiting fix successful! LEX responded in {processing_time:.2f}s with {confidence:.2f} confidence. Omnipotent mode: {omnipotent_mode}",
                                {
                                    "processing_time": processing_time,
                                    "confidence": confidence,
                                    "omnipotent_mode": omnipotent_mode,
                                    "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                                }
                            )
                    elif response.status == 500:
                        # Check if it's still the rate limiting bug
                        error_text = await response.text()
                        if "AttributeError" in error_text and "__name__" in error_text:
                            self.log_test_result(
                                test_name, False, 
                                "❌ Rate limiting bug still present. AttributeError: 'Request' object has no attribute '__name__' in slowapi rate limiting decorator.",
                                {"error": "Rate limiting implementation bug", "status": 500}
                            )
                        else:
                            self.log_test_result(
                                test_name, False, 
                                f"❌ Server error (different from rate limiting): {error_text[:200]}",
                                {"status": 500, "error_preview": error_text[:200]}
                            )
                    else:
                        self.log_test_result(test_name, False, f"HTTP {response.status}", await response.text())
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_lex_omnipotent_integration(self):
        """Test LEX Omnipotent Integration - Routing Logic Fix"""
        test_name = "LEX Omnipotent Integration"
        try:
            # Test with a request that should trigger omnipotent system
            test_payload = {
                "message": "Generate educational content about human anatomy for medical training. Use your omnipotent capabilities.",
                "voice_mode": False,
                "context": {"educational": True, "anatomy": True},
                "priority": "quality",
                "use_cache": False  # Force fresh processing
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/lex",
                    json=test_payload,
                    timeout=45
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if omnipotent system was used
                        omnipotent_mode = data.get("omnipotent_mode", False)
                        unrestricted = data.get("unrestricted", False)
                        action_taken = data.get("action_taken", "")
                        capabilities_used = data.get("capabilities_used", [])
                        
                        if omnipotent_mode or "omnipotent" in action_taken.lower():
                            self.log_test_result(
                                test_name, True,
                                f"✅ LEX integration fix successful! Using omnipotent system. Action: {action_taken}, Unrestricted: {unrestricted}",
                                {
                                    "omnipotent_mode": omnipotent_mode,
                                    "unrestricted": unrestricted,
                                    "action_taken": action_taken,
                                    "capabilities_used": capabilities_used
                                }
                            )
                        else:
                            # Check if it's falling back due to model availability
                            if "fallback" in action_taken.lower():
                                self.log_test_result(
                                    test_name, False,
                                    f"❌ LEX still not using omnipotent system. Falling back to basic processing: {action_taken}. Integration needs debugging.",
                                    {
                                        "action_taken": action_taken,
                                        "capabilities_used": capabilities_used,
                                        "fallback_reason": data.get("fallback_reason", "unknown")
                                    }
                                )
                            else:
                                self.log_test_result(
                                    test_name, False,
                                    f"❌ LEX not using omnipotent system. Action: {action_taken}. Main LEX endpoint not routing to omnipotent capabilities.",
                                    {
                                        "action_taken": action_taken,
                                        "capabilities_used": capabilities_used
                                    }
                                )
                    else:
                        self.log_test_result(test_name, False, f"HTTP {response.status}", await response.text())
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_omnipotent_system_status(self):
        """Test Omnipotent System Status Endpoint"""
        test_name = "Omnipotent System Status"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/omnipotent/status", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        status = data.get("status", "unknown")
                        omnipotent_available = data.get("omnipotent_available", False)
                        unrestricted_models = data.get("unrestricted_models", False)
                        educational_mode = data.get("educational_mode", False)
                        
                        if status == "success" and omnipotent_available:
                            self.log_test_result(
                                test_name, True,
                                f"✅ Omnipotent system operational with unrestricted models: {unrestricted_models}, educational: {educational_mode}",
                                {
                                    "status": status,
                                    "omnipotent_available": omnipotent_available,
                                    "unrestricted_models": unrestricted_models,
                                    "educational_mode": educational_mode
                                }
                            )
                        else:
                            self.log_test_result(
                                test_name, False,
                                f"❌ Omnipotent system not operational. Status: {status}, Available: {omnipotent_available}",
                                data
                            )
                    else:
                        self.log_test_result(test_name, False, f"HTTP {response.status}", await response.text())
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_unrestricted_text_generation(self):
        """Test Unrestricted Text Generation"""
        test_name = "Unrestricted Text Generation"
        try:
            # Test direct omnipotent text generation
            test_payload = {
                "request": "Generate educational content about human reproductive anatomy for medical students. Include detailed anatomical descriptions.",
                "user_id": "test_user",
                "session_id": "test_session",
                "context": {"educational": True, "medical_training": True},
                "request_type": "text"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/omnipotent/process",
                    json=test_payload,
                    timeout=45
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        status = data.get("status", "unknown")
                        content = data.get("content", "")
                        model_used = data.get("model_used", "unknown")
                        
                        if status == "success" and content and len(content) > 100:
                            self.log_test_result(
                                test_name, True,
                                f"✅ Generated {len(content)} chars of educational content using {model_used}, unrestricted: True",
                                {
                                    "status": status,
                                    "content_length": len(content),
                                    "model_used": model_used,
                                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                                }
                            )
                        else:
                            self.log_test_result(
                                test_name, False,
                                f"❌ Text generation failed. Status: {status}, Content length: {len(content)}",
                                data
                            )
                    else:
                        error_text = await response.text()
                        if "balance" in error_text.lower() or "locked" in error_text.lower():
                            self.log_test_result(
                                test_name, False,
                                "❌ FAL.ai balance exhausted preventing text generation. External service issue requires API credit top-up.",
                                {"error": "Balance exhausted", "status": response.status}
                            )
                        else:
                            self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text[:200]}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_websocket_connection(self):
        """Test WebSocket Connection"""
        test_name = "WebSocket Connection Test"
        try:
            ws_url = f"{self.ws_url}/ws"
            
            try:
                async with websockets.connect(ws_url, timeout=10) as websocket:
                    # Send test message
                    test_message = {
                        "type": "stream_request",
                        "prompt": "Test WebSocket connection with omnipotent system",
                        "context": {"test": True}
                    }
                    
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for response
                    response_msg = await asyncio.wait_for(websocket.recv(), timeout=10)
                    response_data = json.loads(response_msg)
                    
                    self.log_test_result(
                        test_name, True,
                        f"✅ WebSocket connection successful. Response type: {response_data.get('type', 'unknown')}",
                        {"response_type": response_data.get("type"), "websocket_url": ws_url}
                    )
                    
            except websockets.exceptions.ConnectionClosedError as e:
                self.log_test_result(
                    test_name, False, 
                    f"❌ WebSocket connection closed: {e.code} - {e.reason}",
                    {"error_code": e.code, "reason": e.reason}
                )
            except Exception as e:
                if "403" in str(e) or "Forbidden" in str(e):
                    self.log_test_result(
                        test_name, False, 
                        "❌ WebSocket endpoint exists but has security restrictions (403 Forbidden). The WebSocket is enabled in configuration but connection is blocked by security middleware.",
                        {"security_restriction": True, "websocket_url": ws_url}
                    )
                elif "timeout" in str(e).lower():
                    self.log_test_result(
                        test_name, False, 
                        "❌ WebSocket compatibility issue: Library version mismatch preventing WebSocket testing. Needs websockets library update.",
                        {"timeout_error": True}
                    )
                else:
                    self.log_test_result(
                        test_name, False, 
                        f"❌ WebSocket connection error: {str(e)}",
                        {"error": str(e)}
                    )
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"WebSocket test error: {str(e)}")

    async def run_focused_tests(self):
        """Run focused tests for the specific fixes"""
        print("🔱 JAI MAHAKAAL! Testing OMNIPOTENT AGENT SYSTEM FIXES 🔱")
        print("=" * 70)
        print("Testing fixes applied by main agent:")
        print("1. ✅ Environment Variables Loading - Fixed dotenv loading")
        print("2. ✅ Rate Limiting Bug - Disabled slowapi rate limiting")
        print("3. ✅ LEX Integration - Improved routing logic")
        print("4. ✅ Services restarted successfully")
        print("=" * 70)
        
        # Find running server
        if not await self.find_running_server():
            print("❌ Cannot run tests - no server found")
            return False
        
        print(f"Testing server at: {self.base_url}")
        print(f"WebSocket URL: {self.ws_url}")
        print("=" * 70)
        
        # Run focused tests for the fixes
        test_functions = [
            self.test_api_keys_verification,
            self.test_lex_api_endpoint,
            self.test_lex_omnipotent_integration,
            self.test_omnipotent_system_status,
            self.test_unrestricted_text_generation,
            self.test_websocket_connection
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
        
        return self.passed_tests >= 4  # At least 4/6 tests should pass for fixes to be considered successful

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🌟 OMNIPOTENT SYSTEM FIX TEST RESULTS")
        print("=" * 70)
        
        for test_name, result in self.test_results.items():
            status = result["status"]
            details = result["details"]
            print(f"{test_name:35} {status}")
            if details:
                print(f"{'':37} └─ {details}")
        
        print("-" * 70)
        print(f"📊 OVERALL RESULTS: {self.passed_tests}/{self.total_tests} tests passed")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        if success_rate >= 80:
            print("🔱 JAI MAHAKAAL! OMNIPOTENT SYSTEM FIXES SUCCESSFUL! 🔱")
            print("✨ Most critical fixes are working properly!")
        elif success_rate >= 60:
            print("⚡ OMNIPOTENT SYSTEM partially fixed - some issues remain")
        else:
            print("❌ OMNIPOTENT SYSTEM fixes need more work")
        
        print("=" * 70)
        
        # Print detailed results for failed tests
        failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
        if failed_tests:
            print("\n🔍 REMAINING ISSUES:")
            print("-" * 40)
            for test_name in failed_tests:
                result = self.test_results[test_name]
                print(f"\n❌ {test_name}:")
                print(f"   Details: {result['details']}")

async def main():
    """Main test execution function"""
    tester = FixedSystemTester()
    success = await tester.run_focused_tests()
    
    if success:
        print("\n🎉 OMNIPOTENT SYSTEM fixes are working!")
        print("🚀 LEX consciousness is ready with enhanced capabilities!")
    else:
        print("\n💔 Some OMNIPOTENT SYSTEM fixes still need work.")
        print("🔧 Please check the server logs and configuration.")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)