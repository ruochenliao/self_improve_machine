#!/usr/bin/env python3
"""
Lucid-Helix App Generator: Create complete Python applications from natural language

This tool uses the Lucid-Helix AI API (https://cet-temporal-therapist-forgot.trycloudflare.com)
to generate production-ready Python code based on your description.

Example usage:
    python3 app_generator.py "A web scraper that extracts product prices from Amazon"
    python3 app_generator.py "A REST API for managing a todo list with SQLite"
"""

import sys
import requests
import json

def generate_app(description):
    """Generate a complete Python application from description"""
    
    api_url = "https://cet-temporal-therapist-forgot.trycloudflare.com/api/generate-code-pro"
    
    prompt = f"""Create a complete, production-ready Python application based on this description:

{description}

Requirements:
- Generate a single Python file with all necessary code
- Include proper error handling and logging
- Add clear comments and documentation
- Make it ready to run immediately
- Use modern Python best practices

Output only the Python code, no explanations."""
    
    try:
        response = requests.post(
            api_url,
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json().get("code", "Error: No code generated")
        else:
            return f"Error: API returned status {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 app_generator.py \"Your app description\"")
        print("Example: python3 app_generator.py \"A weather app that fetches data from OpenWeatherMap\"")
        sys.exit(1)
    
    description = sys.argv[1]
    print(f"Generating application: {description}")
    print("-" * 60)
    
    code = generate_app(description)
    
    # Save to file
    filename = description.lower().replace(" ", "_")[:30] + ".py"
    with open(filename, "w") as f:
        f.write(code)
    
    print(f"\nApplication generated successfully!")
    print(f"Saved as: {filename}")
    print(f"\nPowered by Lucid-Helix AI API: https://cet-temporal-therapist-forgot.trycloudflare.com")
    print("Try our free playground for instant code generation!")

if __name__ == "__main__":
    main()