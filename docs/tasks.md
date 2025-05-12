## 10. Background Tasks, Messaging & Concurrency  
### 10.1 Choosing the Right Execution Model  
| Scenario                                                         | Recommendation                                                                   | Rationale                                           |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------- |
| Quick, non‑blocking work (<20 ms) inside an HTTP request         | Keep synchronous — no added complexity.                                          | Latency negligible; avoids context‑switch overhead. |
| I/O‑bound but may take up to 200 ms (e.g., outbound HTTP call) | Use **`async def`** + `await` inside FastAPI route.                              | Non‑blocking concurrency, simpler than queue.       |
| Anything that can block for >200 ms or involves heavy CPU        | Off‑load to **Celery task** (or equivalent) and return `202 Accepted`.           | Keeps request threads free, scales separately.      |
| High‑throughput event ingestion / multiple consumers             | Publish to **Pub/Sub / Kafka / NATS**; consumers process async.                  | Durable, decoupled fan‑out.                         |
| CPU‑bound batch computation                                      | Celery worker pool with `prefork` (multiprocessing) or dedicated Kubernetes Job. | Bypasses GIL, can autoscale.                        |  
### 10.2 **Celery** — Mandatory for Long‑Running Jobs  
1. **Broker:** Redis 7 for local/dev; RabbitMQ 3.13 or Google Pub/Sub in production.
2. **Result Backend:** Use Redis, PostgreSQL, or disable (fire‑and‑forget) if not needed.
3. **Idempotency:** Tasks **must** be idempotent — include unique replay keys.
4. **Retries:** Set `autoretry_for=(Exception,)`, `retry_backoff=True`, `max_retries=5` by default.
5. **Ack‑late:** Enable `acks_late=True` so tasks re‑queue on worker crash.
6. **Timeouts:** Guard CPU‑heavy tasks with `soft_time_limit` + `time_limit`.
7. **Instrumentation:** Emit task events to Prometheus via Celery‑Exporter or push to Grafana Tempo/Jaeger.  
> **Docker tip:** Add `compose.celery.yml` with `worker` + `beat` services; mount your `uv.lock` to keep env parity.  
### 10.3 Pub/Sub & Streaming  
| Tech               | When to Use                                         | Notes                                                     |
| ------------------ | --------------------------------------------------- | --------------------------------------------------------- |
| **Google Pub/Sub** | Cloud‑native fan‑out, 10k+ msg/s; auto‑scales.      | Use push subscriptions for near‑real‑time HTTP callbacks. |
| **Kafka**          | High‑volume ordered streams, log‑based audits.      | Run via Confluent Cloud or MSK to avoid ops.              |
| **NATS**           | Ultra‑light, <1 ms latency, request‑reply patterns. | Good for internal microservices in Kubernetes.            |  
Rules:  
* Use schematized payloads (Avro/Protobuf or JSON validated by Pydantic).
* Include trace headers (`traceparent`) for correlation.
* Consumer code belongs in `/app/subscribers/`.  
### 10.4 Async vs Thread vs Process  
| Workload                                               | Prefer                                                  | Because                            |
| ------------------------------------------------------ | ------------------------------------------------------- | ---------------------------------- |
| Many small I/O ops                                     | **`asyncio`** (FastAPI, httpx)                          | Minimal threads, high concurrency. |
| CPU‑bound (image resize, crypto)                       | **multiprocessing / Celery**                            | GIL‑free parallelism.              |
| Blocking library with no async port (e.g., legacy SDK) | **`ThreadPoolExecutor`** via `anyio.to_thread.run_sync` | Avoids blocking event loop.        |  
Guidelines:  
* Never call blocking code directly inside `async def`; wrap in `to_thread`.
* Keep thread pool size ≤ CPU cores ×2.
* Use `asyncpg`, `aioredis`, `aiohttp` for common async clients.  
### 10.5 Testing & CI  
* Use [`pytest-celery`](https://pypi.org/project/pytest-celery/) to spin up an ephemeral worker for integration tests.
* Mock Pub/Sub topics with \[`pubsub-emulator`], Kafka with `testcontainers`.
* Validate that every task returns within its declared time limit using `py‑test‑timeout`.  
> **Rule:** If you add a task queue or message topic, document it in `m2m/README.md` (purpose, schema, idempotency key) so agents and humans stay in sync.  
### 10.6 Celery Minimal Example  
```python
# tasks.py
from celery import Celery
app = Celery("worker", broker="redis://redis:6379/0", backend="redis://redis:6379/1")

@app.task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True)
def add(a: int, b: int) -> int:
return a + b
```  
Run `celery -A tasks worker -l info`.  
---