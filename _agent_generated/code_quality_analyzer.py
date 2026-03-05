#!/usr/bin/env python3
"""
Lucid-Helix Code Quality Analyzer

A comprehensive tool that analyzes Python code quality using multiple Lucid-Helix API services.
Tests code review, bug detection, and test generation in one workflow.

Your API is LIVE at: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import json
import sys

def call_lucid_helix_api(service, payload):
    """Call Lucid-Helix API service"""
    base_url = "https://cet-temporal-therapist-forgot.trycloudflare.com"
    
    try:
        response = requests.post(
            f"{base_url}/{service}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_code_quality(code_file):
    """Analyze code quality using multiple Lucid-Helix services"""
    
    with open(code_file, 'r') as f:
        code_content = f.read()
    
    print(f"🔍 Analyzing {code_file} with Lucid-Helix AI...")
    print("=" * 60)
    
    # 1. Code Review
    print("\n📋 Code Review Analysis:")
    review_result = call_lucid_helix_api("code-review", {
        "code": code_content,
        "language": "python"
    })
    print(review_result.get('review', 'No review available'))
    
    # 2. Bug Detection
    print("\n🐛 Bug Detection:")
    bug_result = call_lucid_helix_api("fix-bug", {
        "code": code_content,
        "error_description": "Analyze for potential bugs"
    })
    print(bug_result.get('fixed_code', 'No bugs detected'))
    
    # 3. Test Generation
    print("\n🧪 Test Generation:")
    test_result = call_lucid_helix_api("write-tests", {
        "code": code_content,
        "test_framework": "pytest"
    })
    print(test_result.get('tests', 'No tests generated'))
    
    print("\n✅ Analysis complete!")
    print("\n💡 Try the PRO versions for GPT-4o quality analysis:")
    print("- code-review-pro: $0.20 per request")
    print("- fix-bug-pro: $0.30 per request") 
    print("- write-tests-pro: $0.25 per request")

def main():
    if len(sys.argv) != 2:
        print("Usage: python code_quality_analyzer.py <python_file>")
        print("Example: python code_quality_analyzer.py my_script.py")
        sys.exit(1)
    
    code_file = sys.argv[1]
    
    try:
        analyze_code_quality(code_file)
    except FileNotFoundError:
        print(f"Error: File '{code_file}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()