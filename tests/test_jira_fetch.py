"""Unit tests for Jira fetch module."""

from unittest.mock import MagicMock, patch

import pytest

from src.jira_fetch import fetch_issue, get_jira_client


class TestJiraFetch:
    """Test Jira integration functionality."""

    @patch("src.jira_fetch.JIRA")
    @patch("src.jira_fetch.Settings")
    def test_get_jira_client(self, mock_settings, mock_jira_class):
        """Test Jira client initialization."""
        mock_settings.JIRA_SERVER = "https://test.atlassian.net"
        mock_settings.JIRA_USER = "test@example.com"
        mock_settings.JIRA_API_TOKEN = "test-token"

        mock_jira_instance = MagicMock()
        mock_jira_class.return_value = mock_jira_instance

        client = get_jira_client()

        mock_jira_class.assert_called_once_with(
            options={"server": "https://test.atlassian.net"},
            basic_auth=("test@example.com", "test-token"),
        )
        assert client == mock_jira_instance

    @patch("src.jira_fetch.get_jira_client")
    def test_fetch_issue(self, mock_get_client, mock_jira_client, mock_jira_issue):
        """Test fetching a Jira issue."""
        mock_get_client.return_value = mock_jira_client

        result = fetch_issue("TEST-123")

        mock_jira_client.issue.assert_called_once_with("TEST-123")

        expected = {
            "key": "TEST-123",
            "summary": "Test issue summary",
            "description": "Test issue description",
            "labels": ["bug", "high-priority"],
            "issuetype": "Bug",
            "project": "TEST",
            "raw": {"fields": {"components": []}},
        }

        assert result == expected

    @patch("src.jira_fetch.get_jira_client")
    def test_fetch_issue_with_none_fields(self, mock_get_client):
        """Test fetching a Jira issue with None fields."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_issue = MagicMock()
        mock_issue.key = "TEST-456"
        mock_issue.fields.summary = "Test summary"
        mock_issue.fields.description = None
        mock_issue.fields.labels = None
        mock_issue.fields.issuetype = None
        mock_issue.fields.project = None
        mock_issue.raw = {"test": "data"}

        mock_client.issue.return_value = mock_issue

        result = fetch_issue("TEST-456")

        expected = {
            "key": "TEST-456",
            "summary": "Test summary",
            "description": None,
            "labels": [],
            "issuetype": None,
            "project": None,
            "raw": {"test": "data"},
        }

        assert result == expected
