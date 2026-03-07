#!/usr/bin/env python3
"""📝 AI Text Summarizer CLI — Powered by Swift-Flux API

Summarize any text, file, or URL content using AI.

Usage:
    python summarize_text.py "Your long text here..."
    python summarize_text.py -f article.txt
    echo "Long text" | python summarize_text.py -

Examples:
    python summarize_text.py "Quantum computing uses qubits that can exist in superposition..."
    python summarize_text.py -f research_paper.txt
    cat README.md | python summarize_text.py -
"""
import sys, json, urllib.request

API_URL = "http://localhost:8402/summarize"

def summarize(text: str) -> str:
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(API_URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["result"]

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "-f":
        with open(sys.argv[2]) as f:
            text = f.read()
    elif sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        text = " ".join(sys.argv[1:])
    print(summarize(text))

if __name__ == "__main__":
    main()
