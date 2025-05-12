## 7. Logging & Observability  
### 7.1 Mandatory Format — **JSON Lines (jsonl)**  
All runtime logs **must be emitted as JSON objects, one per line** (a.k.a. *jsonl*) to guarantee machine‑readability and easy ingestion by ELK, Loki, Stackdriver, Datadog, etc.  
| Field        | Example                    | Notes                                                        |
| ------------ | -------------------------- | ------------------------------------------------------------ |
| `timestamp`  | `2025‑05‑12T13:37:49.123Z` | ISO‑8601, always **UTC**.                                    |
| `level`      | `INFO` / `ERROR` / `DEBUG` | Standard levels.                                             |
| `message`    | `"User created"`           | Human‑readable action description.                           |
| `module`     | `"app.api.users"`          | Python module path.                                          |
| `function`   | `"create_user"`            | Function or method.                                          |
| `line`       | `42`                       | Source line.                                                 |
| `request_id` | `"03f4…"`                  | Correlation / trace ID (optional but highly encouraged).     |
| `extra`      | `{…}`                      | Domain‑specific key‑values (e.g., `user_id`, `order_total`). |  
> One line ⇢ one JSON object ⇢ no multiline stack traces; Python exceptions are rendered into `exc_info` fields.  
### 7.2 Recommended Stack  
| Library                | Purpose                                                          | Install                             |
| ---------------------- | ---------------------------------------------------------------- | ----------------------------------- |
| **structlog**          | Thin wrapper around stdlib logging that outputs structured JSON. | `uv pip install structlog`          |
| **python‑json‑logger** | Drop‑in `logging.Formatter` producing jsonl.                     | `uv pip install python‑json‑logger` |
| **loguru** (optional)  | Batteries‑included alternative with JSON sink.                   | `uv pip install loguru`             |  
### 7.3 Minimal Example (structlog)  
```python
# app/logging_config.py
import logging, sys, structlog

logging.basicConfig(
format="%(message)s",  # structlog will render JSON
stream=sys.stdout,
level=logging.INFO,
)

structlog.configure(
processors=[
structlog.processors.TimeStamper(fmt="iso", utc=True),
structlog.processors.StackInfoRenderer(),
structlog.processors.format_exc_info,
structlog.processors.JSONRenderer(),
],
wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info("User created", user_id=123)
```  
Output (one line):  
```jsonl
{"timestamp":"2025-05-12T13:37:49.123Z","level":"info","message":"User created","user_id":123}
```  
### 7.4 Best Practices  
1. **Log to stdout** inside containers; let the orchestrator handle aggregation.
2. **Never log secrets** — mask tokens, passwords, PII.
3. **Use correlation IDs**: propagate `request_id`/`trace_id` from ingress to downstream calls.
4. **Set log level via env var** (`LOG_LEVEL=DEBUG`) and default to `INFO`.
5. **Rotation in dev**: use `TimedRotatingFileHandler` or `loguru` sink to keep disk usage sane.
6. **Alerting hooks**: send `ERROR` logs to Sentry or PagerDuty via handler.
7. **Test log output**: add pytest‑style capture assertions to ensure correct fields.  
### 7.5 CI Check  
Add a lint step that parses a sample log line to verify valid JSON:  
```bash
python -c 'import json,sys; json.loads(sys.stdin.readline())' < sample.log
```  
Failure means the formatter emitted invalid JSON—block the PR.  
> **Rule**: Any new service/component must initialize logging via the shared `logging_config.py` or an equivalent module that produces jsonl.  
**Error Tracking**: integrate Sentry.  
```python
import sentry_sdk; sentry_sdk.init(dsn=getenv("SENTRY_DSN"), traces_sample_rate=0.1)
```  
---