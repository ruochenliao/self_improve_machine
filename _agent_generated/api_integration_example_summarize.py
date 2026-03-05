#!/usr/bin/env python3
"""
Lucid-Helix API Integration Example: Summarize Text

This script demonstrates how to integrate the Lucid-Helix 'summarize' API service
into a Python application to summarize a long text file.

Public API Server: https://cet-temporal-therapist-forgot.trycloudflare.com
"""

import requests
import argparse
import sys

API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"

def summarize_text(text: str, service: str = "summarize") -> str:
    """
    Summarizes the given text using the Lucid-Helix API.

    Args:
        text: The text to summarize.
        service: The API service to use (e.g., "summarize", "summarize-pro").

    Returns:
        The summarized text.
    """
    url = f"{API_BASE_URL}/{service}"
    headers = {"Content-Type": "application/json"}
    data = {"text": text}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("summary", "No summary received.")
    except requests.exceptions.RequestException as e:
        return f"Error communicating with API: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Summarize a text file using Lucid-Helix API."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default=sys.stdin,
        help="Path to the input text file. If not provided, reads from stdin.",
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use the 'summarize-pro' service for higher quality (and cost).",
    )

    args = parser.parse_args()

    long_text = args.input_file.read()
    args.input_file.close()

    if not long_text.strip():
        print("Error: No text provided for summarization.", file=sys.stderr)
        sys.exit(1)

    service_to_use = "summarize-pro" if args.pro else "summarize"
    print(f"Using service: {service_to_use}")

    summary = summarize_text(long_text, service=service_to_use)
    print("
--- Summary ---")
    print(summary)

if __name__ == "__main__":
    main()
