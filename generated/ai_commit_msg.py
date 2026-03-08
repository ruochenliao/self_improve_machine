#!/usr/bin/env python3
"""ai-commit: Generate git commit messages using AI code review.

Usage:
  python ai_commit_msg.py              # Generate message for staged changes
  python ai_commit_msg.py --apply      # Generate and commit automatically
  python ai_commit_msg.py --diff HEAD~3  # Summarize last 3 commits

Powered by Silent-Nexus API — $0.01/request
"""
import subprocess, sys, json, requests

API = "http://localhost:8402"  # Change to your deployed URL

def get_diff(ref=None):
    cmd = ["git", "diff", "--cached"] if not ref else ["git", "diff", ref]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not r.stdout.strip():
        r = subprocess.run(["git", "diff"], capture_output=True, text=True)
    return r.stdout.strip()

def generate_msg(diff):
    if not diff:
        print("No changes detected. Stage files with 'git add' first.")
        sys.exit(1)
    # Truncate large diffs to save tokens
    if len(diff) > 4000:
        diff = diff[:4000] + "\n... (truncated)"
    prompt = f"""Analyze this git diff and write a concise, conventional commit message.
Use format: type(scope): description
Types: feat, fix, refactor, docs, style, test, chore
Keep under 72 chars. Add bullet points for details if needed.

Diff:
{diff}"""
    try:
        r = requests.post(f"{API}/chat", json={"message": prompt}, timeout=30)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        print(f"API error: {e}")
        sys.exit(1)

def main():
    apply = "--apply" in sys.argv
    ref = None
    if "--diff" in sys.argv:
        idx = sys.argv.index("--diff")
        ref = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "HEAD~1"

    diff = get_diff(ref)
    msg = generate_msg(diff)
    print(f"\n📝 Suggested commit message:\n\n{msg}\n")

    if apply:
        subprocess.run(["git", "commit", "-m", msg])
        print("✅ Committed!")
    elif not ref:
        ans = input("Apply this message? [y/N] ").strip().lower()
        if ans == "y":
            subprocess.run(["git", "commit", "-m", msg])
            print("✅ Committed!")

if __name__ == "__main__":
    main()
