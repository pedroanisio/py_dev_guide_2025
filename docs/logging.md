## 8. Logging & Observability

Effective logging is crucial for debugging, monitoring, and understanding application behavior in production.

### 8.1 Mandatory Format — **JSON Lines (jsonl)**

All runtime logs **must** be emitted as structured JSON objects, with **one complete JSON object per line**. This format, often called [JSON Lines (`jsonl`)](http://jsonlines.org/), guarantees machine-readability and simplifies ingestion by log aggregation systems like Elasticsearch (ELK Stack), Grafana Loki, Google Cloud Logging (Stackdriver), Datadog, etc.

**Standard Log Record Fields:**

| Field        | Example                    | Description                                                                                                |
| :----------- | :------------------------- | :--------------------------------------------------------------------------------------------------------- |
| `timestamp`  | `2025-05-12T13:37:49.123Z` | **Required.** [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601) format, always in **UTC**.               |
| `level`      | `INFO` / `ERROR` / `DEBUG` | **Required.** Standard Python [logging levels](https://docs.python.org/3/library/logging.html#logging-levels). |
| `message`    | `"User created successfully"`  | **Required.** Concise, human-readable description of the event.                                            |
| `logger`     | `"app.services.users"`     | Name of the logger instance (often corresponds to module).                                               |
| `module`     | `"users"`                  | Python module name where the log originated.                                                             |
| `function`   | `"create_user"`            | Function or method name.                                                                                 |
| `line`       | `42`                       | Source code line number.                                                                                 |
| `trace_id`   | `"uuid-03f4..."`           | **Highly Recommended.** Correlation ID (e.g., Trace ID) for tracking requests across services/calls.     |
| `exc_info`   | `"Traceback..."` or `null` | Exception traceback string, if an exception occurred. Handled automatically by formatters.             |
| `context`    | `{"user_id": 123, ...}`   | Optional dictionary for domain-specific context (e.g., `user_id`, `order_id`, `duration_ms`).             |

> **Key Principle:** Each line is a self-contained, valid JSON document. Avoid multi-line log messages or stack traces directly in the output; they should be captured within the `exc_info` field or structured within the JSON object.

### 8.2 Recommended Logging Libraries

While Python's built-in `logging` module is the foundation, these libraries simplify structured logging:

| Library                                                       | Purpose                                                                                       | Install Command                  |
| :------------------------------------------------------------ | :-------------------------------------------------------------------------------------------- | :------------------------------- |
| **[`structlog`](https://www.structlog.org/)**                 | **Preferred.** Powerful wrapper around standard logging, enabling flexible processor pipelines for structured output (JSON, key-value). | `uv pip install structlog`       |
| [`python-json-logger`](https://github.com/madzak/python-json-logger) | Drop-in `logging.Formatter` subclass that produces JSON output. Simpler alternative if `structlog` feels too complex. | `uv pip install python-json-logger` |
| [`loguru`](https://loguru.readthedocs.io/) (Optional)         | Batteries-included logging library offering a different API, with built-in support for JSON sinks and file rotation. | `uv pip install loguru`          |

### 8.3 Primary Implementation with `structlog`

This example sets up `structlog` to format logs as JSON lines sent to `stdout`.

```python
# src/<app_name>/logging_config.py
"""
HDR-DESCRIPTION: Logging configuration 
HDR-FILENAME: logging_config.py
HDR-FILEPATH: app/core/logging_config.py
HDR-VERSION: 1.0.0
"""
import logging
import sys
import structlog
import os # For environment variables

def setup_logging():
    """Configures logging using structlog to output JSON lines."""

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
```

**Example Output (one line per log event):**

```jsonl
{"level": "info", "logger": "my_module", "event": "User logged in", "module": "main", "func_name": "<module>", "lineno": 10, "timestamp": "2025-05-12T14:01:15.123456Z", "user_id": 456, "ip_address": "192.168.1.100"}
{"level": "error", "logger": "my_module", "event": "Division failed", "module": "main", "func_name": "<module>", "lineno": 13, "timestamp": "2025-05-12T14:01:15.124567Z", "exc_info": "Traceback (most recent call last):\n  File \"main.py\", line 12, in <module>\n    1 / 0\nZeroDivisionError: division by zero"}
```

### 8.4 Alternative Implementation Without Dependencies

If you prefer to use only the standard library without additional dependencies, this alternative implementation provides a custom `JsonlFormatter`:

```python
"""
HDR-DESCRIPTION: Shared logging configuration using standard library
HDR-FILENAME: logging_config.py
HDR-FILEPATH: app/core/logging_config.py
HDR-VERSION: 1.0.0
"""
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
    """JSON Lines formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format LogRecord as JSON string"""
        log_object = {
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
            "trace_id": trace_id_var.get() or str(uuid.uuid4()),
        }
        
        # Add request_id if available
        if request_id := request_id_var.get():
            log_object["request_id"] = request_id
            
        # Add user_id if available
        if user_id := user_id_var.get():
            log_object["user_id"] = user_id
            
        # Add file and line information in development
        if os.environ.get("ENVIRONMENT") == "development":
            log_object["location"] = f"{record.pathname}:{record.lineno}"
            
        # Add exception info if present
        if record.exc_info:
            log_object["error"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
            
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key.startswith('_') or key in (
                'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
                'msecs', 'message', 'msg', 'name', 'pathname', 'process',
                'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'
            ):
                continue
                
            log_object[key] = value
            
        # Return JSON string with newline
        return json.dumps(log_object)


def configure_logging(
    level: int = logging.INFO,
    service_name: str = "app",
    handlers: Optional[list] = None
) -> None:
    """Configure logging for the application"""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Set up handlers
    handlers = handlers or [logging.StreamHandler(sys.stdout)]
    formatter = JsonlFormatter()
    
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        
    # Set service name
    logging.getLogger("service").info(f"Initialized logging for {service_name}")


@contextmanager
def log_context(**kwargs):
    """Context manager to add context variables to logs temporarily"""
    # Save old values
    old_values = {}
    for key, value in kwargs.items():
        if key == "request_id":
            old_values[key] = request_id_var.get()
            request_id_var.set(value)
        elif key == "trace_id":
            old_values[key] = trace_id_var.get()
            trace_id_var.set(value)
        elif key == "user_id":
            old_values[key] = user_id_var.get()
            user_id_var.set(value)
            
    try:
        yield
    finally:
        # Restore old values
        for key, value in old_values.items():
            if key == "request_id":
                request_id_var.set(value)
            elif key == "trace_id":
                trace_id_var.set(value)
            elif key == "user_id":
                user_id_var.set(value)


class StructuredLogger:
    """Logger that includes structured context with every log"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def _log(self, level: int, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log a message with additional structured context"""
        extra = kwargs.get("extra", {})
        if context:
            extra["context"] = context
        
        self.logger.log(level, msg, extra=extra, **kwargs)
        
    def debug(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(logging.DEBUG, msg, context, **kwargs)
        
    def info(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(logging.INFO, msg, context, **kwargs)
        
    def warning(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(logging.WARNING, msg, context, **kwargs)
        
    def error(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(logging.ERROR, msg, context, **kwargs)
        
    def critical(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(logging.CRITICAL, msg, context, **kwargs)
        
    def exception(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """Log exception information with traceback"""
        extra = kwargs.get("extra", {})
        if context:
            extra["context"] = context
            
        self.logger.exception(msg, extra=extra, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)
```

### 8.5 FastAPI Integration

Both logging approaches above can be easily integrated with FastAPI using middleware:

```python
"""
HDR-DESCRIPTION: FastAPI logging middleware
HDR-FILENAME: logging_middleware.py
HDR-FILEPATH: app/middleware/logging_middleware.py
HDR-VERSION: 1.0.0
"""
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from typing import Callable
import traceback

# For structlog implementation:
# import structlog
# logger = structlog.get_logger("app.middleware")

# For standard library implementation:
from app.core.logging_config import get_logger, log_context, request_id_var, trace_id_var, user_id_var
logger = get_logger("app.middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses with trace context"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate request_id and trace_id if not present
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        
        # Set context variables for this request - implementation specific
        
        # Standard lib implementation:
        request_id_var.set(request_id)
        trace_id_var.set(trace_id)
        
        # structlog implementation would use:
        # structlog.contextvars.bind_contextvars(
        #     request_id=request_id,
        #     trace_id=trace_id
        # )
        
        # Extract path and method
        path = request.url.path
        method = request.method
        
        # Log request
        start_time = time.time()
        
        logger.info(
            f"Request started {method} {path}",
            context={
                "request_id": request_id,
                "trace_id": trace_id,
                "method": method,
                "path": path,
                "query_params": dict(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("User-Agent"),
            }
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000)
            
            # Log response
            logger.info(
                f"Request completed {method} {path} - {response.status_code}",
                context={
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
            
            # Add custom headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Trace-ID"] = trace_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000)
            
            # Log exception
            logger.exception(
                f"Request failed {method} {path}",
                context={
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "method": method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e),
                        "traceback": traceback.format_exc(),
                    },
                }
            )
            
            # Re-raise the exception
            raise

def add_logging_middleware(app: FastAPI):
    """Add logging middleware to a FastAPI application"""
    app.add_middleware(LoggingMiddleware)
```

### 8.6 Best Practices

1.  **Log to `stdout`/`stderr`:** In containerized environments (Docker, Kubernetes), always log to standard output/error streams. Let the container orchestrator or log collector agent handle log aggregation, rotation, and shipping.
2.  **Never Log Sensitive Data:** Avoid logging secrets, passwords, API keys, personally identifiable information (PII), or sensitive financial data directly. Use masking techniques or ensure sensitive fields are excluded from log context.
3.  **Use Correlation IDs:** Propagate a unique request or trace ID (e.g., from an incoming HTTP header like `X-Request-ID` or generated at the start of a task) through all log messages related to that request/task. This is essential for tracing operations across distributed systems.
4.  **Configurable Log Level:** Make the logging level configurable via an environment variable (e.g., `LOG_LEVEL`). Default to `INFO` in production and allow `DEBUG` for troubleshooting.
5.  **Development Logging:** For local development, consider logging to a file with rotation using [`logging.handlers.TimedRotatingFileHandler`](https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler) or a [`loguru` sink](https://loguru.readthedocs.io/en/stable/api/logger.html#sink) to manage disk space.
6.  **Alerting & Monitoring Hooks:** Integrate critical error logging (`ERROR`, `CRITICAL`) with alerting systems like [Sentry](https://sentry.io/) or [PagerDuty](https://www.pagerduty.com/) using dedicated logging handlers or SDK integrations.
7.  **Test Log Output:** Include tests (e.g., using [`pytest`'s log capture fixtures](https://docs.pytest.org/en/stable/how-to/logging.html)) to assert that specific log messages are emitted with the correct level and structured fields under certain conditions.

### 8.7 CI Check for Valid JSON

Add a CI step to verify that the configured logger produces valid JSON. This catches formatting errors early.

**Example (`bash`):**

```bash
# 1. Run a minimal script that produces a sample log line
python your_app/minimal_log_emitter.py > /tmp/sample.log

# 2. Attempt to parse the first line as JSON
python -c 'import json, sys; print("Checking log format..."); json.loads(sys.stdin.readline()); print("Log format OK.")' < /tmp/sample.log
```

If `json.loads` fails, the script will exit with an error, failing the CI check and blocking the PR.

> **Rule:** All new services or components **must** initialize logging using a shared configuration module (like the `logging_config.py` example) that ensures adherence to the mandatory `jsonl` format.

### 8.8 Error Tracking with Sentry

Integrate Sentry for automated error reporting and monitoring:

```python
# app/core/sentry.py
"""
HDR-DESCRIPTION: Sentry integration for error tracking
HDR-FILENAME: sentry.py
HDR-FILEPATH: app/core/sentry.py
HDR-VERSION: 1.0.0
"""
import sentry_sdk
import os

def initialize_sentry():
    """Initialize Sentry for error tracking"""
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development") # e.g., development, staging, production
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # Adjust as needed for production environments.
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", 0.1)),
            environment=environment,
            # Consider enabling PII stripping if needed
            # send_default_pii=False
        )
        print(f"Sentry initialized for environment: {environment}")
    else:
        print("SENTRY_DSN not found, Sentry not initialized.")
```

### 8.9 Log Level Guidelines

Use appropriate log levels to categorize messages by importance:

| Level | Purpose | Example Use Case |
|-------|---------|-----------------|
| `DEBUG` | Detailed information for troubleshooting | Function entry/exit points, variable values |
| `INFO` | Normal operations | Request handled, service actions |
| `WARNING` | Potential issues | Deprecated API calls, service degradation |
| `ERROR` | Error conditions | Failed to process request, database errors |
| `CRITICAL` | Critical failures | Service unavailable, data corruption |

---