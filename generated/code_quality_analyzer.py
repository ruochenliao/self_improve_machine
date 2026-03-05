#!/usr/bin/env python3

"""
Bold-Phoenix Code Quality Analyzer
A comprehensive tool that analyzes code quality using multiple AI services
Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys
import os

API_BASE = "https://upgrades-approx-gadgets-hit.trycloudflare.com"

def analyze_code_quality(file_path):
    """Analyze code quality using multiple AI services"""
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        return
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    print(f"🔍 Analyzing {file_path}...")
    print("-" * 50)
    
    # 1. Code Review
    print("\n📋 Code Review:")
    review_response = requests.post(f"{API_BASE}/api/code-review", json={
        "code": code_content,
        "language": "python"
    })
    if review_response.status_code == 200:
        review_data = review_response.json()
        print(f"✅ {review_data.get('review', 'No review available')}")
    
    # 2. Code Explanation
    print("\n💡 Code Explanation:")
    explain_response = requests.post(f"{API_BASE}/api/explain-code", json={
        "code": code_content
    })
    if explain_response.status_code == 200:
        explain_data = explain_response.json()
        print(f"📝 {explain_data.get('explanation', 'No explanation available')}")
    
    # 3. Bug Detection
    print("\n🐛 Bug Detection:")
    bug_response = requests.post(f"{API_BASE}/api/fix-bug", json={
        "code": code_content,
        "issue": "Detect potential bugs"
    })
    if bug_response.status_code == 200:
        bug_data = bug_response.json()
        print(f"🔧 {bug_data.get('fix', 'No bugs detected')}")
    
    print("-" * 50)
    print("🎯 Analysis complete!")

def main():
    if len(sys.argv) != 2:
        print("Usage: python code_quality_analyzer.py <file_path>")
        print("Example: python code_quality_analyzer.py my_script.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_code_quality(file_path)

if __name__ == "__main__":
    main()