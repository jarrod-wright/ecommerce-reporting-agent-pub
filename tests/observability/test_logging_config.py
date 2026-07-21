"""Tests for observability logging configuration and correlation ID integration."""

import json
import logging

import pytest
import structlog

from agent.observability.logging_config import setup_logging


class LogCapture(logging.Handler):
    """Custom logging handler to capture log records for testing."""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        """Capture log records."""
        self.records.append(record)


def test_logging_includes_correlation_id_in_json_output():
    """Test that structured logging includes correlation ID in JSON output.

    This test ensures that the logging configuration properly integrates
    correlation IDs into structured log messages for the observability framework.
    """
    # Setup logging configuration
    setup_logging()

    # Create a custom handler to capture logs
    log_capture = LogCapture()

    # Configure structlog to use our custom formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer()
    )
    log_capture.setFormatter(formatter)

    # Get the root logger and add our capture handler
    root_logger = logging.getLogger()
    root_logger.addHandler(log_capture)

    # Simulate setting a correlation ID in context using structlog's context vars
    correlation_id = "test-correlation-123"

    # Bind correlation ID to structlog context (this is what the middleware does)
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    try:
        # Create a structlog logger
        logger = structlog.get_logger()

        # Log a simple message
        logger.info("Test log message", extra_field="test_value")

        # Ensure we captured a log record
        assert len(log_capture.records) > 0, f"No log records captured. Records: {log_capture.records}"

        # Get the last log record and format it
        log_record = log_capture.records[-1]
        formatted_message = log_capture.format(log_record)

        # Parse the log message as JSON
        try:
            log_data = json.loads(formatted_message)
        except json.JSONDecodeError as e:
            pytest.fail(f"Log output is not valid JSON. Message: '{formatted_message}', Error: {e}")

        # Assert that correlation_id is present in the JSON log
        assert "correlation_id" in log_data, f"correlation_id not found in log data: {log_data}"
        assert log_data["correlation_id"] == correlation_id, f"Expected {correlation_id}, got {log_data.get('correlation_id')}"

        # Additional assertions to verify the log structure
        assert "event" in log_data
        assert log_data["event"] == "Test log message"
        assert "extra_field" in log_data
        assert log_data["extra_field"] == "test_value"

    finally:
        # Clean up context variables to avoid affecting other tests
        structlog.contextvars.clear_contextvars()
        # Remove our test handler
        root_logger.removeHandler(log_capture)
