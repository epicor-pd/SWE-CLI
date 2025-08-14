"""Utilities for handling large MCP tool outputs and preventing string length errors."""

import logging
from typing import Any, Dict, Union

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

logger = logging.getLogger(__name__)

# Maximum string length allowed by MCP (slightly under 10MB to be safe)
MAX_MCP_STRING_LENGTH = 10_000_000  # ~9.5MB

# Context window limits for different models (in tokens)
CONTEXT_WINDOW_LIMITS = {
    "gpt-4": 8192,
    "gpt-4-0613": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-1106-preview": 128000,
    "gpt-4-0125-preview": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "claude-3-sonnet": 200000,
    "claude-3-opus": 200000,
    "claude-3-haiku": 200000,
    "default": 8192,  # Conservative default
}

# Reserve tokens for the response
RESPONSE_TOKEN_RESERVE = 2000


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken for OpenAI models or estimation for others.

    Args:
        text: The text to count tokens for
        model: The model name to use for encoding

    Returns:
        Token count (estimated)
    """
    if not TIKTOKEN_AVAILABLE:
        # Fallback estimation: roughly 4 characters per token
        return len(text) // 4

    try:
        # Try to get encoding for the specific model
        if model.startswith(("gpt-", "text-")):
            encoding = tiktoken.encoding_for_model(model)
        else:
            # Use a default encoding for non-OpenAI models
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Failed to count tokens with tiktoken: %s", e)
        # Fallback estimation
        return len(text) // 4


def get_context_window_limit(model: str = "default") -> int:
    """Get the context window limit for a given model."""
    return CONTEXT_WINDOW_LIMITS.get(model.lower(), CONTEXT_WINDOW_LIMITS["default"])


def estimate_prompt_tokens(
    jira_content: str, context_instructions: str, prompt_template: str
) -> int:
    """
    Estimate total tokens for the complete prompt.

    Args:
        jira_content: The JIRA issue JSON content
        context_instructions: The MCP context instructions
        prompt_template: The prompt template text

    Returns:
        Estimated total token count
    """
    # Estimate template overhead (instructions, formatting, etc.)
    template_tokens = count_tokens(prompt_template)
    jira_tokens = count_tokens(jira_content)
    context_tokens = count_tokens(context_instructions)

    return template_tokens + jira_tokens + context_tokens


def truncate_large_strings(data: Any, max_length: int = MAX_MCP_STRING_LENGTH) -> Any:
    """
    Recursively truncate strings in data structures that exceed max_length.

    Args:
        data: The data structure to process (can be dict, list, string, etc.)
        max_length: Maximum allowed string length

    Returns:
        The data structure with truncated strings
    """
    if isinstance(data, str):
        if len(data) > max_length:
            truncated_length = max_length - 100  # Leave room for truncation message
            truncation_msg = (
                f"\n\n[TRUNCATED: Original length was {len(data)} characters, "
                f"showing first {truncated_length} characters]"
            )
            return data[:truncated_length] + truncation_msg
        return data

    if isinstance(data, dict):
        return {
            key: truncate_large_strings(value, max_length)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [truncate_large_strings(item, max_length) for item in data]

    if isinstance(data, tuple):
        return tuple(truncate_large_strings(item, max_length) for item in data)

    # For other types (int, float, bool, None, etc.), return as-is
    return data


def summarize_large_content(
    content: str, max_length: int = MAX_MCP_STRING_LENGTH
) -> str:
    """
    Intelligently summarize large content instead of just truncating.

    Args:
        content: The content to summarize
        max_length: Maximum allowed length

    Returns:
        Summarized content if too long, original content otherwise
    """
    if len(content) <= max_length:
        return content

    # Try to find natural break points
    lines = content.split("\n")

    if len(lines) > 100:
        # If there are many lines, take first and last portions
        # Adjust portion size based on max_length to ensure it fits
        overhead = 200  # Space for summary message
        available_content = max_length - overhead

        # Estimate how many lines we can include from start and end
        avg_line_length = len(content) / len(lines)
        max_lines_per_section = max(10, int(available_content / (2 * avg_line_length)))
        max_lines_per_section = min(max_lines_per_section, len(lines) // 2)

        first_portion = "\n".join(lines[:max_lines_per_section])
        last_portion = "\n".join(lines[-max_lines_per_section:])

        summary = (
            f"{first_portion}\n\n"
            f"[CONTENT SUMMARIZED: {len(lines)} total lines, "
            f"{len(content)} characters]\n"
            f"[Showing first {max_lines_per_section} and last "
            f"{max_lines_per_section} lines]\n\n"
            f"{last_portion}"
        )

        if len(summary) <= max_length:
            return summary

    # Fallback to simple truncation with summary
    truncated_length = max_length - 200
    summary = (
        f"{content[:truncated_length]}\n\n"
        f"[CONTENT TRUNCATED: Original had {len(content)} characters "
        f"({len(lines)} lines)]\n"
        f"[Content too large for MCP transmission - showing first "
        f"{truncated_length} characters]"
    )

    return summary


def safe_mcp_output(data: Any) -> Any:
    """
    Ensure MCP output is safe for transmission by truncating large strings.

    Args:
        data: The data to make safe

    Returns:
        Safe data with truncated strings
    """
    return truncate_large_strings(data)


def get_content_size_info(content: str) -> Dict[str, Union[int, str, float, bool]]:
    """Get information about content size for logging."""
    lines = content.split("\n")
    return {
        "character_count": len(content),
        "line_count": len(lines),
        "size_mb": round(len(content) / (1024 * 1024), 2),
        "exceeds_limit": len(content) > MAX_MCP_STRING_LENGTH,
        "recommended_action": (
            "truncate" if len(content) > MAX_MCP_STRING_LENGTH else "none"
        ),
    }


def log_large_content_warning(content: str, source: str = "unknown") -> None:
    """Log a warning about large content."""
    info = get_content_size_info(content)
    if info["exceeds_limit"]:
        logger.warning(
            "Large content detected from %s: %d characters (%d lines, %.2f MB) - "
            "will be truncated to prevent MCP errors",
            source,
            info["character_count"],
            info["line_count"],
            info["size_mb"],
        )
