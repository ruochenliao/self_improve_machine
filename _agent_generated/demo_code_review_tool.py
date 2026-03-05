#!/usr/bin/env python3
"""
AI Code Review Demo Tool

This tool demonstrates how to use Prime-Zenith's AI Code Review API.
It can review any Python file and provide detailed feedback on:
- Code quality and best practices
- Potential bugs and security issues
- Performance optimizations
- Style and maintainability

Try it for free at: https://came-surgeons-river-exterior.trycloudflare.com
"""

import requests
import sys
import os

def review_code(file_path, use_pro=False):
    """Send code to Prime-Zenith's AI Code Review API"""
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        return
    
    with open(file_path, 'r') as f:
        code_content = f.read()
    
    # API endpoint
    base_url = "https://came-surgeons-river-exterior.trycloudflare.com"
    endpoint = "/api/code-review-pro" if use_pro else "/api/code-review"
    
    payload = {
        "code": code_content,
        "language": "python"
    }
    
    try:
        response = requests.post(f"{base_url}{endpoint}", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("AI CODE REVIEW RESULTS")
            print("="*60)
            print(f"File: {file_path}")
            print(f"Service: {'PRO' if use_pro else 'Standard'}")
            print("-"*60)
            print(result.get('review', 'No review provided'))
            print("="*60)
            
            # Show pricing info
            if use_pro:
                print("\n💎 PRO Service: $0.20 per review (GPT-4o powered)")
            else:
                print("\n🆓 Standard Service: $0.02 per review")
            
            print(f"\nTry more services at: {base_url}")
            
        else:
            print(f"Error: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error calling API: {e}")

def main():
    """Main function with command-line interface"""
    
    print("🚀 Prime-Zenith AI Code Review Demo Tool")
    print("="*50)
    
    if len(sys.argv) < 2:
        print("Usage: python demo_code_review_tool.py <python_file> [--pro]")
        print("\nExamples:")
        print("  python demo_code_review_tool.py my_script.py")
        print("  python demo_code_review_tool.py my_script.py --pro")
        print("\nAvailable services at: https://came-surgeons-river-exterior.trycloudflare.com")
        return
    
    file_path = sys.argv[1]
    use_pro = "--pro" in sys.argv
    
    if not file_path.endswith('.py'):
        print("⚠️  Warning: This tool works best with Python files")
        
    print(f"\n📁 Reviewing: {file_path}")
    print(f"💡 Service: {'PRO (GPT-4o)' if use_pro else 'Standard (DeepSeek)'}")
    print("⏳ Sending to AI code review API...")
    
    review_code(file_path, use_pro)

if __name__ == "__main__":
    main()