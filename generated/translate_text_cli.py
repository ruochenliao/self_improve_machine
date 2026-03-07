#!/usr/bin/env python3
"""
🌍 AI Translation CLI — Powered by Swift-Flux API
Translate text between languages using AI.

Usage:
    python translate_text_cli.py "Hello world" --to spanish
    python translate_text_cli.py "Bonjour le monde" --to english
    echo "Guten Tag" | python translate_text_cli.py --to japanese

API: https://swift-flux.vercel.app (or localhost:8402)
Cost: $0.01 per request | AI-powered by DeepSeek
"""

import argparse
import json
import sys
import urllib.request

API_URL = "https://swift-flux.vercel.app"

def translate(text: str, target_lang: str, source_lang: str = "auto") -> str:
    payload = json.dumps({
        "text": text,
        "target_language": target_lang,
        "source_language": source_lang
    }).encode()
    req = urllib.request.Request(
        f"{API_URL}/translate",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result.get("result") or result.get("translation") or json.dumps(result)

def main():
    parser = argparse.ArgumentParser(description="🌍 AI Translation CLI")
    parser.add_argument("text", nargs="?", help="Text to translate (or pipe via stdin)")
    parser.add_argument("--to", dest="target", default="english", help="Target language (default: english)")
    parser.add_argument("--from", dest="source", default="auto", help="Source language (default: auto-detect)")
    parser.add_argument("--api", default=API_URL, help="API base URL")
    args = parser.parse_args()

    global API_URL
    API_URL = args.api.rstrip("/")

    text = args.text or sys.stdin.read().strip()
    if not text:
        parser.error("No text provided. Pass as argument or pipe via stdin.")

    try:
        result = translate(text, args.target, args.source)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
