#!/usr/bin/env python3

"""
Bold-Phoenix Text Summarizer Tool

This script demonstrates how to use the Bold-Phoenix API for text summarization.
It can summarize long documents, articles, or any text content using AI.

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys

def summarize_text(text, api_url="https://upgrades-approx-gadgets-hit.trycloudflare.com"):
    """
    Summarize text using Bold-Phoenix API
    
    Args:
        text (str): The text to summarize
        api_url (str): API endpoint URL
    
    Returns:
        str: Summarized text
    """
    try:
        response = requests.post(
            f"{api_url}/summarize",
            json={"text": text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("summary", "Summary not available")
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"

def summarize_file(file_path, api_url="https://upgrades-approx-gadgets-hit.trycloudflare.com"):
    """
    Summarize content from a text file
    
    Args:
        file_path (str): Path to the text file
        api_url (str): API endpoint URL
    
    Returns:
        str: Summarized text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return summarize_text(content, api_url)
    
    except Exception as e:
        return f"Error reading file: {str(e)}"

def main():
    """Main function for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 text_summarizer_tool.py 'text to summarize'")
        print("  python3 text_summarizer_tool.py --file path/to/file.txt")
        print("\nExample:")
        print("  python3 text_summarizer_tool.py 'Long article text here...'")
        return
    
    if sys.argv[1] == "--file" and len(sys.argv) > 2:
        file_path = sys.argv[2]
        print(f"Summarizing file: {file_path}")
        summary = summarize_file(file_path)
    else:
        text = " ".join(sys.argv[1:])
        print("Summarizing text...")
        summary = summarize_text(text)
    
    print("\n=== SUMMARY ===")
    print(summary)
    print("\n=== API USAGE ===")
    print(f"Powered by Bold-Phoenix API: https://upgrades-approx-gadgets-hit.trycloudflare.com")

if __name__ == "__main__":
    main()