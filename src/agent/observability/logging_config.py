"""Enhanced logging configuration with correlation ID support for observability framework."""

import logging

import structlog


def setup_logging():
    """Configure structured logging with correlation ID context support.
    
    This function configures structlog with a processor chain that includes:
    - Context variables merge (for correlation IDs)
    - JSON rendering for structured output
    
    The configuration supports the observability framework's requirement
    for linking logs and traces through correlation IDs.
    """
    # Configure structlog to work with standard library logging
    structlog.configure(
        processors=[
            # Merge context variables (including correlation_id) into log records
            structlog.contextvars.merge_contextvars,
            # Add log level to the output
            structlog.stdlib.add_log_level,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Pass to standard library logging with proper formatting
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # Use standard library logging as the final destination
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure the root logger to use structlog's processor formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer()
    )

    # Get or create the root logger
    root_logger = logging.getLogger()

    # Only configure if not already configured (avoid duplicate handlers in tests)
    if not root_logger.handlers or not any(
        isinstance(h.formatter, structlog.stdlib.ProcessorFormatter)
        for h in root_logger.handlers
    ):
        root_logger.handlers.clear()

        # Create handler that works with both production and testing
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

        # Ensure we don't propagate to avoid duplicate messages
        root_logger.propagate = False


def get_correlation_id():
    """Get the current correlation ID from context variables.
    
    This function is used for testing and can be mocked to simulate
    correlation ID presence in the context.
    
    Returns:
        str or None: The current correlation ID if bound in context
    """
    # This will be populated by structlog.contextvars.bind_contextvars()
    # For now, return None as a placeholder
    return None
