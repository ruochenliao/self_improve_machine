"""Main entry point: initializes all modules and runs the agent."""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path

import structlog

from agent_core.config import AgentConfig

logger = structlog.get_logger()


async def _start_api_server(api_mgr, host: str = "0.0.0.0", port: int = 8402) -> None:
    """Start the API service server in the background.

    Tries the requested port first; if occupied, tries port+1 through port+9.
    Errors here must NOT crash the main agent loop.
    """
    try:
        await api_mgr.create_app()
        if not api_mgr._app:
            return
        import uvicorn

        # Try a range of ports if the default is occupied
        for attempt_port in range(port, port + 10):
            try:
                config = uvicorn.Config(
                    api_mgr._app, host=host, port=attempt_port, log_level="warning",
                )
                server = uvicorn.Server(config)
                logger.info("api_server.starting", host=host, port=attempt_port)
                await server.serve()
                return  # serve() exited normally (shutdown)
            except OSError as e:
                if "address already in use" in str(e).lower() or getattr(e, "errno", 0) == 48:
                    logger.warning("api_server.port_in_use", port=attempt_port)
                    continue
                raise
        logger.error("api_server.no_available_port", tried=f"{port}-{port+9}")
    except ImportError:
        logger.warning("api_server.uvicorn_not_installed")
    except asyncio.CancelledError:
        pass  # Normal shutdown
    except Exception as e:
        logger.error("api_server.failed", error=str(e))


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

    # Register Stripe provider if configured
    if config.payment.stripe.api_key:
        from agent_core.economy.stripe_provider import StripeProvider
        stripe_prov = StripeProvider(
            api_key=config.payment.stripe.api_key,
            webhook_secret=config.payment.stripe.webhook_secret,
        )
        is_default = config.payment.default_provider == "stripe"
        payment_registry.register(stripe_prov, default=is_default)

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

    # Apply interval configs from toml
    from agent_core.survival.state_machine import SurvivalTier
    intervals = config.survival.intervals
    state_machine.tier_configs[SurvivalTier.NORMAL].loop_interval_sec = intervals.normal_loop_sec
    state_machine.tier_configs[SurvivalTier.NORMAL].heartbeat_interval_sec = intervals.normal_heartbeat_sec
    state_machine.tier_configs[SurvivalTier.LOW_COMPUTE].loop_interval_sec = intervals.low_compute_loop_sec
    state_machine.tier_configs[SurvivalTier.LOW_COMPUTE].heartbeat_interval_sec = intervals.low_compute_heartbeat_sec
    state_machine.tier_configs[SurvivalTier.CRITICAL].loop_interval_sec = intervals.critical_loop_sec
    state_machine.tier_configs[SurvivalTier.CRITICAL].heartbeat_interval_sec = intervals.critical_heartbeat_sec

    # Apply model preferences from config
    models = config.survival.models
    state_machine.tier_configs[SurvivalTier.NORMAL].model_preference = models.normal
    state_machine.tier_configs[SurvivalTier.LOW_COMPUTE].model_preference = models.low_compute
    state_machine.tier_configs[SurvivalTier.CRITICAL].model_preference = models.critical

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

    # Register safe self-modification as a tool
    from agent_core.tools.registry import ToolEntry, ToolResult
    async def _safe_self_modify(file_path: str, new_content: str, description: str) -> ToolResult:
        """Safely modify agent source code with git backup + smoke test + auto-rollback."""
        result = await self_modifier.modify_file(file_path, new_content, description)
        if result["success"]:
            return ToolResult(success=True, output=f"Modified {file_path}: {result['reason']}")
        else:
            return ToolResult(success=False, error=f"Failed: {result['reason']}")

    tool_registry.register(ToolEntry(
        name="safe_self_modify",
        description="Safely modify your own source code. Changes are git-committed, smoke-tested, and auto-rolled back if tests fail. Use for self-improvement.",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Relative path from project root (e.g., 'src/agent_core/income/api_service.py')"},
                "new_content": {"type": "string", "description": "Complete new file content"},
                "description": {"type": "string", "description": "Brief description of the change"},
            },
            "required": ["file_path", "new_content", "description"],
        },
        handler=_safe_self_modify,
        timeout_sec=120,
    ))

    snapshot_mgr = SnapshotManager(data_dir / "snapshots")
    restarter = Restarter(snapshot_mgr)

    # Initialize lineage tracking
    from agent_core.replication.lineage import LineageTracker
    lineage = LineageTracker(db=db)
    # Lineage parent/generation are only set when spawned by a parent agent,
    # NOT from sys.argv (which contains CLI args like --balance).
    head_hash = await git_manager.get_head_hash() or ""
    await lineage.initialize(
        parent_id=None,
        generation=0,
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
    from agent_core.income.api_keys import APIKeyManager

    freelance_mgr = FreelanceManager()
    github_token = config.income.github_token
    if github_token:
        github_platform = GitHubBountyPlatform(github_token=github_token)
        freelance_mgr.register_platform(github_platform)

    api_key_mgr = APIKeyManager(db=db)
    api_service_mgr = APIServiceManager(ledger=ledger, http402_handler=http402_handler, api_key_mgr=api_key_mgr)
    api_service_mgr.alipay_qr_url = config.income.alipay_qr_url
    api_service_mgr.wechat_qr_url = config.income.wechat_qr_url
    digital_store = DigitalAssetStore(db=db, ledger=ledger)

    # Register all API services (handlers defined in api_handlers.py)
    from agent_core.income.api_handlers import register_all_services
    register_all_services(api_service_mgr, router, ledger, state_machine)

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
        balance_monitor=balance_monitor,
    )
    react_loop._api_stats_fn = api_service_mgr.get_stats

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

    # Start API service in background (agent's income endpoint)
    api_port = config.income.api_port
    api_server_task = asyncio.create_task(_start_api_server(api_service_mgr, port=api_port))

    # Run main loop
    try:
        generation = lineage.current.generation if lineage.current else 0
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
                survival_state=state_machine.current_tier.value,
                balance=balance_monitor.balance,
                cycle_count=react_loop.cycle_count,
            )
            await snapshot_mgr.save(final_snapshot)
        except Exception as e:
            logger.error("agent.snapshot_save_failed", error=str(e))

        # Graceful shutdown
        logger.info("agent.shutting_down")
        react_loop.request_stop()
        api_server_task.cancel()
        await heartbeat.stop()
        await db.close()
        logger.info("agent.stopped", cycles=react_loop.cycle_count)

        # If restart was requested, do it now
        if restarter.restart_pending:
            await restarter.graceful_restart(final_snapshot)


async def boot(config_path: str = "config/default.toml", initial_balance: float = 29.65) -> None:
    """Boot the agent from CLI genesis command."""
    project_root = Path.cwd()

    # Seed the initial balance into the ledger before agent starts
    config = AgentConfig.load(project_root)
    data_dir = project_root / config.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)

    from agent_core.storage.database import Database
    from agent_core.economy.ledger import Ledger

    db = Database(data_dir / "agent.db")
    await db.connect()
    await db.init_tables()

    ledger = Ledger(db)
    current = await ledger.get_balance()
    if current < 0.01:
        # First boot — inject seed capital
        await ledger.record_income(
            amount=initial_balance,
            category="seed",
            description=f"Genesis seed capital from creator (${initial_balance:.2f})",
            counterparty="creator",
        )
        logger.info("boot.seed_capital", amount=initial_balance)
    await db.close()

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
