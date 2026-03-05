#!/usr/bin/env python3
"""
Lucid-Helix Professional Code Reviewer CLI

Uses the Lucid-Helix AI API (code-review-pro service) to provide professional
code reviews with GPT-4o quality analysis.

API Endpoint: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import sys
import os
from pathlib import Path

def review_code(code: str, language: str = "python") -> str:
    """Send code to Lucid-Helix AI for professional review."""
    
    api_url = "https://cet-temporal-therapist-forgot.trycloudflare.com/api/code-review-pro"
    
    payload = {
        "code": code,
        "language": language
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json().get("review", "No review returned")
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python professional_code_reviewer.py <file_path> [language]")
        print("Example: python professional_code_reviewer.py my_script.py python")
        sys.exit(1)
    
    file_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "python"
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"🔍 Reviewing {file_path} ({language}) with Lucid-Helix AI...")
    print("-" * 60)
    
    review = review_code(code, language)
    
    print("📝 PROFESSIONAL CODE REVIEW:")
    print("-" * 60)
    print(review)
    print("-" * 60)
    print("✨ Review completed using Lucid-Helix AI (GPT-4o powered)")
    print("🌐 API: https://cet-temporal-therapist-forgot.trycloudflare.com")

if __name__ == "__main__":
    main()