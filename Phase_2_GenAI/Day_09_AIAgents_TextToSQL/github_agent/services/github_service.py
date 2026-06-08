"""
GitHub service module.
Manages all GitHub API interactions via PyGithub >=2.0.
"""

from __future__ import annotations

import os
import time
from dotenv import load_dotenv
from github import Github, GithubException
from github.Repository import Repository  # type: ignore[attr-defined]
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# HTTP status codes
_HTTP_NOT_FOUND = 404
_HTTP_CONFLICT  = 422   # repo already exists / file already there


class GitHubService:
    """Handles repository creation and file upload via the GitHub API."""

    def __init__(self) -> None:
        token = os.getenv("GITHUB_TOKEN", "")
        if not token:
            raise EnvironmentError("GITHUB_TOKEN is missing. Check your .env file.")
        self._gh   = Github(token)
        self._user = self._gh.get_user()
        logger.info("GitHubService initialised | user=%s", self._user.login)

    # ── Repository management ─────────────────────────────────────────────────

    def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = False,
    ) -> Repository:
        """
        Create a new GitHub repository for the authenticated user.

        Args:
            name:        Repository name (must be URL-safe).
            description: Short description string.
            private:     True for a private repository.
            auto_init:   True to initialise with an empty README.

        Returns:
            Created Repository object.

        Raises:
            RuntimeError: On API error or if repo already exists.
        """
        logger.info("Creating repository | name=%s | private=%s", name, private)
        try:
            repo = self._user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init,
            )
            logger.info("Repository created | url=%s", repo.html_url)
            return repo
        except GithubException as exc:
            msg = self._extract_message(exc)
            logger.error("Failed to create repo '%s': status=%s msg=%s", name, exc.status, msg)
            if exc.status == 422:
                raise RuntimeError(
                    f"Repository '{name}' already exists on your GitHub account. "
                    "Try a different project name or delete the existing repo first."
                ) from exc
            if exc.status == 401:
                raise RuntimeError(
                    "GitHub authentication failed. Your GITHUB_TOKEN is invalid or expired."
                ) from exc
            if exc.status == 403:
                raise RuntimeError(
                    "GitHub token lacks 'repo' scope. Create a new Classic PAT with the 'repo' scope at "
                    "https://github.com/settings/tokens/new"
                ) from exc
            raise RuntimeError(f"GitHub repo creation failed: {msg}") from exc

    def get_repository(self, name: str) -> Repository:
        """
        Fetch an existing repository by name.

        Args:
            name: Repository name (without owner prefix).

        Returns:
            Repository object.

        Raises:
            RuntimeError: If the repo does not exist or on API error.
        """
        try:
            return self._user.get_repo(name)
        except GithubException as exc:
            if exc.status == _HTTP_NOT_FOUND:
                raise RuntimeError(f"Repository '{name}' not found.") from exc
            raise RuntimeError(
                f"GitHub error fetching repo: {self._extract_message(exc)}"
            ) from exc

    # ── File operations ───────────────────────────────────────────────────────

    def upload_file(
        self,
        repo: Repository,
        path: str,
        content: str,
        commit_message: str = "Add file",
        branch: str = "main",
    ) -> None:
        """
        Create or update a single file in the repository.

        Args:
            repo:           Target Repository object.
            path:           File path relative to repo root (e.g. 'src/main.py').
            content:        UTF-8 string content of the file.
            commit_message: Git commit message.
            branch:         Target branch name.

        Raises:
            RuntimeError: On GitHub API failure.
        """
        logger.debug("Uploading file | path=%s", path)
        try:
            existing_sha = self._get_file_sha(repo, path, branch)
            if existing_sha:
                repo.update_file(
                    path=path,
                    message=commit_message,
                    content=content,
                    sha=existing_sha,
                    branch=branch,
                )
                logger.debug("Updated file | path=%s", path)
            else:
                repo.create_file(
                    path=path,
                    message=commit_message,
                    content=content,
                    branch=branch,
                )
                logger.debug("Created file | path=%s", path)
        except GithubException as exc:
            msg = self._extract_message(exc)
            logger.error("Failed to upload '%s': %s", path, msg)
            raise RuntimeError(f"Failed to upload {path}: {msg}") from exc

    def commit_files(
        self,
        repo: Repository,
        files: dict[str, str],
        branch: str = "main",
    ) -> None:
        """
        Upload multiple files to the repository with pacing to avoid rate limits.

        Args:
            repo:   Target Repository object.
            files:  Dict mapping relative path → file content string.
            branch: Target branch name.
        """
        total = len(files)
        logger.info("Committing %d files to '%s'", total, repo.name)
        for i, (path, content) in enumerate(files.items(), 1):
            self.upload_file(
                repo=repo,
                path=path,
                content=content,
                commit_message=f"Add {path}",
                branch=branch,
            )
            logger.info("Uploaded %d/%d | %s", i, total, path)
            # Pace uploads: 1 s pause every 5 files to respect GitHub secondary rate limit
            if i % 5 == 0:
                time.sleep(1)

    def create_branch(
        self, repo: Repository, branch: str, from_branch: str = "main"
    ) -> None:
        """
        Create a new branch from an existing one.

        Args:
            repo:        Target Repository object.
            branch:      New branch name.
            from_branch: Source branch name.
        """
        try:
            source_ref = repo.get_git_ref(f"heads/{from_branch}")
            repo.create_git_ref(
                ref=f"refs/heads/{branch}", sha=source_ref.object.sha
            )
            logger.info("Branch created | %s from %s", branch, from_branch)
        except GithubException as exc:
            raise RuntimeError(
                f"Failed to create branch '{branch}': {self._extract_message(exc)}"
            ) from exc

    def get_repository_url(self, repo: Repository) -> str:
        """Return the HTML URL of the repository."""
        return repo.html_url

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _get_file_sha(repo: Repository, path: str, branch: str) -> str | None:
        """
        Return the SHA of an existing file, or None if it does not exist.
        Safely handles the case where get_contents() returns a list (directory).
        """
        try:
            contents = repo.get_contents(path, ref=branch)
            # If path is a directory, get_contents returns a list — not a file
            if isinstance(contents, list):
                return None
            return contents.sha
        except GithubException as exc:
            if exc.status == _HTTP_NOT_FOUND:
                return None
            logger.warning("Unexpected error checking file '%s': %s", path, exc)
            return None

    @staticmethod
    def _extract_message(exc: GithubException) -> str:
        """Extract a human-readable message from a GithubException."""
        try:
            data = exc.data
            if isinstance(data, dict):
                return str(data.get("message", exc.status))
        except AttributeError:
            pass
        return str(exc)
