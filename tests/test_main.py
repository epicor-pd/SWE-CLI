"""Unit tests for main module."""
import argparse
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from src.main import main, _parse_repos


class TestParseRepos:
    """Test the _parse_repos function."""
    
    def test_parse_repos_comma_separated(self):
        """Test parsing comma-separated repo list."""
        result = _parse_repos("repo1,repo2,repo3")
        assert result == ["repo1", "repo2", "repo3"]
    
    def test_parse_repos_space_separated(self):
        """Test parsing space-separated repo list."""
        result = _parse_repos("repo1 repo2 repo3")
        assert result == ["repo1", "repo2", "repo3"]
    
    def test_parse_repos_mixed_separators(self):
        """Test parsing mixed comma and space separators."""
        result = _parse_repos("repo1, repo2 repo3,repo4")
        assert result == ["repo1", "repo2", "repo3", "repo4"]
    
    def test_parse_repos_with_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        result = _parse_repos(" repo1 ,  repo2  , repo3 ")
        assert result == ["repo1", "repo2", "repo3"]
    
    def test_parse_repos_empty_string(self):
        """Test parsing empty string."""
        result = _parse_repos("")
        assert result == []
    
    def test_parse_repos_single_repo(self):
        """Test parsing single repo."""
        result = _parse_repos("repo1")
        assert result == ["repo1"]


class TestMain:
    """Test the main function."""
    
    @patch('src.main.run_codex')
    @patch('src.main.build_context_instructions')
    @patch('src.main.fetch_issue')
    @patch('src.main.Path')
    @patch('sys.argv', ['main.py', '--jira', 'TEST-123', '--ado-repo', 'test-repo'])
    def test_main_without_generate_tests(self, mock_path, mock_fetch_issue, mock_build_context, mock_run_codex):
        """Test main function without generate-tests flag."""
        # Setup mocks
        mock_issue = {"key": "TEST-123", "summary": "Test issue"}
        mock_fetch_issue.return_value = mock_issue
        mock_build_context.return_value = "context instructions"
        
        mock_prompt_path = MagicMock()
        mock_prompt_path.read_text.return_value = "{{JIRA_JSON}} {{CONTEXT_INSTRUCTIONS}}"
        mock_path.return_value = mock_prompt_path
        
        mock_workspace_path = MagicMock()
        mock_workspace_path.expanduser.return_value.resolve.return_value = "/workspace"
        mock_path.side_effect = [mock_prompt_path, mock_workspace_path]
        
        mock_run_codex.return_value = 0
        
        # Run the test
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Verify the correct prompt file was used
        mock_path.assert_any_call("prompts/codegen.md")
        
        # Verify the prompt was processed correctly
        expected_prompt = json.dumps(mock_issue, indent=2) + " context instructions"
        mock_run_codex.assert_called_once_with(expected_prompt, "/workspace")
        
        # Verify exit code
        assert exc_info.value.code == 0
    
    @patch('src.main.run_codex')
    @patch('src.main.build_context_instructions')
    @patch('src.main.fetch_issue')
    @patch('src.main.Path')
    @patch('sys.argv', ['main.py', '--jira', 'TEST-123', '--ado-repo', 'test-repo', '--generate-tests'])
    def test_main_with_generate_tests(self, mock_path, mock_fetch_issue, mock_build_context, mock_run_codex):
        """Test main function with generate-tests flag."""
        # Setup mocks
        mock_issue = {"key": "TEST-123", "summary": "Test issue"}
        mock_fetch_issue.return_value = mock_issue
        mock_build_context.return_value = "context instructions"
        
        mock_prompt_path = MagicMock()
        mock_prompt_path.read_text.return_value = "{{JIRA_JSON}} {{CONTEXT_INSTRUCTIONS}}"
        mock_path.return_value = mock_prompt_path
        
        mock_workspace_path = MagicMock()
        mock_workspace_path.expanduser.return_value.resolve.return_value = "/workspace"
        mock_path.side_effect = [mock_prompt_path, mock_workspace_path]
        
        mock_run_codex.return_value = 0
        
        # Run the test
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Verify the correct prompt file was used
        mock_path.assert_any_call("prompts/codegen_with_tests.md")
        
        # Verify the prompt was processed correctly
        expected_prompt = json.dumps(mock_issue, indent=2) + " context instructions"
        mock_run_codex.assert_called_once_with(expected_prompt, "/workspace")
        
        # Verify exit code
        assert exc_info.value.code == 0
    
    @patch('src.main.Settings')
    @patch('sys.argv', ['main.py', '--jira', 'TEST-123'])
    def test_main_missing_ado_repo(self, mock_settings):
        """Test main function raises error when no ADO repo is provided."""
        mock_settings.ADO_REPO = None
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert "Provide at least one repo" in str(exc_info.value)
    
    @patch('src.main.Settings')
    @patch('src.main.run_codex')
    @patch('src.main.build_context_instructions')
    @patch('src.main.fetch_issue')
    @patch('src.main.Path')
    @patch('sys.argv', ['main.py', '--jira', 'TEST-123'])
    def test_main_uses_settings_ado_repo(self, mock_path, mock_fetch_issue, mock_build_context, mock_run_codex, mock_settings):
        """Test main function uses ADO_REPO from settings when not provided as argument."""
        # Setup mocks
        mock_settings.ADO_REPO = "settings-repo"
        mock_settings.ADO_ORG = "test-org"
        mock_settings.ADO_PROJECT = "test-project"
        
        mock_issue = {"key": "TEST-123", "summary": "Test issue"}
        mock_fetch_issue.return_value = mock_issue
        mock_build_context.return_value = "context instructions"
        
        mock_prompt_path = MagicMock()
        mock_prompt_path.read_text.return_value = "{{JIRA_JSON}} {{CONTEXT_INSTRUCTIONS}}"
        mock_path.return_value = mock_prompt_path
        
        mock_workspace_path = MagicMock()
        mock_workspace_path.expanduser.return_value.resolve.return_value = "/workspace"
        mock_path.side_effect = [mock_prompt_path, mock_workspace_path]
        
        mock_run_codex.return_value = 0
        
        # Run the test
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Verify build_context_instructions was called with the repo from settings
        mock_build_context.assert_called_once_with("test-org", "test-project", ["settings-repo"])
        
        # Verify exit code
        assert exc_info.value.code == 0
    
    @patch('src.main.os.getcwd')
    @patch('src.main.run_codex')
    @patch('src.main.build_context_instructions')
    @patch('src.main.fetch_issue')
    @patch('src.main.Path')
    @patch('sys.argv', ['main.py', '--jira', 'TEST-123', '--ado-repo', 'test-repo'])
    def test_main_uses_default_workspace(self, mock_path, mock_fetch_issue, mock_build_context, mock_run_codex, mock_getcwd):
        """Test main function uses current directory as default workspace."""
        # Setup mocks
        mock_getcwd.return_value = "/current/dir"
        
        mock_issue = {"key": "TEST-123", "summary": "Test issue"}
        mock_fetch_issue.return_value = mock_issue
        mock_build_context.return_value = "context instructions"
        
        mock_prompt_path = MagicMock()
        mock_prompt_path.read_text.return_value = "{{JIRA_JSON}} {{CONTEXT_INSTRUCTIONS}}"
        
        mock_workspace_path = MagicMock()
        mock_workspace_path.expanduser.return_value.resolve.return_value = "/current/dir"
        mock_path.side_effect = [mock_prompt_path, mock_workspace_path]
        
        mock_run_codex.return_value = 0
        
        # Run the test
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Verify Path was called with the current directory
        mock_path.assert_any_call("/current/dir")
        
        # Verify exit code
        assert exc_info.value.code == 0
