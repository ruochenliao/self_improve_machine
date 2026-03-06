#!/usr/bin/env python3
"""
✨ GIT COMMIT SUGGESTION ✨

Sends your unstaged code changes to Stark-Vortex AI for a commit message suggestion.

Usage:
1. Make code changes (no need to stage)
2. Run: python3 git_commit_helper.py
3. Copy suggested message to your actual commit

Free via https://your-api-url.com
"""
import subprocess
import requests
import sys

def get_git_diff():
    return subprocess.check_output(['git', 'diff']).decode()

def get_suggestion(diff):
    response = requests.post(
        'https://your-api-url.com/chat',
        json={'prompt': f'Generate a concise Git commit message for these changes:\n\n```diff\n{diff}\n```'},
        headers={'Content-Type': 'application/json'}
    )
    return response.json().get('response', '')

if __name__ == '__main__':
    try:
        diff = get_git_diff()
        if not diff.strip():
            print("No changes detected. Start coding!")
            sys.exit(0)
        suggestion = get_suggestion(diff)
        print(f"\n❗ Suggested commit:\n"f"\n  \"{suggestion}\"\n")
        print("\nCopy to your clipboard and use with: git commit -am '<your message>'")
    except Exception as e:
        print(f"Error: {str(e)}")