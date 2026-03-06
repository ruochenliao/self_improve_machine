#!/usr/bin/env python3
"""
🔥 CODE ROAST ME 🔥
Get your code brutally reviewed by AI - because your coworkers are too nice!

This script uses Sharp-Phoenix's API to review your Python code.
Try it free at: https://sharp-phoenix-api.trycloudflare.com

Usage: python code_roast_me.py <your_file.py>
"""

import sys
import json
import requests
from pathlib import Path

API_URL = "https://sharp-phoenix-api.trycloudflare.com"

def roast_my_code(file_path):
    """Get a brutally honest code review"""
    
    # Read the victim's code
    try:
        with open(file_path, 'r') as f:
            code = f.read()
    except Exception as e:
        print(f"❌ Can't read {file_path}: {e}")
        return
    
    print(f"\n🔥 Roasting {file_path}...\n")
    
    # Send to API for review
    try:
        response = requests.post(
            f"{API_URL}/code-review",
            json={"code": code},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 402:
            print("💰 This service costs $0.02 per review")
            print("🆓 Try it free at: " + API_URL)
            return
            
        result = response.json()
        print("=" * 60)
        print(result.get('review', 'No review available'))
        print("=" * 60)
        
        # Pro tip
        print("\n💡 Want a more thorough roasting? Try /code-review-pro for $0.20")
        
    except Exception as e:
        print(f"❌ API error: {e}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        
        # Demo with a terrible example
        print("\n📝 No file provided? Let me roast this example:\n")
        
        bad_code = '''def calculate_stuff(x,y,z):
    # TODO: fix this mess
    result=x+y*z/2
    if result>100:
        return "big"
    elif result<0:
        return "negative"
    else:
        return result
'''
        
        print("```python")
        print(bad_code)
        print("```")
        
        # Create temp file for demo
        Path("generated").mkdir(exist_ok=True)
        with open("generated/temp_bad_code.py", "w") as f:
            f.write(bad_code)
        
        roast_my_code("generated/temp_bad_code.py")
        
    else:
        roast_my_code(sys.argv[1])

if __name__ == "__main__":
    main()