"""Unit tests for logging setup module."""

import json
import logging
import os
import tempfile
from unittest.mock import patch

import pytest

from src.logging_setup import JsonFormatter, _state, configure_logging


class TestLoggingSetup:
    """Test logging configuration functionality."""

    def teardown_method(self):
        """Reset logging configuration after each test."""
        # Reset the configured state to allow reconfiguration
        _state.configured = False

        # Clear all handlers from root logger
        root = logging.getLogger()
        for handler in list(root.handlers):
            root.removeHandler(handler)

    def test_configure_logging_default(self):
        """Test default logging configuration."""
        with patch.dict(os.environ, {}, clear=True):
            configure_logging()

            root = logging.getLogger()
            assert root.level == logging.INFO
            assert len(root.handlers) == 1
            assert isinstance(root.handlers[0], logging.StreamHandler)

    def test_configure_logging_debug_level(self):
        """Test logging configuration with DEBUG level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            configure_logging()

            root = logging.getLogger()
            assert root.level == logging.DEBUG

    def test_configure_logging_json_format(self):
        """Test logging configuration with JSON format."""
        with patch.dict(os.environ, {"LOG_FORMAT": "json"}):
            configure_logging()

            root = logging.getLogger()
            handler = root.handlers[0]
            assert isinstance(handler.formatter, JsonFormatter)

    def test_configure_logging_with_file(self):
        """Test logging configuration with file output."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            log_file = tmp.name

        try:
            with patch.dict(os.environ, {"LOG_FILE": log_file}):
                configure_logging()

                root = logging.getLogger()
                assert len(root.handlers) == 2  # Console + file

                # Find the file handler
                file_handler = None
                for handler in root.handlers:
                    if isinstance(handler, logging.FileHandler):
                        file_handler = handler
                        break

                assert file_handler is not None
                assert file_handler.baseFilename == log_file
        finally:
            # Cleanup
            try:
                os.unlink(log_file)
            except OSError:
                pass

    def test_configure_logging_only_once(self):
        """Test that logging is only configured once."""
        configure_logging()
        root = logging.getLogger()
        initial_handler_count = len(root.handlers)

        # Second call should not add more handlers
        configure_logging()
        assert len(root.handlers) == initial_handler_count


class TestJsonFormatter:
    """Test JSON formatter functionality."""

    def test_json_formatter_basic(self):
        """Test basic JSON formatting."""
        formatter = JsonFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_function"

        result = formatter.format(record)
        data = json.loads(result)

        assert data["level"] == "INFO"
        assert data["name"] == "test.logger"
        assert data["message"] == "Test message"
        assert data["module"] == "test"
        assert data["func"] == "test_function"
        assert data["line"] == 42
        assert "time" in data

    def test_json_formatter_with_exception(self):
        """Test JSON formatting with exception info."""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        else:
            exc_info = None

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )
        record.module = "test"
        record.funcName = "test_function"

        result = formatter.format(record)
        data = json.loads(result)

        assert data["level"] == "ERROR"
        assert data["message"] == "Error occurred"
        assert "exc_info" in data
        assert "ValueError: Test exception" in data["exc_info"]
