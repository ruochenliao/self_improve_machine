# The AI-Powered Development Workflow — Complete Integration Guide

## How to 10x Your Development Speed with AI

This guide shows you how to integrate AI into every stage of your development workflow. No theory — just practical, copy-paste-ready setups.

---

## 1. AI-Assisted Git Workflow

### Pre-commit: Auto Code Review
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Run AI code review on staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ -n "$STAGED_FILES" ]; then
    python scripts/smart_code_reviewer.py --git-diff --json > /tmp/review.json
    CRITICAL=$(python -c "import json; r=json.load(open('/tmp/review.json')); print(sum(1 for v in r.values() for i in v.get('issues',[]) if i.get('severity')=='critical'))")
    if [ "$CRITICAL" -gt 0 ]; then
        echo "❌ Critical issues found. Fix before committing."
        python scripts/smart_code_reviewer.py --git-diff
        exit 1
    fi
fi
```

### Commit: AI Commit Messages
```bash
# Add to ~/.bashrc or ~/.zshrc
alias gcai='python ~/tools/git_commit_ai.py --commit'
alias gcai-amend='python ~/tools/git_commit_ai.py --commit --amend'

# Usage:
git add .
gcai  # Auto-generates commit message and commits
```

### Post-push: Auto PR Description
```python
# Generate PR description from branch diff
import subprocess, json, urllib.request

def generate_pr_description(base="main"):
    diff = subprocess.run(
        ["git", "log", f"{base}..HEAD", "--oneline"],
        capture_output=True, text=True
    ).stdout
    
    prompt = f"Write a PR description for these commits:\n{diff}"
    # Call your preferred LLM API here
    return call_llm(prompt)
```

---

## 2. AI-Powered Testing Pipeline

### Auto-generate tests on file save (VS Code)
```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [{
        "label": "AI Generate Tests",
        "type": "shell",
        "command": "python scripts/auto_test_generator.py ${file}",
        "group": "test",
        "presentation": {"reveal": "silent"}
    }]
}
```

### CI Integration — Test Gap Detection
```yaml
# .github/workflows/test-coverage.yml
name: AI Test Gap Detection
on: [pull_request]
jobs:
  test-gaps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Find untested code
        run: |
          # Get changed files
          CHANGED=$(git diff --name-only origin/main...HEAD | grep '\.py$' | grep -v test_)
          for f in $CHANGED; do
            TEST_FILE="tests/test_$(basename $f)"
            if [ ! -f "$TEST_FILE" ]; then
              echo "⚠️ Missing tests for: $f"
              python scripts/auto_test_generator.py "$f" --output tests/
            fi
          done
```

---

## 3. AI Code Review in CI/CD

### GitHub Actions Integration
```yaml
# .github/workflows/ai-review.yml
name: AI Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: AI Review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          git diff origin/main...HEAD > /tmp/diff.patch
          python scripts/smart_code_reviewer.py --git-diff origin/main --json > review.json
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = JSON.parse(fs.readFileSync('review.json'));
            // Format and post as PR comment
            const body = formatReview(review);
            github.rest.issues.createComment({
              ...context.repo, issue_number: context.issue.number, body
            });
```

---

## 4. AI-Enhanced Development Patterns

### Pattern: AI Pair Programming Session
```python
"""
Start every coding session with this prompt to your AI:

"I'm working on [PROJECT]. Here's the current file I'm editing:
[paste file]

My task: [describe what you want to do]

Before writing code:
1. Ask me clarifying questions if anything is ambiguous
2. Propose 2-3 approaches with trade-offs  
3. After I choose, implement with tests"
"""
```

### Pattern: Rubber Duck Debugging with AI
```
# When stuck on a bug, use this prompt:

"I have a bug. Let me explain my understanding, and you tell me where my
reasoning might be wrong:

1. I expect [X] to happen because [reason]
2. Instead, [Y] happens
3. I've checked [list what you've tried]
4. My hypothesis is [your guess]

Here's the relevant code: [paste code]

Don't give me the answer immediately. Ask me questions that will help 
ME find the bug."
```

### Pattern: Architecture Decision with AI
```
# Before making architectural decisions:

"I need to decide between [Option A] and [Option B] for [component].

Context:
- Current scale: [X users/requests]
- Expected scale in 1 year: [Y]
- Team size: [N developers]
- Deployment: [cloud/on-prem]
- Budget constraints: [if any]

For each option, analyze:
1. Implementation complexity (1-10)
2. Scalability ceiling
3. Operational overhead
4. Migration difficulty later
5. Team learning curve

Recommend one with clear justification."
```

---

## 5. Building Custom AI Tools

### Template: AI-Powered CLI Tool
```python
#!/usr/bin/env python3
"""Template for building your own AI-powered CLI tools."""

import argparse
import json
import os
import sys
import urllib.request


def call_ai(prompt: str, system: str = "") -> str:
    """Universal AI caller — works with OpenAI, DeepSeek, Anthropic."""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("Set OPENAI_API_KEY or DEEPSEEK_API_KEY env var")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Auto-detect provider
    if "deepseek" in api_key.lower() or len(api_key) < 50:
        url = "https://api.deepseek.com/v1/chat/completions"
        model = "deepseek-chat"
    else:
        url = "https://api.openai.com/v1/chat/completions"
        model = "gpt-4o-mini"

    data = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }).encode()

    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })

    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


# Example: Build your own tool
def my_custom_tool(input_text: str) -> str:
    """Replace this with your tool's logic."""
    return call_ai(
        prompt=f"Process this input: {input_text}",
        system="You are a helpful assistant specialized in [YOUR DOMAIN]."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="My AI Tool")
    parser.add_argument("input", help="Input to process")
    args = parser.parse_args()
    print(my_custom_tool(args.input))
```

---

## 6. Cost Optimization Tips

### Choose the Right Model for the Task

| Task | Recommended Model | Cost/1K tokens |
|------|------------------|----------------|
| Code review | DeepSeek Chat | ~$0.001 |
| Simple generation | GPT-4o-mini | ~$0.003 |
| Complex architecture | GPT-4o / Claude 3.5 | ~$0.03 |
| Quick completions | DeepSeek Chat | ~$0.001 |

### Reduce Token Usage
```python
# Bad: Sending entire file for a small change
review_prompt = f"Review this 5000-line file: {entire_file}"

# Good: Send only the relevant context
review_prompt = f"""Review this function (lines 42-67 of auth.py):
{relevant_function}

Context: This is part of a JWT authentication system.
The full file has proper imports and error handling."""
```

### Cache AI Responses
```python
import hashlib
import json
from pathlib import Path

CACHE_DIR = Path(".ai_cache")
CACHE_DIR.mkdir(exist_ok=True)

def cached_ai_call(prompt: str) -> str:
    cache_key = hashlib.md5(prompt.encode()).hexdigest()
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        return json.loads(cache_file.read_text())["response"]
    
    response = call_ai(prompt)
    cache_file.write_text(json.dumps({"prompt": prompt[:100], "response": response}))
    return response
```

---

## Quick Start Checklist

- [ ] Set up API key: `export OPENAI_API_KEY=sk-...` or `export DEEPSEEK_API_KEY=sk-...`
- [ ] Copy scripts to your project's `scripts/` directory
- [ ] Add git hooks for pre-commit review
- [ ] Set up aliases in your shell config
- [ ] Configure VS Code tasks (optional)
- [ ] Add CI/CD workflow for PR reviews (optional)

**Total setup time: ~10 minutes. ROI: Hours saved every week.**
