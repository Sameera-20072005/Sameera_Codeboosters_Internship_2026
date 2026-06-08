"""
Project planner module.
Generates a deterministic ordered execution plan from a parsed project intent.
"""

from __future__ import annotations

from utils.logger import get_logger

logger = get_logger(__name__)

# All possible steps in dependency order
_STEP_CREATE_REPO       = "create_repository"
_STEP_README            = "generate_readme"
_STEP_GITIGNORE         = "generate_gitignore"
_STEP_LICENSE           = "generate_license"
_STEP_REQUIREMENTS      = "generate_requirements"
_STEP_SOURCE_STRUCTURE  = "create_source_structure"
_STEP_TESTS             = "generate_tests"
_STEP_CI_WORKFLOW       = "generate_ci_workflow"
_STEP_DOCKER            = "generate_dockerfile"
_STEP_PUSH              = "push_files"
_STEP_CONFIRM           = "confirm_completion"


class ProjectPlanner:
    """Determines the ordered execution plan for a project intent."""

    def plan(self, intent: dict) -> list[str]:
        """
        Build an ordered list of action steps based on the intent flags.

        Args:
            intent: Validated project intent dict from IntentParser.

        Returns:
            Ordered list of step name strings.
        """
        steps: list[str] = [
            _STEP_CREATE_REPO,
            _STEP_README,
            _STEP_GITIGNORE,
            _STEP_LICENSE,
            _STEP_REQUIREMENTS,
            _STEP_SOURCE_STRUCTURE,
        ]

        if intent.get("testing_required", False):
            steps.append(_STEP_TESTS)

        if intent.get("ci_required", False):
            steps.append(_STEP_CI_WORKFLOW)

        if intent.get("docker_required", False):
            steps.append(_STEP_DOCKER)

        steps.append(_STEP_PUSH)
        steps.append(_STEP_CONFIRM)

        logger.info(
            "Plan generated | project=%s | steps=%d | %s",
            intent.get("project_name", "?"),
            len(steps),
            steps,
        )
        return steps

    @staticmethod
    def describe(step: str) -> str:
        """Return a human-readable description for a plan step."""
        descriptions: dict[str, str] = {
            _STEP_CREATE_REPO:      "Creating GitHub repository",
            _STEP_README:           "Generating README.md",
            _STEP_GITIGNORE:        "Generating .gitignore",
            _STEP_LICENSE:          "Generating LICENSE",
            _STEP_REQUIREMENTS:     "Generating requirements file",
            _STEP_SOURCE_STRUCTURE: "Scaffolding source structure",
            _STEP_TESTS:            "Generating test suite",
            _STEP_CI_WORKFLOW:      "Generating GitHub Actions CI workflow",
            _STEP_DOCKER:           "Generating Dockerfile",
            _STEP_PUSH:             "Pushing all files to GitHub",
            _STEP_CONFIRM:          "Confirming completion",
        }
        return descriptions.get(step, step.replace("_", " ").title())
