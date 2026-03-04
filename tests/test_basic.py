"""Basic tests to verify module structure and imports."""

import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


class TestProjectStructure:
    """Verify project structure is correct."""

    def test_constitution_exists(self):
        assert (PROJECT_ROOT / "CONSTITUTION.md").exists()

    def test_soul_exists(self):
        assert (PROJECT_ROOT / "SOUL.md").exists()

    def test_config_exists(self):
        assert (PROJECT_ROOT / "config" / "default.toml").exists()

    def test_pyproject_exists(self):
        assert (PROJECT_ROOT / "pyproject.toml").exists()


class TestSyntax:
    """Verify all Python files have valid syntax."""

    def test_all_py_files_valid_syntax(self):
        src_dir = PROJECT_ROOT / "src"
        errors = []
        for f in src_dir.rglob("*.py"):
            try:
                compile(f.read_text(encoding="utf-8"), str(f), "exec")
            except SyntaxError as e:
                errors.append(f"{f.relative_to(PROJECT_ROOT)}: {e}")
        assert not errors, f"Syntax errors found:\n" + "\n".join(errors)


class TestConfig:
    """Test configuration loading."""

    def test_config_loads(self):
        from agent_core.config import AgentConfig
        config = AgentConfig.load(PROJECT_ROOT)
        assert config.name == "SIM-Agent"
        assert config.version == "0.1.0"

    def test_config_has_all_sections(self):
        from agent_core.config import AgentConfig
        config = AgentConfig.load(PROJECT_ROOT)
        assert config.llm is not None
        assert config.payment is not None
        assert config.cloud is not None
        assert config.survival is not None
        assert config.memory is not None
        assert config.income is not None
        assert config.self_mod is not None
        assert config.creator is not None

    def test_survival_thresholds(self):
        from agent_core.config import AgentConfig
        config = AgentConfig.load(PROJECT_ROOT)
        assert config.survival.normal_threshold_usd > config.survival.low_compute_threshold_usd
        assert config.survival.low_compute_threshold_usd > config.survival.critical_threshold_usd


class TestSelfMod:
    """Test self-modification module structure."""

    def test_snapshot_create_and_serialize(self):
        from agent_core.self_mod.snapshot import AgentSnapshot
        snap = AgentSnapshot(
            version="test",
            survival_state="NORMAL",
            balance=42.0,
            cycle_count=10,
        )
        d = snap.to_dict()
        assert d["balance"] == 42.0
        assert d["survival_state"] == "NORMAL"

        recovered = AgentSnapshot.from_dict(d)
        assert recovered.balance == 42.0
        assert recovered.cycle_count == 10

    def test_audit_action_enum(self):
        from agent_core.self_mod.audit import AuditAction
        assert AuditAction.SELF_MODIFY.value == "self_modify"
        assert AuditAction.CREATOR_PAYOUT.value == "creator_payout"


class TestLineage:
    """Test lineage tracking."""

    def test_lineage_record_creation(self):
        from agent_core.replication.lineage import LineageRecord
        record = LineageRecord(creator="human", generation=0)
        assert record.instance_id  # Should auto-generate
        assert record.generation == 0
        assert record.creator == "human"

    def test_lineage_to_dict(self):
        from agent_core.replication.lineage import LineageRecord
        record = LineageRecord(instance_id="test-123", generation=1)
        d = record.to_dict()
        assert d["instance_id"] == "test-123"
        assert d["generation"] == 1
