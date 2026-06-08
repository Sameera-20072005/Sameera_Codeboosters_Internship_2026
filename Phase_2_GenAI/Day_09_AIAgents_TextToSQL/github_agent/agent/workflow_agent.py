"""
Workflow agent module.
Orchestrates the full repository scaffolding pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from agent.intent_parser import IntentParser
from agent.planner import ProjectPlanner
from services.llm_service import GroqLLMService
from services.github_service import GitHubService
from services.file_generator import FileGeneratorService
from services.history_service import HistoryService
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentResult:
    """Holds the complete result of a workflow agent run."""

    success:          bool
    repository_url:   str          = ""
    repository_name:  str          = ""
    intent:           dict         = field(default_factory=dict)
    plan:             list[str]    = field(default_factory=list)
    files_generated:  list[str]    = field(default_factory=list)
    steps_completed:  list[str]    = field(default_factory=list)
    error:            str          = ""


class WorkflowAgent:
    """
    Autonomous agent that converts a natural language project description
    into a fully scaffolded GitHub repository.
    """

    def __init__(
        self,
        llm_service:   GroqLLMService,
        github_service: GitHubService,
        history_service: HistoryService,
    ) -> None:
        self._llm       = llm_service
        self._github    = github_service
        self._history   = history_service
        self._parser    = IntentParser(llm_service)
        self._planner   = ProjectPlanner()
        self._generator = FileGeneratorService()

    def run(
        self,
        user_request: str,
        visibility: str = "public",
        progress_callback: Callable[[str], None] | None = None,
    ) -> AgentResult:
        """
        Execute the full agent workflow from request to repository URL.

        Args:
            user_request:       Natural language project description.
            visibility:         'public' or 'private'.
            progress_callback:  Optional callable(message) for UI progress updates.

        Returns:
            AgentResult with success flag, URL, and metadata.
        """
        def _progress(msg: str) -> None:
            logger.info("Agent step | %s", msg)
            if progress_callback:
                progress_callback(msg)

        result = AgentResult(success=False)

        try:
            # ── Step 1: Parse intent ──────────────────────────────────────────
            _progress("🔍 Parsing project requirements...")
            intent = self._parser.parse(user_request)
            intent["visibility"] = visibility
            result.intent = intent

            # ── Step 2: Build execution plan ──────────────────────────────────
            _progress("📋 Building execution plan...")
            plan = self._planner.plan(intent)
            result.plan = plan

            # ── Step 3: Execute plan ──────────────────────────────────────────
            repo_url, repo_name, files = self.execute_plan(intent, plan, _progress)

            result.repository_url  = repo_url
            result.repository_name = repo_name
            result.files_generated = list(files.keys())
            result.success         = True

            # ── Step 4: Persist history ───────────────────────────────────────
            self._history.save_history(
                request=user_request,
                repository_name=repo_name,
                repository_url=repo_url,
                intent=intent,
            )

            self.confirm_completion(repo_url, _progress)

        except (ValueError, RuntimeError, EnvironmentError) as exc:
            result.error = str(exc)
            logger.error("Agent run failed: %s", exc, exc_info=True)

        return result

    def execute_plan(
        self,
        intent: dict,
        plan: list[str],
        progress: Callable[[str], None],
    ) -> tuple[str, str, dict[str, str]]:
        """
        Execute the ordered plan steps and return (repo_url, repo_name, files).

        Args:
            intent:   Validated project intent.
            plan:     Ordered list of step names.
            progress: Callable for status updates.

        Returns:
            Tuple of (repository_html_url, repository_name, files_dict).
        """
        desc        = intent.get("description", "")
        name        = intent.get("project_name", "my-project")
        private     = intent.get("visibility", "public") == "private"
        steps_done: list[str] = []

        # ── LLM artefact generation ───────────────────────────────────────────
        progress(f"📝 {self._planner.describe('generate_readme')}...")
        llm_readme = self._llm.generate_readme(intent)
        steps_done.append("generate_readme")

        progress(f"📦 {self._planner.describe('generate_requirements')}...")
        llm_requirements = self._llm.generate_requirements(intent)
        steps_done.append("generate_requirements")

        progress(f"🗂️ {self._planner.describe('create_source_structure')}...")
        llm_structure = self._llm.generate_folder_structure(intent)
        steps_done.append("create_source_structure")

        # ── Assemble all files ────────────────────────────────────────────────
        files = self._generator.generate(
            intent=intent,
            llm_readme=llm_readme,
            llm_requirements=llm_requirements,
            llm_structure=llm_structure,
        )

        # ── Create GitHub repository ──────────────────────────────────────────
        progress(f"🏗️ {self._planner.describe('create_repository')} '{name}'...")
        repo = self._github.create_repository(
            name=name,
            description=desc,
            private=private,
            auto_init=False,
        )
        steps_done.append("create_repository")

        # ── Push files ────────────────────────────────────────────────────────
        progress(f"🚀 {self._planner.describe('push_files')} ({len(files)} files)...")
        self._github.commit_files(repo=repo, files=files)
        steps_done.append("push_files")

        repo_url = self._github.get_repository_url(repo)
        return repo_url, name, files

    @staticmethod
    def confirm_completion(repo_url: str, progress: Callable[[str], None]) -> None:
        """Log and surface a completion message."""
        progress(f"✅ Repository ready: {repo_url}")
        logger.info("Agent completed | url=%s", repo_url)
