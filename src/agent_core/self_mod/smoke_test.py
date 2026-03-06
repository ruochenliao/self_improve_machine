"""Smoke test runner for validating self-modifications."""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path

import structlog

log = structlog.get_logger()


@dataclass
class SmokeTestResult:
    """Result of a smoke test run."""
    passed: bool
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


class SmokeTestRunner:
    """Runs smoke tests to verify agent integrity after self-modification."""

    def __init__(self, project_root: Path | str | None = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()

    async def run_import_test(self) -> SmokeTestResult:
        """Test that all core modules can be imported.

        Uses dynamic discovery: scans src/agent_core for all .py files that
        define real modules (not just __init__), then also checks a hardcoded
        list of critical modules for safety.
        """
        import time
        start = time.monotonic()

        # --- Critical modules that MUST always be tested ---
        critical_modules = {
            "agent_core.config",
            "agent_core.storage.database",
            "agent_core.identity.identity",
            "agent_core.llm.base",
            "agent_core.llm.router",
            "agent_core.survival.state_machine",
            "agent_core.survival.balance_monitor",
            "agent_core.economy.payment_provider",
            "agent_core.economy.ledger",
            "agent_core.tools.registry",
            "agent_core.memory.vector_store",
            "agent_core.memory.rag",
            "agent_core.agent.react_loop",
            "agent_core.income.api_service",
            "agent_core.income.api_handlers",
            "agent_core.income.api_keys",
        }

        # --- Dynamic discovery: all .py under src/agent_core ---
        discovered: set[str] = set()
        agent_core_dir = self.project_root / "src" / "agent_core"
        if agent_core_dir.is_dir():
            for py_file in agent_core_dir.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                # Convert path to module name
                rel = py_file.relative_to(self.project_root / "src")
                mod_name = str(rel.with_suffix("")).replace("/", ".").replace("\\", ".")
                discovered.add(mod_name)

        modules = sorted(critical_modules | discovered)
        errors: list[str] = []
        passed_count = 0
        for mod in modules:
            try:
                __import__(mod)
                passed_count += 1
            except Exception as e:
                errors.append(f"Import {mod}: {e}")

        elapsed = time.monotonic() - start
        return SmokeTestResult(
            passed=len(errors) == 0,
            tests_run=len(modules),
            tests_passed=passed_count,
            tests_failed=len(errors),
            errors=errors,
            duration_seconds=elapsed,
        )

    async def run_syntax_check(self) -> SmokeTestResult:
        """Check all .py files for syntax errors."""
        import time
        start = time.monotonic()
        src_dir = self.project_root / "src"
        py_files = list(src_dir.rglob("*.py"))
        errors: list[str] = []
        passed_count = 0
        for f in py_files:
            try:
                compile(f.read_text(encoding="utf-8"), str(f), "exec")
                passed_count += 1
            except SyntaxError as e:
                errors.append(f"{f.relative_to(self.project_root)}: {e}")

        elapsed = time.monotonic() - start
        return SmokeTestResult(
            passed=len(errors) == 0,
            tests_run=len(py_files),
            tests_passed=passed_count,
            tests_failed=len(errors),
            errors=errors,
            duration_seconds=elapsed,
        )

    async def run_pytest(self, timeout: int = 60) -> SmokeTestResult:
        """Run pytest with a timeout."""
        import time
        start = time.monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pytest", "tests/", "-x", "-q",
                "--tb=short", "--no-header",
                cwd=str(self.project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            elapsed = time.monotonic() - start
            output = stdout.decode()
            passed = proc.returncode == 0

            # Parse pytest output for counts
            tests_run = tests_passed = tests_failed = 0
            for line in output.splitlines():
                if "passed" in line or "failed" in line:
                    import re
                    m_passed = re.search(r"(\d+) passed", line)
                    m_failed = re.search(r"(\d+) failed", line)
                    if m_passed:
                        tests_passed = int(m_passed.group(1))
                    if m_failed:
                        tests_failed = int(m_failed.group(1))
                    tests_run = tests_passed + tests_failed

            errors = []
            if not passed:
                errors.append(output[-500:] if len(output) > 500 else output)

            return SmokeTestResult(
                passed=passed,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                errors=errors,
                duration_seconds=elapsed,
            )
        except asyncio.TimeoutError:
            return SmokeTestResult(
                passed=False,
                errors=[f"Pytest timed out after {timeout}s"],
                duration_seconds=timeout,
            )
        except Exception as e:
            elapsed = time.monotonic() - start
            return SmokeTestResult(
                passed=False,
                errors=[f"Pytest execution error: {e}"],
                duration_seconds=elapsed,
            )

    async def run_all(self) -> SmokeTestResult:
        """Run all smoke tests. Returns combined result."""
        import time
        start = time.monotonic()

        results = await asyncio.gather(
            self.run_syntax_check(),
            self.run_import_test(),
        )

        all_errors: list[str] = []
        total_run = total_passed = total_failed = 0
        all_passed = True

        for r in results:
            total_run += r.tests_run
            total_passed += r.tests_passed
            total_failed += r.tests_failed
            all_errors.extend(r.errors)
            if not r.passed:
                all_passed = False

        elapsed = time.monotonic() - start
        result = SmokeTestResult(
            passed=all_passed,
            tests_run=total_run,
            tests_passed=total_passed,
            tests_failed=total_failed,
            errors=all_errors,
            duration_seconds=elapsed,
        )

        log.info(
            "smoke_test.complete",
            passed=result.passed,
            tests_run=result.tests_run,
            failures=result.tests_failed,
            duration=f"{result.duration_seconds:.2f}s",
        )
        return result
