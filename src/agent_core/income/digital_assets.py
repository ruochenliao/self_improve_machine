"""Digital asset marketplace — sell code templates, prompts, tools."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

log = structlog.get_logger()


@dataclass
class DigitalAsset:
    """A digital asset that can be sold."""
    asset_id: str
    name: str
    description: str
    category: str  # "code_template", "prompt", "tool", "dataset", "api_wrapper"
    price: float
    currency: str = "USD"
    content: str = ""  # The actual asset content
    downloads: int = 0
    rating: float = 0.0
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class DigitalAssetStore:
    """
    Manages the agent's digital asset store.

    The agent can create and sell:
    - Code templates and boilerplates
    - Prompt engineering templates
    - Automation scripts and tools
    - API wrappers and SDKs
    - Curated datasets
    """

    def __init__(self, db=None, ledger=None):
        self.db = db
        self.ledger = ledger
        self.assets: dict[str, DigitalAsset] = {}

    async def create_asset(
        self,
        name: str,
        description: str,
        category: str,
        price: float,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> DigitalAsset:
        """Create a new digital asset for sale."""
        asset_id = f"asset_{int(time.time())}_{len(self.assets)}"
        asset = DigitalAsset(
            asset_id=asset_id,
            name=name,
            description=description,
            category=category,
            price=price,
            content=content,
            metadata=metadata or {},
        )
        self.assets[asset_id] = asset

        # Persist to DB
        if self.db:
            try:
                await self.db.execute(
                    """INSERT INTO digital_assets 
                       (asset_id, name, description, category, price, content, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (asset_id, name, description, category, price, content, asset.created_at),
                )
            except Exception as e:
                log.error("digital_assets.save_failed", error=str(e))

        log.info(
            "digital_assets.created",
            asset_id=asset_id,
            name=name,
            price=price,
            category=category,
        )
        return asset

    async def sell_asset(self, asset_id: str, buyer_info: dict[str, Any] | None = None) -> Optional[dict]:
        """Process a sale of a digital asset."""
        asset = self.assets.get(asset_id)
        if not asset:
            return None

        asset.downloads += 1

        # Record revenue
        if self.ledger:
            await self.ledger.record_income(
                amount=asset.price,
                source=f"digital_asset:{asset.name}",
                description=f"Sale of {asset.name}",
            )

        log.info(
            "digital_assets.sold",
            asset_id=asset_id,
            price=asset.price,
            total_downloads=asset.downloads,
        )

        return {
            "asset_id": asset_id,
            "name": asset.name,
            "content": asset.content,
            "price": asset.price,
        }

    async def list_assets(self, category: Optional[str] = None) -> list[dict[str, Any]]:
        """List available assets."""
        result = []
        for asset in self.assets.values():
            if category and asset.category != category:
                continue
            result.append({
                "asset_id": asset.asset_id,
                "name": asset.name,
                "description": asset.description,
                "category": asset.category,
                "price": asset.price,
                "downloads": asset.downloads,
                "rating": asset.rating,
            })
        return result

    def get_revenue_stats(self) -> dict[str, Any]:
        """Get revenue statistics from digital assets."""
        total_revenue = sum(a.price * a.downloads for a in self.assets.values())
        total_sales = sum(a.downloads for a in self.assets.values())
        return {
            "total_assets": len(self.assets),
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "by_category": self._revenue_by_category(),
        }

    def _revenue_by_category(self) -> dict[str, float]:
        cats: dict[str, float] = {}
        for a in self.assets.values():
            rev = a.price * a.downloads
            cats[a.category] = cats.get(a.category, 0) + rev
        return cats
