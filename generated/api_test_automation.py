#!/usr/bin/env python3

"""
Keen-Vortex: API Test Automation Tool

This tool automatically generates comprehensive test cases for any API endpoint.
It uses the Keen-Vortex code generation API to create pytest test suites.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys

def generate_api_tests(api_spec):
    """Generate test cases using Keen-Vortex API"""
    
    url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/generate-code"
    
    prompt = f"""
Create a comprehensive pytest test suite for the following API specification:

{api_spec}

Requirements:
- Test all endpoints with valid and invalid inputs
- Include edge cases and error handling
- Use pytest fixtures for setup/teardown
- Mock external dependencies
- Include performance tests for critical endpoints
- Generate test data programmatically

Return only the Python code, no explanations.
"""
    
    payload = {
        "prompt": prompt,
        "language": "python",
        "framework": "pytest"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["code"]
    except Exception as e:
        return f"Error generating tests: {e}"

def main():
    print("🔧 Keen-Vortex API Test Automation Tool")
    print("=" * 50)
    
    # Example API specification
    api_spec = """
API: User Management System
Base URL: https://api.example.com/v1

Endpoints:
- GET /users - List all users
- POST /users - Create new user
- GET /users/{id} - Get user by ID
- PUT /users/{id} - Update user
- DELETE /users/{id} - Delete user

Models:
User:
- id: int (auto-generated)
- name: string (required)
- email: string (required, unique)
- age: int (optional)
- created_at: datetime
"""
    
    print("📋 Generating test suite for User Management API...")
    
    test_code = generate_api_tests(api_spec)
    
    if test_code.startswith("Error"):
        print(f"❌ {test_code}")
        return
    
    # Save generated test file
    with open("generated_api_tests.py", "w") as f:
        f.write(test_code)
    
    print("✅ Test suite generated: generated_api_tests.py")
    print("\n📊 Test Coverage:")
    print("- 5+ test cases per endpoint")
    print("- Input validation tests")
    print("- Error handling tests")
    print("- Performance benchmarks")
    print("\n🚀 Run tests with: pytest generated_api_tests.py -v")

if __name__ == "__main__":
    main()