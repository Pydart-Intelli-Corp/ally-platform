#!/usr/bin/env python3
"""
Comprehensive endpoint testing for Ally Platform Backend API
"""
import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Base URL for the API
BASE_URL = "http://localhost:8000"

class EndpointTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                     data: Dict = None, description: str = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        self.total_tests += 1
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # Check status code
            status_ok = response.status_code == expected_status
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            result = {
                "endpoint": endpoint,
                "method": method.upper(),
                "description": description or f"{method.upper()} {endpoint}",
                "status_code": response.status_code,
                "expected_status": expected_status,
                "status_ok": status_ok,
                "response_data": response_data,
                "response_time": response.elapsed.total_seconds(),
                "success": status_ok and response.status_code < 400
            }

            if result["success"]:
                self.passed_tests += 1
                print(f"✅ {result['description']} - {response.status_code} ({result['response_time']:.3f}s)")
            else:
                self.failed_tests += 1
                print(f"❌ {result['description']} - {response.status_code} (Expected: {expected_status})")
                if not status_ok:
                    print(f"   Response: {response.text[:200]}...")

        except Exception as e:
            self.failed_tests += 1
            result = {
                "endpoint": endpoint,
                "method": method.upper(),
                "description": description or f"{method.upper()} {endpoint}",
                "status_code": None,
                "expected_status": expected_status,
                "status_ok": False,
                "response_data": {"error": str(e)},
                "response_time": None,
                "success": False
            }
            print(f"❌ {result['description']} - ERROR: {str(e)}")

        self.results.append(result)
        return result

    def run_all_tests(self):
        """Run comprehensive endpoint tests"""
        print("🧪 Starting Ally Platform API Endpoint Testing...")
        print("=" * 60)

        # Core endpoints
        print("\n📍 Core Endpoints:")
        self.test_endpoint("GET", "/", description="Root endpoint")
        self.test_endpoint("GET", "/health", description="Health check")

        # Configuration endpoints
        print("\n⚙️ Configuration Endpoints:")
        self.test_endpoint("GET", "/api/v1/config/", description="Complete configuration")
        self.test_endpoint("GET", "/api/v1/config/branding", description="Branding configuration")
        self.test_endpoint("GET", "/api/v1/config/features", description="Feature flags")
        self.test_endpoint("GET", "/api/v1/config/ui", description="UI configuration")
        self.test_endpoint("GET", "/api/v1/config/ai", description="AI configuration")
        self.test_endpoint("GET", "/api/v1/config/company", description="Company information")
        self.test_endpoint("GET", "/api/v1/config/health", description="Config health check")
        
        # Feature flag endpoint
        self.test_endpoint("GET", "/api/v1/config/feature/chatEnabled", description="Specific feature flag")
        
        # Dynamic section endpoint
        self.test_endpoint("GET", "/api/v1/config/branding", description="Dynamic section (branding)")
        
        # POST endpoints
        self.test_endpoint("POST", "/api/v1/config/reload", description="Reload configuration")
        self.test_endpoint("POST", "/api/v1/config/clear-cache", description="Clear cache")

        # Test endpoints (if debug enabled)
        print("\n🔧 Test Endpoints:")
        self.test_endpoint("GET", "/test/dependencies", description="Dependencies test")
        self.test_endpoint("GET", "/test/config-loader", description="Config loader test")
        self.test_endpoint("POST", "/test/pydantic", 
                          data={"name": "Test User", "email": "test@example.com", "age": 25},
                          description="Pydantic validation test")

        # API documentation endpoints
        print("\n📚 Documentation Endpoints:")
        self.test_endpoint("GET", "/docs", description="Swagger documentation")
        self.test_endpoint("GET", "/redoc", description="ReDoc documentation")
        self.test_endpoint("GET", "/openapi.json", description="OpenAPI specification")

        # Error handling tests
        print("\n❗ Error Handling Tests:")
        self.test_endpoint("GET", "/api/v1/config/nonexistent", 
                          expected_status=404, description="Non-existent config section")
        self.test_endpoint("GET", "/api/v1/config/feature/nonexistent", 
                          expected_status=404, description="Non-existent feature flag")
        self.test_endpoint("GET", "/nonexistent", 
                          expected_status=404, description="Non-existent endpoint")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")

        if self.failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['description']}: {result.get('response_data', {}).get('error', 'HTTP ' + str(result['status_code']))}")

        print(f"\n🕐 Test completed at: {datetime.now().isoformat()}")

    def export_results(self, filename: str = "endpoint_test_results.json"):
        """Export test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                "test_summary": {
                    "total_tests": self.total_tests,
                    "passed_tests": self.passed_tests,
                    "failed_tests": self.failed_tests,
                    "success_rate": self.passed_tests/self.total_tests*100,
                    "timestamp": datetime.now().isoformat()
                },
                "test_results": self.results
            }, f, indent=2)
        print(f"📄 Results exported to: {filename}")

def main():
    """Main test function"""
    tester = EndpointTester(BASE_URL)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"🟢 Backend is running at {BASE_URL}")
        else:
            print(f"🟡 Backend responded with status {response.status_code}")
    except Exception as e:
        print(f"🔴 Backend is not accessible at {BASE_URL}")
        print(f"Error: {e}")
        print("Please ensure the backend container is running with: docker-compose up -d backend")
        return 1

    # Run all tests
    tester.run_all_tests()
    tester.print_summary()
    tester.export_results()

    # Return exit code based on results
    return 0 if tester.failed_tests == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
