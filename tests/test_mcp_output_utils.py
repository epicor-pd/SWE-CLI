"""Tests for MCP output utilities that handle large strings."""

import pytest

from src.mcp_output_utils import (
    MAX_MCP_STRING_LENGTH,
    get_content_size_info,
    safe_mcp_output,
    summarize_large_content,
    truncate_large_strings,
)


class TestMCPOutputUtils:
    """Test MCP output utility functions."""

    def test_truncate_large_strings_small_string(self):
        """Test that small strings are not modified."""
        small_string = "This is a small string"
        result = truncate_large_strings(small_string)
        assert result == small_string

    def test_truncate_large_strings_large_string(self):
        """Test that large strings are truncated."""
        large_string = "x" * (MAX_MCP_STRING_LENGTH + 1000)
        result = truncate_large_strings(large_string)

        assert len(result) < len(large_string)
        assert len(result) <= MAX_MCP_STRING_LENGTH
        assert "[TRUNCATED:" in result
        assert "Original length was" in result

    def test_truncate_large_strings_dict(self):
        """Test truncation in dictionary values."""
        large_string = "x" * (MAX_MCP_STRING_LENGTH + 1000)
        test_dict = {"small": "small value", "large": large_string, "number": 42}

        result = truncate_large_strings(test_dict)

        assert result["small"] == "small value"
        assert len(result["large"]) < len(large_string)
        assert "[TRUNCATED:" in result["large"]
        assert result["number"] == 42

    def test_truncate_large_strings_list(self):
        """Test truncation in list items."""
        large_string = "x" * (MAX_MCP_STRING_LENGTH + 1000)
        test_list = ["small", large_string, 123]

        result = truncate_large_strings(test_list)

        assert result[0] == "small"
        assert len(result[1]) < len(large_string)
        assert "[TRUNCATED:" in result[1]
        assert result[2] == 123

    def test_truncate_large_strings_nested(self):
        """Test truncation in nested data structures."""
        large_string = "x" * (MAX_MCP_STRING_LENGTH + 1000)
        nested_data = {
            "level1": {
                "level2": {"large_content": large_string, "small_content": "small"},
                "list": [large_string, "small"],
            }
        }

        result = truncate_large_strings(nested_data)

        assert result["level1"]["level2"]["small_content"] == "small"
        assert "[TRUNCATED:" in result["level1"]["level2"]["large_content"]
        assert "[TRUNCATED:" in result["level1"]["list"][0]
        assert result["level1"]["list"][1] == "small"

    def test_summarize_large_content_small(self):
        """Test that small content is not modified."""
        small_content = "Small content"
        result = summarize_large_content(small_content)
        assert result == small_content

    def test_summarize_large_content_many_lines(self):
        """Test summarization of content with many lines."""
        lines = [f"Line {i}" for i in range(200)]
        large_content = "\n".join(lines)

        result = summarize_large_content(large_content, max_length=1000)

        assert len(result) < len(large_content)
        assert "CONTENT SUMMARIZED:" in result
        assert "total lines" in result
        assert "Line 0" in result  # First line should be present
        assert "Line 199" in result  # Last line should be present

    def test_summarize_large_content_single_long_line(self):
        """Test summarization of single very long line."""
        large_content = "x" * (MAX_MCP_STRING_LENGTH + 1000)

        result = summarize_large_content(large_content, max_length=1000)

        assert len(result) <= 1000
        assert "CONTENT TRUNCATED:" in result
        assert "Original had" in result

    def test_get_content_size_info(self):
        """Test content size information calculation."""
        content = "Line 1\nLine 2\nLine 3"
        info = get_content_size_info(content)

        assert info["character_count"] == len(content)
        assert info["line_count"] == 3
        assert info["size_mb"] == round(len(content) / (1024 * 1024), 2)
        assert info["exceeds_limit"] == (len(content) > MAX_MCP_STRING_LENGTH)
        assert info["recommended_action"] in ["none", "truncate"]

    def test_get_content_size_info_large(self):
        """Test content size info for large content."""
        large_content = "x" * (MAX_MCP_STRING_LENGTH + 1000)
        info = get_content_size_info(large_content)

        assert info["exceeds_limit"] is True
        assert info["recommended_action"] == "truncate"
        assert info["character_count"] > MAX_MCP_STRING_LENGTH

    def test_safe_mcp_output(self):
        """Test the main safe output function."""
        large_string = "x" * (MAX_MCP_STRING_LENGTH + 1000)
        test_data = {
            "results": [
                {"content": large_string, "id": 1},
                {"content": "small", "id": 2},
            ],
            "metadata": {"total": 2},
        }

        result = safe_mcp_output(test_data)

        assert result["metadata"]["total"] == 2
        assert result["results"][1]["content"] == "small"
        assert result["results"][1]["id"] == 2
        assert len(result["results"][0]["content"]) < len(large_string)
        assert "[TRUNCATED:" in result["results"][0]["content"]
