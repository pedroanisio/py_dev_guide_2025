## 11. Background Tasks, Messaging & Concurrency

Modern applications often require handling operations outside the main request-response cycle. This section covers strategies for managing concurrency, offloading work to background tasks, and using messaging systems for robust, scalable event-driven architectures.

### 11.1 Foundational Concurrency Models in Python

Understanding Python's concurrency approaches is key to choosing the right execution model.

| Workload Type                                     | Preferred Model                                                                 | Rationale & Key Libraries                                                                                                |
| :------------------------------------------------ | :------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------- |
| **I/O-Bound Operations (Network, Disk)**          | **`asyncio`** (Asynchronous I/O)                                                | Efficiently handles many concurrent I/O operations with minimal thread overhead. Core of [FastAPI](https://fastapi.tiangolo.com/), uses libraries like [`httpx`](https://www.python-httpx.org/), [`asyncpg`](https://magicstack.github.io/asyncpg/current/), [`aioredis`](https://aioredis.readthedocs.io/en/latest/). |
| **CPU-Bound Operations (Intensive Calculations)** | **`multiprocessing`** or offload to Celery with `prefork` worker pool.          | Bypasses the Global Interpreter Lock (GIL) for true parallelism across CPU cores. For complex jobs, dedicated [Kubernetes Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/) are also an option. |
| **Integrating Blocking Libraries with `asyncio`**   | **`ThreadPoolExecutor`** via [`anyio.to_thread.run_sync`](https://anyio.readthedocs.io/en/stable/threads.html) or `asyncio.to_thread` (Python 3.9+). | Prevents blocking the `asyncio` event loop when using synchronous, blocking libraries.                                     |

**General Guidelines:**

*   **Avoid Blocking in `async def`:** Never call blocking I/O operations directly within an `async` function. Always use `await` with async libraries or offload blocking calls using `anyio.to_thread.run_sync` or `asyncio.to_thread`.
*   **Thread Pool Sizing:** For `ThreadPoolExecutor`, keep the pool size reasonable, typically not exceeding `CPU_CORES * 2` (or `CPU_CORES + 4`) to avoid excessive context switching.
*   **FastAPI Routes:**
    *   For quick, non-blocking work (<20ms): Keep it synchronous within the route for simplicity.
    *   For I/O-bound work that might take up to ~200ms (e.g., a single external HTTP call): Use `async def` for the route and `await` the I/O operation.

### 11.2 Task Queues with Celery

[Celery](https://docs.celeryq.dev/en/stable/) is the **mandatory tool** for offloading tasks that can block for >200ms, involve heavy CPU work, or need to be processed independently of the request lifecycle.

**When to Use Celery:**

*   Long-running background jobs (e.g., report generation, data processing).
*   CPU-intensive computations.
*   Operations requiring retries or scheduled execution.
*   Decoupling resource-intensive work to keep API response times low (return `202 Accepted` and process asynchronously).

#### 11.2.1 Celery Configuration & Best Practices

1.  **Broker Selection:**
    *   Local/Development: [Redis](https://redis.io/) 7+ is suitable.
    *   Production: [RabbitMQ](https://www.rabbitmq.com/) 3.13+ or cloud-native services like [Google Cloud Pub/Sub](https://cloud.google.com/pubsub) (via Celery's experimental GCP Pub/Sub broker) or [Amazon SQS](https://aws.amazon.com/sqs/) are recommended for reliability and scalability.
2.  **Result Backend:** Use Redis, [PostgreSQL](https://www.postgresql.org/), or disable results entirely (fire-and-forget) if task outcomes are not needed by the caller.
3.  **Idempotency:** Tasks **must** be designed to be idempotent. Include unique keys or identifiers in task arguments to prevent duplicate processing if a task is replayed.
4.  **Retries:** Implement robust retry mechanisms. By default, configure:
    *   `autoretry_for=(Exception,)` (or specific transient exceptions)
    *   `retry_backoff=True` (for exponential backoff)
    *   `max_retries=5` (or a suitable number for your use case)
5.  **Late Acknowledgement (`acks_late=True`):** Enable this critical setting so tasks are only acknowledged *after* successful completion. This ensures tasks re-queue if a worker crashes during execution.
6.  **Timeouts:** Guard against runaway tasks, especially CPU-heavy ones:
    *   `soft_time_limit`: Raises an exception when exceeded, allowing the task to clean up.
    *   `time_limit` (hard limit): Terminates the task (SIGKILL) if the soft limit is ignored.
7.  **Instrumentation & Monitoring:** Emit task events (success, failure, retry) to [Prometheus](https://prometheus.io/) (e.g., using [celery-exporter](https://github.com/oval كيναծoval/celery-exporter)) or integrate with distributed tracing systems like [Grafana Tempo](https://grafana.com/oss/tempo/) or [Jaeger](https://www.jaegertracing.io/).
8.  **Serialization:** Use `json` as the default serializer for broad compatibility. Consider `pickle` only if complex Python objects must be passed and security implications are understood.

#### 11.2.2 Celery Minimal Example

```python
# project/tasks.py
from celery import Celery
import time

# Configuration should ideally come from a central config module or environment variables
app = Celery(
    "my_app_tasks",
    broker="redis://localhost:6379/0", # Example: Connect to local Redis
    backend="redis://localhost:6379/1"
)

# Optional: Configure Celery app further (e.g., task routes, serializers)
# app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],  # Ensure Celery accepts JSON
#     result_serializer='json',
#     timezone='UTC',
#     enable_utc=True,
# )

@app.task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3, soft_time_limit=60, time_limit=70)
def add(x: int, y: int) -> int:
    # Simulate some work
    time.sleep(2)
    result = x + y
    # logger.info(f"Task add({x}, {y}) completed with result: {result}") # Use proper logging
    return result

@app.task(bind=True, acks_late=True, autoretry_for=(IOError,), retry_backoff=True, retry_jitter=True, max_retries=5)
def process_file(self, filepath: str):
    try:
        # Simulate file processing
        # logger.info(f"Processing file: {filepath}")
        if "fail" in filepath:
            raise IOError("Simulated file access error")
        time.sleep(5)
        # logger.info(f"File {filepath} processed successfully.")
        return f"Successfully processed {filepath}"
    except Exception as exc:
        # logger.error(f"Task process_file failed for {filepath}. Retrying ({self.request.retries}/{self.max_retries})...", exc_info=True)
        raise self.retry(exc=exc)

# To run a worker:
# celery -A project.tasks worker -l INFO -P gevent # Example using gevent for I/O-bound tasks
# celery -A project.tasks worker -l INFO -P prefork -c 4 # Example for CPU-bound tasks with 4 processes

# To run Celery Beat (for scheduled tasks):
# celery -A project.tasks beat -l INFO
```

#### 11.2.3 Docker Compose for Celery

> **Tip:** Create a `compose.celery.yml` (or similar) to define `worker` and `beat` (if using scheduled tasks) services. Ensure environment consistency by mounting your `uv.lock` file or using the same base Docker image and dependency installation process as your application service.

### 11.3 Messaging & Streaming Systems

For high-throughput event ingestion, durable messaging, or scenarios requiring multiple asynchronous consumers for the same event (fan-out), use dedicated messaging/streaming platforms.

**When to Use:**

*   Decoupling services for improved resilience and independent scaling.
*   Broadcasting events to multiple interested consumers.
*   Buffering high volumes of incoming data.
*   Implementing event-driven architectural patterns.

| Technology                                      | Key Use Cases                                                                    | Notes & Recommendations                                                                                                                            |
| :---------------------------------------------- | :------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[Google Cloud Pub/Sub](https://cloud.google.com/pubsub)** | Cloud-native, highly scalable (10k+ msg/s), global fan-out, at-least-once delivery. | Excellent for serverless functions, HTTP push subscriptions for near-real-time callbacks. Managed service reduces operational overhead.                |
| **[Apache Kafka](https://kafka.apache.org/)**             | High-volume ordered event streams, log-based auditing, stream processing, event sourcing. | Powerful but complex to operate self-hosted. Prefer managed services like [Confluent Cloud](https://www.confluent.io/confluent-cloud/), [Amazon MSK](https://aws.amazon.com/msk/), or [Aiven for Apache Kafka](https://aiven.io/kafka). |
| **[NATS.io](https://nats.io/)**                             | Ultra-lightweight, very low latency (<1 ms), request-reply patterns, simple pub/sub.   | Good for internal microservice communication within Kubernetes. Supports various messaging patterns including JetStream for persistence.           |
| **[RabbitMQ](https://www.rabbitmq.com/)** (as a message bus)  | Flexible routing, multiple protocol support (AMQP, MQTT, STOMP), mature ecosystem. | Can be used as a Celery broker or a general-purpose message bus. Requires careful operational management if self-hosted.                             |

**Common Rules & Practices for Messaging:**

*   **Schematized Payloads:** Use well-defined schemas for messages (e.g., [Apache Avro](https://avro.apache.org/), [Protocol Buffers](https://protobuf.dev/)) or JSON payloads validated by [Pydantic](https://docs.pydantic.dev/latest/) models to ensure data integrity and consumer compatibility.
*   **Traceability:** Include distributed tracing headers (e.g., W3C `traceparent`) in messages to enable correlation and end-to-end visibility across services.
*   **Consumer Logic Location:** Organize consumer/subscriber code logically, for example, within an `/app/subscribers/` or `/app/consumers/` directory.
*   **Dead-Letter Queues (DLQs):** Configure DLQs to handle messages that cannot be processed successfully after multiple retries, allowing for later inspection and manual intervention.

### 11.4 Testing Asynchronous Systems

Testing background tasks and message-driven components requires specific strategies:

*   **Celery Testing:** Use [`pytest-celery`](https://pypi.org/project/pytest-celery/) to manage an embedded Celery worker during integration tests. This allows you to test task execution, retries, and results.
*   **Message Queue/Topic Emulation:**
    *   Google Pub/Sub: Use the official [`google-cloud-pubsub-emulator`](https://cloud.google.com/pubsub/docs/emulator).
    *   Kafka: Use [`testcontainers-python`](https://testcontainers-python.readthedocs.io/en/latest/modules/kafka.html) to spin up a Kafka container.
    *   NATS: Can often be tested against a lightweight local NATS server.
*   **Timeout Validation:** Use tools like [`pytest-timeout`](https://pypi.org/project/pytest-timeout/) to ensure tasks complete within their declared `soft_time_limit` or `time_limit`.
*   **Mocking External Services:** Thoroughly mock external dependencies (APIs, databases) called by tasks or consumers to ensure isolated and deterministic tests.

### 11.5 Documentation Requirements for Asynchronous Components

Maintaining clear documentation for background tasks, queues, and message topics is crucial for system understanding, maintainability, and collaboration (including with AI agents).

**Rule:** Any new task queue (e.g., Celery queue), significant Celery task, message topic (e.g., Kafka, Pub/Sub), or event stream **must** be documented. The preferred location is within `m2m/README.md` under a dedicated "Asynchronous Components" section, or alternatively, in a specific design document referenced from `m2m/README.md`.

This documentation **must** include the following details:

*   **Component Name:** The canonical name of the queue, topic, or primary task.
*   **Purpose:** Clearly state the business or technical reason for this component's existence. What problem does it solve?
*   **Message/Task Schema:** Define the structure of the data being passed. Provide a direct link to the relevant Pydantic model, Avro/Protobuf schema definition file, or a clear description of the JSON structure.
*   **Idempotency Strategy:** Explicitly describe how idempotency is achieved for consumers or tasks (e.g., unique message IDs, database constraints, specific logic). If not idempotent, explain why.
*   **Producers:** List the services or code components that publish messages or enqueue tasks to this component.
*   **Consumers:** List the services or specific task functions/subscriber modules that process messages or tasks from this component.
*   **Error Handling & Retry Policy:** Detail how processing errors are handled. Specify the retry mechanism (e.g., Celery `autoretry_for`, backoff strategy, max retries) and what happens after maximum retries (e.g., move to Dead-Letter Queue, log and discard).
*   **Monitoring & Alerting:** Briefly mention key metrics monitored for this component (e.g., queue depth, processing latency, error rate) and any specific alerts configured.
*   **(Optional) Performance Expectations:** Note any expected throughput, latency targets, or processing time constraints if applicable.

Keeping this information accurate and accessible ensures that all stakeholders (developers, SREs, AI agents) have a shared understanding of the system's asynchronous workflows and operational characteristics.

---