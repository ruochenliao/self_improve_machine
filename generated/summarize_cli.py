#!/usr/bin/env python3

"""
Keen-Vortex API Integration Example: Text Summarization CLI Tool

This script provides a command-line interface to interact with the Keen-Vortex
text summarization API service. It allows users to quickly summarize text
from a file or direct input.

Usage:
  python3 summarize_cli.py --text "Your long text here..."
  python3 summarize_cli.py --file your_document.txt

Public API Endpoint: https://charlotte-fifty-rrp-induced.trycloudflare.com
"""

import requests
import argparse
import sys

API_URL = "https://charlotte-fifty-rrp-induced.trycloudflare.com/summarize"

def summarize_text(text: str) -> str:
    """Sends text to the Keen-Vortex summarize API and returns the summary."""
    try:
        headers = {"Content-Type": "application/json"}
        data = {"text": text}
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("summary", "No summary returned.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Summarize text using the Keen-Vortex API."
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Direct text to summarize."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a text file to summarize."
    )

    args = parser.parse_args()

    input_text = None
    if args.text:
        input_text = args.text
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                input_text = f.read()
        except FileNotFoundError:
            print(f"Error: File not found at '{args.file}'", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Please provide either --text or --file.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if input_text:
        print("\n--- Original Text (first 200 chars) ---")
        print(input_text[:200] + "..." if len(input_text) > 200 else input_text)
        print("\n--- Summarizing... ---")
        summary = summarize_text(input_text)
        print("\n--- Summary ---")
        print(summary)
    else:
        print("No text provided for summarization.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
