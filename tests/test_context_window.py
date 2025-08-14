"""Tests for context window management functionality."""

from unittest.mock import patch

import pytest

from src.config import Settings
from src.main import _manage_prompt_size
from src.mcp_output_utils import (
    CONTEXT_WINDOW_LIMITS,
    count_tokens,
    estimate_prompt_tokens,
    get_context_window_limit,
)


class TestTokenCounting:
    """Test token counting functionality."""

    def test_count_tokens_basic(self):
        """Test basic token counting."""
        text = "Hello world, this is a test."
        tokens = count_tokens(text)

        # Should return a reasonable number of tokens
        assert isinstance(tokens, int)
        assert tokens > 0
        assert tokens < len(text)  # Should be fewer tokens than characters

    def test_count_tokens_with_model(self):
        """Test token counting with specific model."""
        text = "Hello world, this is a test."
        gpt4_tokens = count_tokens(text, "gpt-4")
        claude_tokens = count_tokens(text, "claude-3-sonnet")

        assert isinstance(gpt4_tokens, int)
        assert isinstance(claude_tokens, int)
        assert gpt4_tokens > 0
        assert claude_tokens > 0

    def test_count_tokens_empty_string(self):
        """Test token counting with empty string."""
        tokens = count_tokens("")
        assert tokens == 0

    def test_get_context_window_limit(self):
        """Test getting context window limits for different models."""
        assert get_context_window_limit("gpt-4") == 8192
        assert get_context_window_limit("gpt-4-32k") == 32768
        assert get_context_window_limit("claude-3-sonnet") == 200000
        assert get_context_window_limit("unknown-model") == 8192  # default

    def test_estimate_prompt_tokens(self):
        """Test prompt token estimation."""
        jira_content = '{"issue": "EP-1234", "summary": "Test issue"}'
        context_instructions = "Repository analysis for project..."
        prompt_template = "You are an engineering agent..."

        tokens = estimate_prompt_tokens(
            jira_content, context_instructions, prompt_template
        )

        assert isinstance(tokens, int)
        assert tokens > 0


class TestPromptSizeManagement:
    """Test prompt size management functionality."""

    def test_manage_prompt_size_small_prompt(self):
        """Test that small prompts are not modified."""
        small_prompt = "This is a small prompt that should not be truncated."

        with patch.object(Settings, "MODEL_NAME", "gpt-4"):
            with patch.object(Settings, "MAX_CONTEXT_TOKENS", 0):
                with patch.object(Settings, "CONTEXT_SAFETY_MARGIN", 0.8):
                    result = _manage_prompt_size(small_prompt, "gpt-4")

        assert result == small_prompt

    def test_manage_prompt_size_large_prompt(self):
        """Test that large prompts are truncated."""
        # Create a very large prompt that would exceed token limits
        large_prompt = "This is a test line.\n" * 10000  # ~50KB of text

        with patch.object(Settings, "MODEL_NAME", "gpt-4"):
            with patch.object(Settings, "MAX_CONTEXT_TOKENS", 1000):  # Force low limit
                with patch.object(Settings, "CONTEXT_SAFETY_MARGIN", 0.8):
                    result = _manage_prompt_size(large_prompt, "gpt-4")

        assert len(result) < len(large_prompt)
        assert "CONTENT" in result  # Should contain truncation/summary marker

    def test_manage_prompt_size_with_custom_token_limit(self):
        """Test prompt size management with custom token limit."""
        prompt = "Test prompt content " * 100

        with patch.object(Settings, "MODEL_NAME", "gpt-4"):
            with patch.object(Settings, "MAX_CONTEXT_TOKENS", 500):
                with patch.object(Settings, "CONTEXT_SAFETY_MARGIN", 0.8):
                    result = _manage_prompt_size(prompt, "gpt-4")

        # Should be processed (either truncated or kept as-is)
        assert isinstance(result, str)
        assert len(result) > 0


class TestContextWindowLimits:
    """Test context window limit constants and configurations."""

    def test_context_window_limits_exist(self):
        """Test that context window limits are defined for common models."""
        expected_models = ["gpt-4", "gpt-4-32k", "gpt-3.5-turbo", "claude-3-sonnet"]

        for model in expected_models:
            assert model in CONTEXT_WINDOW_LIMITS
            assert CONTEXT_WINDOW_LIMITS[model] > 0

    def test_default_limit_exists(self):
        """Test that a default limit is defined."""
        assert "default" in CONTEXT_WINDOW_LIMITS
        assert CONTEXT_WINDOW_LIMITS["default"] > 0
