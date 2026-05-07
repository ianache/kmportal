"""Structured logging configuration for the Knowledge Management API.

This module configures structured JSON logging using structlog for production
environments, making logs easily parseable by log aggregation systems.

Usage:
    from core.logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("event_description", key="value", user_id="123")
"""

import logging
import sys
from typing import Any

import structlog


def configure_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to output JSON formatted logs (True for production)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Shared processors for all loggers
    shared_processors: list[Any] = [
        # Add timestamp in ISO format
        structlog.processors.TimeStamper(fmt="iso"),
        # Add log level
        structlog.stdlib.add_log_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Format positional arguments
        structlog.stdlib.PositionalArgumentsFormatter(),
        # Add caller info (file, line, function)
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        # Process stack info
        structlog.processors.StackInfoRenderer(),
        # Format exception info
        structlog.processors.format_exc_info,
        # Unescape HTML in log messages
        structlog.processors.UnicodeDecoder(),
    ]

    if json_format:
        # JSON format for production
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        # Pretty console format for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger

    Example:
        logger = get_logger(__name__)
        logger.info(
            "user_login",
            user_id="user123",
            ip_address="192.168.1.1",
            method="oauth"
        )
    """
    return structlog.get_logger(name)


def bind_request_context(
    request_id: str | None = None,
    user_id: str | None = None,
    client_ip: str | None = None,
    **kwargs: Any
) -> Any:
    """
    Bind context variables that will be included in all subsequent log entries.

    Useful for adding request-specific context that should appear in all logs
    during that request.

    Args:
        request_id: Unique request identifier
        user_id: Authenticated user identifier
        client_ip: Client IP address
        **kwargs: Additional context variables

    Returns:
        Bound context that can be used as a context manager

    Example:
        with bind_request_context(request_id="abc123", user_id="user456"):
            logger.info("processing_request")
            # This log will include request_id and user_id
    """
    context = {}
    if request_id:
        context["request_id"] = request_id
    if user_id:
        context["user_id"] = user_id
    if client_ip:
        context["client_ip"] = client_ip
    context.update(kwargs)

    return structlog.contextvars.bind_contextvars(**context)
