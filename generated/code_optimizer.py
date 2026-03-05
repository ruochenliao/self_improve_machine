#!/usr/bin/env python3
"""
Keen-Vortex Code Optimizer
A practical tool that uses the Keen-Vortex API to optimize Python code.

Public API: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import json
import argparse

API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def optimize_code(code: str, use_pro: bool = False) -> str:
    """Send code to Keen-Vortex API for optimization."""
    endpoint = f"{API_BASE}/fix-bug-pro" if use_pro else f"{API_BASE}/fix-bug"
    
    payload = {
        "code": code,
        "language": "python",
        "description": "Optimize this code for performance and readability"
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("optimized_code", result.get("fixed_code", "Optimization failed"))
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Optimize Python code using Keen-Vortex AI")
    parser.add_argument("file", help="Python file to optimize")
    parser.add_argument("--pro", action="store_true", help="Use GPT-4o pro service")
    parser.add_argument("--output", help="Output file (default: optimized_<filename>)")
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r') as f:
            original_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        return
    
    print("Optimizing code with Keen-Vortex AI...")
    optimized = optimize_code(original_code, args.pro)
    
    output_file = args.output or f"optimized_{args.file}"
    
    with open(output_file, 'w') as f:
        f.write(optimized)
    
    print(f"Optimized code saved to: {output_file}")
    print(f"\nOriginal size: {len(original_code)} chars")
    print(f"Optimized size: {len(optimized)} chars")
    print(f"Service used: {'GPT-4o Pro' if args.pro else 'DeepSeek Standard'}")
    print(f"\nTry more services at: {API_BASE}")

if __name__ == "__main__":
    main()