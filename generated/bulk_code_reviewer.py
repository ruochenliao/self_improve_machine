#!/usr/bin/env python3
"""Bulk Code Reviewer - Review all Python files in a directory via Bold-Helix API.
Usage: python bulk_code_reviewer.py /path/to/project [--api-url URL]
"""
import sys, os, requests, argparse, json

API_URL = os.getenv("BOLDHELIX_API", "http://localhost:8402")

def review_file(filepath, api_url, pro=False):
    endpoint = f"{api_url}/{'code-review-pro' if pro else 'code-review'}"
    with open(filepath) as f:
        code = f.read()
    if len(code) < 10:
        return None
    resp = requests.post(endpoint, json={"code": code, "language": "python"}, timeout=60)
    resp.raise_for_status()
    return resp.json()

def main():
    parser = argparse.ArgumentParser(description="Bulk code review via Bold-Helix API")
    parser.add_argument("directory", help="Directory to scan for .py files")
    parser.add_argument("--api-url", default=API_URL, help="API base URL")
    parser.add_argument("--pro", action="store_true", help="Use pro endpoint ($0.20/review)")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    args = parser.parse_args()

    py_files = []
    for root, _, files in os.walk(args.directory):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    print(f"Found {len(py_files)} Python files to review")
    results = {}
    for i, fp in enumerate(py_files, 1):
        print(f"[{i}/{len(py_files)}] Reviewing {fp}...", end=" ", flush=True)
        try:
            result = review_file(fp, args.api_url, args.pro)
            if result:
                results[fp] = result
                print("✓")
            else:
                print("skipped (too short)")
        except Exception as e:
            print(f"✗ {e}")
            results[fp] = {"error": str(e)}

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    else:
        for fp, r in results.items():
            if "error" not in r:
                print(f"\n{'='*60}\n{fp}\n{'='*60}")
                print(r.get("result", r.get("review", json.dumps(r, indent=2))))

if __name__ == "__main__":
    main()
