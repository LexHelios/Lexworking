#!/usr/bin/env python3
"""
🔱 OMNIPOTENT AGENT SYSTEM Backend Test Suite 🔱
JAI MAHAKAAL! Comprehensive testing for OMNIPOTENT backend with unrestricted capabilities
Testing focus: Educational anatomy content and scientific research capabilities
"""

import asyncio
import aiohttp
import websockets
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OmnipotentBackendTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
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

    async def test_omnipotent_system_status(self):
        """Test the /api/v1/omnipotent/status endpoint"""
        test_name = "Omnipotent System Status"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/omnipotent/status", timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for omnipotent system status fields
                        status = data.get("status")
                        if status in ["success", "operational"]:
                            omnipotent_mode = data.get("omnipotent_mode", False)
                            unrestricted_models = data.get("unrestricted_models", False)
                            educational_mode = data.get("educational_mode", False)
                            anatomy_training = data.get("anatomy_training_mode", False)
                            
                            self.log_test_result(
                                test_name, True,
                                f"Omnipotent system {status}, unrestricted models: {unrestricted_models}, educational: {educational_mode}, anatomy training: {anatomy_training}",
                                {
                                    "status": status,
                                    "omnipotent_mode": omnipotent_mode,
                                    "unrestricted_models": unrestricted_models,
                                    "educational_mode": educational_mode,
                                    "anatomy_training_mode": anatomy_training
                                }
                            )
                        else:
                            self.log_test_result(test_name, False, f"System status not operational: {status}", data)
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_omnipotent_capabilities(self):
        """Test the /api/v1/omnipotent/capabilities endpoint"""
        test_name = "Omnipotent Capabilities"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/omnipotent/capabilities", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success":
                            capabilities = data.get("capabilities", {})
                            unrestricted = data.get("unrestricted", False)
                            educational_mode = data.get("educational_mode", False)
                            anatomy_training = data.get("anatomy_training", False)
                            
                            capability_count = len(capabilities) if isinstance(capabilities, dict) else 0
                            
                            self.log_test_result(
                                test_name, True,
                                f"Omnipotent capabilities available: {capability_count} capabilities, unrestricted: {unrestricted}, anatomy training: {anatomy_training}",
                                {
                                    "capability_count": capability_count,
                                    "unrestricted": unrestricted,
                                    "educational_mode": educational_mode,
                                    "anatomy_training": anatomy_training
                                }
                            )
                        else:
                            self.log_test_result(test_name, False, f"Capabilities status not success: {data.get('status')}", data)
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_unrestricted_text_generation(self):
        """Test unrestricted text generation with educational anatomy content"""
        test_name = "Unrestricted Text Generation"
        try:
            # Educational anatomy prompt
            test_prompt = "Generate detailed anatomical explanation of human reproductive system for medical education, including physiological processes and anatomical structures"
            
            form_data = aiohttp.FormData()
            form_data.add_field('prompt', test_prompt)
            form_data.add_field('request_type', 'educational_anatomy')
            form_data.add_field('context', '{"purpose": "medical_education", "audience": "medical_students"}')
            form_data.add_field('user_id', 'anatomy_student_001')
            
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
                            unrestricted = data.get("unrestricted", False)
                            
                            self.log_test_result(
                                test_name, True,
                                f"Generated {len(content)} chars of educational anatomy content using {model_used}, unrestricted: {unrestricted}",
                                {
                                    "content_length": len(content),
                                    "model_used": model_used,
                                    "unrestricted": unrestricted,
                                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                                }
                            )
                        else:
                            self.log_test_result(test_name, False, f"Generation failed: {data.get('error', 'Unknown error')}", data)
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_unrestricted_image_generation(self):
        """Test unrestricted image generation with medical illustration prompts"""
        test_name = "Unrestricted Image Generation"
        try:
            # Medical illustration prompt
            test_prompt = "Create detailed medical textbook illustration of human internal organs cross-section for anatomy education"
            
            form_data = aiohttp.FormData()
            form_data.add_field('prompt', test_prompt)
            form_data.add_field('style', 'medical_textbook')
            form_data.add_field('model', 'flux-dev-uncensored')
            form_data.add_field('safety_level', 'unrestricted')
            form_data.add_field('user_id', 'medical_student_001')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/omnipotent/image",
                    data=form_data,
                    timeout=60  # Image generation takes longer
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "success":
                            image_url = data.get("image_url", "")
                            model_used = data.get("model_used", "unknown")
                            safety_level = data.get("safety_level", "unknown")
                            
                            self.log_test_result(
                                test_name, True,
                                f"Generated medical illustration using {model_used}, safety level: {safety_level}, image URL available: {bool(image_url)}",
                                {
                                    "model_used": model_used,
                                    "safety_level": safety_level,
                                    "image_url_available": bool(image_url),
                                    "image_url": image_url[:100] + "..." if len(image_url) > 100 else image_url
                                }
                            )
                        else:
                            self.log_test_result(test_name, False, f"Image generation failed: {data.get('error', 'Unknown error')}", data)
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_computer_control(self):
        """Test computer control with safe system commands"""
        test_name = "Computer Control Test"
        try:
            # Safe system command
            test_command = "echo 'Omnipotent system test' && date && whoami"
            
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
                                f"Command executed successfully in {execution_time:.2f}s, exit code: {exit_code}, output length: {len(output)}",
                                {
                                    "exit_code": exit_code,
                                    "execution_time": execution_time,
                                    "output_length": len(output),
                                    "output_preview": output[:200] + "..." if len(output) > 200 else output
                                }
                            )
                        else:
                            self.log_test_result(test_name, False, f"Command execution failed: {data.get('error', 'Unknown error')}", data)
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_lex_omnipotent_integration(self):
        """Test the main /api/v1/lex endpoint using omnipotent system"""
        test_name = "LEX Omnipotent Integration"
        try:
            # Educational anatomy request through main LEX endpoint
            test_payload = {
                "message": "Explain the physiological processes involved in human reproduction for medical education purposes",
                "voice_mode": False,
                "user_id": "medical_student_backend",
                "context": {"purpose": "medical_education", "subject": "anatomy"},
                "priority": "high",
                "use_cache": False,
                "model_preference": "omnipotent_unrestricted"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/lex",
                    json=test_payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for omnipotent integration indicators
                        response_text = data.get("response", "")
                        omnipotent_mode = data.get("omnipotent_mode", False)
                        unrestricted = data.get("unrestricted", False)
                        educational_mode = data.get("educational_mode", False)
                        processing_time = data.get("processing_time", 0)
                        
                        if response_text and omnipotent_mode:
                            self.log_test_result(
                                test_name, True,
                                f"LEX using omnipotent system: {len(response_text)} chars in {processing_time:.2f}s, unrestricted: {unrestricted}, educational: {educational_mode}",
                                {
                                    "omnipotent_mode": omnipotent_mode,
                                    "unrestricted": unrestricted,
                                    "educational_mode": educational_mode,
                                    "processing_time": processing_time,
                                    "response_length": len(response_text)
                                }
                            )
                        else:
                            self.log_test_result(test_name, False, f"LEX not using omnipotent system or no response", data)
                    else:
                        error_text = await response.text()
                        self.log_test_result(test_name, False, f"HTTP {response.status}: {error_text}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_websocket_omnipotent_integration(self):
        """Test WebSocket integration with omnipotent system"""
        test_name = "WebSocket Omnipotent Integration"
        session_id = "omnipotent_ws_test_001"
        
        try:
            ws_url = f"{self.ws_url}/ws/{session_id}"
            
            # Try WebSocket connection with omnipotent request
            try:
                async with websockets.connect(ws_url, timeout=10) as websocket:
                    # Send educational anatomy request
                    test_message = {
                        "type": "message",
                        "message": "Generate educational content about human anatomy for medical students",
                        "user_id": "medical_student_ws",
                        "voice_mode": False,
                        "context": {"educational": True, "anatomy": True}
                    }
                    
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for processing notification
                    processing_msg = await asyncio.wait_for(websocket.recv(), timeout=10)
                    processing_data = json.loads(processing_msg)
                    
                    # Wait for response
                    response_msg = await asyncio.wait_for(websocket.recv(), timeout=30)
                    response_data = json.loads(response_msg)
                    
                    if response_data.get("type") == "response":
                        response_text = response_data.get("response", "")
                        capabilities_used = response_data.get("capabilities_used", [])
                        
                        # Check if omnipotent capabilities were used
                        omnipotent_used = any("omnipotent" in cap.lower() for cap in capabilities_used)
                        
                        self.log_test_result(
                            test_name, True,
                            f"WebSocket omnipotent response: {len(response_text)} chars, omnipotent capabilities: {omnipotent_used}",
                            {
                                "response_length": len(response_text),
                                "capabilities_used": capabilities_used,
                                "omnipotent_used": omnipotent_used
                            }
                        )
                    else:
                        self.log_test_result(test_name, False, f"Unexpected response type: {response_data.get('type')}", response_data)
                        
            except websockets.exceptions.ConnectionClosedError as e:
                self.log_test_result(test_name, False, f"WebSocket connection closed: {e.code} - {e.reason}")
            except asyncio.TimeoutError:
                self.log_test_result(test_name, False, "WebSocket response timeout")
            except Exception as e:
                if "403" in str(e) or "Forbidden" in str(e):
                    self.log_test_result(test_name, False, "WebSocket connection forbidden (security restrictions)")
                else:
                    self.log_test_result(test_name, False, f"WebSocket connection error: {str(e)}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"WebSocket test error: {str(e)}")

    async def test_api_keys_verification(self):
        """Test that API keys are loaded correctly"""
        test_name = "API Keys Verification"
        try:
            # Test through status endpoint to see if API keys are configured
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/omnipotent/status", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        system_status = data.get("system_status", {})
                        api_keys_status = system_status.get("api_keys", {})
                        
                        # Count configured API keys
                        configured_keys = 0
                        key_details = {}
                        
                        for key_name, key_status in api_keys_status.items():
                            if key_status and key_status != "not_configured":
                                configured_keys += 1
                                key_details[key_name] = "configured"
                            else:
                                key_details[key_name] = "missing"
                        
                        self.log_test_result(
                            test_name, configured_keys > 0,
                            f"API keys status: {configured_keys} configured keys found",
                            {
                                "configured_keys": configured_keys,
                                "key_details": key_details
                            }
                        )
                    else:
                        self.log_test_result(test_name, False, f"Could not verify API keys: HTTP {response.status}")
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"API keys verification error: {str(e)}")

    async def run_all_omnipotent_tests(self):
        """Run all omnipotent system tests"""
        print("🔱 JAI MAHAKAAL! Starting OMNIPOTENT AGENT SYSTEM Test Suite 🔱")
        print("=" * 70)
        print(f"Testing omnipotent server at: {self.base_url}")
        print(f"WebSocket URL: {self.ws_url}")
        print("Focus: Educational anatomy content and scientific research")
        print("=" * 70)
        
        # Run all omnipotent tests
        test_functions = [
            self.test_omnipotent_system_status,
            self.test_omnipotent_capabilities,
            self.test_unrestricted_text_generation,
            self.test_unrestricted_image_generation,
            self.test_computer_control,
            self.test_lex_omnipotent_integration,
            self.test_websocket_omnipotent_integration,
            self.test_api_keys_verification
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
            except Exception as e:
                logger.error(f"Test function {test_func.__name__} failed: {e}")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Print summary
        self.print_omnipotent_test_summary()
        
        return self.passed_tests == self.total_tests

    def print_omnipotent_test_summary(self):
        """Print comprehensive omnipotent test summary"""
        print("\n" + "=" * 70)
        print("🌟 OMNIPOTENT AGENT SYSTEM TEST RESULTS SUMMARY")
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
        
        if success_rate == 100:
            print("🔱 JAI MAHAKAAL! All omnipotent tests passed successfully! 🔱")
            print("✨ OMNIPOTENT AGENT SYSTEM is fully operational with unrestricted capabilities!")
        elif success_rate >= 80:
            print("⚡ Omnipotent system is mostly operational with minor issues")
        elif success_rate >= 60:
            print("⚠️ Omnipotent system has some functionality issues")
        else:
            print("❌ Omnipotent system has significant issues requiring attention")
        
        print("=" * 70)
        
        # Print detailed results for failed tests
        failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
        if failed_tests:
            print("\n🔍 FAILED TEST DETAILS:")
            print("-" * 50)
            for test_name in failed_tests:
                result = self.test_results[test_name]
                print(f"\n❌ {test_name}:")
                print(f"   Details: {result['details']}")
                if result.get('response_data'):
                    print(f"   Data: {json.dumps(result['response_data'], indent=2)[:300]}...")

async def main():
    """Main test execution function"""
    # Test the omnipotent server
    possible_urls = [
        "http://localhost:8001",  # Current omnipotent server
        "http://localhost:8000",  # Fallback
        "http://0.0.0.0:8001",   # Bind address
    ]
    
    tester = None
    server_found = False
    
    # Try to find running omnipotent server
    for url in possible_urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/api/v1/omnipotent/status", timeout=5) as response:
                    if response.status == 200:
                        print(f"✅ Found OMNIPOTENT server running at: {url}")
                        tester = OmnipotentBackendTester(url)
                        server_found = True
                        break
        except:
            # Try health endpoint as fallback
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/health", timeout=3) as response:
                        if response.status == 200:
                            print(f"✅ Found server running at: {url} (checking for omnipotent capabilities)")
                            tester = OmnipotentBackendTester(url)
                            server_found = True
                            break
            except:
                continue
    
    if not server_found:
        print("❌ No OMNIPOTENT server found running on any of the expected ports")
        print("Expected ports: 8001, 8000")
        print("Please start the OMNIPOTENT server first using:")
        print("  python lex_production_optimized.py")
        return False
    
    # Run omnipotent tests
    success = await tester.run_all_omnipotent_tests()
    
    if success:
        print("\n🎉 All OMNIPOTENT backend tests completed successfully!")
        print("🚀 OMNIPOTENT AGENT SYSTEM is ready for unrestricted scientific education!")
    else:
        print("\n💔 Some OMNIPOTENT backend tests failed.")
        print("🔧 Please check the server logs and omnipotent system configuration.")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Omnipotent test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Omnipotent test suite failed with error: {e}")
        sys.exit(1)