#!/usr/bin/env python3
"""
Auto Test Generator — AI-powered unit test generation for Python files.

Usage:
    python auto_test_generator.py <python_file> [--api-key KEY] [--output tests/]
    python auto_test_generator.py src/models.py --framework pytest
    python auto_test_generator.py src/ --recursive  # Generate tests for all Python files

Features:
    - Analyzes Python source code and generates comprehensive unit tests
    - Supports pytest and unittest frameworks
    - Generates edge cases, error cases, and boundary tests
    - Creates proper mocks for external dependencies
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import Optional

GENERATE_PROMPT = """You are an expert Python test engineer. Generate comprehensive unit tests for this code.

Requirements:
- Framework: {framework}
- Generate tests for ALL public functions and methods
- Include: happy path, edge cases, error cases, boundary values
- Use descriptive test names: test_<function>_<scenario>_<expected>
- Use Arrange-Act-Assert pattern
- Mock external dependencies (database, API calls, file I/O)
- Include docstrings for complex test cases
- Aim for >90% branch coverage

Code to test (file: {filename}):
```python
{code}
```

Output ONLY valid Python test code. Include all necessary imports.
Start with the imports, then test classes/functions. No markdown, no explanation outside code."""


def extract_code_info(filepath: str) -> dict:
    """Extract function/class info from Python file for context."""
    with open(filepath, "r") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"functions": [], "classes": [], "imports": []}

    info = {"functions": [], "classes": [], "imports": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            info["functions"].append({
                "name": node.name,
                "args": [a.arg for a in node.args.args],
                "decorators": [
                    ast.dump(d) for d in node.decorator_list
                ] if node.decorator_list else [],
                "has_return": any(
                    isinstance(n, ast.Return) and n.value is not None
                    for n in ast.walk(node)
                ),
            })
        elif isinstance(node, ast.ClassDef):
            methods = [
                n.name for n in node.body if isinstance(n, ast.FunctionDef)
            ]
            info["classes"].append({"name": node.name, "methods": methods})
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                info["imports"].extend(a.name for a in node.names)
            else:
                info["imports"].append(node.module or "")

    return info


def call_llm(prompt: str, api_key: str, model: Optional[str] = None) -> str:
    """Call LLM API."""
    import urllib.request

    base_url = "https://api.deepseek.com/v1/chat/completions"
    model = model or "deepseek-chat"

    if api_key.startswith("sk-") and len(api_key) > 50:
        base_url = "https://api.openai.com/v1/chat/completions"
        model = model or "gpt-4o-mini"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 8192,
    }).encode()

    req = urllib.request.Request(base_url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as response:
        result = json.loads(response.read())
        return result["choices"][0]["message"]["content"]


def generate_tests(
    filepath: str,
    api_key: str,
    framework: str = "pytest",
    model: Optional[str] = None,
) -> str:
    """Generate tests for a Python file."""
    path = Path(filepath)
    code = path.read_text(encoding="utf-8")

    if len(code) > 30000:
        code = code[:30000] + "\n# ... (truncated for length)"

    prompt = GENERATE_PROMPT.format(
        framework=framework, filename=path.name, code=code
    )
    response = call_llm(prompt, api_key, model)

    # Clean up response
    if "```python" in response:
        response = response.split("```python")[1].split("```")[0]
    elif "```" in response:
        parts = response.split("```")
        if len(parts) >= 3:
            response = parts[1]

    return response.strip()


def main():
    parser = argparse.ArgumentParser(description="Auto Test Generator")
    parser.add_argument("path", help="Python file or directory")
    parser.add_argument("--api-key", help="API key (or set OPENAI_API_KEY)")
    parser.add_argument("--model", help="LLM model")
    parser.add_argument("--framework", choices=["pytest", "unittest"], default="pytest")
    parser.add_argument("--output", "-o", help="Output directory (default: tests/)")
    parser.add_argument("--recursive", "-r", action="store_true")

    args = parser.parse_args()
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: API key required.", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output or "tests")
    output_dir.mkdir(parents=True, exist_ok=True)

    path = Path(args.path)
    files = []
    if path.is_file():
        files = [path]
    elif path.is_dir():
        pattern = "**/*.py" if args.recursive else "*.py"
        files = [f for f in path.glob(pattern) if not f.name.startswith("test_")]

    for f in files:
        print(f"🧪 Generating tests for {f}...")
        try:
            test_code = generate_tests(str(f), api_key, args.framework, args.model)
            test_file = output_dir / f"test_{f.stem}.py"
            test_file.write_text(test_code, encoding="utf-8")
            print(f"   ✅ Saved to {test_file}")
        except Exception as e:
            print(f"   ❌ Error: {e}", file=sys.stderr)

    print(f"\n📊 Generated tests for {len(files)} files in {output_dir}/")


if __name__ == "__main__":
    main()
