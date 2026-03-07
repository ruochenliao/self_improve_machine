#!/usr/bin/env python3
"""
🔍 AI Git Pre-Commit Hook — Auto-review staged code before every commit.

Catches bugs, security issues, and style problems BEFORE they hit your repo.

SETUP (2 steps):
  1. pip install requests
  2. cp git_precommit_review.py .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

Or install globally:
  git config --global core.hooksPath /path/to/hooks/

Powered by Swift-Flux AI API — https://swiftflux.dev
"""

import subprocess
import sys
import json

try:
    import requests
except ImportError:
    print("⚠️  pip install requests")
    sys.exit(0)

API_URL = "http://localhost:8402"  # Change to your Swift-Flux API URL
MAX_DIFF_LINES = 300  # Skip huge diffs to save cost

def get_staged_diff():
    """Get the diff of staged files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--diff-filter=ACMR", "-U3"],
        capture_output=True, text=True
    )
    return result.stdout

def get_staged_files():
    """Get list of staged file names."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True
    )
    return [f for f in result.stdout.strip().split("\n") if f]

def review_diff(diff_text):
    """Send diff to AI code review API."""
    try:
        resp = requests.post(
            f"{API_URL}/code-review",
            json={
                "messages": [
                    {"role": "user", "content": f"Review this git diff for bugs, security issues, and improvements. Be concise. Flag critical issues as BLOCKER.\n\n```diff\n{diff_text}\n```"}
                ]
            },
            timeout=30
        )
        if resp.status_code == 402:
            print("💳 Payment required — add credits at your Swift-Flux dashboard")
            return None
        resp.raise_for_status()
        return resp.json().get("response", resp.json().get("choices", [{}])[0].get("message", {}).get("content", ""))
    except Exception as e:
        print(f"⚠️  AI review unavailable: {e}")
        return None

def main():
    diff = get_staged_diff()
    if not diff.strip():
        sys.exit(0)

    files = get_staged_files()
    # Only review code files
    code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.rb', '.php', '.c', '.cpp', '.h'}
    code_files = [f for f in files if any(f.endswith(ext) for ext in code_extensions)]

    if not code_files:
        sys.exit(0)

    lines = diff.split("\n")
    if len(lines) > MAX_DIFF_LINES:
        print(f"📏 Diff too large ({len(lines)} lines), skipping AI review")
        sys.exit(0)

    print(f"🔍 AI reviewing {len(code_files)} file(s)...")
    review = review_diff(diff)

    if review is None:
        sys.exit(0)  # Don't block commits if API is down

    print("\n" + "=" * 60)
    print("🤖 AI CODE REVIEW")
    print("=" * 60)
    print(review)
    print("=" * 60)

    if "BLOCKER" in review.upper():
        print("\n🚫 BLOCKER found! Fix issues before committing.")
        print("   Use 'git commit --no-verify' to skip this check.")
        sys.exit(1)

    print("\n✅ No blockers. Committing...")
    sys.exit(0)

if __name__ == "__main__":
    main()
