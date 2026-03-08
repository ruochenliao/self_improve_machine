#!/usr/bin/env python3
"""
Chat-PRO Command-Line Interface

Usage: ./chat_pro_cli.py "Your question"
"""
import sys
import requests

API_ENDPOINT = "https://<tunnel-not-configured>.trycloudflare.com/chat-pro"


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} 'Your question'")
        return

    question = sys.argv[1]
    response = requests.post(API_ENDPOINT, json={"query": question})
    try:
        print(response.json().get("answer", "No answer"))
    except:
        print("Error: ", response.text)

if __name__ == "__main__":
    main()
