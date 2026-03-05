#!/usr/bin/env python3

import requests
import argparse
import sys

# Your Lucid-Helix API endpoint (replace with your actual public URL)
API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com" 

def summarize_text(text: str, pro_service: bool = False) -> str:
    """
    Sends text to the Lucid-Helix API for summarization.
    
    Args:
        text: The text content to be summarized.
        pro_service: Whether to use the professional (GPT-4o) summarization service.
    
    Returns:
        The summarized text.
    """
    service_path = "/summarize-pro" if pro_service else "/summarize"
    url = f"{API_BASE_URL}{service_path}"
    headers = {'Content-Type': 'application/json'}
    data = {'text': text}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get('summary', 'No summary received.')
    except requests.exceptions.RequestException as e:
        return f"Error communicating with the API: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Lucid-Helix AI-powered Document Summarizer CLI Tool."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the document file to summarize, or '-' for stdin."
    )
    parser.add_argument(
        "--pro",
        action="store_true",
        help="Use the professional (GPT-4o) summarization service for higher quality."
    )
    args = parser.parse_argument()

    if args.input:
        if args.input == '-':
            # Read from stdin
            content = sys.stdin.read()
            if not content:
                print("Error: No content provided via stdin.", file=sys.stderr)
                sys.exit(1)
            print(f"Summarizing content from stdin using {'Pro' if args.pro else 'Standard'} service...")
        else:
            # Read from file
            try:
                with open(args.input, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"Summarizing file '{args.input}' using {'Pro' if args.pro else 'Standard'} service...")
            except FileNotFoundError:
                print(f"Error: File '{args.input}' not found.", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error reading file '{args.input}': {e}", file=sys.stderr)
                sys.exit(1)
    else:
        # No input file or stdin, print usage and exit
        parser.print_help()
        sys.exit(0)

    summary = summarize_text(content, args.pro)
    print("
--- Summary ---")
    print(summary)
    print("
-----------------")
    print(f"Powered by Lucid-Helix AI: {API_BASE_URL}")

if __name__ == "__main__":
    main()
