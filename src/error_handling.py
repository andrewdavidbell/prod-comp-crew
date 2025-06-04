"""
Error Handling System for AI Product Research System

This module provides a comprehensive error handling system for the AI Product Research System.
It defines custom exceptions, error logging, and error recovery mechanisms.
"""

import logging
import sys
import traceback
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Add file handler for logging
file_handler = logging.FileHandler(logs_dir / "system.log")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logging.getLogger().addHandler(file_handler)

# Create logger
logger = logging.getLogger("ai_product_research")


class ErrorSeverity(Enum):
    """Enum for error severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SystemError(Exception):
    """Base exception class for all system errors."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.severity = severity
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(SystemError):
    """Exception raised for errors in the configuration."""

    pass


class APIError(SystemError):
    """Exception raised for errors in API calls."""

    pass


class DataProcessingError(SystemError):
    """Exception raised for errors in data processing."""

    pass


class AgentError(SystemError):
    """Exception raised for errors in agent operations."""

    pass


class ValidationError(SystemError):
    """Exception raised for validation errors."""

    pass


def log_error(
    error: Union[SystemError, Exception], context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an error with context information.

    Args:
        error: The error to log
        context: Additional context information
    """
    context = context or {}

    if isinstance(error, SystemError):
        severity = error.severity
        details = error.details
    else:
        severity = ErrorSeverity.ERROR
        details = {}

    error_info = {
        "message": str(error),
        "type": error.__class__.__name__,
        "severity": severity.value
        if isinstance(severity, ErrorSeverity)
        else str(severity),
        "details": details,
        "context": context,
        "traceback": traceback.format_exc(),
    }

    if severity == ErrorSeverity.CRITICAL:
        logger.critical(f"CRITICAL ERROR: {error}", extra={"error_info": error_info})
    elif severity == ErrorSeverity.ERROR:
        logger.error(f"ERROR: {error}", extra={"error_info": error_info})
    elif severity == ErrorSeverity.WARNING:
        logger.warning(f"WARNING: {error}", extra={"error_info": error_info})
    else:
        logger.info(f"INFO: {error}", extra={"error_info": error_info})


def handle_error(
    error: Union[SystemError, Exception],
    context: Optional[Dict[str, Any]] = None,
    exit_on_critical: bool = True,
) -> Dict[str, Any]:
    """
    Handle an error by logging it and returning a structured error response.

    Args:
        error: The error to handle
        context: Additional context information
        exit_on_critical: Whether to exit the program on critical errors

    Returns:
        A structured error response
    """
    context = context or {}

    # Log the error
    log_error(error, context)

    # Determine severity
    if isinstance(error, SystemError):
        severity = error.severity
    else:
        severity = ErrorSeverity.ERROR

    # Create error response
    error_response = {
        "success": False,
        "error": {
            "message": str(error),
            "type": error.__class__.__name__,
            "severity": severity.value
            if isinstance(severity, ErrorSeverity)
            else str(severity),
        },
    }

    # Exit on critical errors if specified
    if severity == ErrorSeverity.CRITICAL and exit_on_critical:
        logger.critical("Exiting due to critical error")
        sys.exit(1)

    return error_response


def safe_execute(func, *args, **kwargs):
    """
    Execute a function safely, catching and handling any exceptions.

    Args:
        func: The function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function or an error response
    """
    try:
        return {"success": True, "result": func(*args, **kwargs)}
    except Exception as e:
        return handle_error(
            e, {"function": func.__name__, "args": args, "kwargs": kwargs}
        )


class ErrorHandler:
    """
    Context manager for handling errors in a block of code.

    Example:
        with ErrorHandler(context={"operation": "data_processing"}) as handler:
            # Code that might raise exceptions
            process_data()

        if handler.has_error:
            # Handle the error
            print(f"Error occurred: {handler.error}")
    """

    def __init__(
        self, context: Optional[Dict[str, Any]] = None, exit_on_critical: bool = False
    ):
        self.context = context or {}
        self.exit_on_critical = exit_on_critical
        self.error = None
        self.has_error = False
        self.error_response = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.has_error = True
            self.error = exc_val
            self.error_response = handle_error(
                exc_val, self.context, self.exit_on_critical
            )
            return True  # Suppress the exception
        return False


def retry(max_attempts: int = 3, retry_exceptions: Optional[List[type]] = None):
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        retry_exceptions: List of exception types to retry on

    Returns:
        Decorated function
    """
    retry_exceptions = retry_exceptions or [Exception]

    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            last_error = None

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if not retry_exceptions or any(
                        isinstance(e, exc) for exc in retry_exceptions
                    ):
                        attempts += 1
                        last_error = e
                        logger.warning(
                            f"Retry {attempts}/{max_attempts} for {func.__name__} due to: {e}"
                        )
                        if attempts >= max_attempts:
                            break
                    else:
                        # If the exception is not in the retry_exceptions list, re-raise it
                        raise

            # If we get here, all retries failed
            if last_error:
                return handle_error(
                    last_error,
                    {
                        "function": func.__name__,
                        "args": args,
                        "kwargs": kwargs,
                        "attempts": attempts,
                    },
                )

            # This should never happen, but just in case
            return handle_error(
                SystemError(
                    f"All {max_attempts} retry attempts failed for unknown reasons"
                ),
                {"function": func.__name__, "args": args, "kwargs": kwargs},
            )

        return wrapper

    return decorator
