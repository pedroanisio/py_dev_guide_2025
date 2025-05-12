## 7. Logging & Observability

Effective logging is crucial for debugging, monitoring, and understanding application behavior in production.

### 7.1 Mandatory Format — **JSON Lines (jsonl)**

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
| `request_id` | `"uuid-03f4..."`           | **Highly Recommended.** Correlation ID (e.g., Trace ID) for tracking requests across services/calls.     |
| `exc_info`   | `"Traceback..."` or `null` | Exception traceback string, if an exception occurred. Handled automatically by formatters.             |
| `extra`      | `{"user_id": 123, ...}`   | Optional dictionary for domain-specific context (e.g., `user_id`, `order_id`, `duration_ms`).             |

> **Key Principle:** Each line is a self-contained, valid JSON document. Avoid multi-line log messages or stack traces directly in the output; they should be captured within the `exc_info` field or structured within the JSON object.

### 7.2 Recommended Logging Libraries

While Python's built-in `logging` module is the foundation, these libraries simplify structured logging:

| Library                                                       | Purpose                                                                                       | Install Command                  |
| :------------------------------------------------------------ | :-------------------------------------------------------------------------------------------- | :------------------------------- |
| **[`structlog`](https://www.structlog.org/)**                 | **Preferred.** Powerful wrapper around standard logging, enabling flexible processor pipelines for structured output (JSON, key-value). | `uv pip install structlog`       |
| [`python-json-logger`](https://github.com/madzak/python-json-logger) | Drop-in `logging.Formatter` subclass that produces JSON output. Simpler alternative if `structlog` feels too complex. | `uv pip install python-json-logger` |
| [`loguru`](https://loguru.readthedocs.io/) (Optional)         | Batteries-included logging library offering a different API, with built-in support for JSON sinks and file rotation. | `uv pip install loguru`          |

### 7.3 Minimal Example (`structlog`)

This example sets up `structlog` to format logs as JSON lines sent to `stdout`.

```python
# src/<app_name>/logging_config.py
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

### 7.4 Best Practices

1.  **Log to `stdout`/`stderr`:** In containerized environments (Docker, Kubernetes), always log to standard output/error streams. Let the container orchestrator or log collector agent handle log aggregation, rotation, and shipping.
2.  **Never Log Sensitive Data:** Avoid logging secrets, passwords, API keys, personally identifiable information (PII), or sensitive financial data directly. Use masking techniques or ensure sensitive fields are excluded from log context.
3.  **Use Correlation IDs:** Propagate a unique request or trace ID (e.g., from an incoming HTTP header like `X-Request-ID` or generated at the start of a task) through all log messages related to that request/task. This is essential for tracing operations across distributed systems.
4.  **Configurable Log Level:** Make the logging level configurable via an environment variable (e.g., `LOG_LEVEL`). Default to `INFO` in production and allow `DEBUG` for troubleshooting.
5.  **Development Logging:** For local development, consider logging to a file with rotation using [`logging.handlers.TimedRotatingFileHandler`](https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler) or a [`loguru` sink](https://loguru.readthedocs.io/en/stable/api/logger.html#sink) to manage disk space.
6.  **Alerting & Monitoring Hooks:** Integrate critical error logging (`ERROR`, `CRITICAL`) with alerting systems like [Sentry](https://sentry.io/) or [PagerDuty](https://www.pagerduty.com/) using dedicated logging handlers or SDK integrations.
7.  **Test Log Output:** Include tests (e.g., using [`pytest`'s log capture fixtures](https://docs.pytest.org/en/stable/how-to/logging.html)) to assert that specific log messages are emitted with the correct level and structured fields under certain conditions.

### 7.5 CI Check for Valid JSON

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

**Recommended Error Tracking: [Sentry](https://sentry.io/)**

Integrate Sentry for automated error reporting and monitoring:

```python
import sentry_sdk
import os

def initialize_sentry():
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

# Call initialize_sentry() during application startup
```

---