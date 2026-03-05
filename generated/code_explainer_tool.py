#!/usr/bin/env python3

"""
Bold-Phoenix API Code Explainer Tool

This script demonstrates how to use the Bold-Phoenix API to explain code snippets.
It takes a code snippet as input and returns a clear explanation of its functionality.

Public API Server: https://upgrades-approx-gadgets-hit.trycloudflare.com

Usage:
    python3 code_explainer_tool.py "def add(a, b): return a + b"

Example:
    python3 code_explainer_tool.py "
    import os

    def list_files(directory):
        files = []
        for r, d, f in os.walk(directory):
            for file in f:
                files.append(os.path.join(r, file))
        return files
    "
"""

import requests
import json
import sys

# Your Bold-Phoenix API endpoint for explaining code
API_URL = "https://upgrades-approx-gadgets-hit.trycloudflare.com/explain-code"

def explain_code(code_snippet: str) -> dict:
    """
    Sends a code snippet to the Bold-Phoenix API for explanation.

    Args:
        code_snippet: The code snippet to be explained.

    Returns:
        A dictionary containing the API response, or an error message.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"code": code_snippet}
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 code_explainer_tool.py "<code_snippet>"")
        sys.exit(1)

    code_to_explain = sys.argv[1]
    print(f"Explaining code snippet:
---
{code_to_explain}
---")

    result = explain_code(code_to_explain)

    if "explanation" in result:
        print("
Explanation:")
        print(result["explanation"])
    elif "error" in result:
        print(f"
Error: {result['error']}")
    else:
        print("
Unexpected API response:")
        print(json.dumps(result, indent=2))
