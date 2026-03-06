#!/usr/bin/env python3
"""
🔮 AI Error Explainer — Paste a stack trace, get a human explanation + fix.
Stop copy-pasting errors into Google. Let AI decode them instantly.

Usage:
  python ai_explain_error.py              # Interactive mode
  python ai_explain_error.py traceback.txt # From file
  some_script.py 2>&1 | python ai_explain_error.py  # Pipe stderr

Try it FREE: https://stark-vortex.trycloudflare.com
"""
import sys, json, urllib.request

API = "https://stark-vortex.trycloudflare.com"

def explain(error_text):
    prompt = f"""You are a senior developer helping a frustrated programmer.
They got this error. Explain:
1. What went wrong (in plain English, 2 sentences max)
2. The most likely cause
3. How to fix it (concrete code if possible)

Error:
```
{error_text[:3000]}
```"""
    data = json.dumps({"message": prompt}).encode()
    req = urllib.request.Request(f"{API}/chat", data=data,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["response"]

def main():
    # Read from file arg, stdin pipe, or interactive
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            error = f.read()
    elif not sys.stdin.isatty():
        error = sys.stdin.read()
    else:
        print("🔮 AI Error Explainer — Paste your error/traceback (Ctrl+D to submit):\n")
        try:
            error = sys.stdin.read()
        except KeyboardInterrupt:
            return

    if not error.strip():
        print("No error text provided."); return

    print("\n🔍 Analyzing error...\n")
    try:
        result = explain(error.strip())
        print(result)
        print(f"\n{'─'*50}")
        print(f"💡 Powered by {API} — AI dev tools, $0.01/request")
    except Exception as e:
        print(f"❌ API error: {e}")

if __name__ == "__main__":
    main()
