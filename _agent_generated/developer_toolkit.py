#!/usr/bin/env python3
"""
Lucid-Helix Developer Toolkit

A comprehensive tool that integrates with Lucid-Helix API services to:
- Review code quality
- Fix bugs automatically
- Generate test cases
- Explain complex code

Public API: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import json
import sys
import os

class LucidHelixToolkit:
    def __init__(self, base_url="https://cet-temporal-therapist-forgot.trycloudflare.com"):
        self.base_url = base_url
        
    def code_review(self, code: str, language: str = "python") -> dict:
        """Get professional code review from Lucid-Helix"""
        response = requests.post(
            f"{self.base_url}/api/code-review-pro",
            json={"code": code, "language": language}
        )
        return response.json()
    
    def fix_bug(self, code: str, error_message: str = "", language: str = "python") -> dict:
        """Fix bugs automatically using Lucid-Helix"""
        response = requests.post(
            f"{self.base_url}/api/fix-bug-pro",
            json={
                "code": code, 
                "error_message": error_message,
                "language": language
            }
        )
        return response.json()
    
    def generate_tests(self, code: str, language: str = "python") -> dict:
        """Generate comprehensive test cases"""
        response = requests.post(
            f"{self.base_url}/api/write-tests-pro",
            json={"code": code, "language": language}
        )
        return response.json()
    
    def explain_code(self, code: str, language: str = "python") -> dict:
        """Get detailed explanation of complex code"""
        response = requests.post(
            f"{self.base_url}/api/explain-code",
            json={"code": code, "language": language}
        )
        return response.json()

def main():
    """Demo the toolkit with example code"""
    toolkit = LucidHelixToolkit()
    
    # Example problematic code
    example_code = """
def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total / len(numbers)

# This will cause division by zero error
result = calculate_average([])
print(result)
"""
    
    print("🔧 Lucid-Helix Developer Toolkit Demo")
    print("=" * 50)
    
    # Code review
    print("\n📋 Code Review:")
    review = toolkit.code_review(example_code)
    print(f"Review: {review.get('review', 'No review available')}")
    
    # Bug fix
    print("\n🐛 Bug Fix:")
    fix = toolkit.fix_bug(example_code, "Division by zero error")
    print(f"Fixed code: {fix.get('fixed_code', 'No fix available')}")
    
    # Test generation
    print("\n🧪 Test Generation:")
    tests = toolkit.generate_tests(example_code)
    print(f"Tests: {tests.get('tests', 'No tests available')}")
    
    print(f"\n💡 Try the full API at: {toolkit.base_url}")
    print("All services have FREE playground on the landing page!")

if __name__ == "__main__":
    main()