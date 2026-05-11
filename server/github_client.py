import base64
from dataclasses import dataclass
from typing import Optional

import requests
from decouple import config


GITHUB_TOKEN = config("GITHUB_TOKEN")
OWNER = config("GITHUB_OWNER")
REPO = config("GITHUB_REPO")
BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


@dataclass
class GitHubFile:
    name: str
    path: str
    content: str
    sha: str
    size: int
    encoding: Optional[str] = None


@dataclass
class GitHubError:
    message: str
    status_code: int
    path: Optional[str] = None


def _get(url: str, params: Optional[dict] = None) -> tuple[int, dict]:
    """Low-level GET against the GitHub API. Returns (status_code, body)."""
    response = requests.get(url, headers=HEADERS, params=params)
    return response.status_code, response.json()


def list_repository_files(path: str = "") -> list[dict] | GitHubError:
    """
    List files and directories at the given repo path (default: root).

    Returns a list of GitHub content objects on success, or a GitHubError.
    """
    url = f"{BASE_URL}/contents/{path}".rstrip("/")
    status_code, data = _get(url)

    if status_code != 200:
        return GitHubError(
            message=data.get("message", "Failed to list repository files"),
            status_code=status_code,
            path=path or "/",
        )

    return data


def read_repository_file(file_path: str) -> GitHubFile | GitHubError:
    """
    Read a single file from the repository.

    Decodes base64-encoded content automatically.
    Returns a GitHubFile on success, or a GitHubError.
    """
    url = f"{BASE_URL}/contents/{file_path}"
    status_code, data = _get(url)

    if status_code != 200:
        return GitHubError(
            message=data.get("message", "Failed to read file"),
            status_code=status_code,
            path=file_path,
        )

    raw_content = data.get("content", "")
    encoding = data.get("encoding")

    if encoding == "base64":
        raw_content = base64.b64decode(raw_content).decode("utf-8")

    return GitHubFile(
        name=data["name"],
        path=data["path"],
        content=raw_content,
        sha=data["sha"],
        size=data["size"],
        encoding=encoding,
    )


def read_multiple_files(file_paths: list[str]) -> dict[str, GitHubFile | GitHubError]:
    """
    Read multiple files in one call.

    Returns a dict mapping each file path to either a GitHubFile or a GitHubError.
    """
    return {path: read_repository_file(path) for path in file_paths}