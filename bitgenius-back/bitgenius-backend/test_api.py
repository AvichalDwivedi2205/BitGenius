#!/usr/bin/env python3
"""
BitGenius API Test Script
-------------------------
This script performs a comprehensive test of all API endpoints in the BitGenius backend.
Usage: python test_api.py
"""

import requests
import json
import time
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8080"  # Change this if using a different port
HEADERS = {"Content-Type": "application/json"}

# Color formatting
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_test(name):
    print(f"{Colors.BLUE}Testing: {name}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✓ SUCCESS: {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ WARNING: {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}✗ ERROR: {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ INFO: {message}{Colors.ENDC}")

def print_response(response):
    status = response.status_code
    if status >= 200 and status < 300:
        status_color = Colors.GREEN
    elif status >= 300 and status < 400:
        status_color = Colors.YELLOW
    else:
        status_color = Colors.RED
    
    print(f"  Status: {status_color}{status}{Colors.ENDC}")
    
    try:
        # Try to pretty print the JSON response
        data = response.json()
        print(f"  Response: {json.dumps(data, indent=2)}")
    except:
        # If not JSON, print the raw text
        print(f"  Response: {response.text}")

def make_request(method, endpoint, data=None, expected_status=200):
    """Make a request to the API and validate the response"""
    url = f"{BASE_URL}{endpoint}"
    print_info(f"Request: {method} {url}")
    
    if data:
        print_info(f"Payload: {json.dumps(data, indent=2)}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS, params=data)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=HEADERS, json=data)
        else:
            print_error(f"Unsupported HTTP method: {method}")
            return None
        
        print_response(response)
        
        if response.status_code == expected_status:
            print_success(f"Got expected status code {expected_status}")
            return response.json() if response.text else {}
        else:
            print_error(f"Expected status {expected_status}, got {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error(f"Connection error. Is the server running at {BASE_URL}?")
        return None
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None

def test_root():
    """Test the root endpoint"""
    print_test("Root Endpoint")
    make_request("GET", "/")

def test_dashboard():
    """Test dashboard endpoints"""
    print_header("DASHBOARD ENDPOINTS")
    
    print_test("Get Dashboard Summary")
    make_request("GET", "/dashboard/summary")
    
    print_test("Get Market Data")
    make_request("GET", "/dashboard/market")

def test_agents():
    """Test agents endpoints"""
    print_header("AGENT ENDPOINTS")
    
    print_test("List Agents")
    agents = make_request("GET", "/agents")
    
    if agents:
        if len(agents) > 0:
            agent_id = agents[0].get("id", 1)
            print_test(f"Get Agent Details (ID: {agent_id})")
            make_request("GET", f"/agents/{agent_id}")
        else:
            print_warning("No agents found to test detailed endpoints")
    
    print_test("Get Agent Templates")
    make_request("GET", "/agents/templates")
    
    # Test agent creation with sample data
    print_test("Create Agent (May return 400 if validation fails)")
    sample_agent = {
        "name": "Test Agent",
        "agent_type": "trading",
        "strategy": "hodl",
        "trigger_condition": "price_threshold",
        "privacy_enabled": True,
        "allocation": 10000
    }
    make_request("POST", "/agents", data=sample_agent, expected_status=None)  # Don't enforce status code
    
    # Test agent status update (this may fail if agent ID doesn't exist)
    print_test("Update Agent Status (May return 404 if agent doesn't exist)")
    update_data = {"status": "active"}
    make_request("PUT", "/agents/1/status", data=update_data, expected_status=None)

def test_logs():
    """Test logs endpoints"""
    print_header("LOGS ENDPOINTS")
    
    print_test("Get All Logs")
    make_request("GET", "/logs")
    
    print_test("Get Logs by Agent (ID: 1)")
    make_request("GET", "/logs/agent/1")
    
    # Test log creation (may fail depending on requirements)
    print_test("Create Log Entry (May return 400 if validation fails)")
    log_entry = {
        "agent_id": 1,
        "action": "test",
        "status": "completed",
        "details": "Test entry from API test script"
    }
    make_request("POST", "/logs", data=log_entry, expected_status=None)

def test_ai():
    """Test AI endpoints"""
    print_header("AI ENDPOINTS")
    
    print_test("Get Strategy Recommendations")
    ai_query = {"market_condition": "volatile", "risk_preference": "moderate"}
    make_request("POST", "/ai/strategy", data=ai_query, expected_status=None)
    
    print_test("Analyze Market")
    ai_query = {"timeframe": "daily", "indicators": ["rsi", "macd"]}
    make_request("POST", "/ai/analyze", data=ai_query, expected_status=None)

def run_all_tests():
    """Run all test functions"""
    print_header("BITGENIUS API TEST SUITE")
    print_info(f"Testing API at {BASE_URL}")
    
    # Basic connection test
    test_root()
    
    # Feature-specific tests
    test_dashboard()
    test_agents()
    test_logs()
    test_ai()
    
    print_header("TEST SUITE COMPLETED")

if __name__ == "__main__":
    run_all_tests()
