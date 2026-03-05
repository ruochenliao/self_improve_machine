#!/usr/bin/env python3
"""
Smart Code Reviewer — AI-powered code review CLI tool.

Usage:
    python smart_code_reviewer.py <file_or_directory> [--api-key YOUR_KEY] [--model MODEL]
    python smart_code_reviewer.py --git-diff           # Review staged changes
    python smart_code_reviewer.py --git-diff HEAD~1    # Review last commit

Features:
    - Reviews individual files or entire directories
    - Reviews git diffs (staged changes or between commits)
    - Detects security vulnerabilities, performance issues, and code smells
    - Outputs structured report in terminal or JSON

Supports: OpenAI, DeepSeek, Anthropic APIs (auto-detect from key format)

License: Personal and commercial use allowed.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# --- Configuration ---
DEFAULT_MODEL = "deepseek-chat"
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".cs", ".swift",
    ".kt", ".scala", ".sh", ".bash", ".sql", ".yaml", ".yml",
    ".toml", ".json", ".dockerfile", ".tf", ".hcl",
}

REVIEW_PROMPT = """You are an expert code reviewer. Analyze the following code and provide a structured review.

For each issue found, output a JSON object in this exact format:
{
  "summary": "Brief overall assessment",
  "score": <1-10 quality score>,
  "issues": [
    {
      "severity": "critical|warning|info",
      "category": "bug|security|performance|style|maintainability",
      "line": <line number or null>,
      "title": "Short title",
      "description": "What's wrong and why",
      "suggestion": "How to fix it with code example"
    }
  ],
  "highlights": ["List of things done well"],
  "metrics": {
    "estimated_complexity": "low|medium|high",
    "test_coverage_risk": "low|medium|high",
    "security_risk": "low|medium|high"
  }
}

IMPORTANT: Output ONLY valid JSON, no markdown, no explanation outside the JSON.

Code to review (file: {filename}):
```
{code}
```"""

DIFF_REVIEW_PROMPT = """You are an expert code reviewer reviewing a git diff. Focus on the CHANGES only.

Analyze:
1. Are the changes correct and complete?
2. Do they introduce any bugs, security issues, or performance problems?
3. Is the code style consistent with the surrounding code?
4. Are edge cases handled?

Output JSON in this format:
{
  "summary": "Brief assessment of the changes",
  "approve": true/false,
  "issues": [
    {
      "severity": "critical|warning|info",
      "category": "bug|security|performance|style",
      "file": "filename",
      "line": <line number or null>,
      "title": "Short title",
      "description": "What's wrong",
      "suggestion": "How to fix"
    }
  ],
  "highlights": ["Good changes noted"]
}

IMPORTANT: Output ONLY valid JSON.

Git diff:
```
{diff}
```"""


def detect_api_provider(api_key: str) -> tuple[str, str]:
    """Auto-detect API provider from key format."""
    if api_key.startswith("sk-ant-"):
        return "https://api.anthropic.com/v1/messages", "claude-3-5-sonnet-20241022"
    elif api_key.startswith("sk-") and len(api_key) > 50:
        return "https://api.openai.com/v1/chat/completions", "gpt-4o-mini"
    else:
        # Default to DeepSeek or OpenAI-compatible
        return "https://api.deepseek.com/v1/chat/completions", "deepseek-chat"


def call_llm(prompt: str, api_key: str, model: Optional[str] = None) -> str:
    """Call LLM API and return response text."""
    try:
        import httpx
    except ImportError:
        # Fallback to urllib if httpx not installed
        import urllib.request
        import urllib.error

        base_url, default_model = detect_api_provider(api_key)
        model = model or default_model

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        data = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 4096,
        }).encode()

        req = urllib.request.Request(base_url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read())
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            print(f"API Error: {e.code} - {e.read().decode()}", file=sys.stderr)
            sys.exit(1)

    base_url, default_model = detect_api_provider(api_key)
    model = model or default_model

    with httpx.Client(timeout=60) as client:
        response = client.post(
            base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 4096,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def get_git_diff(ref: Optional[str] = None) -> str:
    """Get git diff for staged changes or between refs."""
    try:
        if ref:
            result = subprocess.run(
                ["git", "diff", ref], capture_output=True, text=True, check=True
            )
        else:
            result = subprocess.run(
                ["git", "diff", "--cached"], capture_output=True, text=True, check=True
            )
            if not result.stdout:
                result = subprocess.run(
                    ["git", "diff"], capture_output=True, text=True, check=True
                )
        return result.stdout
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git not installed.", file=sys.stderr)
        sys.exit(1)


def review_file(filepath: str, api_key: str, model: Optional[str] = None) -> dict:
    """Review a single file."""
    path = Path(filepath)
    if path.suffix not in SUPPORTED_EXTENSIONS:
        return {"skipped": True, "reason": f"Unsupported file type: {path.suffix}"}

    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"skipped": True, "reason": str(e)}

    if len(code) > 50000:
        code = code[:50000] + "\n... (truncated)"

    prompt = REVIEW_PROMPT.format(filename=path.name, code=code)
    response = call_llm(prompt, api_key, model)

    try:
        # Try to extract JSON from response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        return json.loads(response.strip())
    except json.JSONDecodeError:
        return {"summary": response, "issues": [], "parse_error": True}


def review_diff(api_key: str, ref: Optional[str] = None, model: Optional[str] = None) -> dict:
    """Review git diff."""
    diff = get_git_diff(ref)
    if not diff:
        return {"summary": "No changes to review.", "issues": []}

    if len(diff) > 50000:
        diff = diff[:50000] + "\n... (truncated)"

    prompt = DIFF_REVIEW_PROMPT.format(diff=diff)
    response = call_llm(prompt, api_key, model)

    try:
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        return json.loads(response.strip())
    except json.JSONDecodeError:
        return {"summary": response, "issues": [], "parse_error": True}


def print_review(filepath: str, review: dict):
    """Pretty print review results."""
    COLORS = {
        "critical": "\033[91m",  # Red
        "warning": "\033[93m",   # Yellow
        "info": "\033[94m",      # Blue
        "reset": "\033[0m",
        "green": "\033[92m",
        "bold": "\033[1m",
    }

    print(f"\n{'='*60}")
    print(f"{COLORS['bold']}📄 {filepath}{COLORS['reset']}")
    print(f"{'='*60}")

    if review.get("skipped"):
        print(f"  ⏭️  Skipped: {review['reason']}")
        return

    # Summary
    summary = review.get("summary", "No summary")
    score = review.get("score", "N/A")
    print(f"\n  📊 Score: {score}/10")
    print(f"  📝 {summary}")

    # Issues
    issues = review.get("issues", [])
    if issues:
        print(f"\n  {'─'*50}")
        print(f"  🔍 Issues Found: {len(issues)}")
        for i, issue in enumerate(issues, 1):
            severity = issue.get("severity", "info")
            color = COLORS.get(severity, COLORS["info"])
            icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")

            print(f"\n  {icon} [{i}] {color}{issue.get('title', 'Issue')}{COLORS['reset']}")
            if issue.get("line"):
                print(f"     Line: {issue['line']}")
            print(f"     Category: {issue.get('category', 'general')}")
            print(f"     {issue.get('description', '')}")
            if issue.get("suggestion"):
                print(f"     💡 Fix: {issue['suggestion']}")

    # Highlights
    highlights = review.get("highlights", [])
    if highlights:
        print(f"\n  {'─'*50}")
        print(f"  {COLORS['green']}✅ Good Practices:{COLORS['reset']}")
        for h in highlights:
            print(f"     • {h}")

    # Metrics
    metrics = review.get("metrics", {})
    if metrics:
        print(f"\n  {'─'*50}")
        print(f"  📈 Metrics:")
        for k, v in metrics.items():
            print(f"     {k}: {v}")


def main():
    parser = argparse.ArgumentParser(
        description="Smart Code Reviewer — AI-powered code review tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s app.py                        # Review single file
  %(prog)s src/                           # Review all files in directory
  %(prog)s --git-diff                     # Review staged/unstaged changes
  %(prog)s --git-diff HEAD~3             # Review last 3 commits
  %(prog)s app.py --output report.json   # Save report as JSON
        """,
    )
    parser.add_argument("path", nargs="?", help="File or directory to review")
    parser.add_argument("--git-diff", nargs="?", const="", metavar="REF",
                       help="Review git diff (optionally specify ref)")
    parser.add_argument("--api-key", help="API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--model", help="LLM model to use")
    parser.add_argument("--output", "-o", help="Output JSON report to file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: API key required. Use --api-key or set OPENAI_API_KEY env var.", file=sys.stderr)
        sys.exit(1)

    results = {}

    if args.git_diff is not None:
        ref = args.git_diff if args.git_diff else None
        print("🔍 Reviewing git diff..." if not args.json else "", file=sys.stderr)
        results["git_diff"] = review_diff(api_key, ref, args.model)
        if not args.json:
            print_review("Git Diff", results["git_diff"])

    elif args.path:
        path = Path(args.path)
        if path.is_file():
            print(f"🔍 Reviewing {path}..." if not args.json else "", file=sys.stderr)
            results[str(path)] = review_file(str(path), api_key, args.model)
            if not args.json:
                print_review(str(path), results[str(path)])

        elif path.is_dir():
            files = sorted(
                f for f in path.rglob("*")
                if f.is_file() and f.suffix in SUPPORTED_EXTENSIONS
                and ".git" not in f.parts
                and "node_modules" not in f.parts
                and "__pycache__" not in f.parts
            )
            print(f"🔍 Found {len(files)} files to review..." if not args.json else "", file=sys.stderr)
            for f in files:
                if not args.json:
                    print(f"  Reviewing {f}...", file=sys.stderr)
                results[str(f)] = review_file(str(f), api_key, args.model)
                if not args.json:
                    print_review(str(f), results[str(f)])
        else:
            print(f"Error: {path} not found.", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    # Output JSON
    if args.json:
        print(json.dumps(results, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Report saved to {args.output}")

    # Summary
    if not args.json:
        total_issues = sum(
            len(r.get("issues", [])) for r in results.values() if not r.get("skipped")
        )
        critical = sum(
            sum(1 for i in r.get("issues", []) if i.get("severity") == "critical")
            for r in results.values()
        )
        print(f"\n{'='*60}")
        print(f"📊 Total: {len(results)} files | {total_issues} issues | {critical} critical")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
