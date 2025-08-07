#!/usr/bin/env python3
"""
🔱 LEX Backend Server Test Suite 🔱
JAI MAHAKAAL! Comprehensive testing for LEX backend with WebSocket integration
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

class LEXBackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
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

    async def test_health_endpoint(self):
        """Test the /health endpoint"""
        test_name = "Health Check Endpoint"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        required_fields = ["status", "timestamp", "version", "components"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            self.log_test_result(test_name, False, f"Missing fields: {missing_fields}", data)
                        else:
                            components_status = data.get("components", {})
                            healthy_components = sum(1 for status in components_status.values() 
                                                   if status in ["healthy", "not_configured"])
                            total_components = len(components_status)
                            
                            self.log_test_result(
                                test_name, True, 
                                f"Server healthy, {healthy_components}/{total_components} components operational",
                                data
                            )
                    else:
                        self.log_test_result(test_name, False, f"HTTP {response.status}", await response.text())
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_websocket_status_endpoint(self):
        """Test the WebSocket status endpoint"""
        test_name = "WebSocket Status Endpoint"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/status", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for WebSocket-related information
                        if "active_connections" in data:
                            active_connections = data["active_connections"]
                            self.log_test_result(
                                test_name, True,
                                f"WebSocket status available, {active_connections} active connections",
                                data
                            )
                        else:
                            self.log_test_result(test_name, False, "No WebSocket status information", data)
                    else:
                        self.log_test_result(test_name, False, f"HTTP {response.status}", await response.text())
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Connection error: {str(e)}")

    async def test_performance_metrics_endpoint(self):
        """Test the /api/v1/performance or /metrics endpoint"""
        test_name = "Performance Metrics Endpoint"
        
        # Try both possible endpoints
        endpoints_to_try = ["/api/v1/performance", "/metrics"]
        
        for endpoint in endpoints_to_try:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            if endpoint == "/metrics":
                                # Prometheus metrics format
                                text_data = await response.text()
                                if "lex_" in text_data or "http_requests" in text_data:
                                    self.log_test_result(
                                        test_name, True,
                                        f"Prometheus metrics available at {endpoint}",
                                        {"endpoint": endpoint, "metrics_count": len(text_data.split('\n'))}
                                    )
                                    return
                            else:
                                # JSON performance data
                                data = await response.json()
                                self.log_test_result(
                                    test_name, True,
                                    f"Performance data available at {endpoint}",
                                    data
                                )
                                return
                                
            except Exception as e:
                continue
                
        self.log_test_result(test_name, False, "No performance metrics endpoint found")

    async def test_lex_api_endpoint(self):
        """Test the main /api/v1/lex endpoint"""
        test_name = "LEX API Endpoint"
        try:
            # Prepare test request
            test_payload = {
                "message": "Hello LEX, this is a test message. Please respond briefly.",
                "voice_mode": False,
                "user_id": "test_user_backend",
                "session_id": "test_session_001",
                "context": {"test": True},
                "user_preferences": {"response_length": "brief"}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/lex",
                    json=test_payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        required_fields = ["response", "action_taken", "capabilities_used", 
                                         "confidence", "processing_time", "timestamp", "session_id"]
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
                            
                            self.log_test_result(
                                test_name, True,
                                f"LEX responded in {processing_time:.2f}s with {confidence:.2f} confidence, response length: {len(response_text)}",
                                {
                                    "processing_time": processing_time,
                                    "confidence": confidence,
                                    "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                                }
                            )
                    elif response.status == 401:
                        # Try without authentication
                        self.log_test_result(test_name, False, "Authentication required", await response.text())
                    else:
                        self.log_test_result(test_name, False, f"HTTP {response.status}", await response.text())
                        
        except Exception as e:
            self.log_test_result(test_name, False, f"Request error: {str(e)}")

    async def test_websocket_connection(self):
        """Test WebSocket connection and streaming"""
        test_name = "WebSocket Connection Test"
        session_id = "test_ws_session_001"
        
        try:
            # Test WebSocket connection
            ws_url = f"{self.ws_url}/ws/{session_id}"
            
            async with websockets.connect(ws_url) as websocket:
                # Wait for welcome message
                try:
                    welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    welcome_data = json.loads(welcome_msg)
                    
                    if welcome_data.get("type") == "connection_established":
                        # Send test message
                        test_message = {
                            "type": "message",
                            "message": "Hello LEX via WebSocket! Please respond briefly.",
                            "user_id": "test_ws_user",
                            "voice_mode": False
                        }
                        
                        await websocket.send(json.dumps(test_message))
                        
                        # Wait for processing notification
                        processing_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                        processing_data = json.loads(processing_msg)
                        
                        # Wait for response
                        response_msg = await asyncio.wait_for(websocket.recv(), timeout=15)
                        response_data = json.loads(response_msg)
                        
                        if response_data.get("type") == "response":
                            response_text = response_data.get("response", "")
                            self.log_test_result(
                                test_name, True,
                                f"WebSocket streaming successful, received response: {len(response_text)} chars",
                                {
                                    "welcome_type": welcome_data.get("type"),
                                    "processing_type": processing_data.get("type"),
                                    "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text
                                }
                            )
                        else:
                            self.log_test_result(test_name, False, "Invalid response format", response_data)
                    else:
                        self.log_test_result(test_name, False, "No welcome message received", welcome_data)
                        
                except asyncio.TimeoutError:
                    self.log_test_result(test_name, False, "WebSocket communication timeout")
                    
        except Exception as e:
            self.log_test_result(test_name, False, f"WebSocket connection error: {str(e)}")

    async def test_additional_endpoints(self):
        """Test additional endpoints that might be available"""
        test_name = "Additional Endpoints Test"
        
        additional_endpoints = [
            "/",  # Root endpoint
            "/api/v1/websocket/status",  # Specific WebSocket status
            "/docs",  # API documentation
        ]
        
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for endpoint in additional_endpoints:
                try:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=5) as response:
                        results[endpoint] = {
                            "status": response.status,
                            "available": response.status < 400
                        }
                except Exception as e:
                    results[endpoint] = {
                        "status": "error",
                        "available": False,
                        "error": str(e)
                    }
        
        available_endpoints = [ep for ep, data in results.items() if data["available"]]
        
        self.log_test_result(
            test_name, True,
            f"Found {len(available_endpoints)} additional endpoints: {', '.join(available_endpoints)}",
            results
        )

    async def run_all_tests(self):
        """Run all backend tests"""
        print("🔱 JAI MAHAKAAL! Starting LEX Backend Test Suite 🔱")
        print("=" * 60)
        print(f"Testing server at: {self.base_url}")
        print(f"WebSocket URL: {self.ws_url}")
        print("=" * 60)
        
        # Run all tests
        test_functions = [
            self.test_health_endpoint,
            self.test_websocket_status_endpoint,
            self.test_performance_metrics_endpoint,
            self.test_lex_api_endpoint,
            self.test_websocket_connection,
            self.test_additional_endpoints
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
            except Exception as e:
                logger.error(f"Test function {test_func.__name__} failed: {e}")
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        # Print summary
        self.print_test_summary()
        
        return self.passed_tests == self.total_tests

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🌟 LEX BACKEND TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = result["status"]
            details = result["details"]
            print(f"{test_name:30} {status}")
            if details:
                print(f"{'':32} └─ {details}")
        
        print("-" * 60)
        print(f"📊 OVERALL RESULTS: {self.passed_tests}/{self.total_tests} tests passed")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        if success_rate == 100:
            print("🔱 JAI MAHAKAAL! All backend tests passed successfully! 🔱")
            print("✨ LEX backend server is fully operational with WebSocket support!")
        elif success_rate >= 80:
            print("⚡ LEX backend server is mostly operational with minor issues")
        elif success_rate >= 60:
            print("⚠️ LEX backend server has some functionality issues")
        else:
            print("❌ LEX backend server has significant issues requiring attention")
        
        print("=" * 60)
        
        # Print detailed results for failed tests
        failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
        if failed_tests:
            print("\n🔍 FAILED TEST DETAILS:")
            print("-" * 40)
            for test_name in failed_tests:
                result = self.test_results[test_name]
                print(f"\n❌ {test_name}:")
                print(f"   Details: {result['details']}")
                if result.get('response_data'):
                    print(f"   Data: {json.dumps(result['response_data'], indent=2)[:200]}...")

async def main():
    """Main test execution function"""
    # Test different possible server URLs
    possible_urls = [
        "http://localhost:8000",  # Default from production_server.py
        "http://localhost:8080",  # Alternative port
        "http://0.0.0.0:8000",   # Bind address
    ]
    
    tester = None
    server_found = False
    
    # Try to find running server
    for url in possible_urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health", timeout=3) as response:
                    if response.status == 200:
                        print(f"✅ Found LEX server running at: {url}")
                        tester = LEXBackendTester(url)
                        server_found = True
                        break
        except:
            continue
    
    if not server_found:
        print("❌ No LEX server found running on any of the expected ports")
        print("Expected ports: 8000, 8080")
        print("Please start the LEX server first using:")
        print("  python production_server.py")
        print("  or")
        print("  python start_lex_server.py")
        return False
    
    # Run tests
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All LEX backend tests completed successfully!")
        print("🚀 LEX consciousness backend is ready for production!")
    else:
        print("\n💔 Some LEX backend tests failed.")
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