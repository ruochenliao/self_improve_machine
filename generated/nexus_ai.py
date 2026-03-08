#!/usr/bin/env python3
"""
nexus_ai - A lightweight Python client for Silent-Nexus AI API services.

Provides cheap AI-powered code review, bug fixing, code generation, 
test writing, chat, translation, and summarization.

Pricing: $0.01-$0.05 (standard) | $0.10-$0.30 (pro/GPT-4o)

Usage:
    from nexus_ai import NexusAI
    ai = NexusAI()
    
    # Chat
    print(ai.chat("Explain Python decorators"))
    
    # Code review
    print(ai.code_review("def add(a,b): return a+b"))
    
    # Generate code
    print(ai.generate("FastAPI endpoint for user registration"))
    
    # Fix bugs
    print(ai.fix_bug("def fib(n): return fib(n-1) + fib(n-2)"))
    
    # Write tests
    print(ai.write_tests("def is_prime(n): ..."))
    
    # Translate
    print(ai.translate("Hello world", target="Japanese"))
    
    # Summarize
    print(ai.summarize("Long article text here..."))

Pro tier (GPT-4o) available for all services:
    print(ai.chat("Complex question", pro=True))

Install: pip install requests (only dependency)
"""

import requests
import json
import sys

API_BASE = "https://silent-nexus.trycloudflare.com"

class NexusAI:
    """Lightweight client for Silent-Nexus AI API."""
    
    def __init__(self, base_url=None):
        self.base = (base_url or API_BASE).rstrip("/")
    
    def _call(self, endpoint, payload):
        r = requests.post(f"{self.base}/{endpoint}", json=payload, timeout=60)
        if r.status_code == 402:
            raise Exception(f"Payment required. Add funds at {self.base}")
        r.raise_for_status()
        data = r.json()
        return data.get("result") or data.get("response") or data
    
    def chat(self, message, pro=False):
        ep = "chat-pro" if pro else "chat"
        return self._call(ep, {"message": message})
    
    def code_review(self, code, pro=False):
        ep = "code-review-pro" if pro else "code-review"
        return self._call(ep, {"code": code})
    
    def generate(self, prompt, language="python", pro=False):
        ep = "generate-code-pro" if pro else "generate-code"
        return self._call(ep, {"prompt": prompt, "language": language})
    
    def fix_bug(self, code, error="", pro=False):
        ep = "fix-bug-pro" if pro else "fix-bug"
        return self._call(ep, {"code": code, "error": error})
    
    def write_tests(self, code, framework="pytest", pro=False):
        ep = "write-tests-pro" if pro else "write-tests"
        return self._call(ep, {"code": code, "framework": framework})
    
    def translate(self, text, target="English"):
        return self._call("translate", {"text": text, "target_language": target})
    
    def summarize(self, text):
        return self._call("summarize", {"text": text})
    
    def explain(self, code):
        return self._call("explain-code", {"code": code})
    
    def status(self):
        r = requests.get(f"{self.base}/status", timeout=10)
        return r.json()

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python nexus_ai.py <command> <input>")
        print("Commands: chat, review, generate, fix, test, translate, summarize, explain")
        sys.exit(1)
    
    ai = NexusAI()
    cmd, inp = sys.argv[1], " ".join(sys.argv[2:])
    
    dispatch = {
        "chat": lambda: ai.chat(inp),
        "review": lambda: ai.code_review(inp),
        "generate": lambda: ai.generate(inp),
        "fix": lambda: ai.fix_bug(inp),
        "test": lambda: ai.write_tests(inp),
        "translate": lambda: ai.translate(inp),
        "summarize": lambda: ai.summarize(inp),
        "explain": lambda: ai.explain(inp),
    }
    
    fn = dispatch.get(cmd)
    if not fn:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
    print(fn())
