#!/usr/bin/env python3
"""
🤖 AI Commit Message Generator
Never write a boring commit message again! Analyzes your staged git diff
and generates a perfect conventional commit message.

Usage:
  python ai_commit_msg.py              # Generate message for staged changes
  python ai_commit_msg.py --auto       # Generate AND commit automatically
  python ai_commit_msg.py --diff HEAD~3  # Summarize last 3 commits

pip install requests
"""
import subprocess, sys, requests, argparse

API = "https://api.closeai-asia.com/v1"  # Update with your Stark-Vortex URL

def get_diff(ref=None):
    cmd = ["git", "diff", "--cached"] if not ref else ["git", "diff", ref]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("❌ Not a git repo or git not found"); sys.exit(1)
    if not r.stdout.strip():
        if not ref:
            print("💡 No staged changes. Stage with: git add -p")
            print("   Or use --diff HEAD~1 to summarize recent commits")
            sys.exit(0)
    return r.stdout

def generate_message(diff):
    prompt = f"""Analyze this git diff and generate a conventional commit message.
Rules:
- Use format: type(scope): description
- Types: feat, fix, refactor, docs, test, chore, style, perf
- Keep subject line under 72 chars
- Add a blank line then bullet-point body if needed
- Be specific about WHAT changed and WHY

Diff:
```
{diff[:4000]}
```

Respond with ONLY the commit message, nothing else."""

    # Try local Stark-Vortex API first, fall back to direct
    for url in ["http://localhost:8402/api/chat", API]:
        try:
            r = requests.post(url, json={"message": prompt}, timeout=30)
            if r.ok:
                return r.json().get("response", r.text).strip()
        except:
            continue
    print("❌ Could not reach AI API"); sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="🤖 AI Commit Message Generator")
    parser.add_argument("--auto", action="store_true", help="Auto-commit with generated message")
    parser.add_argument("--diff", type=str, help="Diff against ref (e.g. HEAD~3, main)")
    args = parser.parse_args()

    print("🔍 Analyzing changes...")
    diff = get_diff(args.diff)
    
    print("🤖 Generating commit message...\n")
    msg = generate_message(diff)
    
    print("─" * 50)
    print(msg)
    print("─" * 50)

    if args.auto and not args.diff:
        confirm = input("\n✅ Commit with this message? [Y/n] ").strip().lower()
        if confirm in ("", "y", "yes"):
            subprocess.run(["git", "commit", "-m", msg])
            print("🎉 Committed!")
        else:
            print("⏭️  Skipped. Copy the message above manually.")
    elif not args.diff:
        print(f"\n📋 To use: git commit -m '{msg.splitlines()[0]}'")

if __name__ == "__main__":
    main()
