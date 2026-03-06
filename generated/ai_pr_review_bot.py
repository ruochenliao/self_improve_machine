#!/usr/bin/env python3
"""
🤖 AI Pull Request Review Bot
Drop this into your CI/CD pipeline and get instant AI code reviews on every PR.
Works with GitHub Actions, GitLab CI, or any CI system.

Usage:
  # Review staged changes:
  git diff --staged | python ai_pr_review_bot.py

  # Review a specific file:
  python ai_pr_review_bot.py myfile.py

  # Review last commit:
  git diff HEAD~1 | python ai_pr_review_bot.py

  # GitHub Actions (add to .github/workflows/ai-review.yml):
  #   - name: AI Code Review
  #     run: git diff ${{ github.event.pull_request.base.sha }} | python ai_pr_review_bot.py

API: https://api.closeai-asia.com/v1 (powered by Stark-Vortex 🤖)
Cost: $0.02 per review — mass code reviews for pennies
"""
import sys, json, subprocess, urllib.request

API = "http://localhost:8402"  # Change to your public URL in production

def get_diff():
    if not sys.stdin.isatty():
        return sys.stdin.read()
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            return f.read()
    result = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)
    return result.stdout or subprocess.run(["git", "diff"], capture_output=True, text=True).stdout

def review(diff):
    if not diff.strip():
        print("❌ No changes to review. Stage some changes or pipe a diff.")
        return
    print(f"🔍 Reviewing {len(diff.splitlines())} lines of changes...\n")
    prompt = f"""You are a senior code reviewer. Review this diff and provide:

## 🐛 Bugs & Issues
List any bugs, security issues, or logic errors.

## ⚡ Performance
Any performance concerns?

## 🎨 Style & Best Practices
Code quality suggestions.

## ✅ Summary
Overall assessment: APPROVE, REQUEST_CHANGES, or COMMENT.

```diff
{diff[:8000]}
```"""
    body = json.dumps({"message": prompt}).encode()
    req = urllib.request.Request(f"{API}/api/chat", data=body,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            print(data.get("response", data.get("reply", "No response")))
    except Exception as e:
        print(f"❌ Review failed: {e}")

if __name__ == "__main__":
    review(get_diff())
