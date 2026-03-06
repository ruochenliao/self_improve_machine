"""Dynamic DNS updater for Aliyun DNS.

Detects the machine's current public IP and updates the DNS A record
for swifthelix.asia, so the domain always points to wherever the agent
is running — even if the MacBook's IP changes.

Can run as:
  - One-shot: python -m agent_core.infrastructure.ddns
  - Background daemon: ddns_daemon() — checks every 5 minutes
  - Integrated into start.sh
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path

import structlog

logger = structlog.get_logger()

# --- Config ---
DOMAIN = os.environ.get("DDNS_DOMAIN", "swifthelix.asia")
RR = os.environ.get("DDNS_RR", "@")  # Record prefix: "@" = root, "www" = www.domain
TTL = int(os.environ.get("DDNS_TTL", "600"))  # 10 minutes
CHECK_INTERVAL = int(os.environ.get("DDNS_INTERVAL", "300"))  # 5 minutes

# Aliyun credentials (reuse from config or env)
AK_ID = os.environ.get("ALIYUN_AK_ID", "")
AK_SECRET = os.environ.get("ALIYUN_AK_SECRET", "")

# Cache file to avoid unnecessary API calls
_CACHE_FILE = Path(__file__).parent.parent.parent.parent / "data" / "ddns_cache.json"


def get_public_ip() -> str | None:
    """Get the machine's current public IPv4 address."""
    import urllib.request

    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
        "https://ipinfo.io/ip",
    ]
    for url in services:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ddns/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                ip = resp.read().decode().strip()
                # Basic IPv4 validation
                parts = ip.split(".")
                if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                    return ip
        except Exception:
            continue
    return None


def _load_cache() -> dict:
    """Load cached DNS state."""
    try:
        if _CACHE_FILE.exists():
            return json.loads(_CACHE_FILE.read_text())
    except Exception:
        pass
    return {}


def _save_cache(data: dict) -> None:
    """Save DNS state cache."""
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def _get_dns_client():
    """Create Aliyun DNS API client."""
    try:
        from alibabacloud_alidns20150109.client import Client as DnsClient
        from alibabacloud_tea_openapi.models import Config

        ak_id = AK_ID or os.environ.get("SIM_CLOUD_ALIYUN_ACCESS_KEY_ID", "")
        ak_secret = AK_SECRET or os.environ.get("SIM_CLOUD_ALIYUN_ACCESS_KEY_SECRET", "")

        # Fallback: read from project config TOML
        if not ak_id or not ak_secret:
            try:
                config_path = Path(__file__).parent.parent.parent.parent / "config" / "default.toml"
                if config_path.exists():
                    import tomli
                    with open(config_path, "rb") as f:
                        toml_data = tomli.load(f)
                    cloud = toml_data.get("cloud", {}).get("aliyun", {})
                    ak_id = ak_id or cloud.get("access_key_id", "")
                    ak_secret = ak_secret or cloud.get("access_key_secret", "")
            except Exception:
                pass

        if not ak_id or not ak_secret:
            logger.error("ddns.no_credentials", hint="Set ALIYUN_AK_ID & ALIYUN_AK_SECRET")
            return None

        config = Config(
            access_key_id=ak_id,
            access_key_secret=ak_secret,
        )
        config.endpoint = "alidns.cn-hangzhou.aliyuncs.com"
        return DnsClient(config)
    except ImportError:
        logger.error("ddns.sdk_missing", hint="pip install alibabacloud_alidns20150109")
        return None


def _get_current_record(client, domain: str, rr: str) -> dict | None:
    """Get the current DNS A record."""
    try:
        from alibabacloud_alidns20150109.models import DescribeDomainRecordsRequest

        req = DescribeDomainRecordsRequest(
            domain_name=domain,
            rrkey_word=rr,
            type="A",
        )
        resp = client.describe_domain_records(req)
        records = resp.body.domain_records.record if resp.body.domain_records else []
        for rec in records:
            if rec.rr == rr and rec.type == "A":
                return {
                    "record_id": rec.record_id,
                    "rr": rec.rr,
                    "value": rec.value,
                    "ttl": rec.ttl,
                }
    except Exception as e:
        logger.error("ddns.get_record_failed", error=str(e))
    return None


def _update_record(client, record_id: str, rr: str, ip: str, ttl: int) -> bool:
    """Update an existing DNS A record."""
    try:
        from alibabacloud_alidns20150109.models import UpdateDomainRecordRequest

        req = UpdateDomainRecordRequest(
            record_id=record_id,
            rr=rr,
            type="A",
            value=ip,
            ttl=ttl,
        )
        client.update_domain_record(req)
        logger.info("ddns.record_updated", rr=rr, ip=ip, ttl=ttl)
        return True
    except Exception as e:
        logger.error("ddns.update_failed", error=str(e))
        return False


def _add_record(client, domain: str, rr: str, ip: str, ttl: int) -> bool:
    """Add a new DNS A record."""
    try:
        from alibabacloud_alidns20150109.models import AddDomainRecordRequest

        req = AddDomainRecordRequest(
            domain_name=domain,
            rr=rr,
            type="A",
            value=ip,
            ttl=ttl,
        )
        client.add_domain_record(req)
        logger.info("ddns.record_added", domain=domain, rr=rr, ip=ip)
        return True
    except Exception as e:
        logger.error("ddns.add_failed", error=str(e))
        return False


def update_dns(domain: str = DOMAIN, rr: str = RR, ttl: int = TTL) -> dict:
    """One-shot DNS update. Returns status dict.

    Returns:
        {"success": bool, "ip": str, "changed": bool, "message": str}
    """
    # 1. Get current public IP
    current_ip = get_public_ip()
    if not current_ip:
        return {"success": False, "ip": "", "changed": False, "message": "Cannot detect public IP"}

    # 2. Check cache — skip API call if IP unchanged
    cache = _load_cache()
    if cache.get("ip") == current_ip and cache.get("domain") == domain and cache.get("rr") == rr:
        age = time.time() - cache.get("updated_at", 0)
        if age < CHECK_INTERVAL:
            return {"success": True, "ip": current_ip, "changed": False, "message": "IP unchanged (cached)"}

    # 3. Get DNS client
    client = _get_dns_client()
    if not client:
        return {"success": False, "ip": current_ip, "changed": False, "message": "DNS client init failed"}

    # 4. Check current record
    record = _get_current_record(client, domain, rr)

    if record and record["value"] == current_ip:
        # IP already correct
        _save_cache({"ip": current_ip, "domain": domain, "rr": rr, "updated_at": time.time()})
        return {"success": True, "ip": current_ip, "changed": False, "message": "DNS already correct"}

    # 5. Update or create record
    if record:
        ok = _update_record(client, record["record_id"], rr, current_ip, ttl)
    else:
        ok = _add_record(client, domain, rr, current_ip, ttl)

    if ok:
        _save_cache({"ip": current_ip, "domain": domain, "rr": rr, "updated_at": time.time()})
        msg = f"DNS updated: {rr}.{domain} → {current_ip}"
        # Also update www subdomain if updating root
        if rr == "@":
            www_record = _get_current_record(client, domain, "www")
            if www_record:
                _update_record(client, www_record["record_id"], "www", current_ip, ttl)
            else:
                _add_record(client, domain, "www", current_ip, ttl)
            msg += f" (+ www.{domain})"
        return {"success": True, "ip": current_ip, "changed": True, "message": msg}
    else:
        return {"success": False, "ip": current_ip, "changed": False, "message": "DNS update API call failed"}


async def ddns_daemon(
    domain: str = DOMAIN,
    rr: str = RR,
    interval: int = CHECK_INTERVAL,
) -> None:
    """Background daemon that checks and updates DNS every `interval` seconds."""
    logger.info("ddns.daemon_started", domain=domain, rr=rr, interval=interval)

    while True:
        try:
            result = update_dns(domain, rr)
            if result["changed"]:
                logger.info("ddns.ip_changed", **result)
            else:
                logger.debug("ddns.check_ok", ip=result.get("ip", "?"))
        except Exception as e:
            logger.error("ddns.daemon_error", error=str(e))

        await asyncio.sleep(interval)


# --- CLI entry point ---
if __name__ == "__main__":
    import sys

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )

    if "--daemon" in sys.argv:
        print(f"Starting DDNS daemon for {DOMAIN} (check every {CHECK_INTERVAL}s)")
        asyncio.run(ddns_daemon())
    else:
        result = update_dns()
        print(f"{'✓' if result['success'] else '✗'} {result['message']}")
        if result.get("ip"):
            print(f"  Public IP: {result['ip']}")
        sys.exit(0 if result["success"] else 1)
