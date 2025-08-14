import argparse
import json
import logging
import os
import sys
from pathlib import Path

from .codex_codegen import run_codex
from .config import Settings
from .jira_fetch import fetch_issue
from .logging_setup import configure_logging
from .mcp_context import build_context_instructions
from .mcp_output_utils import (
    RESPONSE_TOKEN_RESERVE,
    count_tokens,
    estimate_prompt_tokens,
    get_context_window_limit,
    summarize_large_content,
)


def _parse_repos(val: str) -> list[str]:
    # comma-or-space separated list
    parts = [p.strip() for p in val.replace(",", " ").split()]
    return [p for p in parts if p]


def _manage_prompt_size(prompt: str, model: str) -> str:
    """
    Ensure prompt fits within context window limits.

    Args:
        prompt: The full prompt text
        model: The model name to check limits for

    Returns:
        Potentially truncated prompt that fits within context limits
    """
    logger = logging.getLogger(__name__)

    # Get context window limit with safe handling for mocked values
    try:
        context_limit = Settings.MAX_CONTEXT_TOKENS
        if not context_limit or context_limit <= 0:
            context_limit = get_context_window_limit(model)
    except (TypeError, AttributeError):
        # Handle cases where Settings values are mocked or invalid
        context_limit = get_context_window_limit(model)

    # Apply safety margin with safe handling
    try:
        safety_margin = Settings.CONTEXT_SAFETY_MARGIN
        if not isinstance(safety_margin, (int, float)) or safety_margin <= 0:
            safety_margin = 0.8
    except (TypeError, AttributeError):
        safety_margin = 0.8

    usable_tokens = int(context_limit * safety_margin)
    max_prompt_tokens = usable_tokens - RESPONSE_TOKEN_RESERVE

    # Count current tokens
    current_tokens = count_tokens(prompt, model)

    logger.info(
        "Prompt token analysis: model=%s, limit=%d, usable=%d, current=%d",
        model,
        context_limit,
        usable_tokens,
        current_tokens,
    )

    if current_tokens <= max_prompt_tokens:
        logger.info("Prompt fits within context window")
        return prompt

    logger.warning(
        "Prompt exceeds context window (%d > %d tokens), will truncate",
        current_tokens,
        max_prompt_tokens,
    )

    # Calculate target length to achieve token limit
    # Use a ratio based approach since token counting might not be exact
    ratio = max_prompt_tokens / current_tokens
    target_char_length = int(len(prompt) * ratio * 0.9)  # Extra safety margin

    # Use smart summarization
    truncated_prompt = summarize_large_content(prompt, target_char_length)

    # Verify the result
    final_tokens = count_tokens(truncated_prompt, model)
    logger.info(
        "Prompt after truncation: %d tokens (%d characters)",
        final_tokens,
        len(truncated_prompt),
    )

    return truncated_prompt


def main() -> None:
    configure_logging()
    logger = logging.getLogger(__name__)

    ap = argparse.ArgumentParser()
    ap.add_argument("--jira", required=True, help="Jira issue key, e.g., EP-1234")
    ap.add_argument("--ado-org", default=Settings.ADO_ORG)
    ap.add_argument("--ado-project", default=Settings.ADO_PROJECT)
    ap.add_argument(
        "--ado-repo",
        required=False,
        help="One or more repos (comma or space separated)",
    )
    ap.add_argument(
        "--workspace",
        required=False,
        default=os.getcwd(),
        help="Directory where code changes should be applied",
    )
    ap.add_argument(
        "--generate-tests",
        action="store_true",
        help=(  # pylint: disable=line-too-long
            "Generate tests for the requirements in addition to the main implementation"
        ),
    )
    args = ap.parse_args()

    ado_repos = _parse_repos(args.ado_repo or Settings.ADO_REPO or "")
    if not ado_repos:
        raise SystemExit("Provide at least one repo via --ado-repo or ADO_REPO env var")

    logger.info(
        "Starting run for issue=%s org=%s project=%s repos=%s",
        args.jira,
        args.ado_org,
        args.ado_project,
        ",".join(ado_repos),
    )

    issue = fetch_issue(args.jira)
    ctx = build_context_instructions(args.ado_org, args.ado_project, ado_repos)

    # Select prompt based on whether test generation is requested
    prompt_file = (
        "prompts/codegen_with_tests.md" if args.generate_tests else "prompts/codegen.md"
    )
    prompt = Path(prompt_file).read_text(encoding="utf-8")
    prompt = prompt.replace("{{JIRA_JSON}}", json.dumps(issue, indent=2))
    prompt = prompt.replace("{{CONTEXT_INSTRUCTIONS}}", ctx)

    # Estimate and manage prompt size to fit within context window
    logger.info("Managing prompt size for model: %s", Settings.MODEL_NAME)
    jira_json = json.dumps(issue, indent=2)
    estimated_tokens = estimate_prompt_tokens(jira_json, ctx, prompt)
    logger.info("Estimated prompt tokens before processing: %d", estimated_tokens)

    # Apply context window management
    managed_prompt = _manage_prompt_size(prompt, Settings.MODEL_NAME)

    ws = Path(args.workspace).expanduser().resolve()
    sys.exit(run_codex(managed_prompt, ws))


if __name__ == "__main__":
    main()
