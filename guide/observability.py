from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import json
import os
import sys
import logging
import datetime
import uuid
import traceback
from contextlib import contextmanager
import contextvars

@dataclass
class LogField:
    """Represents a standard log record field"""
    name: str
    example: str
    description: str
    required: bool = False


@dataclass
class LoggingLibrary:
    """Represents a recommended logging library"""
    name: str
    url: str
    purpose: str
    install_command: str
    is_preferred: bool = False


class LoggingObservabilityStandards:
    """
    Logging & Observability Standards
    
    A class representing the standard logging and observability practices
    for Python applications.
    """
    
    def __init__(self):
        self.name = "Logging & Observability Standards"
        self.format = "JSON Lines (jsonl)"
        self.format_description = "All runtime logs must be emitted as structured JSON objects, with one complete JSON object per line."
        
        # Standard Log Record Fields
        self.standard_fields = [
            LogField("timestamp", "2025-05-12T13:37:49.123Z", "ISO-8601 format, always in UTC.", True),
            LogField("level", "INFO / ERROR / DEBUG", "Standard Python logging levels.", True),
            LogField("message", "User created successfully", "Concise, human-readable description of the event.", True),
            LogField("logger", "app.services.users", "Name of the logger instance (often corresponds to module)."),
            LogField("module", "users", "Python module name where the log originated."),
            LogField("function", "create_user", "Function or method name."),
            LogField("line", "42", "Source code line number."),
            LogField("trace_id", "uuid-03f4...", "Correlation ID for tracking requests across services/calls."),
            LogField("exc_info", "Traceback... or null", "Exception traceback string, if an exception occurred."),
            LogField("context", '{"user_id": 123, ...}', "Optional dictionary for domain-specific context."),
        ]
        
        # Recommended logging libraries
        self.recommended_libraries = [
            LoggingLibrary(
                "structlog", 
                "https://www.structlog.org/", 
                "Powerful wrapper around standard logging, enabling flexible processor pipelines for structured output (JSON, key-value).",
                "uv pip install structlog",
                True
            ),
            LoggingLibrary(
                "python-json-logger",
                "https://github.com/madzak/python-json-logger",
                "Drop-in logging.Formatter subclass that produces JSON output. Simpler alternative if structlog feels too complex.",
                "uv pip install python-json-logger"
            ),
            LoggingLibrary(
                "loguru",
                "https://loguru.readthedocs.io/",
                "Batteries-included logging library offering a different API, with built-in support for JSON sinks and file rotation.",
                "uv pip install loguru"
            )
        ]
        
        # Best practices
        self.best_practices = [
            "Log to stdout/stderr: In containerized environments, always log to standard output/error streams.",
            "Never Log Sensitive Data: Avoid logging secrets, passwords, API keys, PII, or sensitive financial data.",
            "Use Correlation IDs: Propagate a unique request or trace ID through all log messages related to that request/task.",
            "Configurable Log Level: Make the logging level configurable via an environment variable (e.g., LOG_LEVEL).",
            "Development Logging: For local development, consider logging to a file with rotation.",
            "Alerting & Monitoring Hooks: Integrate critical error logging with alerting systems.",
            "Test Log Output: Include tests to assert that specific log messages are emitted correctly."
        ]
        
        # Log level guidelines
        self.log_levels = {
            "DEBUG": "Detailed information for troubleshooting (function entry/exit points, variable values)",
            "INFO": "Normal operations (request handled, service actions)",
            "WARNING": "Potential issues (deprecated API calls, service degradation)",
            "ERROR": "Error conditions (failed to process request, database errors)",
            "CRITICAL": "Critical failures (service unavailable, data corruption)"
        }
        
        # Context variables for request tracking
        self.request_id_var = contextvars.ContextVar("request_id", default=None)
        self.trace_id_var = contextvars.ContextVar("trace_id", default=None)
        self.user_id_var = contextvars.ContextVar("user_id", default=None)
    
    def get_structlog_implementation(self) -> str:
        """Returns the recommended structlog implementation code"""
        return """
# src/<app_name>/logging_config.py
import logging
import sys
import structlog
import os # For environment variables

def setup_logging():
    \"\"\"Configures logging using structlog to output JSON lines.\"\"\"

    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Configure standard logging first
    logging.basicConfig(
        format="%(message)s", # Basic format, structlog processors will handle the details
        stream=sys.stdout,    # Log to stdout for containerized environments
        level=log_level,
    )

    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level and logger name info from the standard logger
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            # Add contextual information (bound variables)
            structlog.contextvars.merge_contextvars,
            # Add caller info (module, function, line number)
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            # Add timestamp in ISO format (UTC)
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            # Render exceptions
            structlog.processors.StackInfoRenderer(), # Adds stack info for exceptions
            structlog.processors.format_exc_info,     # Formats exception info
            # Render the final log record as JSON
            structlog.processors.JSONRenderer(),
        ],
        # Use a standard logger wrapper for compatibility
        wrapper_class=structlog.stdlib.BoundLogger,
        # Use logger factory that integrates with standard logging
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Cache logger instances for performance
        cache_logger_on_first_use=True,
    )

# Call this function early in your application startup
# setup_logging()

# Get a logger instance
# logger = structlog.get_logger("my_module")

# Example Usage:
# logger.info("User logged in", user_id=456, ip_address="192.168.1.100")
# try:
#     1 / 0
# except ZeroDivisionError:
#     logger.error("Division failed", exc_info=True)
"""
    
    def get_stdlib_implementation(self) -> str:
        """Returns the standard library implementation code"""
        return """
import logging
import json
import sys
import traceback
import datetime
from typing import Dict, Any, Optional, Union
from contextlib import contextmanager
import uuid
import os

# Thread-local storage for request context
import contextvars
request_id_var = contextvars.ContextVar("request_id", default=None)
trace_id_var = contextvars.ContextVar("trace_id", default=None)
user_id_var = contextvars.ContextVar("user_id", default=None)


class JsonlFormatter(logging.Formatter):
    \"\"\"JSON Lines formatter for structured logging\"\"\"
    
    def format(self, record: logging.LogRecord) -> str:
        \"\"\"Format LogRecord as JSON string\"\"\"
        log_object = {
            # Standard fields (always included)
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            
            # Source location fields
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            
            # Context fields
            "trace_id": getattr(record, "trace_id", None) or trace_id_var.get(),
            "request_id": getattr(record, "request_id", None) or request_id_var.get(),
            "user_id": getattr(record, "user_id", None) or user_id_var.get(),
        }
        
        # Include exception info if present
        if record.exc_info:
            log_object["exc_info"] = self.formatException(record.exc_info)
        
        # Include any extra attributes from the LogRecord
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename",
                          "funcName", "id", "levelname", "levelno", "lineno", "module",
                          "msecs", "message", "msg", "name", "pathname", "process",
                          "processName", "relativeCreated", "stack_info", "thread", "threadName",
                          "trace_id", "request_id", "user_id"]:
                log_object[key] = value
        
        return json.dumps(log_object)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    \"\"\"Set up a logger with JSON Lines formatting\"\"\"
    # Get the log level from the string name
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Create a handler that writes to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonlFormatter())
    root_logger.addHandler(handler)
    
    return root_logger


@contextmanager
def log_context(**context):
    \"\"\"Context manager for adding context to logs\"\"\"
    # Store the previous context values
    prev_trace_id = trace_id_var.get()
    prev_request_id = request_id_var.get()
    prev_user_id = user_id_var.get()
    
    # Set the new context values
    if "trace_id" in context:
        trace_id_var.set(context["trace_id"])
    if "request_id" in context:
        request_id_var.set(context["request_id"])
    if "user_id" in context:
        user_id_var.set(context["user_id"])
    
    try:
        yield
    finally:
        # Restore the previous context values
        trace_id_var.set(prev_trace_id)
        request_id_var.set(prev_request_id)
        user_id_var.set(prev_user_id)


# Example usage:
# logger = setup_logging("DEBUG")
# with log_context(request_id="req-123", user_id=456):
#     logger.info("Processing request")
#     try:
#         # Some operation
#         result = 1 / 0
#     except Exception as e:
#         logger.error("Operation failed", exc_info=True, operation="division")
"""
    
    def get_fastapi_integration(self) -> str:
        """Returns FastAPI integration code"""
        return """
import uuid
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import structlog
import logging
import os

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format="%(message)s",
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("api")

# Create a context var for storing trace ID
request_id_var = contextvars.ContextVar("request_id", default=None)
user_id_var = contextvars.ContextVar("user_id", default=None)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a unique ID for this request
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Add the request ID to request state for handlers to access
        request.state.request_id = request_id
        
        # Log the start of the request
        logger.info(
            "Request started", 
            method=request.method, 
            path=request.url.path,
            request_id=request_id,
            client=request.client.host if request.client else None
        )
        
        # Time the request
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log the completed request
            logger.info(
                "Request completed",
                request_id=request_id,
                status_code=response.status_code,
                process_time=f"{process_time:.4f}s",
            )
            
            return response
            
        except Exception as e:
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log the exception
            logger.error(
                "Request failed",
                request_id=request_id,
                error=str(e),
                exc_info=True,
                process_time=f"{process_time:.4f}s",
            )
            raise


# Example usage:
# app = FastAPI()
# app.add_middleware(LoggingMiddleware)
# 
# @app.get("/")
# async def root():
#     logger.info("Inside root endpoint", custom_field="value")
#     return {"message": "Hello World"}
"""
    
    def get_sentry_integration(self) -> str:
        """Returns code for Sentry integration"""
        return """
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

# Configure standard logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Sentry for error tracking
sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/12345",  # Replace with your actual DSN
    # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
    # We recommend adjusting this value in production
    traces_sample_rate=0.2,  # Capture 20% of transactions
    
    # Configure Sentry to capture logs
    integrations=[
        LoggingIntegration(
            level=logging.INFO,      # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        ),
    ],
    
    # Include environment info
    environment=os.getenv("ENVIRONMENT", "development"),
    
    # Associate users with errors by setting the user context
    # sentry_sdk.set_user({"id": user_id, "email": user_email})
)

# Example usage:
# try:
#     division_by_zero = 1 / 0
# except Exception as e:
#     logger.error("Error performing calculation", exc_info=True)
#     # Error will be captured by Sentry
"""
    
    def create_basic_jsonl_logger(self) -> logging.Logger:
        """Create and return a basic JSONL-formatted logger"""
        # Configure a logger using Python's built-in logging module
        class JsonlFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "logger": record.name,
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                
                # Add extra fields if available
                for key, value in record.__dict__.items():
                    if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename",
                                "funcName", "id", "levelname", "levelno", "lineno", "module",
                                "msecs", "message", "msg", "name", "pathname", "process",
                                "processName", "relativeCreated", "stack_info", "thread", "threadName"]:
                        log_record[key] = value
                
                # Add exception info if present
                if record.exc_info:
                    log_record["exc_info"] = self.formatException(record.exc_info)
                
                return json.dumps(log_record)
        
        # Create logger
        logger = logging.getLogger("app")
        logger.setLevel(logging.INFO)
        
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonlFormatter())
        
        # Only add the handler if it's not already there
        if not logger.handlers:
            logger.addHandler(handler)
        
        return logger
    
    def __str__(self):
        """String representation of logging standards"""
        return f"{self.name} with {self.format} format"


# Example usage
if __name__ == "__main__":
    logging_standards = LoggingObservabilityStandards()
    
    print(f"🔍 {logging_standards}")
    
    print("\n📋 Standard Log Record Fields:")
    for field in logging_standards.standard_fields:
        req_mark = "*" if field.required else " "
        print(f"{req_mark} {field.name}: {field.example}")
        print(f"  {field.description}")
    
    print("\n📚 Recommended Libraries:")
    for lib in logging_standards.recommended_libraries:
        star = "⭐" if lib.is_preferred else " "
        print(f"{star} {lib.name}: {lib.purpose}")
        print(f"  {lib.url}")
        print(f"  Install: {lib.install_command}")
    
    print("\n✅ Best Practices:")
    for practice in logging_standards.best_practices:
        print(f"• {practice}")
    
    print("\n🔧 Log Level Guidelines:")
    for level, description in logging_standards.log_levels.items():
        print(f"• {level}: {description}")
    
    print("\n💻 Example Implementation (structlog):")
    print(logging_standards.get_structlog_implementation()) 