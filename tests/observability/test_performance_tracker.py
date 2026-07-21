import time
from unittest.mock import Mock, patch

from agent.observability.performance_tracker import timing_decorator


def test_timing_decorator_logs_execution_time():
    """Test that timing_decorator logs execution time for decorated functions."""
    # Arrange
    with patch("structlog.get_logger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Define a dummy function that takes some time
        @timing_decorator
        def sample_function():
            time.sleep(0.1)

        # Act
        sample_function()

        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args

        # Check message
        assert call_args[0][0] == "Function execution time"

        # Check duration_ms is present and is a float > 100
        assert "duration_ms" in call_args[1]
        duration = call_args[1]["duration_ms"]
        assert isinstance(duration, float)
        assert duration > 100
