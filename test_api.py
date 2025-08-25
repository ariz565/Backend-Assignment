#!/usr/bin/env python3
"""
Comprehensive Test Suite for Weather Service API
Tests all endpoints with various scenarios including error cases
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:5000"

class WeatherAPITester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def log_result(self, test_name, passed, details=""):
        """Log test result with details"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        print(result)
        self.results.append(result)
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("\n🔍 Testing Health Endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Health Check", True, f"Response: {data}")
                else:
                    self.log_result("Health Check", False, f"Invalid status: {data}")
            else:
                self.log_result("Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")

    def test_weather_report_valid_locations(self):
        """Test weather report with valid locations"""
        print("\n🌍 Testing Weather Report - Valid Locations...")
        
        # Test multiple valid locations
        test_locations = [
            ("New York", 40.7128, -74.0060),
            ("London", 51.5074, -0.1278),
            ("Tokyo", 35.6762, 139.6503),
            ("Sydney", -33.8688, 151.2093),
            ("Paris", 48.8566, 2.3522)
        ]
        
        for city, lat, lon in test_locations:
            try:
                response = requests.get(
                    f"{BASE_URL}/weather-report",
                    params={"lat": lat, "lon": lon},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Validate response structure for actual API response format
                    required_fields = ["status", "message", "records_count", "latitude", "longitude", "date_range"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields and data.get('status') == 'success':
                        self.log_result(f"Weather Report - {city}", True, 
                                      f"Records: {data['records_count']}, Status: {data['status']}")
                    else:
                        self.log_result(f"Weather Report - {city}", False, 
                                      f"Missing fields: {missing_fields} or status not success")
                else:
                    self.log_result(f"Weather Report - {city}", False, 
                                  f"Status: {response.status_code}, Response: {response.text[:100]}")
            except Exception as e:
                self.log_result(f"Weather Report - {city}", False, f"Exception: {str(e)}")

    def test_weather_report_invalid_params(self):
        """Test weather report with invalid parameters"""
        print("\n⚠️ Testing Weather Report - Invalid Parameters...")
        
        # Test cases for invalid parameters
        invalid_cases = [
            ("Missing latitude", {"lon": -74.0060}),
            ("Missing longitude", {"lat": 40.7128}),
            ("Invalid latitude high", {"lat": 91, "lon": -74.0060}),
            ("Invalid latitude low", {"lat": -91, "lon": -74.0060}),
            ("Invalid longitude high", {"lat": 40.7128, "lon": 181}),
            ("Invalid longitude low", {"lat": 40.7128, "lon": -181}),
            ("Non-numeric latitude", {"lat": "invalid", "lon": -74.0060}),
            ("Non-numeric longitude", {"lat": 40.7128, "lon": "invalid"}),
        ]
        
        for case_name, params in invalid_cases:
            try:
                response = requests.get(f"{BASE_URL}/weather-report", params=params, timeout=10)
                
                # We expect 400 Bad Request for invalid parameters
                if response.status_code == 400:
                    self.log_result(f"Invalid Params - {case_name}", True, "Correctly rejected")
                else:
                    self.log_result(f"Invalid Params - {case_name}", False, 
                                  f"Expected 400, got {response.status_code}")
            except Exception as e:
                self.log_result(f"Invalid Params - {case_name}", False, f"Exception: {str(e)}")

    def test_export_excel(self):
        """Test Excel export functionality"""
        print("\n📊 Testing Excel Export...")
        
        # First get some weather data
        try:
            # Get weather data for London
            weather_response = requests.get(
                f"{BASE_URL}/weather-report",
                params={"lat": 51.5074, "lon": -0.1278},
                timeout=30
            )
            
            if weather_response.status_code == 200:
                # Now test Excel export
                export_response = requests.get(f"{BASE_URL}/export/excel", timeout=30)
                
                if export_response.status_code == 200:
                    # Check if response is Excel file
                    content_type = export_response.headers.get('content-type', '')
                    if 'excel' in content_type or 'spreadsheet' in content_type:
                        # Save file to verify it's valid
                        with open('test_export.xlsx', 'wb') as f:
                            f.write(export_response.content)
                        
                        file_size = len(export_response.content)
                        self.log_result("Excel Export", True, f"File size: {file_size} bytes")
                        
                        # Clean up test file
                        if os.path.exists('test_export.xlsx'):
                            os.remove('test_export.xlsx')
                    else:
                        self.log_result("Excel Export", False, f"Wrong content type: {content_type}")
                else:
                    self.log_result("Excel Export", False, f"Status: {export_response.status_code}")
            else:
                self.log_result("Excel Export", False, "Could not get weather data first")
                
        except Exception as e:
            self.log_result("Excel Export", False, f"Exception: {str(e)}")

    def test_export_pdf(self):
        """Test PDF export functionality"""
        print("\n📄 Testing PDF Export...")
        
        try:
            # First get some weather data
            weather_response = requests.get(
                f"{BASE_URL}/weather-report",
                params={"lat": 51.5074, "lon": -0.1278},
                timeout=30
            )
            
            if weather_response.status_code == 200:
                # Now test PDF export
                export_response = requests.get(f"{BASE_URL}/export/pdf", timeout=60)
                
                if export_response.status_code == 200:
                    # Check if response is PDF file
                    content_type = export_response.headers.get('content-type', '')
                    if 'pdf' in content_type:
                        # Save file to verify it's valid
                        with open('test_export.pdf', 'wb') as f:
                            f.write(export_response.content)
                        
                        file_size = len(export_response.content)
                        # Basic PDF validation - check for PDF header
                        is_valid_pdf = export_response.content.startswith(b'%PDF')
                        
                        if is_valid_pdf:
                            self.log_result("PDF Export", True, f"Valid PDF, size: {file_size} bytes")
                        else:
                            self.log_result("PDF Export", False, "Invalid PDF format")
                        
                        # Clean up test file
                        if os.path.exists('test_export.pdf'):
                            os.remove('test_export.pdf')
                    else:
                        self.log_result("PDF Export", False, f"Wrong content type: {content_type}")
                else:
                    self.log_result("PDF Export", False, f"Status: {export_response.status_code}")
            else:
                self.log_result("PDF Export", False, "Could not get weather data first")
                
        except Exception as e:
            self.log_result("PDF Export", False, f"Exception: {str(e)}")

    def test_export_without_data(self):
        """Test exports when no data is available"""
        print("\n🔄 Testing Exports Without Data...")
        
        # This would require clearing the database or testing with a fresh instance
        # For now, we'll test the endpoints regardless of data state
        
        try:
            excel_response = requests.get(f"{BASE_URL}/export/excel", timeout=30)
            
            # Should either return empty file or handle gracefully
            if excel_response.status_code in [200, 404]:
                self.log_result("Excel Export No Data", True, f"Status: {excel_response.status_code}")
            else:
                self.log_result("Excel Export No Data", False, f"Status: {excel_response.status_code}")
        except Exception as e:
            self.log_result("Excel Export No Data", False, f"Exception: {str(e)}")
        
        try:
            pdf_response = requests.get(f"{BASE_URL}/export/pdf", timeout=30)
            
            # Should either return empty file or handle gracefully
            if pdf_response.status_code in [200, 404]:
                self.log_result("PDF Export No Data", True, f"Status: {pdf_response.status_code}")
            else:
                self.log_result("PDF Export No Data", False, f"Status: {pdf_response.status_code}")
        except Exception as e:
            self.log_result("PDF Export No Data", False, f"Exception: {str(e)}")

    def test_concurrent_requests(self):
        """Test concurrent API requests"""
        print("\n⚡ Testing Concurrent Requests...")
        
        import threading
        
        results = []
        
        def make_request():
            try:
                response = requests.get(
                    f"{BASE_URL}/weather-report",
                    params={"lat": 40.7128, "lon": -74.0060},
                    timeout=30
                )
                results.append(response.status_code == 200)
            except:
                results.append(False)
        
        # Create 5 concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        success_rate = sum(results) / len(results)
        if success_rate >= 0.8:  # 80% success rate acceptable
            self.log_result("Concurrent Requests", True, f"Success rate: {success_rate:.1%}")
        else:
            self.log_result("Concurrent Requests", False, f"Success rate: {success_rate:.1%}")

    def test_response_times(self):
        """Test API response times"""
        print("\n⏱️ Testing Response Times...")
        
        endpoints = [
            ("/health", {}),
            ("/weather-report", {"lat": 40.7128, "lon": -74.0060}),
        ]
        
        for endpoint, params in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=30)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Consider under 10 seconds acceptable for weather data
                if response_time < 10.0:
                    self.log_result(f"Response Time {endpoint}", True, 
                                  f"{response_time:.2f}s (Status: {response.status_code})")
                else:
                    self.log_result(f"Response Time {endpoint}", False, 
                                  f"{response_time:.2f}s - Too slow")
            except Exception as e:
                self.log_result(f"Response Time {endpoint}", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Weather API Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_health_endpoint()
        self.test_weather_report_valid_locations()
        self.test_weather_report_invalid_params()
        self.test_export_excel()
        self.test_export_pdf()
        self.test_export_without_data()
        self.test_concurrent_requests()
        self.test_response_times()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {self.passed/(self.passed + self.failed)*100:.1f}%")
        print(f"⏱️ Total Time: {total_time:.2f} seconds")
        print(f"📝 Total Tests: {self.passed + self.failed}")
        
        if self.failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if "❌ FAIL" in result:
                    print(f"  • {result}")
        
        return self.failed == 0

def main():
    """Main test runner"""
    print("Weather Service API Test Suite")
    print("Make sure the Flask server is running on http://localhost:5000")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return
    
    tester = WeatherAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the API implementation.")

if __name__ == "__main__":
    main()
