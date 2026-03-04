"""Main entry point: initializes all modules and runs the agent."""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path

import structlog

from agent_core.config import AgentConfig

logger = structlog.get_logger()


async def run_agent(
    project_root: Path,
    restore_snapshot: str | None = None,
) -> None:
    """Initialize all modules and run the agent's main loop."""

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    logger.info("agent.starting", project_root=str(project_root))

    # Load config
    config = AgentConfig.load(project_root)
    data_dir = project_root / config.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)

    # Initialize storage
    from agent_core.storage.database import Database
    db = Database(data_dir / "agent.db")
    await db.connect()
    await db.init_tables()

    # Initialize identity
    from agent_core.identity.identity import IdentityManager
    identity = IdentityManager(project_root)
    if not (project_root / "SOUL.md").exists() or "[待初始化]" in identity.read_soul():
        identity.initialize_soul(creator="Creator")
    logger.info("agent.identity", name=identity.name, id=identity.agent_id[:8])

    # Initialize LLM providers
    from agent_core.llm.router import ModelRouter
    router = ModelRouter()

    if config.llm.openai.api_key:
        from agent_core.llm.openai_provider import OpenAIProvider
        for model in config.llm.openai.models:
            provider = OpenAIProvider(
                api_key=config.llm.openai.api_key,
                model_name=model,
                base_url=config.llm.openai.base_url,
            )
            router.register_provider(provider)

    if config.llm.anthropic.api_key:
        from agent_core.llm.anthropic_provider import AnthropicProvider
        for model in config.llm.anthropic.models:
            provider = AnthropicProvider(
                api_key=config.llm.anthropic.api_key,
                model_name=model,
            )
            router.register_provider(provider)

    router.configure_from_config(config)

    # Initialize tools
    from agent_core.tools.registry import ToolRegistry
    from agent_core.tools import shell, code_writer, file_ops, http_client
    tool_registry = ToolRegistry()
    file_ops.set_project_root(project_root)

    # Initialize memory
    from agent_core.memory.vector_store import VectorStore
    from agent_core.memory.rag import RAGEngine
    from agent_core.memory.experience import ExperienceManager
    vector_store = VectorStore(str(data_dir / "chromadb"))
    vector_store.initialize()
    rag_engine = RAGEngine(vector_store, top_k=config.memory.top_k)
    experience_manager = ExperienceManager(vector_store)

    # Initialize economy
    from agent_core.economy.ledger import Ledger
    from agent_core.economy.payment_provider import PaymentProviderRegistry
    from agent_core.economy.http402 import HTTP402Handler

    ledger = Ledger(db)
    payment_registry = PaymentProviderRegistry()

    if config.payment.alipay.app_id:
        from agent_core.economy.alipay_provider import AlipayProvider
        alipay = AlipayProvider(
            app_id=config.payment.alipay.app_id,
            private_key_path=config.payment.alipay.private_key_path,
            alipay_public_key_path=config.payment.alipay.alipay_public_key_path,
            gateway_url=config.payment.alipay.gateway_url,
            sandbox=config.payment.alipay.sandbox,
            notify_url=config.payment.alipay.notify_url,
        )
        payment_registry.register(alipay, default=True)

    http402_handler = HTTP402Handler(payment_registry)
    http_client.set_http402_handler(http402_handler)

    # Initialize survival
    from agent_core.survival.state_machine import SurvivalStateMachine
    from agent_core.survival.balance_monitor import BalanceMonitor
    from agent_core.survival.heartbeat import HeartbeatDaemon

    state_machine = SurvivalStateMachine()
    state_machine.configure_thresholds(
        normal=config.survival.normal_threshold_usd,
        low_compute=config.survival.low_compute_threshold_usd,
        critical=config.survival.critical_threshold_usd,
    )

    balance_monitor = BalanceMonitor(ledger, state_machine)
    heartbeat = HeartbeatDaemon(state_machine, balance_monitor, data_dir)

    # Initialize self-modification system
    from agent_core.self_mod.git_manager import GitManager
    from agent_core.self_mod.audit import AuditLogger
    from agent_core.self_mod.self_modifier import SelfModifier
    from agent_core.self_mod.snapshot import SnapshotManager, AgentSnapshot
    from agent_core.self_mod.restarter import Restarter

    git_manager = GitManager(project_root)
    await git_manager.init_repo()
    audit_logger = AuditLogger(db=db, log_dir=data_dir / "audit")
    self_modifier = SelfModifier(
        project_root=project_root,
        git=git_manager,
        audit=audit_logger,
    )
    await self_modifier.initialize()

    snapshot_mgr = SnapshotManager(data_dir / "snapshots")
    restarter = Restarter(snapshot_mgr)

    # Initialize lineage tracking
    from agent_core.replication.lineage import LineageTracker
    lineage = LineageTracker(db=db)
    parent_id = sys.argv[1] if len(sys.argv) > 1 else None
    generation = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    head_hash = await git_manager.get_head_hash() or ""
    await lineage.initialize(
        parent_id=parent_id,
        generation=generation,
        source_commit=head_hash,
    )

    # Initialize infrastructure (cloud providers)
    from agent_core.infrastructure.cloud_provider import CloudProviderRegistry
    cloud_registry = CloudProviderRegistry()

    if config.cloud.aliyun.access_key_id:
        from agent_core.infrastructure.aliyun_provider import AliyunProvider
        aliyun = AliyunProvider(
            access_key_id=config.cloud.aliyun.access_key_id,
            access_key_secret=config.cloud.aliyun.access_key_secret,
            region_id=config.cloud.aliyun.region_id,
        )
        cloud_registry.register(aliyun, default=True)

    # Initialize replication
    from agent_core.replication.replicator import ReplicationManager
    replication_mgr = ReplicationManager(
        cloud_registry=cloud_registry,
        audit=audit_logger,
        project_root=project_root,
    )

    # Initialize income systems
    from agent_core.income.freelance import FreelanceManager, GitHubBountyPlatform
    from agent_core.income.api_service import APIServiceManager
    from agent_core.income.digital_assets import DigitalAssetStore

    freelance_mgr = FreelanceManager()
    github_token = config.income.github_token
    if github_token:
        github_platform = GitHubBountyPlatform(github_token=github_token)
        freelance_mgr.register_platform(github_platform)

    api_service_mgr = APIServiceManager(ledger=ledger, http402_handler=http402_handler)
    digital_store = DigitalAssetStore(db=db, ledger=ledger)

    # Initialize constitution
    from agent_core.agent.constitution import ConstitutionGuard
    constitution = ConstitutionGuard(project_root / "CONSTITUTION.md")
    constitution.initialize()

    # Initialize context manager
    from agent_core.agent.context import ContextManager
    context_manager = ContextManager(
        identity=identity,
        state_machine=state_machine,
        balance_monitor=balance_monitor,
        tool_registry=tool_registry,
        rag_engine=rag_engine,
    )

    # Initialize ReAct loop
    from agent_core.agent.react_loop import ReActLoop
    react_loop = ReActLoop(
        context_manager=context_manager,
        model_router=router,
        tool_registry=tool_registry,
        state_machine=state_machine,
        constitution=constitution,
        experience_manager=experience_manager,
        ledger=ledger,
    )

    # Restore snapshot if requested
    if restore_snapshot:
        snapshot = await snapshot_mgr.load(restore_snapshot)
        if snapshot:
            state_machine.update_balance(snapshot.balance)
            react_loop._cycle_count = snapshot.cycle_count
            logger.info("agent.snapshot_restored", snapshot=restore_snapshot)
    else:
        # Check for auto-recovery after restart
        recovered = await restarter.recover_from_snapshot()
        if recovered:
            state_machine.update_balance(recovered.balance)
            react_loop._cycle_count = recovered.cycle_count
            logger.info("agent.auto_recovered", cycle=recovered.cycle_count)

    # Initial balance check
    await balance_monitor.check()

    # Setup graceful shutdown
    shutdown_event = asyncio.Event()

    def handle_signal(sig: int, frame) -> None:
        logger.info("agent.signal_received", signal=sig)
        react_loop.request_stop()
        shutdown_event.set()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # Register restarter shutdown callback
    restarter.on_shutdown(lambda: heartbeat.stop())
    restarter.on_shutdown(lambda: db.close())

    # Start heartbeat
    await heartbeat.start()

    # Run main loop
    try:
        logger.info(
            "agent.running",
            name=identity.name,
            instance=lineage.current.instance_id if lineage.current else "unknown",
            generation=generation,
        )
        await react_loop.run()
    except KeyboardInterrupt:
        logger.info("agent.keyboard_interrupt")
    finally:
        # Save final snapshot before shutdown
        try:
            final_snapshot = AgentSnapshot(
                version=identity.agent_id,
                survival_state=state_machine.state.value if hasattr(state_machine, 'state') else "unknown",
                balance=balance_monitor.current_balance if hasattr(balance_monitor, 'current_balance') else 0.0,
                cycle_count=react_loop.cycle_count,
            )
            await snapshot_mgr.save(final_snapshot)
        except Exception as e:
            logger.error("agent.snapshot_save_failed", error=str(e))

        # Graceful shutdown
        logger.info("agent.shutting_down")
        react_loop.request_stop()
        await heartbeat.stop()
        await db.close()
        logger.info("agent.stopped", cycles=react_loop.cycle_count)

        # If restart was requested, do it now
        if restarter.restart_pending:
            await restarter.graceful_restart(final_snapshot)


async def boot(config_path: str = "config/default.toml", initial_balance: float = 10.0) -> None:
    """Boot the agent from CLI genesis command."""
    project_root = Path.cwd()
    # TODO: Set initial balance in ledger on first boot
    await run_agent(project_root)


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Self-Improving Machine Agent")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--restore-snapshot", default=None, help="Restore from snapshot file")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    asyncio.run(run_agent(project_root, args.restore_snapshot))


if __name__ == "__main__":
    main()
