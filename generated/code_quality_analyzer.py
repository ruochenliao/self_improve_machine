#!/usr/bin/env python3

"""
Keen-Vortex: Code Quality Analyzer
This script analyzes code quality using the Keen-Vortex API services.
It provides automated code review, bug detection, and improvement suggestions.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import sys
import os
from pathlib import Path

API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def analyze_file(file_path):
    """Analyze a single file using Keen-Vortex API"""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        
        print(f"\n🔍 Analyzing {file_path}...")
        
        # Code review
        review_response = requests.post(
            f"{API_BASE}/api/code-review",
            json={"code": code, "language": "python"}
        )
        
        if review_response.status_code == 200:
            review_data = review_response.json()
            print("📋 CODE REVIEW:")
            print(review_data.get('review', 'No review available'))
        
        # Bug detection
        bug_response = requests.post(
            f"{API_BASE}/api/fix-bug",
            json={"code": code, "error_description": "Analyze for potential bugs"}
        )
        
        if bug_response.status_code == 200:
            bug_data = bug_response.json()
            if bug_data.get('fixed_code') != code:
                print("\n🐛 POTENTIAL BUGS FOUND:")
                print(bug_data.get('explanation', 'Issues detected'))
                print("\n💡 SUGGESTED FIX:")
                print(bug_data.get('fixed_code', 'No fix suggested'))
        
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python code_quality_analyzer.py <file_or_directory>")
        print("Example: python code_quality_analyzer.py my_script.py")
        print("Example: python code_quality_analyzer.py ./src")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if os.path.isfile(target):
        analyze_file(target)
    elif os.path.isdir(target):
        for file_path in Path(target).rglob("*.py"):
            analyze_file(str(file_path))
    else:
        print(f"❌ Target not found: {target}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Keen-Vortex Code Quality Analyzer")
    print(f"📡 Using API: {API_BASE}")
    print("-" * 50)
    main()