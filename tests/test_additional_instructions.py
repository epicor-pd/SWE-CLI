"""Additional tests for the additional instructions functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import main


class TestAdditionalInstructions:
    """Test cases specifically for the additional instructions feature."""

    @patch("src.main.run_codex")
    @patch("src.main.build_context_instructions")
    @patch("src.main.fetch_issue")
    @patch("src.main.Path")
    @patch(
        "sys.argv",
        [
            "main.py",
            "--jira",
            "TEST-123",
            "--ado-repo",
            "test-repo",
            "--additional-instructions",
            "",
        ],
    )
    def test_empty_additional_instructions(
        self, mock_path, mock_fetch_issue, mock_build_context, mock_run_codex
    ):
        """Test main function with empty additional instructions."""
        # Setup mocks
        mock_issue = {"key": "TEST-123", "summary": "Test issue"}
        mock_fetch_issue.return_value = mock_issue
        mock_build_context.return_value = "context instructions"

        mock_prompt_path = MagicMock()
        mock_prompt_path.read_text.return_value = (
            "{{JIRA_JSON}} {{CONTEXT_INSTRUCTIONS}} {{ADDITIONAL_INSTRUCTIONS}}"
        )
        mock_path.return_value = mock_prompt_path

        mock_workspace_path = MagicMock()
        mock_workspace_path.expanduser.return_value.resolve.return_value = "/workspace"
        mock_path.side_effect = [mock_prompt_path, mock_workspace_path]

        mock_run_codex.return_value = 0

        # Run the test
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Verify the prompt was processed correctly (empty additional instructions should result in empty string)
        args, kwargs = mock_run_codex.call_args
        prompt_content = args[0]

        # Should not contain placeholder anymore
        assert "{{ADDITIONAL_INSTRUCTIONS}}" not in prompt_content

        # Verify exit code
        assert exc_info.value.code == 0

    @patch("src.main.run_codex")
    @patch("src.main.build_context_instructions")
    @patch("src.main.fetch_issue")
    @patch("src.main.Path")
    @patch(
        "sys.argv",
        [
            "main.py",
            "--jira",
            "TEST-123",
            "--ado-repo",
            "test-repo",
            "--additional-instructions",
            "Very long instructions that might impact token counting and context window management. This is to test the interaction between additional instructions and the context window management system. These instructions should be included in the token estimation process to ensure that the prompt does not exceed the model context limits.",
        ],
    )
    def test_long_additional_instructions(
        self, mock_path, mock_fetch_issue, mock_build_context, mock_run_codex
    ):
        """Test main function with very long additional instructions to test token estimation."""
        # Setup mocks
        mock_issue = {"key": "TEST-123", "summary": "Test issue"}
        mock_fetch_issue.return_value = mock_issue
        mock_build_context.return_value = "context instructions"

        mock_prompt_path = MagicMock()
        mock_prompt_path.read_text.return_value = (
            "{{JIRA_JSON}} {{CONTEXT_INSTRUCTIONS}} {{ADDITIONAL_INSTRUCTIONS}}"
        )
        mock_path.return_value = mock_prompt_path

        mock_workspace_path = MagicMock()
        mock_workspace_path.expanduser.return_value.resolve.return_value = "/workspace"
        mock_path.side_effect = [mock_prompt_path, mock_workspace_path]

        mock_run_codex.return_value = 0

        # Run the test
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Verify the prompt was processed correctly
        args, kwargs = mock_run_codex.call_args
        prompt_content = args[0]

        # Should contain the long instructions
        assert (
            "Very long instructions that might impact token counting" in prompt_content
        )
        assert "{{ADDITIONAL_INSTRUCTIONS}}" not in prompt_content

        # Verify exit code
        assert exc_info.value.code == 0

    @patch("src.main.run_codex")
    @patch("src.main.build_context_instructions")
    @patch("src.main.fetch_issue")
    @patch("src.main.Path")
    @patch(
        "sys.argv",
        [
            "main.py",
            "--jira",
            "TEST-123",
            "--ado-repo",
            "test-repo",
            "--additional-instructions",
            "Instructions with\nmultiple\nlines\nand special characters: !@#$%^&*()",
        ],
    )
    def test_multiline_additional_instructions(
        self, mock_path, mock_fetch_issue, mock_build_context, mock_run_codex
    ):
        """Test main function with multiline additional instructions containing special characters."""
        # Setup mocks
        mock_issue = {"key": "TEST-123", "summary": "Test issue"}
        mock_fetch_issue.return_value = mock_issue
        mock_build_context.return_value = "context instructions"

        mock_prompt_path = MagicMock()
        mock_prompt_path.read_text.return_value = (
            "{{JIRA_JSON}} {{CONTEXT_INSTRUCTIONS}} {{ADDITIONAL_INSTRUCTIONS}}"
        )
        mock_path.return_value = mock_prompt_path

        mock_workspace_path = MagicMock()
        mock_workspace_path.expanduser.return_value.resolve.return_value = "/workspace"
        mock_path.side_effect = [mock_prompt_path, mock_workspace_path]

        mock_run_codex.return_value = 0

        # Run the test
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Verify the prompt was processed correctly
        args, kwargs = mock_run_codex.call_args
        prompt_content = args[0]

        # Should contain the multiline instructions and special characters
        assert "Instructions with\nmultiple\nlines" in prompt_content
        assert "!@#$%^&*()" in prompt_content
        assert "{{ADDITIONAL_INSTRUCTIONS}}" not in prompt_content

        # Verify exit code
        assert exc_info.value.code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
