#!/usr/bin/env python3
"""
📝 AI Docstring Generator — Auto-generate docstrings for Python functions/classes

Usage:
    python ai_docstring_generator.py myfile.py              # Print with docstrings added
    python ai_docstring_generator.py myfile.py --inplace     # Modify file in-place
    python ai_docstring_generator.py myfile.py -o output.py  # Write to new file

Powered by Swift-Flux AI API (free tier available)
"""
import ast, sys, os, json, urllib.request, textwrap, argparse

API_URL = os.environ.get("AI_API_URL", "https://swiftflux-api.trycloudflare.com")

def get_functions(source: str):
    """Extract functions/methods missing docstrings with their line info."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    targets = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Check if first statement is a docstring
            has_doc = (node.body and isinstance(node.body[0], ast.Expr)
                       and isinstance(node.body[0].value, (ast.Constant, ast.Str)))
            if not has_doc:
                # Get the source of just this function
                start = node.lineno - 1
                end = node.end_lineno
                func_source = "".join(lines[start:end])
                targets.append({
                    "name": node.name,
                    "type": type(node).__name__,
                    "line": node.lineno,
                    "body_line": node.body[0].lineno if node.body else node.lineno + 1,
                    "source": func_source[:500],  # Limit size
                    "col_offset": node.col_offset,
                })
    return targets

def generate_docstring(func_info: dict) -> str:
    """Call AI API to generate a docstring."""
    prompt = (f"Generate a concise Python docstring for this {func_info['type']}. "
              f"Return ONLY the docstring text (no quotes, no code):\n\n{func_info['source']}")
    payload = json.dumps({"prompt": prompt, "language": "python"}).encode()
    req = urllib.request.Request(f"{API_URL}/api/explain-code",
                                data=payload,
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("result", "").strip().strip('"').strip("'")
    except Exception as e:
        return f"TODO: Add docstring ({e})"

def add_docstrings(source: str) -> str:
    """Add AI-generated docstrings to all functions/classes missing them."""
    targets = get_functions(source)
    if not targets:
        print("✅ All functions/classes already have docstrings!")
        return source

    print(f"🔍 Found {len(targets)} functions/classes without docstrings")
    lines = source.splitlines(keepends=True)

    # Process in reverse order so line numbers stay valid
    for func in sorted(targets, key=lambda x: x["body_line"], reverse=True):
        print(f"  📝 Generating docstring for {func['name']}...")
        docstring = generate_docstring(func)
        if docstring:
            indent = " " * (func["col_offset"] + 4)
            doc_lines = textwrap.wrap(docstring, width=72)
            if len(doc_lines) == 1:
                doc_str = f'{indent}"""{doc_lines[0]}"""\n'
            else:
                doc_str = f'{indent}"""\n'
                for dl in doc_lines:
                    doc_str += f"{indent}{dl}\n"
                doc_str += f'{indent}"""\n'
            # Insert after the def/class line (at body_line - 1)
            insert_idx = func["body_line"] - 1
            lines.insert(insert_idx, doc_str)

    return "".join(lines)

def main():
    parser = argparse.ArgumentParser(description="AI Docstring Generator")
    parser.add_argument("file", help="Python file to process")
    parser.add_argument("--inplace", "-i", action="store_true", help="Modify file in-place")
    parser.add_argument("-o", "--output", help="Output file path")
    args = parser.parse_args()

    with open(args.file) as f:
        source = f.read()

    result = add_docstrings(source)

    if args.inplace:
        with open(args.file, "w") as f:
            f.write(result)
        print(f"✅ Updated {args.file} in-place")
    elif args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"✅ Written to {args.output}")
    else:
        print("\n" + "=" * 60)
        print(result)

if __name__ == "__main__":
    main()
