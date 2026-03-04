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
        # TODO: Implement GitHub issue comment
        log.info("github_bounty.applied", task_id=task_id)
        return True

    async def submit_work(self, task_id: str, deliverables: dict[str, Any]) -> bool:
        """Submit a pull request with the solution."""
        # TODO: Implement PR creation
        log.info("github_bounty.submitted", task_id=task_id)
        return True

    async def check_payment(self, task_id: str) -> Optional[float]:
        """Check if bounty has been paid."""
        # TODO: Implement payment verification
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
