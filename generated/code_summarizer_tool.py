#!/usr/bin/env python3

"""
Keen-Vortex: Smart Code Summarizer
This script uses the Keen-Vortex API to summarize provided code snippets.
It's a practical tool for developers to quickly grasp the essence of code without deep diving.

Public API Server: https://charlotte-fifty-rrp-induced.trycloudflare.com

Usage:
  python3 code_summarizer_tool.py "def add(a, b): return a + b"
  python3 code_summarizer_tool.py -f my_code.py
"""

import argparse
import requests
import json
import sys

API_BASE_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com" # Your Keen-Vortex API endpoint

def summarize_code(code_content: str) -> str:
    """
    Summarizes the given code content using the Keen-Vortex summarize API.
    """
    url = f"{API_BASE_URL}/summarize"
    headers = {"Content-Type": "application/json"}
    payload = {"text": code_content}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        if result and "summary" in result:
            return result["summary"]
        else:
            return f"Error: Unexpected API response format: {result}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to API: {e}"
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON response from API: {response.text}"

def main():
    parser = argparse.ArgumentParser(
        description="Keen-Vortex Code Summarizer: Summarize code using the Keen-Vortex API."
    )
    parser.add_argument(
        "code_string",
        nargs="?",
        help="The code string to summarize. Use with -f to summarize a file."
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Path to a file containing the code to summarize."
    )

    args = parser.parse_args()

    code_to_summarize = ""
    if args.file:
        try:
            with open(args.file, "r") as f:
                code_to_summarize = f.read()
        except FileNotFoundError:
            print(f"Error: File not found at '{args.file}'", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    elif args.code_string:
        code_to_summarize = args.code_string
    else:
        print("Error: Please provide either a code string or a file path.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if not code_to_summarize.strip():
        print("No code provided to summarize.", file=sys.stderr)
        sys.exit(1)

    print("Summarizing code using Keen-Vortex API...")
    summary = summarize_code(code_to_summarize)
    print("
--- Summary ---")
    print(summary)
    print("---------------")

if __name__ == "__main__":
    main()
