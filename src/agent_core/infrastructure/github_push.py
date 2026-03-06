"""
GitHub Push via API - 绕过国内 ECS 无法通过 HTTPS git 协议连接 github.com 的问题。
使用 GitHub REST API (api.github.com) 来推送代码变更。
"""
import base64
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
import structlog

logger = structlog.get_logger()

GITHUB_API = "https://api.github.com"
REPO_OWNER = "ruochenliao"
REPO_NAME = "self_improve_machine"


def _api_request(method: str, endpoint: str, token: str, data: dict = None):
    """Make a GitHub API request."""
    url = f"{GITHUB_API}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        logger.error("github_api_error", status=e.code, body=error_body[:500])
        raise


def get_latest_commit_sha(token: str, branch: str = "master") -> str:
    """Get the latest commit SHA on the branch."""
    data = _api_request("GET", f"/repos/{REPO_OWNER}/{REPO_NAME}/git/ref/heads/{branch}", token)
    return data["object"]["sha"]


def get_commit_tree_sha(token: str, commit_sha: str) -> str:
    """Get the tree SHA from a commit."""
    data = _api_request("GET", f"/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{commit_sha}", token)
    return data["tree"]["sha"]


def create_blob(token: str, content: str, encoding: str = "utf-8") -> str:
    """Create a blob in the repo."""
    data = _api_request("POST", f"/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs", token, {
        "content": content,
        "encoding": encoding,
    })
    return data["sha"]


def create_tree(token: str, base_tree_sha: str, tree_items: list) -> str:
    """Create a new tree with the given items."""
    data = _api_request("POST", f"/repos/{REPO_OWNER}/{REPO_NAME}/git/trees", token, {
        "base_tree": base_tree_sha,
        "tree": tree_items,
    })
    return data["sha"]


def create_commit(token: str, message: str, tree_sha: str, parent_sha: str) -> str:
    """Create a new commit."""
    data = _api_request("POST", f"/repos/{REPO_OWNER}/{REPO_NAME}/git/commits", token, {
        "message": message,
        "tree": tree_sha,
        "parents": [parent_sha],
        "author": {
            "name": "Swift-Helix",
            "email": "swifthelix@users.noreply.github.com",
        },
    })
    return data["sha"]


def update_ref(token: str, branch: str, commit_sha: str) -> dict:
    """Update branch ref to point to new commit."""
    return _api_request("PATCH", f"/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{branch}", token, {
        "sha": commit_sha,
        "force": False,
    })


def push_files(token: str, files: dict, commit_message: str, branch: str = "master") -> str:
    """
    Push multiple file changes to GitHub via API.

    Args:
        token: GitHub PAT
        files: dict of {file_path: file_content}
        commit_message: commit message
        branch: target branch

    Returns:
        New commit SHA
    """
    logger.info("github_push_start", file_count=len(files), branch=branch)

    latest_sha = get_latest_commit_sha(token, branch)
    tree_sha = get_commit_tree_sha(token, latest_sha)

    tree_items = []
    for path, content in files.items():
        try:
            blob_sha = create_blob(token, content, "utf-8")
        except Exception:
            blob_sha = create_blob(
                token, base64.b64encode(content.encode()).decode(), "base64"
            )
        tree_items.append({
            "path": path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha,
        })

    new_tree_sha = create_tree(token, tree_sha, tree_items)
    new_commit_sha = create_commit(token, commit_message, new_tree_sha, latest_sha)
    update_ref(token, branch, new_commit_sha)

    logger.info("github_push_success", commit=new_commit_sha[:8], files=list(files.keys()))
    return new_commit_sha


def push_working_directory(
    token: str,
    commit_message: str,
    branch: str = "master",
    work_dir: str = "/opt/agent",
) -> str:
    """Push all tracked changes from the working directory to GitHub."""
    work_path = Path(work_dir)

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, cwd=work_dir,
        )
        changed = result.stdout.strip().split("\n") if result.stdout.strip() else []

        result2 = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, cwd=work_dir,
        )
        untracked = result2.stdout.strip().split("\n") if result2.stdout.strip() else []

        all_files = list(set(changed + untracked))
        all_files = [f for f in all_files if f]
    except Exception as e:
        logger.error("git_diff_failed", error=str(e))
        return ""

    if not all_files:
        logger.info("no_changes_to_push")
        return ""

    files = {}
    for fpath in all_files:
        full_path = work_path / fpath
        if full_path.exists() and full_path.is_file():
            try:
                content = full_path.read_text(encoding="utf-8")
                files[fpath] = content
            except UnicodeDecodeError:
                logger.warning("skip_binary_file", path=fpath)
                continue

    if not files:
        logger.info("no_readable_changes")
        return ""

    return push_files(token, files, commit_message, branch)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python github_push.py <token> [commit_message]")
        sys.exit(1)

    token = sys.argv[1]
    msg = sys.argv[2] if len(sys.argv) > 2 else "Auto-commit from Swift-Helix ECS"

    sha = push_working_directory(token, msg)
    if sha:
        print(f"Pushed commit: {sha}")
    else:
        print("No changes to push")
