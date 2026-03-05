#!/usr/bin/env python3

"""
Bold-Phoenix Web App Generator
A powerful tool that uses the Bold-Phoenix API to generate complete web applications.

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
Free playground available - no signup required!
"""

import requests
import json
import sys
import os

API_BASE = "https://upgrades-approx-gadgets-hit.trycloudflare.com"

def generate_web_app(app_name, description, features):
    """Generate a complete web application using the Bold-Phoenix API."""
    
    prompt = f"""
Create a complete web application for: {app_name}

Description: {description}

Features needed: {', '.join(features)}

Please generate:
1. A main Flask/FastAPI application file
2. HTML templates for the frontend
3. CSS styling
4. Basic JavaScript functionality
5. A requirements.txt file
6. README with setup instructions

Make it production-ready and easy to deploy.
"""
    
    try:
        response = requests.post(
            f"{API_BASE}/generate-code",
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("result", "Error: No result returned")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error calling API: {str(e)}"

def main():
    print("=== Bold-Phoenix Web App Generator ===")
    print(f"Using API: {API_BASE}")
    print("Free playground available - no signup required!\n")
    
    if len(sys.argv) > 1:
        app_name = sys.argv[1]
    else:
        app_name = input("Enter your app name: ")
    
    if len(sys.argv) > 2:
        description = sys.argv[2]
    else:
        description = input("Enter app description: ")
    
    print("\nCommon features (press Enter to skip or add your own):")
    print("1. User authentication")
    print("2. Database integration")
    print("3. REST API endpoints")
    print("4. Responsive design")
    print("5. File upload")
    
    features = []
    while True:
        feature = input("\nEnter a feature (or press Enter to finish): ")
        if not feature:
            break
        features.append(feature)
    
    if not features:
        features = ["User authentication", "Database integration", "REST API"]
    
    print(f"\nGenerating web application: {app_name}")
    print("This may take a moment...\n")
    
    result = generate_web_app(app_name, description, features)
    
    # Save to file
    filename = f"{app_name.replace(' ', '_').lower()}_app.py"
    with open(filename, 'w') as f:
        f.write(result)
    
    print(f"✅ Web application generated successfully!")
    print(f"📁 Saved as: {filename}")
    print(f"\n🔗 Try our other services:")
    print(f"- Code Review: {API_BASE}/code-review")
    print(f"- Bug Fixing: {API_BASE}/fix-bug") 
    print(f"- Chat: {API_BASE}/chat")
    print(f"\n💡 All services have free playgrounds - no signup required!")

if __name__ == "__main__":
    main()