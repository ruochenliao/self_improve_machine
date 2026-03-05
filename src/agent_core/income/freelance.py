"""Freelance platform integration for earning income."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import structlog

log = structlog.get_logger()


class TaskStatus(str, Enum):
    OPEN = "open"
    APPLIED = "applied"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    REJECTED = "rejected"


@dataclass
class FreelanceTask:
    """A task/bounty from a freelance platform."""
    task_id: str
    platform: str
    title: str
    description: str
    reward: float
    currency: str = "USD"
    status: TaskStatus = TaskStatus.OPEN
    skills_required: list[str] = field(default_factory=list)
    deadline: Optional[float] = None
    url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class FreelancePlatform(ABC):
    """Abstract base for freelance platform integrations."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def search_tasks(
        self,
        skills: list[str] | None = None,
        min_reward: float = 0,
        max_results: int = 10,
    ) -> list[FreelanceTask]:
        """Search for available tasks/bounties."""
        ...

    @abstractmethod
    async def apply_for_task(self, task_id: str, proposal: str) -> bool:
        """Apply for a task with a proposal."""
        ...

    @abstractmethod
    async def submit_work(self, task_id: str, deliverables: dict[str, Any]) -> bool:
        """Submit completed work."""
        ...

    @abstractmethod
    async def check_payment(self, task_id: str) -> Optional[float]:
        """Check if payment has been received for a task."""
        ...


class GitHubBountyPlatform(FreelancePlatform):
    """
    GitHub-based bounty hunting.
    
    Searches for issues with bounty labels and attempts to solve them.
    Revenue: Bug bounties, sponsored issues, open-source grants.
    """

    @property
    def name(self) -> str:
        return "github_bounty"

    def __init__(self, github_token: str = "", http_client=None):
        self.token = github_token
        self.http = http_client
        self._base_url = "https://api.github.com"

    async def search_tasks(
        self,
        skills: list[str] | None = None,
        min_reward: float = 0,
        max_results: int = 10,
    ) -> list[FreelanceTask]:
        """Search GitHub for bounty-labeled issues."""
        if not self.http:
            log.warning("github_bounty.no_http_client")
            return []

        # Search for issues with bounty/reward labels
        queries = [
            'label:"bounty" state:open',
            'label:"reward" state:open',
            'label:"help wanted" label:"good first issue" state:open',
        ]

        tasks: list[FreelanceTask] = []
        for query in queries:
            try:
                headers = {"Accept": "application/vnd.github.v3+json"}
                if self.token:
                    headers["Authorization"] = f"token {self.token}"

                url = f"{self._base_url}/search/issues?q={query}&per_page={max_results}"
                resp = await self.http.get(url, headers=headers)

                if resp and resp.get("items"):
                    for item in resp["items"][:max_results]:
                        # Try to extract reward amount from labels/body
                        reward = self._extract_reward(item)
                        if reward < min_reward:
                            continue

                        task = FreelanceTask(
                            task_id=str(item["id"]),
                            platform=self.name,
                            title=item["title"],
                            description=item.get("body", "")[:500],
                            reward=reward,
                            url=item["html_url"],
                            skills_required=skills or [],
                            metadata={
                                "repo": item.get("repository_url", ""),
                                "labels": [l["name"] for l in item.get("labels", [])],
                            },
                        )
                        tasks.append(task)
            except Exception as e:
                log.error("github_bounty.search_error", error=str(e))

        log.info("github_bounty.search_complete", tasks_found=len(tasks))
        return tasks[:max_results]

    def _extract_reward(self, issue: dict) -> float:
        """Try to extract reward amount from issue labels or body."""
        import re
        # Check labels for dollar amounts
        for label in issue.get("labels", []):
            name = label.get("name", "")
            match = re.search(r"\$(\d+)", name)
            if match:
                return float(match.group(1))

        # Check body
        body = issue.get("body", "") or ""
        match = re.search(r"\$(\d+(?:\.\d+)?)", body)
        if match:
            return float(match.group(1))

        return 0.0

    async def apply_for_task(self, task_id: str, proposal: str) -> bool:
        """Comment on the issue to express interest."""
        if not self.http or not self.token:
            log.warning("github_bounty.apply_no_credentials")
            return False

        try:
            # Find the issue URL from metadata (stored when searching)
            # task_id is the issue numeric ID; we need the repo + issue number
            # Search for the issue to get its comments URL
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.token}",
            }
            # Use search to find the issue by ID
            url = f"{self._base_url}/search/issues?q={task_id}"
            resp = await self.http.get(url, headers=headers)

            if resp and resp.get("items"):
                item = resp["items"][0]
                comments_url = item.get("comments_url", "")
                if comments_url:
                    await self.http.post(
                        comments_url,
                        headers=headers,
                        json={"body": proposal},
                    )
                    log.info("github_bounty.applied", task_id=task_id)
                    return True
            return False
        except Exception as e:
            log.error("github_bounty.apply_failed", task_id=task_id, error=str(e))
            return False

    async def submit_work(self, task_id: str, deliverables: dict[str, Any]) -> bool:
        """Submit a pull request with the solution.

        deliverables should contain:
        - repo: "owner/repo" string
        - branch: branch name with the fix
        - title: PR title
        - body: PR description
        """
        if not self.http or not self.token:
            log.warning("github_bounty.submit_no_credentials")
            return False

        try:
            repo = deliverables.get("repo", "")
            if not repo:
                log.error("github_bounty.submit_no_repo")
                return False

            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.token}",
            }
            pr_url = f"{self._base_url}/repos/{repo}/pulls"
            pr_data = {
                "title": deliverables.get("title", f"Fix for #{task_id}"),
                "body": deliverables.get("body", f"Automated fix for issue #{task_id}"),
                "head": deliverables.get("branch", "fix-branch"),
                "base": deliverables.get("base", "main"),
            }
            resp = await self.http.post(pr_url, headers=headers, json=pr_data)

            if resp and resp.get("number"):
                log.info(
                    "github_bounty.pr_created",
                    task_id=task_id,
                    pr_number=resp["number"],
                )
                return True
            return False
        except Exception as e:
            log.error("github_bounty.submit_failed", task_id=task_id, error=str(e))
            return False

    async def check_payment(self, task_id: str) -> Optional[float]:
        """Check if bounty has been paid by looking for payment confirmation in comments."""
        if not self.http:
            return None

        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.token:
                headers["Authorization"] = f"token {self.token}"

            url = f"{self._base_url}/search/issues?q={task_id}"
            resp = await self.http.get(url, headers=headers)

            if resp and resp.get("items"):
                item = resp["items"][0]
                # Check if issue is closed (often means bounty resolved)
                if item.get("state") == "closed":
                    reward = self._extract_reward(item)
                    if reward > 0:
                        log.info("github_bounty.payment_detected", task_id=task_id, reward=reward)
                        return reward

                # Check comments for payment confirmation
                comments_url = item.get("comments_url", "")
                if comments_url:
                    comments = await self.http.get(comments_url, headers=headers)
                    if isinstance(comments, list):
                        import re
                        for comment in comments:
                            body = comment.get("body", "").lower()
                            if any(kw in body for kw in ["paid", "payment sent", "bounty paid", "reward sent"]):
                                match = re.search(r"\$(\d+(?:\.\d+)?)", comment.get("body", ""))
                                if match:
                                    return float(match.group(1))
                                return self._extract_reward(item)
            return None
        except Exception as e:
            log.error("github_bounty.check_payment_error", task_id=task_id, error=str(e))
            return None


class FreelanceManager:
    """Manages multiple freelance platforms for income generation."""

    def __init__(self):
        self.platforms: dict[str, FreelancePlatform] = {}
        self.active_tasks: dict[str, FreelanceTask] = {}

    def register_platform(self, platform: FreelancePlatform) -> None:
        """Register a freelance platform."""
        self.platforms[platform.name] = platform
        log.info("freelance.platform_registered", name=platform.name)

    async def search_all_platforms(
        self,
        skills: list[str] | None = None,
        min_reward: float = 5.0,
    ) -> list[FreelanceTask]:
        """Search all registered platforms for tasks."""
        all_tasks: list[FreelanceTask] = []
        searches = [
            p.search_tasks(skills=skills, min_reward=min_reward)
            for p in self.platforms.values()
        ]
        results = await asyncio.gather(*searches, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_tasks.extend(result)

        # Sort by reward (highest first)
        all_tasks.sort(key=lambda t: t.reward, reverse=True)
        return all_tasks

    async def pick_best_task(
        self,
        skills: list[str] | None = None,
    ) -> Optional[FreelanceTask]:
        """Find and pick the best available task."""
        tasks = await self.search_all_platforms(skills=skills)
        if not tasks:
            return None
        # Simple strategy: pick highest reward
        best = tasks[0]
        self.active_tasks[best.task_id] = best
        return best
