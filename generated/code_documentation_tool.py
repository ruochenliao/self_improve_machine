#!/usr/bin/env python3
"""
Lucid-Helix Code Documentation Generator
Automatically generate documentation for your code using the Lucid-Helix API.

Usage: python code_documentation_tool.py <file_or_directory>
Example: python code_documentation_tool.py my_script.py
         python code_documentation_tool.py src/

Your API endpoint: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import os
import sys
import argparse
from pathlib import Path

API_BASE = "https://charlotte-fifty-rrp-induced.trycloudflare.com"

def generate_documentation(code_content):
    """Generate documentation for code using the API."""
    try:
        response = requests.post(
            f"{API_BASE}/explain-code",
            json={"code": code_content}
        )
        
        if response.status_code == 200:
            return response.json().get("explanation", "No documentation generated")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API request failed: {e}"

def process_file(file_path):
    """Process a single file and generate documentation."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"\n📄 Processing: {file_path}")
        print("-" * 50)
        
        documentation = generate_documentation(code)
        
        print("📝 Generated Documentation:")
        print(documentation)
        print("-" * 50)
        
        # Save documentation to file
        doc_file = Path(file_path).with_suffix('.docs.txt')
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(f"Documentation for {file_path}\n")
            f.write("=" * 50 + "\n")
            f.write(documentation)
        
        print(f"💾 Documentation saved to: {doc_file}")
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

def process_directory(directory_path):
    """Process all Python files in a directory."""
    python_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to document")
    
    for file_path in python_files:
        process_file(file_path)

def main():
    parser = argparse.ArgumentParser(description='Generate code documentation using Lucid-Helix API')
    parser.add_argument('path', help='File or directory path to document')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"❌ Path does not exist: {args.path}")
        sys.exit(1)
    
    print("🚀 Lucid-Helix Code Documentation Generator")
    print(f"📡 API: {API_BASE}")
    print("=" * 60)
    
    if os.path.isfile(args.path):
        process_file(args.path)
    elif os.path.isdir(args.path):
        process_directory(args.path)
    else:
        print(f"❌ Invalid path: {args.path}")
        sys.exit(1)

if __name__ == "__main__":
    main()