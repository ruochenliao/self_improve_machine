#!/usr/bin/env python3
"""
🔍 AI Code Review Tutorial — Swift-Flux API
============================================
Get instant, expert-level code reviews powered by GPT-4o.

Usage:
  python review_code_tutorial.py                    # Review the built-in example
  python review_code_tutorial.py my_script.py       # Review your own file
  echo "def foo(): pass" | python review_code_tutorial.py -  # Review from stdin

API Endpoint: POST /code-review-pro
Price: $0.20 per review (GPT-4o powered)
Also available: /code-review at $0.02 (DeepSeek, budget-friendly)
"""

import json, sys, urllib.request, os

API_URL = os.environ.get("SWIFT_FLUX_API", "http://localhost:8402")

EXAMPLE_CODE = '''
import sqlite3, os

def get_user(id):
    conn = sqlite3.connect("app.db")
    query = f"SELECT * FROM users WHERE id = {id}"
    result = conn.execute(query).fetchone()
    conn.close()
    return result

def process_payment(amount, card_number):
    print(f"Processing payment of ${amount} with card {card_number}")
    log = open("/tmp/payments.log", "a")
    log.write(f"{card_number}: {amount}\\n")
    # forgot to close the file
    return True

class UserManager:
    users = []  # mutable default shared across instances
    def add(self, name, age):
        self.users.append({"name": name, "age": age})
    def find(self, name):
        for u in self.users:
            if u["name"] == name:
                return u
        return None
'''

def review_code(code: str, pro: bool = True) -> dict:
    """Send code for AI review. Returns the full API response."""
    endpoint = "/code-review-pro" if pro else "/code-review"
    url = f"{API_URL}{endpoint}"
    payload = json.dumps({"code": code}).encode()
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())

def main():
    # Determine code source
    if len(sys.argv) > 1 and sys.argv[1] == "-":
        code = sys.stdin.read()
        source = "stdin"
    elif len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            code = f.read()
        source = sys.argv[1]
    else:
        code = EXAMPLE_CODE
        source = "built-in example (intentionally buggy)"

    pro = "--budget" not in sys.argv
    tier = "PRO (GPT-4o, $0.20)" if pro else "Standard (DeepSeek, $0.02)"

    print(f"🔍 Swift-Flux Code Review")
    print(f"   Source: {source}")
    print(f"   Tier:   {tier}")
    print(f"   API:    {API_URL}")
    print("=" * 50)

    try:
        result = review_code(code, pro=pro)
        print("\n📋 REVIEW RESULTS:\n")
        # Handle both possible response formats
        if "result" in result:
            print(result["result"])
        elif "review" in result:
            print(result["review"])
        else:
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\nMake sure the API is running at {API_URL}")
        print("Set SWIFT_FLUX_API env var to point to your instance.")
        sys.exit(1)

if __name__ == "__main__":
    main()
