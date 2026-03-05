#!/usr/bin/env python3
"""
Git Commit AI — Generate meaningful commit messages from git diffs.

Usage:
    python git_commit_ai.py                  # Generate message for staged changes
    python git_commit_ai.py --commit         # Generate and commit directly
    python git_commit_ai.py --style angular  # Use Angular commit convention

Supports: Conventional Commits, Angular, Semantic, or Custom styles.
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Optional

COMMIT_STYLES = {
    "conventional": """Generate a commit message following Conventional Commits (https://www.conventionalcommits.org/):
Format: <type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
- feat: new feature
- fix: bug fix
- docs: documentation only
- style: formatting, no logic change
- refactor: code restructuring
- perf: performance improvement
- test: adding/fixing tests
- build: build system changes
- ci: CI configuration
- chore: maintenance

Body (if needed): Explain WHY, not WHAT (the diff shows what).
Footer: BREAKING CHANGE: if applicable.""",

    "angular": """Generate a commit message following Angular convention:
Format: <type>(<scope>): <short summary>

Types: build, ci, docs, feat, fix, perf, refactor, test
- Keep subject under 50 chars
- Use imperative mood ("add" not "added")
- No period at end""",

    "semantic": """Generate a semantic commit message:
Format: [TYPE] Brief description

Types: [FEATURE], [FIX], [DOCS], [REFACTOR], [TEST], [CHORE], [PERF]
Include a brief body explaining the change.""",
}

PROMPT_TEMPLATE = """Analyze this git diff and generate a commit message.

{style_guide}

Rules:
1. Subject line: max 50 chars, imperative mood, no period
2. If the change is simple, one line is enough
3. If complex, add a body separated by a blank line (max 72 chars/line)
4. Focus on WHY, not WHAT (the diff shows what)
5. If multiple changes, use bullet points in body

Output ONLY the commit message, nothing else. No quotes, no markdown.

Git diff:
```
{diff}
```"""


def get_staged_diff() -> str:
    """Get diff of staged changes."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat"], capture_output=True, text=True
    )
    if not result.stdout.strip():
        # Nothing staged, show unstaged
        result = subprocess.run(
            ["git", "diff", "--stat"], capture_output=True, text=True
        )
        if not result.stdout.strip():
            print("No changes to commit.", file=sys.stderr)
            sys.exit(0)
        print("⚠️  No staged changes. Showing unstaged changes.", file=sys.stderr)
        print("   Run 'git add' first to stage changes.\n", file=sys.stderr)

    # Get the actual diff
    result = subprocess.run(
        ["git", "diff", "--cached"], capture_output=True, text=True
    )
    if not result.stdout:
        result = subprocess.run(
            ["git", "diff"], capture_output=True, text=True
        )
    return result.stdout


def call_llm(prompt: str, api_key: str, model: Optional[str] = None) -> str:
    """Call LLM API."""
    import urllib.request

    base_url = "https://api.deepseek.com/v1/chat/completions"
    model = model or "deepseek-chat"

    if api_key.startswith("sk-") and len(api_key) > 50:
        base_url = "https://api.openai.com/v1/chat/completions"
        model = model or "gpt-4o-mini"

    data = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 500,
    }).encode()

    req = urllib.request.Request(
        base_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read())
        return result["choices"][0]["message"]["content"].strip()


def main():
    parser = argparse.ArgumentParser(description="Git Commit AI")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--model", help="LLM model")
    parser.add_argument("--style", choices=list(COMMIT_STYLES.keys()),
                       default="conventional", help="Commit style")
    parser.add_argument("--commit", "-c", action="store_true",
                       help="Directly create the commit")
    parser.add_argument("--amend", action="store_true",
                       help="Amend the last commit")

    args = parser.parse_args()
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: API key required.", file=sys.stderr)
        sys.exit(1)

    diff = get_staged_diff()
    if len(diff) > 30000:
        diff = diff[:30000] + "\n... (truncated)"

    print("🤖 Generating commit message...", file=sys.stderr)
    style_guide = COMMIT_STYLES[args.style]
    prompt = PROMPT_TEMPLATE.format(style_guide=style_guide, diff=diff)
    message = call_llm(prompt, api_key, args.model)

    # Clean up
    message = message.strip().strip('"').strip("'").strip("`")

    if args.commit or args.amend:
        cmd = ["git", "commit"]
        if args.amend:
            cmd.append("--amend")
        cmd.extend(["-m", message])
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Committed: {message.split(chr(10))[0]}")
        else:
            print(f"❌ Commit failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"\n{'─'*50}")
        print(message)
        print(f"{'─'*50}")
        print("\n💡 To commit: git commit -m '<message above>'")
        print("   Or rerun with --commit flag to auto-commit")


if __name__ == "__main__":
    main()
