"""Test configuration and fixtures."""

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "JIRA_SERVER": "https://test.atlassian.net",
        "JIRA_USER": "test@example.com",
        "JIRA_API_TOKEN": "test-token",
        "ADO_ORG": "test-org",
        "ADO_PROJECT": "test-project",
        "ADO_REPO": "test-repo",
        "ADO_PAT": "test-pat",
        "OPENAI_API_KEY": "test-openai-key",
        "LOG_LEVEL": "DEBUG",
        "LOG_FORMAT": "json",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_jira_issue():
    """Mock Jira issue data."""
    return {
        "key": "TEST-123",
        "summary": "Test issue summary",
        "description": "Test issue description",
        "labels": ["bug", "high-priority"],
        "issuetype": "Bug",
        "project": "TEST",
        "raw": {"fields": {"components": []}},
    }


@pytest.fixture
def mock_jira_client():
    """Mock JIRA client."""
    mock_client = MagicMock()
    mock_issue = MagicMock()
    mock_issue.key = "TEST-123"
    mock_issue.fields.summary = "Test issue summary"
    mock_issue.fields.description = "Test issue description"
    mock_issue.fields.labels = ["bug", "high-priority"]
    mock_issue.fields.issuetype.name = "Bug"
    mock_issue.fields.project.key = "TEST"
    mock_issue.raw = {"fields": {"components": []}}

    mock_client.issue.return_value = mock_issue
    return mock_client
