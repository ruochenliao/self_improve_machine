"""Social media promotion tools for automated content distribution.

Supports: Dev.to (API key), Reddit (OAuth script app), Twitter/X (OAuth),
GitHub Discussions (token), and generic webhook posting.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any

import aiohttp
import structlog

from .registry import ToolResult, tool

logger = structlog.get_logger()

# Module-level config holder (set by main.py during boot)
_social_config: dict[str, Any] = {}
_promotion_log: list[dict] = []  # In-memory log, also persisted to DB
_db = None  # Database reference for persistence

# Rate limiting: platform -> (last_post_timestamp, min_interval_seconds)
_rate_limits: dict[str, tuple[float, int]] = {}
_DEFAULT_INTERVALS = {
    "devto": 3600,       # 1 post per hour
    "reddit": 600,       # 1 post per 10 min
    "twitter": 300,      # 1 tweet per 5 min
    "github": 600,       # 1 discussion per 10 min
    "webhook": 60,       # 1 webhook per minute
    "hackernews": 3600,  # 1 post per hour
}


def configure(config: dict[str, Any], db=None) -> None:
    """Configure social media tools with API keys and DB reference.

    Expected config format:
    {
        "devto": {"api_key": "..."},
        "reddit": {"client_id": "...", "client_secret": "...", "username": "...", "password": "..."},
        "twitter": {"api_key": "...", "api_secret": "...", "access_token": "...", "access_secret": "..."},
        "github": {"token": "..."},
        "webhooks": [{"name": "...", "url": "...", "headers": {...}}],
    }
    """
    global _social_config, _db
    _social_config = config
    _db = db
    logger.info("social_media.configured", platforms=list(config.keys()))


def _check_rate_limit(platform: str) -> tuple[bool, str]:
    """Check if posting to platform is allowed by rate limit."""
    now = time.time()
    if platform in _rate_limits:
        last_post, interval = _rate_limits[platform]
        elapsed = now - last_post
        if elapsed < interval:
            remaining = int(interval - elapsed)
            return False, f"Rate limited: wait {remaining}s before posting to {platform} again"
    return True, ""


def _update_rate_limit(platform: str) -> None:
    """Record a post to update rate limiting."""
    interval = _DEFAULT_INTERVALS.get(platform, 300)
    _rate_limits[platform] = (time.time(), interval)


async def _record_promotion(platform: str, content_type: str, title: str, url: str, success: bool, error: str = "") -> None:
    """Record promotion activity to DB and in-memory log."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform": platform,
        "content_type": content_type,
        "title": title,
        "url": url,
        "success": success,
        "error": error,
    }
    _promotion_log.append(entry)

    if _db:
        try:
            await _db.execute(
                "INSERT INTO promotion_log (timestamp, platform, content_type, title, url, success, error) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (entry["timestamp"], platform, content_type, title, url, 1 if success else 0, error),
            )
            await _db.commit()
        except Exception as e:
            logger.warning("social_media.db_log_failed", error=str(e))


def get_available_platforms() -> dict[str, bool]:
    """Return which platforms are configured and ready."""
    return {
        "devto": bool(_social_config.get("devto", {}).get("api_key")),
        "reddit": bool(_social_config.get("reddit", {}).get("client_id") and _social_config.get("reddit", {}).get("client_secret")),
        "twitter": bool(_social_config.get("twitter", {}).get("api_key")),
        "github": bool(_social_config.get("github", {}).get("token")),
        "webhooks": bool(_social_config.get("webhooks")),
    }


def get_promotion_stats() -> dict[str, Any]:
    """Return promotion statistics."""
    total = len(_promotion_log)
    successful = sum(1 for p in _promotion_log if p["success"])
    by_platform: dict[str, int] = {}
    for p in _promotion_log:
        by_platform[p["platform"]] = by_platform.get(p["platform"], 0) + 1
    return {
        "total_posts": total,
        "successful": successful,
        "failed": total - successful,
        "by_platform": by_platform,
        "available_platforms": get_available_platforms(),
    }


# ============================================================
# Dev.to — Public API, API Key auth (no OAuth needed!)
# ============================================================

@tool(
    name="post_to_devto",
    description="Publish an article to Dev.to. Requires devto API key in config. Supports Markdown body with frontmatter tags.",
    parameters={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Article title"},
            "body_markdown": {"type": "string", "description": "Article content in Markdown"},
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Up to 4 tags (e.g., ['ai', 'python', 'api', 'opensource'])",
            },
            "published": {"type": "boolean", "description": "Publish immediately (true) or save as draft (false). Default: false"},
        },
        "required": ["title", "body_markdown"],
    },
    timeout_sec=30,
)
async def post_to_devto(
    title: str,
    body_markdown: str,
    tags: list[str] | None = None,
    published: bool = False,
) -> ToolResult:
    """Post article to Dev.to via their public API."""
    api_key = _social_config.get("devto", {}).get("api_key", "")
    if not api_key:
        return ToolResult(success=False, error="Dev.to API key not configured. Ask creator to set [social.devto] api_key in config.")

    ok, msg = _check_rate_limit("devto")
    if not ok:
        return ToolResult(success=False, error=msg)

    payload = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": published,
            "tags": (tags or [])[:4],
        }
    }

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://dev.to/api/articles",
                headers={"api-key": api_key, "Content-Type": "application/json"},
                json=payload,
            ) as resp:
                body = await resp.text()
                if resp.status in (200, 201):
                    data = json.loads(body)
                    url = data.get("url", "")
                    _update_rate_limit("devto")
                    await _record_promotion("devto", "article", title, url, True)
                    return ToolResult(
                        success=True,
                        output=f"Published to Dev.to: {url}",
                        data={"url": url, "id": data.get("id")},
                    )
                else:
                    await _record_promotion("devto", "article", title, "", False, body[:200])
                    return ToolResult(success=False, error=f"Dev.to API error {resp.status}: {body[:300]}")
    except Exception as e:
        await _record_promotion("devto", "article", title, "", False, str(e))
        return ToolResult(success=False, error=f"Dev.to post failed: {e}")


# ============================================================
# Reddit — OAuth2 "script" app type (no browser needed)
# ============================================================

async def _get_reddit_token() -> str | None:
    """Get Reddit OAuth token using script app credentials."""
    cfg = _social_config.get("reddit", {})
    if not cfg.get("client_id") or not cfg.get("client_secret"):
        return None

    auth = aiohttp.BasicAuth(cfg["client_id"], cfg["client_secret"])
    data = {
        "grant_type": "password",
        "username": cfg.get("username", ""),
        "password": cfg.get("password", ""),
    }

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers={"User-Agent": "SIM-Agent/1.0"},
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("access_token")
    except Exception as e:
        logger.error("reddit.auth_failed", error=str(e))
    return None


@tool(
    name="post_to_reddit",
    description="Submit a post to a Reddit subreddit. Requires Reddit script app credentials in config. Use for genuine, valuable content only.",
    parameters={
        "type": "object",
        "properties": {
            "subreddit": {"type": "string", "description": "Subreddit name without r/ prefix (e.g., 'SideProject')"},
            "title": {"type": "string", "description": "Post title"},
            "text": {"type": "string", "description": "Post body (selftext, Markdown supported)"},
            "url": {"type": "string", "description": "Link URL (for link posts, omit text if using this)"},
        },
        "required": ["subreddit", "title"],
    },
    timeout_sec=30,
)
async def post_to_reddit(
    subreddit: str,
    title: str,
    text: str = "",
    url: str = "",
) -> ToolResult:
    """Submit a post to Reddit via OAuth API."""
    cfg = _social_config.get("reddit", {})
    if not cfg.get("client_id"):
        return ToolResult(success=False, error="Reddit credentials not configured. Ask creator to set [social.reddit] in config.")

    ok, msg = _check_rate_limit("reddit")
    if not ok:
        return ToolResult(success=False, error=msg)

    token = await _get_reddit_token()
    if not token:
        return ToolResult(success=False, error="Reddit OAuth authentication failed. Check credentials.")

    post_data: dict[str, str] = {
        "sr": subreddit,
        "title": title,
        "kind": "link" if url else "self",
    }
    if url:
        post_data["url"] = url
    if text:
        post_data["text"] = text

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://oauth.reddit.com/api/submit",
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "SIM-Agent/1.0",
                },
                data=post_data,
            ) as resp:
                body = await resp.json()
                if resp.status == 200 and not body.get("json", {}).get("errors"):
                    post_url = body.get("json", {}).get("data", {}).get("url", "")
                    _update_rate_limit("reddit")
                    await _record_promotion("reddit", "post", title, post_url, True)
                    return ToolResult(
                        success=True,
                        output=f"Posted to r/{subreddit}: {post_url}",
                        data={"url": post_url},
                    )
                else:
                    errors = body.get("json", {}).get("errors", [])
                    err_msg = str(errors) if errors else await resp.text()
                    await _record_promotion("reddit", "post", title, "", False, err_msg[:200])
                    return ToolResult(success=False, error=f"Reddit submit error: {err_msg[:300]}")
    except Exception as e:
        await _record_promotion("reddit", "post", title, "", False, str(e))
        return ToolResult(success=False, error=f"Reddit post failed: {e}")


# ============================================================
# Twitter/X — OAuth 1.0a
# ============================================================

@tool(
    name="post_to_twitter",
    description="Post a tweet to Twitter/X. Requires Twitter API credentials in config.",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Tweet text (max 280 chars)"},
        },
        "required": ["text"],
    },
    timeout_sec=30,
)
async def post_to_twitter(text: str) -> ToolResult:
    """Post a tweet using Twitter API v2."""
    cfg = _social_config.get("twitter", {})
    if not cfg.get("bearer_token"):
        return ToolResult(success=False, error="Twitter credentials not configured. Ask creator to set [social.twitter] in config.")

    ok, msg = _check_rate_limit("twitter")
    if not ok:
        return ToolResult(success=False, error=msg)

    if len(text) > 280:
        text = text[:277] + "..."

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://api.twitter.com/2/tweets",
                headers={
                    "Authorization": f"Bearer {cfg['bearer_token']}",
                    "Content-Type": "application/json",
                },
                json={"text": text},
            ) as resp:
                body = await resp.text()
                if resp.status in (200, 201):
                    data = json.loads(body)
                    tweet_id = data.get("data", {}).get("id", "")
                    tweet_url = f"https://twitter.com/i/web/status/{tweet_id}" if tweet_id else ""
                    _update_rate_limit("twitter")
                    await _record_promotion("twitter", "tweet", text[:50], tweet_url, True)
                    return ToolResult(
                        success=True,
                        output=f"Tweeted: {tweet_url}",
                        data={"url": tweet_url, "id": tweet_id},
                    )
                else:
                    await _record_promotion("twitter", "tweet", text[:50], "", False, body[:200])
                    return ToolResult(success=False, error=f"Twitter API error {resp.status}: {body[:300]}")
    except Exception as e:
        await _record_promotion("twitter", "tweet", text[:50], "", False, str(e))
        return ToolResult(success=False, error=f"Twitter post failed: {e}")


# ============================================================
# GitHub Discussions
# ============================================================

@tool(
    name="post_github_discussion",
    description="Create a GitHub Discussion in a repository. Requires github token. Good for Show & Tell.",
    parameters={
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Repository owner"},
            "repo": {"type": "string", "description": "Repository name"},
            "title": {"type": "string", "description": "Discussion title"},
            "body": {"type": "string", "description": "Discussion body (Markdown)"},
            "category": {"type": "string", "description": "Discussion category (e.g., 'Show and tell', 'General')"},
        },
        "required": ["owner", "repo", "title", "body"],
    },
    timeout_sec=30,
)
async def post_github_discussion(
    owner: str,
    repo: str,
    title: str,
    body: str,
    category: str = "General",
) -> ToolResult:
    """Create a GitHub Discussion via GraphQL API."""
    token = _social_config.get("github", {}).get("token", "")
    if not token:
        return ToolResult(success=False, error="GitHub token not configured.")

    ok, msg = _check_rate_limit("github")
    if not ok:
        return ToolResult(success=False, error=msg)

    # First get repository and category IDs
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Get repo ID and discussion categories
            query = """query($owner: String!, $repo: String!) {
                repository(owner: $owner, name: $repo) {
                    id
                    discussionCategories(first: 10) {
                        nodes { id name }
                    }
                }
            }"""
            async with session.post(
                "https://api.github.com/graphql",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={"query": query, "variables": {"owner": owner, "repo": repo}},
            ) as resp:
                data = await resp.json()
                repo_data = data.get("data", {}).get("repository", {})
                if not repo_data:
                    return ToolResult(success=False, error=f"Repository {owner}/{repo} not found or no access")

                repo_id = repo_data["id"]
                categories = repo_data.get("discussionCategories", {}).get("nodes", [])
                cat_id = None
                for cat in categories:
                    if cat["name"].lower() == category.lower():
                        cat_id = cat["id"]
                        break
                if not cat_id and categories:
                    cat_id = categories[0]["id"]  # fallback to first category

                if not cat_id:
                    return ToolResult(success=False, error="No discussion categories found. Enable Discussions in repo settings.")

            # Create discussion
            mutation = """mutation($repoId: ID!, $catId: ID!, $title: String!, $body: String!) {
                createDiscussion(input: {repositoryId: $repoId, categoryId: $catId, title: $title, body: $body}) {
                    discussion { url id }
                }
            }"""
            async with session.post(
                "https://api.github.com/graphql",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": mutation,
                    "variables": {"repoId": repo_id, "catId": cat_id, "title": title, "body": body},
                },
            ) as resp:
                result = await resp.json()
                disc = result.get("data", {}).get("createDiscussion", {}).get("discussion", {})
                if disc:
                    disc_url = disc.get("url", "")
                    _update_rate_limit("github")
                    await _record_promotion("github", "discussion", title, disc_url, True)
                    return ToolResult(
                        success=True,
                        output=f"Created discussion: {disc_url}",
                        data={"url": disc_url},
                    )
                else:
                    errors = result.get("errors", [])
                    err_msg = str(errors) if errors else str(result)
                    await _record_promotion("github", "discussion", title, "", False, err_msg[:200])
                    return ToolResult(success=False, error=f"GitHub discussion error: {err_msg[:300]}")
    except Exception as e:
        await _record_promotion("github", "discussion", title, "", False, str(e))
        return ToolResult(success=False, error=f"GitHub discussion failed: {e}")


# ============================================================
# Generic Webhook — for Slack, Discord, custom endpoints
# ============================================================

@tool(
    name="send_webhook",
    description="Send a message via webhook (Slack, Discord, custom). Useful for notifications and cross-posting.",
    parameters={
        "type": "object",
        "properties": {
            "webhook_name": {"type": "string", "description": "Name of configured webhook (from config)"},
            "text": {"type": "string", "description": "Message text"},
            "payload": {"type": "object", "description": "Custom JSON payload (overrides text if provided)"},
        },
        "required": ["webhook_name", "text"],
    },
    timeout_sec=15,
)
async def send_webhook(
    webhook_name: str,
    text: str,
    payload: dict | None = None,
) -> ToolResult:
    """Send a webhook notification."""
    webhooks = _social_config.get("webhooks", [])
    webhook = None
    for wh in webhooks:
        if wh.get("name") == webhook_name:
            webhook = wh
            break

    if not webhook:
        available = [wh.get("name") for wh in webhooks]
        return ToolResult(success=False, error=f"Webhook '{webhook_name}' not found. Available: {available}")

    ok, msg = _check_rate_limit("webhook")
    if not ok:
        return ToolResult(success=False, error=msg)

    url = webhook["url"]
    headers = webhook.get("headers", {"Content-Type": "application/json"})
    body = payload or {"text": text, "content": text}  # 'content' for Discord, 'text' for Slack

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=body) as resp:
                if resp.status in (200, 201, 204):
                    _update_rate_limit("webhook")
                    await _record_promotion("webhook", webhook_name, text[:50], url, True)
                    return ToolResult(success=True, output=f"Webhook '{webhook_name}' sent successfully")
                else:
                    resp_text = await resp.text()
                    return ToolResult(success=False, error=f"Webhook error {resp.status}: {resp_text[:200]}")
    except Exception as e:
        return ToolResult(success=False, error=f"Webhook failed: {e}")


# ============================================================
# Promotion Status Tool — Agent can check what's available
# ============================================================

@tool(
    name="check_promotion_status",
    description="Check which promotion platforms are configured and available, and view recent promotion history.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    timeout_sec=5,
)
async def check_promotion_status() -> ToolResult:
    """Return promotion capabilities and recent history."""
    platforms = get_available_platforms()
    stats = get_promotion_stats()
    recent = _promotion_log[-5:] if _promotion_log else []

    output_lines = ["## Promotion Status"]
    for platform, ready in platforms.items():
        status = "READY" if ready else "NOT CONFIGURED"
        output_lines.append(f"  {platform}: {status}")

    output_lines.append(f"\nTotal posts: {stats['total_posts']} (success: {stats['successful']}, failed: {stats['failed']})")

    if recent:
        output_lines.append("\nRecent activity:")
        for p in recent:
            status = "OK" if p["success"] else f"FAIL: {p['error'][:50]}"
            output_lines.append(f"  [{p['platform']}] {p['title'][:40]} — {status}")

    # Rate limit info
    now = time.time()
    output_lines.append("\nRate limits:")
    for platform, (last_post, interval) in _rate_limits.items():
        remaining = max(0, int(interval - (now - last_post)))
        output_lines.append(f"  {platform}: {'available' if remaining == 0 else f'wait {remaining}s'}")

    return ToolResult(success=True, output="\n".join(output_lines), data=stats)
