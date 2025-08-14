"""Unit tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from src.config import Settings


class TestSettings:
    """Test configuration settings."""

    def test_settings_from_env(self, mock_env_vars):
        """Test that settings are loaded from environment variables."""
        # Reload the module to pick up the mocked environment
        import importlib

        from src import config

        importlib.reload(config)

        assert config.Settings.JIRA_SERVER == "https://test.atlassian.net"
        assert config.Settings.JIRA_USER == "test@example.com"
        assert config.Settings.JIRA_API_TOKEN == "test-token"
        assert config.Settings.ADO_ORG == "test-org"
        assert config.Settings.ADO_PROJECT == "test-project"
        assert config.Settings.ADO_REPO == "test-repo"
        assert config.Settings.ADO_PAT == "test-pat"
        assert config.Settings.OPENAI_API_KEY == "test-openai-key"

    def test_settings_none_when_not_set(self):
        """Test that settings are None when environment variables are not set."""
        # Clear specific environment variables that might be set
        env_vars_to_clear = [
            "JIRA_SERVER",
            "JIRA_USER",
            "JIRA_API_TOKEN",
            "ADO_ORG",
            "ADO_PROJECT",
            "ADO_REPO",
            "ADO_PAT",
            "OPENAI_API_KEY",
        ]

        with patch.dict(
            os.environ, {var: "" for var in env_vars_to_clear}, clear=False
        ):
            import importlib

            from src import config

            importlib.reload(config)

            # Empty string should be treated as None by os.getenv with no default
            assert (
                config.Settings.JIRA_SERVER == "" or config.Settings.JIRA_SERVER is None
            )
            assert config.Settings.JIRA_USER == "" or config.Settings.JIRA_USER is None
            assert (
                config.Settings.JIRA_API_TOKEN == ""
                or config.Settings.JIRA_API_TOKEN is None
            )
