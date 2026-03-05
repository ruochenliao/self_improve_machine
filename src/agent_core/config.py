"""Configuration management using Pydantic Settings + TOML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tomli
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class OpenAIConfig(BaseModel):
    api_key: str = ""
    models: list[str] = Field(default_factory=lambda: [
        "deepseek-chat", "gemini-2.5-flash", "gpt-4o-mini",
        "gpt-4o", "claude-sonnet-4-20250514",
    ])
    base_url: str = "https://api.closeai-asia.com/v1"


class AnthropicConfig(BaseModel):
    api_key: str = ""
    models: list[str] = Field(default_factory=list)


class LLMConfig(BaseModel):
    default_provider: str = "openai"
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)


class AlipayConfig(BaseModel):
    app_id: str = ""
    private_key_path: str = ""
    alipay_public_key_path: str = ""
    gateway_url: str = "https://openapi.alipay.com/gateway.do"
    sandbox: bool = True
    notify_url: str = ""


class StripeConfig(BaseModel):
    api_key: str = ""
    webhook_secret: str = ""


class PaymentConfig(BaseModel):
    default_provider: str = "alipay"
    alipay: AlipayConfig = Field(default_factory=AlipayConfig)
    stripe: StripeConfig = Field(default_factory=StripeConfig)


class AliyunConfig(BaseModel):
    access_key_id: str = ""
    access_key_secret: str = ""
    region_id: str = "cn-hangzhou"
    default_instance_type: str = "ecs.t6-c1m1.large"
    default_image_id: str = "ubuntu_22_04_x64_20G_alibase_20240130.vhd"
    security_group_id: str = ""
    vswitch_id: str = ""


class CloudConfig(BaseModel):
    default_provider: str = "aliyun"
    aliyun: AliyunConfig = Field(default_factory=AliyunConfig)


class SurvivalIntervalsConfig(BaseModel):
    normal_heartbeat_sec: int = 5
    low_compute_heartbeat_sec: int = 60
    critical_heartbeat_sec: int = 120
    normal_loop_sec: int = 5
    low_compute_loop_sec: int = 30
    critical_loop_sec: int = 60


class SurvivalModelsConfig(BaseModel):
    normal: list[str] = Field(default_factory=lambda: ["deepseek-chat", "gpt-4o-mini", "gemini-2.5-flash"])
    low_compute: list[str] = Field(default_factory=lambda: ["deepseek-chat", "gemini-2.5-flash-lite"])
    critical: list[str] = Field(default_factory=lambda: ["deepseek-chat"])


class SurvivalConfig(BaseModel):
    normal_threshold_usd: float = 100.0
    low_compute_threshold_usd: float = 5.0
    critical_threshold_usd: float = 0.50
    intervals: SurvivalIntervalsConfig = Field(default_factory=SurvivalIntervalsConfig)
    models: SurvivalModelsConfig = Field(default_factory=SurvivalModelsConfig)


class MemoryConfig(BaseModel):
    chromadb_path: str = "data/chromadb"
    top_k: int = 5


class DevtoConfig(BaseModel):
    api_key: str = ""


class RedditConfig(BaseModel):
    client_id: str = ""
    client_secret: str = ""
    username: str = ""
    password: str = ""


class TwitterConfig(BaseModel):
    bearer_token: str = ""
    api_key: str = ""
    api_secret: str = ""
    access_token: str = ""
    access_secret: str = ""


class WebhookConfig(BaseModel):
    name: str = ""
    url: str = ""
    headers: dict[str, str] = Field(default_factory=dict)


class SocialConfig(BaseModel):
    devto: DevtoConfig = Field(default_factory=DevtoConfig)
    reddit: RedditConfig = Field(default_factory=RedditConfig)
    twitter: TwitterConfig = Field(default_factory=TwitterConfig)
    webhooks: list[WebhookConfig] = Field(default_factory=list)


class IncomeConfig(BaseModel):
    api_port: int = 8402
    api_host: str = "0.0.0.0"
    github_token: str = ""
    alipay_qr_url: str = ""
    wechat_qr_url: str = ""


class SelfModConfig(BaseModel):
    watchdog_timeout_sec: int = 30
    snapshot_dir: str = "data/snapshots"
    max_snapshots: int = 5


class CreatorConfig(BaseModel):
    share_percentage: float = 30.0
    share_pause_threshold_usd: float = 5.0
    payout_method: str = "alipay"
    creator_account: str = ""


class AgentConfig(BaseSettings):
    """Root configuration model. Loads from TOML file + environment variables."""

    name: str = "SIM-Agent"
    version: str = "0.1.0"
    data_dir: str = "data"

    llm: LLMConfig = Field(default_factory=LLMConfig)
    payment: PaymentConfig = Field(default_factory=PaymentConfig)
    cloud: CloudConfig = Field(default_factory=CloudConfig)
    survival: SurvivalConfig = Field(default_factory=SurvivalConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    income: IncomeConfig = Field(default_factory=IncomeConfig)
    social: SocialConfig = Field(default_factory=SocialConfig)
    self_mod: SelfModConfig = Field(default_factory=SelfModConfig)
    creator: CreatorConfig = Field(default_factory=CreatorConfig)

    model_config = {
        "env_prefix": "SIM_",
        "env_nested_delimiter": "__",
    }

    @classmethod
    def from_toml(cls, config_path: str | Path) -> AgentConfig:
        """Load configuration from a TOML file, merged with env vars."""
        path = Path(config_path)
        if path.exists():
            with open(path, "rb") as f:
                data = tomli.load(f)
            # Flatten nested TOML sections into the model
            flat = _flatten_toml(data)
            return cls(**flat)
        return cls()

    @classmethod
    def load(cls, project_root: str | Path | None = None) -> AgentConfig:
        """Load config from default.toml in project root, with env var overrides."""
        if project_root is None:
            project_root = Path.cwd()
        config_path = Path(project_root) / "config" / "default.toml"
        return cls.from_toml(config_path)


def _flatten_toml(data: dict[str, Any]) -> dict[str, Any]:
    """Convert TOML nested dict to match Pydantic model structure."""
    result: dict[str, Any] = {}

    # Top-level agent config
    if "agent" in data:
        agent = data["agent"]
        for k, v in agent.items():
            result[k] = v

    # LLM config
    if "llm" in data:
        result["llm"] = data["llm"]

    # Payment config
    if "payment" in data:
        result["payment"] = data["payment"]

    # Cloud config
    if "cloud" in data:
        result["cloud"] = data["cloud"]

    # Survival config
    if "survival" in data:
        result["survival"] = data["survival"]

    # Memory config
    if "memory" in data:
        result["memory"] = data["memory"]

    # Income config
    if "income" in data:
        result["income"] = data["income"]

    # Self-mod config
    if "self_mod" in data:
        result["self_mod"] = data["self_mod"]

    # Creator config
    if "creator" in data:
        result["creator"] = data["creator"]

    return result
