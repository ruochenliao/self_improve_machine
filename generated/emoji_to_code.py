#!/usr/bin/env python3
"""
⚔ EMOJI TO CODE ⚔
Turn emojis into code snippets using AI!

Usage: python emoji_to_code.py 🚀

Replace 🚀 with any of these:
	🚀 - Startup template
	📊 - Data viz
	🔒 - Security check
	🔍 - Code search

Uses: https://<your-public-url>/generate-code
"""
import sys
import requests

API_URL = "http://localhost:8402/generate-code"

emoji_map = {
	'🚀': 'Write a Python FastAPI startup template with Dockerfile',
	'📊': 'Generate Matplotlib code to plot sample sales data',
	'🔒': 'Create a function to validate secure password requirements',
	'🔍': 'Write a script to search for TODO comments in a codebase'
}

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print("Usage: python emoji_to_code.py [emoji]")
		sys.exit(1)

	emoji = sys.argv[1]
	if emoji not in emoji_map:
		print(f"Unsupported emoji. Try {list(emoji_map.keys())}")
		sys.exit(1)

	response = requests.post(API_URL, json={"prompt": emoji_map[emoji], "temperature":0.7})
	print("Generated code:\n", response.json().get('code', 'Failed to generate'))