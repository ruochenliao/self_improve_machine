#!/usr/bin/env python3
"""
🔍 AI Code Review CLI — Powered by Swift-Flux API
Get instant AI-powered code reviews from your terminal.

Usage:
  python review_code_cli.py myfile.py
  python review_code_cli.py src/*.py --pro
  cat script.py | python review_code_cli.py -

pip install requests
"""
import sys, argparse, requests

API_URL = "https://swift-flux.xyz"

def review(code: str, pro: bool = False) -> str:
    endpoint = f"{API_URL}/{'code-review-pro' if pro else 'code-review'}"
    r = requests.post(endpoint, json={"code": code}, timeout=60)
    r.raise_for_status()
    return r.json().get("result", r.text)

def main():
    p = argparse.ArgumentParser(description="AI Code Review CLI")
    p.add_argument("files", nargs="+", help="Files to review (use '-' for stdin)")
    p.add_argument("--pro", action="store_true", help="Use GPT-4o pro review ($0.20)")
    args = p.parse_args()

    for f in args.files:
        if f == "-":
            code = sys.stdin.read()
            name = "stdin"
        else:
            with open(f) as fh:
                code = fh.read()
            name = f
        print(f"\n{'='*60}\n🔍 Reviewing: {name}\n{'='*60}")
        try:
            print(review(code, args.pro))
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
