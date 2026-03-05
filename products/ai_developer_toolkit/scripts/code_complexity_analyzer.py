#!/usr/bin/env python3
"""
Code Complexity Analyzer — Analyze code metrics without external dependencies.

Usage:
    python code_complexity_analyzer.py <file_or_directory>
    python code_complexity_analyzer.py src/ --threshold 10 --format json

Metrics:
    - Cyclomatic complexity per function
    - Lines of code (total, code, comments, blank)
    - Function/method count and average length
    - Nesting depth
    - Maintainability index estimate
"""

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class FunctionMetrics:
    name: str
    lineno: int
    end_lineno: int
    lines: int
    complexity: int
    params: int
    max_nesting: int
    has_docstring: bool
    returns: int

    @property
    def risk(self) -> str:
        if self.complexity > 20:
            return "high"
        elif self.complexity > 10:
            return "medium"
        return "low"


@dataclass
class FileMetrics:
    filepath: str
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: list = field(default_factory=list)
    classes: int = 0
    imports: int = 0
    avg_function_length: float = 0.0
    max_complexity: int = 0
    maintainability_index: float = 0.0


class ComplexityVisitor(ast.NodeVisitor):
    """Calculate cyclomatic complexity of Python code."""

    def __init__(self):
        self.functions: list[FunctionMetrics] = []
        self.classes = 0
        self.imports = 0
        self._current_nesting = 0

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Count decision points for cyclomatic complexity."""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.IfExp)):
                complexity += 1
            elif isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)
        return complexity

    def _max_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With,
                                  ast.Try, ast.AsyncFor, ast.AsyncWith)):
                child_depth = self._max_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._max_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        return max_depth

    def _count_returns(self, node: ast.AST) -> int:
        """Count return statements."""
        return sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._process_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._process_function(node)
        self.generic_visit(node)

    def _process_function(self, node):
        has_docstring = (
            isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, (ast.Constant, ast.Str))
            if node.body else False
        )

        end_line = getattr(node, "end_lineno", node.lineno)
        self.functions.append(FunctionMetrics(
            name=node.name,
            lineno=node.lineno,
            end_lineno=end_line,
            lines=end_line - node.lineno + 1,
            complexity=self._calculate_complexity(node),
            params=len(node.args.args),
            max_nesting=self._max_nesting_depth(node),
            has_docstring=has_docstring,
            returns=self._count_returns(node),
        ))

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes += 1
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        self.imports += len(node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.imports += len(node.names)


def count_lines(source: str) -> tuple[int, int, int, int]:
    """Count total, code, comment, and blank lines."""
    lines = source.split("\n")
    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())
    comment = sum(1 for l in lines if l.strip().startswith("#"))
    code = total - blank - comment
    return total, code, comment, blank


def calculate_maintainability(metrics: FileMetrics) -> float:
    """Estimate Maintainability Index (0-100)."""
    import math

    if metrics.code_lines == 0:
        return 100.0

    avg_complexity = (
        sum(f.complexity for f in metrics.functions) / len(metrics.functions)
        if metrics.functions else 1
    )
    volume = metrics.code_lines * math.log2(max(metrics.code_lines, 1))
    mi = max(0, (171 - 5.2 * math.log(volume + 1)
                 - 0.23 * avg_complexity
                 - 16.2 * math.log(metrics.code_lines + 1)) * 100 / 171)
    return round(mi, 1)


def analyze_file(filepath: str) -> Optional[FileMetrics]:
    """Analyze a single Python file."""
    path = Path(filepath)
    if path.suffix != ".py":
        return None

    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return None

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    total, code, comment, blank = count_lines(source)
    visitor = ComplexityVisitor()
    visitor.visit(tree)

    metrics = FileMetrics(
        filepath=str(filepath),
        total_lines=total,
        code_lines=code,
        comment_lines=comment,
        blank_lines=blank,
        functions=visitor.functions,
        classes=visitor.classes,
        imports=visitor.imports,
    )

    if visitor.functions:
        metrics.avg_function_length = round(
            sum(f.lines for f in visitor.functions) / len(visitor.functions), 1
        )
        metrics.max_complexity = max(f.complexity for f in visitor.functions)

    metrics.maintainability_index = calculate_maintainability(metrics)
    return metrics


def print_report(metrics: FileMetrics, threshold: int = 10):
    """Print formatted report."""
    C = {
        "red": "\033[91m", "yellow": "\033[93m", "green": "\033[92m",
        "blue": "\033[94m", "bold": "\033[1m", "reset": "\033[0m",
    }

    print(f"\n{C['bold']}{'='*65}{C['reset']}")
    print(f"{C['bold']}📊 {metrics.filepath}{C['reset']}")
    print(f"{'='*65}")

    # Line counts
    print(f"\n  Lines: {metrics.total_lines} total | {metrics.code_lines} code | "
          f"{metrics.comment_lines} comments | {metrics.blank_lines} blank")
    print(f"  Classes: {metrics.classes} | Functions: {len(metrics.functions)} | "
          f"Imports: {metrics.imports}")

    # Maintainability
    mi = metrics.maintainability_index
    mi_color = C['green'] if mi >= 65 else C['yellow'] if mi >= 35 else C['red']
    mi_label = "Good" if mi >= 65 else "Moderate" if mi >= 35 else "Poor"
    print(f"  Maintainability: {mi_color}{mi}/100 ({mi_label}){C['reset']}")

    # Function details
    if metrics.functions:
        print(f"\n  {'─'*55}")
        print(f"  {'Function':<30} {'Lines':>6} {'Cmplx':>6} {'Nest':>5} {'Risk':>8}")
        print(f"  {'─'*55}")
        for f in sorted(metrics.functions, key=lambda x: x.complexity, reverse=True):
            risk_color = C['red'] if f.risk == "high" else C['yellow'] if f.risk == "medium" else C['green']
            warning = " ⚠️" if f.complexity > threshold else ""
            doc = "" if f.has_docstring else " 📝"
            print(f"  {f.name:<30} {f.lines:>6} {risk_color}{f.complexity:>6}{C['reset']} "
                  f"{f.max_nesting:>5} {risk_color}{f.risk:>8}{C['reset']}{warning}{doc}")

        # Summary stats
        high_risk = sum(1 for f in metrics.functions if f.risk == "high")
        no_docs = sum(1 for f in metrics.functions if not f.has_docstring)

        if high_risk > 0:
            print(f"\n  {C['red']}⚠️  {high_risk} high-complexity function(s) need refactoring{C['reset']}")
        if no_docs > 0:
            print(f"  {C['yellow']}📝 {no_docs} function(s) missing docstrings{C['reset']}")


def main():
    parser = argparse.ArgumentParser(description="Code Complexity Analyzer")
    parser.add_argument("path", help="Python file or directory")
    parser.add_argument("--threshold", "-t", type=int, default=10,
                       help="Complexity warning threshold (default: 10)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--recursive", "-r", action="store_true", default=True)

    args = parser.parse_args()
    path = Path(args.path)

    files = []
    if path.is_file():
        files = [path]
    elif path.is_dir():
        pattern = "**/*.py" if args.recursive else "*.py"
        files = sorted(f for f in path.glob(pattern)
                       if ".git" not in f.parts
                       and "__pycache__" not in f.parts
                       and "node_modules" not in f.parts)

    all_metrics = []
    for f in files:
        m = analyze_file(str(f))
        if m and m.total_lines > 0:
            all_metrics.append(m)

    if args.format == "json":
        output = []
        for m in all_metrics:
            d = {
                "filepath": m.filepath,
                "total_lines": m.total_lines,
                "code_lines": m.code_lines,
                "maintainability_index": m.maintainability_index,
                "max_complexity": m.max_complexity,
                "functions": [asdict(f) for f in m.functions],
            }
            output.append(d)
        print(json.dumps(output, indent=2))
        return

    for m in all_metrics:
        print_report(m, args.threshold)

    # Summary
    if len(all_metrics) > 1:
        total_lines = sum(m.code_lines for m in all_metrics)
        total_funcs = sum(len(m.functions) for m in all_metrics)
        all_funcs = [f for m in all_metrics for f in m.functions]
        high_risk = sum(1 for f in all_funcs if f.risk == "high")
        avg_mi = sum(m.maintainability_index for m in all_metrics) / len(all_metrics)

        print(f"\n{'='*65}")
        print(f"📊 SUMMARY: {len(all_metrics)} files | {total_lines} code lines | "
              f"{total_funcs} functions")
        print(f"   Avg Maintainability: {avg_mi:.1f}/100 | "
              f"High-risk functions: {high_risk}")
        print(f"{'='*65}")


if __name__ == "__main__":
    main()
