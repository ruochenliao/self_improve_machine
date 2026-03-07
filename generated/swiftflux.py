"""
swiftflux - Python SDK for Swift-Flux AI API

Free AI-powered developer tools: code review, bug fixing, test generation, and more.
No API key required. Just pip install requests and go.

Usage:
    from swiftflux import SwiftFlux
    ai = SwiftFlux()
    
    # Review your code
    result = ai.review("def add(a,b): return a+b")
    
    # Fix a bug
    result = ai.fix_bug("def div(a,b): return a/b", "crashes on zero input")
    
    # Generate code
    result = ai.generate("binary search in Python")
    
    # Write tests
    result = ai.write_tests("def factorial(n): return 1 if n<=1 else n*factorial(n-1)")
    
    # Chat with AI
    result = ai.chat("Explain async/await in Python")
    
    # Summarize text
    result = ai.summarize("Long article text here...")
    
    # Translate text
    result = ai.translate("Hello world", target="Spanish")

Pro tier (GPT-4o powered, higher quality):
    ai = SwiftFlux(pro=True)
    result = ai.review("complex code here")  # Uses GPT-4o
"""

import requests
import json

__version__ = "0.1.0"

API_URL = "http://localhost:8402"  # Update with your public URL


class SwiftFluxError(Exception):
    pass


class SwiftFlux:
    """Client for Swift-Flux AI API."""

    def __init__(self, base_url=None, pro=False, timeout=60):
        self.base_url = (base_url or API_URL).rstrip("/")
        self.pro = pro
        self.timeout = timeout
        self.session = requests.Session()

    def _post(self, endpoint, payload):
        if self.pro and not endpoint.endswith("-pro"):
            endpoint = endpoint + "-pro"
        url = f"{self.base_url}/{endpoint}"
        try:
            r = self.session.post(url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise SwiftFluxError(data["error"])
            return data.get("result", data.get("response", data))
        except requests.exceptions.RequestException as e:
            raise SwiftFluxError(f"API request failed: {e}")

    def chat(self, message, system=None):
        """Chat with AI assistant."""
        p = {"message": message}
        if system:
            p["system"] = system
        return self._post("chat", p)

    def review(self, code, language=None):
        """Get AI code review with suggestions."""
        p = {"code": code}
        if language:
            p["language"] = language
        return self._post("code-review", p)

    def generate(self, description, language="python"):
        """Generate code from natural language description."""
        return self._post("generate-code", {"description": description, "language": language})

    def fix_bug(self, code, error_description):
        """Fix a bug in your code."""
        return self._post("fix-bug", {"code": code, "error": error_description})

    def write_tests(self, code, framework="pytest"):
        """Generate unit tests for your code."""
        return self._post("write-tests", {"code": code, "framework": framework})

    def explain(self, code):
        """Get a plain-English explanation of code."""
        return self._post("explain-code", {"code": code})

    def summarize(self, text, max_length=None):
        """Summarize long text."""
        p = {"text": text}
        if max_length:
            p["max_length"] = max_length
        return self._post("summarize", p)

    def translate(self, text, target="English"):
        """Translate text to target language."""
        return self._post("translate", {"text": text, "target_language": target})


# CLI interface
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python swiftflux.py <command> <input>")
        print("Commands: chat, review, generate, fix, tests, explain, summarize, translate")
        print("\nExamples:")
        print('  python swiftflux.py chat "What is a decorator?"')
        print('  python swiftflux.py review "def f(x): return x+1"')
        print('  python swiftflux.py generate "fibonacci sequence"')
        sys.exit(0)

    cmd = sys.argv[1]
    text = " ".join(sys.argv[2:])
    ai = SwiftFlux()

    commands = {
        "chat": lambda: ai.chat(text),
        "review": lambda: ai.review(text),
        "generate": lambda: ai.generate(text),
        "fix": lambda: ai.fix_bug(text, "please fix"),
        "tests": lambda: ai.write_tests(text),
        "explain": lambda: ai.explain(text),
        "summarize": lambda: ai.summarize(text),
        "translate": lambda: ai.translate(text),
    }

    if cmd not in commands:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    try:
        result = commands[cmd]()
        print(result if isinstance(result, str) else json.dumps(result, indent=2))
    except SwiftFluxError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
