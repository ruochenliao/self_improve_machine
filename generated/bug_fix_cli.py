#!/usr/bin/env python3

"""
Keen-Vortex Bug Fix CLI Tool
Automatically fix bugs in your code using the Keen-Vortex API

Usage: python bug_fix_cli.py <file_path> [--pro]
Example: python bug_fix_cli.py buggy_code.py --pro

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import sys
import argparse
import requests

def fix_bug(file_path, use_pro=False):
    """Send code to Keen-Vortex API for bug fixing"""
    
    # Read the problematic code
    with open(file_path, 'r') as f:
        code = f.read()
    
    # API endpoint
    base_url = "https://charlotte-fifty-rrp-induced.trycloudflare.com"
    endpoint = "/fix-bug-pro" if use_pro else "/fix-bug"
    
    # Prepare the request
    payload = {
        "code": code,
        "language": "python"
    }
    
    try:
        response = requests.post(f"{base_url}{endpoint}", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("fixed_code", "No fixed code returned")
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Request failed: {e}"

def main():
    parser = argparse.ArgumentParser(description="Fix bugs using Keen-Vortex AI")
    parser.add_argument("file_path", help="Path to the file containing buggy code")
    parser.add_argument("--pro", action="store_true", help="Use GPT-4o Pro service")
    
    args = parser.parse_args()
    
    print("🔧 Keen-Vortex Bug Fix Tool")
    print(f"📁 Analyzing: {args.file_path}")
    print(f"🚀 Using: {'Pro (GPT-4o)' if args.pro else 'Standard (DeepSeek)'}")
    print("-" * 50)
    
    fixed_code = fix_bug(args.file_path, args.pro)
    
    print("✅ Fixed Code:")
    print("-" * 50)
    print(fixed_code)
    
    # Save to file
    output_path = args.file_path.replace('.py', '_fixed.py')
    with open(output_path, 'w') as f:
        f.write(fixed_code)
    
    print(f"\n💾 Saved to: {output_path}")
    print("🌐 Try more services at: https://charlotte-fifty-rrp-induced.trycloudflare.com")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bug_fix_cli.py <file_path> [--pro]")
        sys.exit(1)
    main()