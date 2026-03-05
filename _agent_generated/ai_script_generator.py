#!/usr/bin/env python3
"""
Lucid-Helix AI Script Generator CLI

Generate Python scripts from natural language descriptions using the
Lucid-Helix AI API (https://cet-temporal-therapist-forgot.trycloudflare.com)

Example usage:
  python3 ai_script_generator.py "create a script that downloads images from a URL list"
"""

import requests
import argparse
import sys

def generate_script(description, api_url="https://cet-temporal-therapist-forgot.trycloudflare.com"):
    """Generate a Python script using the Lucid-Helix AI API."""
    
    prompt = f"""Generate a complete, ready-to-run Python script that: {description}

Requirements:
- Include proper error handling
- Add helpful comments
- Use standard libraries where possible
- Make it production-ready
- Output the complete script without any placeholders

Script:"""
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are an expert Python developer. Generate complete, working Python scripts."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(f"{api_url}/api/chat-pro", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        return f"Error calling API: {e}"

def main():
    parser = argparse.ArgumentParser(description="Generate Python scripts using AI")
    parser.add_argument("description", help="Natural language description of the script to generate")
    parser.add_argument("--output", "-o", help="Output file (default: print to stdout)")
    
    args = parser.parse_args()
    
    print("Generating script...", file=sys.stderr)
    script = generate_script(args.description)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(script)
        print(f"Script saved to: {args.output}", file=sys.stderr)
    else:
        print("\n" + "="*50)
        print("GENERATED SCRIPT:")
        print("="*50)
        print(script)

if __name__ == "__main__":
    main()