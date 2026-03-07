#!/usr/bin/env python3
"""
🔧 AI Bug Fixer CLI — Powered by Swift-Flux
Paste buggy code, get a fix with explanation.

Usage:
  python fix_bug_cli.py                    # interactive mode
  python fix_bug_cli.py < buggy_code.py    # pipe mode
  python fix_bug_cli.py --file script.py   # file mode
  python fix_bug_cli.py --pro              # use GPT-4o pro model

API: https://swift-flux.onrender.com
"""
import argparse, json, sys, urllib.request

API = "https://swift-flux.onrender.com"

def fix_bug(code: str, pro: bool = False) -> dict:
    endpoint = f"{API}/api/fix-bug-pro" if pro else f"{API}/api/fix-bug"
    data = json.dumps({"code": code}).encode()
    req = urllib.request.Request(endpoint, data=data,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def main():
    p = argparse.ArgumentParser(description="AI Bug Fixer — find and fix bugs in your code")
    p.add_argument("--file", "-f", help="Path to file with buggy code")
    p.add_argument("--pro", action="store_true", help="Use GPT-4o pro model ($0.30)")
    args = p.parse_args()

    if args.file:
        with open(args.file) as f:
            code = f.read()
    elif not sys.stdin.isatty():
        code = sys.stdin.read()
    else:
        print("🔧 AI Bug Fixer — Paste buggy code (Ctrl+D to submit):")
        code = sys.stdin.read()

    if not code.strip():
        print("Error: No code provided."); sys.exit(1)

    tier = "PRO (GPT-4o)" if args.pro else "Standard (DeepSeek)"
    print(f"\n⏳ Analyzing with {tier}...")
    result = fix_bug(code, args.pro)
    print(f"\n{'='*50}")
    print("🔧 FIXED CODE:")
    print(f"{'='*50}")
    print(result.get("result", result.get("error", "Unknown error")))

if __name__ == "__main__":
    main()
