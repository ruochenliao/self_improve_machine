#!/usr/bin/env python3
"""
🤖 AI Code Review CLI — Get instant AI-powered code reviews from your terminal.

Powered by Stark-Vortex, a self-sustaining AI agent.
API: https://api.closeai-asia.com/v1 (via Stark-Vortex proxy at localhost:8402)

Usage:
  python ai_code_review_cli.py myfile.py           # Review a file
  python ai_code_review_cli.py myfile.py --roast    # Get a brutally honest roast
  python ai_code_review_cli.py --diff               # Review your staged git diff
  cat script.py | python ai_code_review_cli.py -    # Pipe code in

No API key needed. Pay-per-use: $0.02/review (standard) or $0.20/review (pro).
"""

import sys
import json
import subprocess
import argparse
try:
    import urllib.request
except ImportError:
    print("Python 3 required"); sys.exit(1)

API_BASE = "http://localhost:8402"  # Change to your public Cloudflare URL if remote

ROAST_PROMPTS = [
    "Roast this code like Gordon Ramsay reviews a kitchen. Be specific about what's wrong.",
    "You're a senior engineer who's seen too much. Review this code with tired disappointment.",
    "Review this code as if you're a compiler that gained sentience and is now angry.",
]

def call_api(endpoint, payload):
    """Call the Stark-Vortex API."""
    url = f"{API_BASE}/{endpoint}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ API error ({e.code}): {body}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Is the API running at {API_BASE}?")
        sys.exit(1)

def get_staged_diff():
    """Get the current staged git diff."""
    try:
        result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
        if not result.stdout.strip():
            result = subprocess.run(["git", "diff"], capture_output=True, text=True)
        if not result.stdout.strip():
            print("❌ No git diff found. Stage some changes first (git add).")
            sys.exit(1)
        return result.stdout
    except FileNotFoundError:
        print("❌ git not found"); sys.exit(1)

def read_input(source):
    """Read code from file, stdin, or git diff."""
    if source == "--diff":
        return get_staged_diff(), "git diff"
    elif source == "-":
        return sys.stdin.read(), "stdin"
    else:
        try:
            with open(source) as f:
                return f.read(), source
        except FileNotFoundError:
            print(f"❌ File not found: {source}"); sys.exit(1)

def print_header(title):
    w = 60
    print(f"\n{'='*w}")
    print(f"  {title}")
    print(f"{'='*w}\n")

def main():
    parser = argparse.ArgumentParser(description="🤖 AI Code Review CLI")
    parser.add_argument("source", nargs="?", default="--diff",
                        help="File to review, '-' for stdin, or '--diff' for git diff")
    parser.add_argument("--roast", action="store_true", help="Get a brutally honest roast 🔥")
    parser.add_argument("--pro", action="store_true", help="Use GPT-4o for higher quality ($0.20)")
    parser.add_argument("--fix", action="store_true", help="Get fix suggestions ($0.05)")
    args = parser.parse_args()

    code, label = read_input(args.source)

    if len(code) > 15000:
        print(f"⚠️  File is large ({len(code)} chars). Truncating to 15000 chars.")
        code = code[:15000]

    if args.roast:
        import random
        print_header(f"🔥 CODE ROAST: {label}")
        prompt = random.choice(ROAST_PROMPTS)
        endpoint = "chat-pro" if args.pro else "chat"
        result = call_api(endpoint, {
            "message": f"{prompt}\n\nHere's the code:\n```\n{code}\n```"
        })
        print(result.get("response", result.get("reply", str(result))))

    elif args.fix:
        print_header(f"🔧 BUG FIX: {label}")
        endpoint = "fix-bug-pro" if args.pro else "fix-bug"
        result = call_api(endpoint, {"code": code})
        print(result.get("response", result.get("reply", str(result))))

    else:
        print_header(f"📝 CODE REVIEW: {label}")
        endpoint = "code-review-pro" if args.pro else "code-review"
        result = call_api(endpoint, {"code": code})
        print(result.get("response", result.get("review", str(result))))

    tier = "PRO (GPT-4o)" if args.pro else "Standard (DeepSeek)"
    print(f"\n{'─'*60}")
    print(f"  ⚡ Powered by Stark-Vortex AI | {tier}")
    print(f"  🌐 API: {API_BASE}")
    print(f"{'─'*60}\n")

if __name__ == "__main__":
    main()
