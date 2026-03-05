"""Tests for self-modification system: smoke tests, audit, rollback."""

from __future__ import annotations

import json
import pytest

from agent_core.self_mod.audit import AuditLogger, AuditAction, AuditEntry


class TestAuditAction:
    """Test AuditAction enum."""

    def test_action_values(self):
        assert AuditAction.SELF_MODIFY.value == "self_modify"
        assert AuditAction.ROLLBACK.value == "rollback"
        assert AuditAction.REPLICATE.value == "replicate"
        assert AuditAction.CREATOR_PAYOUT.value == "creator_payout"

    def test_all_actions_are_strings(self):
        for action in AuditAction:
            assert isinstance(action.value, str)


class TestAuditEntry:
    """Test AuditEntry data class."""

    def test_create_entry(self):
        entry = AuditEntry(
            timestamp=1234567890.0,
            action="self_modify",
            description="Modified config.py",
        )
        assert entry.success is True
        assert entry.actor == "agent"

    def test_to_dict(self):
        entry = AuditEntry(
            timestamp=1234567890.0,
            action="test",
            description="test entry",
            details={"key": "value"},
        )
        d = entry.to_dict()
        assert d["action"] == "test"
        assert d["details"]["key"] == "value"

    def test_to_json(self):
        entry = AuditEntry(
            timestamp=1234567890.0,
            action="test",
            description="test json",
        )
        j = entry.to_json()
        parsed = json.loads(j)
        assert parsed["action"] == "test"


class TestAuditLogger:
    """Test AuditLogger file and DB writing."""

    @pytest.mark.asyncio
    async def test_log_action(self, audit_logger):
        entry = await audit_logger.log_action(
            AuditAction.SELF_MODIFY,
            "Modified test.py",
            details={"file": "test.py", "lines_changed": 5},
        )
        assert entry.action == "self_modify"
        assert entry.success is True

    @pytest.mark.asyncio
    async def test_log_action_writes_file(self, audit_logger):
        await audit_logger.log_action(
            AuditAction.CONFIG_CHANGE,
            "Changed heartbeat interval",
        )
        assert audit_logger._log_file.exists()
        content = audit_logger._log_file.read_text()
        assert "config_change" in content

    @pytest.mark.asyncio
    async def test_get_recent(self, audit_logger):
        await audit_logger.log_action(AuditAction.SELF_MODIFY, "mod1")
        await audit_logger.log_action(AuditAction.ROLLBACK, "rollback1")
        await audit_logger.log_action(AuditAction.SELF_MODIFY, "mod2")

        entries = await audit_logger.get_recent(n=10)
        assert len(entries) == 3

    @pytest.mark.asyncio
    async def test_get_recent_with_filter(self, audit_logger):
        await audit_logger.log_action(AuditAction.SELF_MODIFY, "mod")
        await audit_logger.log_action(AuditAction.ROLLBACK, "roll")

        entries = await audit_logger.get_recent(n=10, action="self_modify")
        assert len(entries) == 1
        assert entries[0]["action"] == "self_modify"

    @pytest.mark.asyncio
    async def test_log_failure(self, audit_logger):
        entry = await audit_logger.log_action(
            AuditAction.SELF_MODIFY,
            "Smoke test failed",
            success=False,
        )
        assert entry.success is False

    @pytest.mark.asyncio
    async def test_get_stats(self, audit_logger):
        await audit_logger.log_action(AuditAction.SELF_MODIFY, "mod1")
        await audit_logger.log_action(AuditAction.SELF_MODIFY, "mod2", success=False)
        await audit_logger.log_action(AuditAction.ROLLBACK, "roll1")

        stats = await audit_logger.get_stats()
        assert stats["total"] == 3
        assert "by_action" in stats
        assert stats["by_action"]["self_modify"] == 2


class TestSmokeTest:
    """Test the smoke test runner."""

    def test_syntax_check_valid_code(self, tmp_path):
        # Create a minimal project structure
        src = tmp_path / "src"
        src.mkdir()
        test_file = src / "valid.py"
        test_file.write_text("x = 1 + 2\n")

        import ast
        try:
            ast.parse(test_file.read_text())
            valid = True
        except SyntaxError:
            valid = False
        assert valid is True

    def test_syntax_check_invalid_code(self, tmp_path):
        test_file = tmp_path / "invalid.py"
        test_file.write_text("def broken(\n")

        import ast
        try:
            ast.parse(test_file.read_text())
            valid = True
        except SyntaxError:
            valid = False
        assert valid is False

    @pytest.mark.asyncio
    async def test_run_syntax_check(self, project_root):
        from agent_core.self_mod.smoke_test import SmokeTestRunner
        runner = SmokeTestRunner(project_root=project_root)
        result = await runner.run_syntax_check()
        assert result.passed is True
        assert result.tests_run > 0

    @pytest.mark.asyncio
    async def test_run_import_test(self, project_root):
        from agent_core.self_mod.smoke_test import SmokeTestRunner
        runner = SmokeTestRunner(project_root=project_root)
        result = await runner.run_import_test()
        assert result.tests_run > 0
