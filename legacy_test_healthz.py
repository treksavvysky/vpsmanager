#!/usr/bin/env python3
"""
Test script for /healthz endpoint and other API endpoints.
This script reads API_KEY from environment variables to avoid exposing secrets.
"""
import requests
import os
import json

# Base URL for the VPS Manager API
BASE_URL = "http://localhost:8971"

def test_healthz():
    """Test the /healthz endpoint (no auth required)"""
    print("Testing /healthz endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        if response.status_code != 200:
            return False

        # Basic structure validation
        if "status" not in data or "hosts" not in data:
            print("❌ Test failed: Missing 'status' or 'hosts' in response.")
            return False

        for host, status in data["hosts"].items():
            if not isinstance(status, dict) or "ping_reachable" not in status or "ssh_successful" not in status:
                print(f"❌ Test failed: Invalid status for host '{host}'. Missing 'ping_reachable' or 'ssh_successful'.")
                return False

            if status["ssh_successful"]:
                if "hostname" not in status or "uptime" not in status:
                    print(f"❌ Test failed: Missing 'hostname' or 'uptime' for successful SSH on host '{host}'.")
                    return False
            else: # if ssh was not successful
                if "error" not in status:
                     print(f"❌ Test failed: Missing 'error' for failed SSH on host '{host}'.")
                     return False

        print("✅ Test passed: /healthz response format is valid.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error testing /healthz: {e}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Test failed: Could not decode JSON response.")
        return False

def test_with_auth(endpoint, method="GET", data=None):
    """Test an endpoint that requires authentication"""
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("❌ API_KEY environment variable not set. Cannot test authenticated endpoints.")
        return False
    
    headers = {"Authorization": api_key}
    
    print(f"Testing {method} {endpoint} with authentication...")
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error testing {endpoint}: {e}")
        return False

def main():
    print("🚀 VPS Manager API Test Suite")
    print("=" * 50)
    
    # Test healthz endpoint (no auth required)
    healthz_success = test_healthz()
    print()
    
    # Test authenticated endpoints if API_KEY is available
    if os.getenv("API_KEY"):
        print("Testing authenticated endpoints...")
        print("-" * 30)
        
        # Test VPS status
        test_with_auth("/vps/status")
        print()
        
        # Test server list
        test_with_auth("/servers/list")
        print()
        
        # Test SSH sessions list
        test_with_auth("/ssh_execute/list_sessions")
        print()
        
    else:
        print("💡 To test authenticated endpoints, set the API_KEY environment variable:")
        print("   export API_KEY='your-api-key-here'")
        print("   python3 test_healthz.py")
    
    print("✅ Test completed!" if healthz_success else "❌ Healthz test failed!")

if __name__ == "__main__":
    main()
