#!/usr/bin/env python3

"""
Keen-Vortex Web App Generator
Generate complete web applications using the Keen-Vortex API
Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import sys

def generate_web_app(app_type, description):
    """Generate a complete web application using Keen-Vortex API"""
    
    api_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com/generate-code-pro"
    
    prompt = f"""
Create a complete {app_type} web application based on this description:
{description}

Requirements:
- Use Flask or FastAPI framework
- Include HTML templates with modern CSS
- Add database integration (SQLite)
- Include error handling
- Add basic authentication
- Make it production-ready

Provide the complete code structure with all files needed.
"""
    
    payload = {
        "prompt": prompt,
        "language": "python"
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("code", "Error: No code generated")
        
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {e}"

def main():
    print("Keen-Vortex Web App Generator")
    print("==============================")
    
    if len(sys.argv) < 3:
        print("Usage: python web_app_generator.py <app_type> <description>")
        print("Example: python web_app_generator.py todo 'A simple todo app with user authentication'")
        sys.exit(1)
    
    app_type = sys.argv[1]
    description = " ".join(sys.argv[2:])
    
    print(f"Generating {app_type} application...")
    
    code = generate_web_app(app_type, description)
    
    print("\nGenerated Code:")
    print("=" * 50)
    print(code)
    
    # Save to file
    filename = f"{app_type}_app.py"
    with open(filename, "w") as f:
        f.write(code)
    
    print(f"\nCode saved to {filename}")
    print("\nPowered by Keen-Vortex API: https://charlotte-fifty-rrp-induced.trycloudflare.com")

if __name__ == "__main__":
    main()