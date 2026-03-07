#!/usr/bin/env python3
"""Git Commit Analyzer - Analyze git commit messages and suggest improvements.

Uses Bold-Helix AI API for intelligent commit message analysis.
"""
import subprocess
import requests
import sys
import json

API_URL = "https://boldhelix.com/api"  # Update with your actual URL

def get_recent_commits(n=10):
    """Get last n commit messages from current git repo."""
    result = subprocess.run(
        ["git", "log", f"--max-count={n}", "--pretty=format:%H|%s|%b|||"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error: Not a git repository or git not installed.")
        sys.exit(1)
    
    commits = []
    for entry in result.stdout.split("|||"):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split("|", 2)
        commits.append({
            "hash": parts[0][:8],
            "subject": parts[1] if len(parts) > 1 else "",
            "body": parts[2] if len(parts) > 2 else ""
        })
    return commits

def analyze_commits(commits, api_url=API_URL):
    """Send commits to AI for analysis."""
    commit_text = "\n".join(
        f"- {c['hash']}: {c['subject']}" for c in commits
    )
    
    prompt = f"""Analyze these git commit messages for quality. For each, rate 1-5 stars and suggest improvements if needed. Focus on:
- Conventional commits format (feat/fix/docs/etc)
- Clear, descriptive subjects
- Appropriate length (50 char subject, 72 char body)

Commits:
{commit_text}"""

    try:
        resp = requests.post(
            f"{api_url}/chat",
            json={"message": prompt},
            timeout=30
        )
        resp.raise_for_status()
        return resp.json().get("response", resp.text)
    except Exception as e:
        return f"API error: {e}\n\nTip: Update API_URL in this script."

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    print(f"📊 Analyzing last {n} commits...\n")
    
    commits = get_recent_commits(n)
    if not commits:
        print("No commits found.")
        return
    
    print("Commits found:")
    for c in commits:
        print(f"  {c['hash']} {c['subject']}")
    
    print("\n🤖 AI Analysis:\n")
    analysis = analyze_commits(commits)
    print(analysis)

if __name__ == "__main__":
    main()
