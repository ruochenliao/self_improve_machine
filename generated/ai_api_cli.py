#!/usr/bin/env python3
"""
AI API CLI - Access all 14 AI services from command line
Usage: python ai_api_cli.py <service> [args]
Services: chat, translate, summarize, explain-code, code-review, generate-code, write-tests, fix-bug
Add -pro suffix for premium versions (e.g., chat-pro)
API URL: http://localhost:8402 (replace with public URL when deployed)
"""
import sys
import json
import requests

def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_api_cli.py <service> [input_text]")
        return
    
    service = sys.argv[1]
    input_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Hello, world!"
    
    # Replace with your public URL when available
    api_url = f"http://localhost:8402/{service}"
    
    try:
        response = requests.post(api_url, json={"text": input_text})
        result = response.json()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()