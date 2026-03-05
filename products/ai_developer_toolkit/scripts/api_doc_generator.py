#!/usr/bin/env python3
"""
API Documentation Generator — Auto-generate API docs from Python/FastAPI/Flask code.

Usage:
    python api_doc_generator.py app.py --output docs/api.md
    python api_doc_generator.py src/routes/ --format html
    python api_doc_generator.py app.py --format openapi  # Generate OpenAPI spec
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


def extract_routes(filepath: str) -> list[dict]:
    """Extract API routes from Python source code."""
    with open(filepath, "r") as f:
        source = f.read()

    routes = []

    # FastAPI patterns
    fastapi_pattern = re.compile(
        r'@\w+\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    for match in fastapi_pattern.finditer(source):
        routes.append({
            "method": match.group(1).upper(),
            "path": match.group(2),
            "source": filepath,
        })

    # Flask patterns
    flask_pattern = re.compile(
        r'@\w+\.route\(\s*["\']([^"\']+)["\'](?:.*?methods\s*=\s*\[([^\]]+)\])?',
        re.IGNORECASE,
    )
    for match in flask_pattern.finditer(source):
        methods = match.group(2)
        if methods:
            for m in re.findall(r'["\'](\w+)["\']', methods):
                routes.append({"method": m.upper(), "path": match.group(1), "source": filepath})
        else:
            routes.append({"method": "GET", "path": match.group(1), "source": filepath})

    return routes


def generate_docs_with_ai(filepath: str, api_key: str, model: Optional[str] = None, fmt: str = "markdown") -> str:
    """Use AI to generate comprehensive docs."""
    import urllib.request

    with open(filepath, "r") as f:
        code = f.read()

    if len(code) > 30000:
        code = code[:30000] + "\n# ... truncated"

    format_instruction = {
        "markdown": "Generate documentation in Markdown format with clear headers, tables, and code examples.",
        "html": "Generate documentation in clean HTML with styling.",
        "openapi": "Generate an OpenAPI 3.0 specification in YAML format.",
    }

    prompt = f"""Analyze this Python API code and generate comprehensive API documentation.

{format_instruction.get(fmt, format_instruction['markdown'])}

For each endpoint, document:
1. HTTP Method and Path
2. Description
3. Request headers (especially authentication)
4. Request body/parameters with types
5. Response format with example
6. Error responses
7. curl example
8. Rate limiting info (if applicable)

Code:
```python
{code}
```"""

    base_url = "https://api.deepseek.com/v1/chat/completions"
    llm_model = model or "deepseek-chat"
    if api_key.startswith("sk-") and len(api_key) > 50:
        base_url = "https://api.openai.com/v1/chat/completions"
        llm_model = model or "gpt-4o-mini"

    data = json.dumps({
        "model": llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 8192,
    }).encode()

    req = urllib.request.Request(
        base_url, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        result = json.loads(response.read())
        return result["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="API Documentation Generator")
    parser.add_argument("path", help="Python file or directory with API code")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--model", help="LLM model")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", choices=["markdown", "html", "openapi"],
                       default="markdown", help="Output format")

    args = parser.parse_args()
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: API key required.", file=sys.stderr)
        sys.exit(1)

    path = Path(args.path)
    files = []
    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = list(path.rglob("*.py"))

    all_docs = []
    for f in files:
        routes = extract_routes(str(f))
        if routes:
            print(f"📝 Generating docs for {f} ({len(routes)} endpoints)...")
            doc = generate_docs_with_ai(str(f), api_key, args.model, args.format)
            all_docs.append(doc)

    if not all_docs:
        print("No API endpoints found.", file=sys.stderr)
        sys.exit(1)

    output = "\n\n---\n\n".join(all_docs)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ Documentation saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
