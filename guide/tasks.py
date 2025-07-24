from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple, Union
from enum import Enum
import os
import json
import textwrap
import jinja2


class WorkloadType(Enum):
    """Types of workloads that determine concurrency approach"""
    IO_BOUND = "I/O-Bound Operations (Network, Disk)"
    CPU_BOUND = "CPU-Bound Operations (Intensive Calculations)"
    BLOCKING_WITH_ASYNCIO = "Integrating Blocking Libraries with asyncio"


@dataclass
class ConcurrencyModel:
    """Represents a concurrency model for Python"""
    name: str
    workload_type: WorkloadType
    rationale: str
    key_libraries: List[str]
    example_code: str = ""


@dataclass
class TaskQueueConfig:
    """Configuration for Celery task queues"""
    broker: str
    backend: Optional[str] = None
    acks_late: bool = True
    autoretry_for: Tuple[str, ...] = ("Exception",)
    retry_backoff: bool = True
    max_retries: int = 5
    soft_time_limit: int = 60
    time_limit: int = 70
    serializer: str = "json"
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Return configuration as a dictionary for Celery app.conf.update()"""
        return {
            "broker_url": self.broker,
            "result_backend": self.backend if self.backend else None,
            "task_acks_late": self.acks_late,
            "task_serializer": self.serializer,
            "accept_content": [self.serializer],
            "result_serializer": self.serializer,
            "timezone": "UTC",
            "enable_utc": True,
        }


@dataclass
class MessagingSystem:
    """Represents a messaging or streaming system"""
    name: str
    url: str
    key_use_cases: List[str]
    notes: str
    python_libraries: List[str]
    is_cloud_native: bool = False


@dataclass
class TestingStrategy:
    """Strategy for testing asynchronous components"""
    component_type: str
    testing_tools: List[str]
    description: str
    example_code: Optional[str] = None


@dataclass
class AsyncComponentDoc:
    """Documentation requirements for async components"""
    component_name: str
    purpose: str
    schema: str
    idempotency_strategy: str
    producers: List[str]
    consumers: List[str]
    error_handling: str
    monitoring: str
    performance_expectations: Optional[str] = None


class BackgroundTasksAndConcurrency:
    """
    Background Tasks, Messaging & Concurrency
    
    A class representing best practices for handling operations outside 
    the main request-response cycle, including concurrency models,
    background tasks, and messaging systems.
    """
    
    def __init__(self):
        self.name = "Background Tasks, Messaging & Concurrency"
        
        # Initialize the foundational concurrency models
        self.concurrency_models = [
            ConcurrencyModel(
                name="asyncio",
                workload_type=WorkloadType.IO_BOUND,
                rationale="Efficiently handles many concurrent I/O operations with minimal thread overhead.",
                key_libraries=["FastAPI", "httpx", "asyncpg", "aioredis"],
                example_code="""
async def fetch_user_data(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        return response.json()
"""
            ),
            ConcurrencyModel(
                name="multiprocessing",
                workload_type=WorkloadType.CPU_BOUND,
                rationale="Bypasses the Global Interpreter Lock (GIL) for true parallelism across CPU cores.",
                key_libraries=["multiprocessing", "Celery with prefork pool", "Kubernetes Jobs"],
                example_code="""
from multiprocessing import Pool

def cpu_intensive_task(data):
    # Complex calculation
    result = perform_calculation(data)
    return result

def process_in_parallel(data_list):
    with Pool(processes=os.cpu_count()) as pool:
        results = pool.map(cpu_intensive_task, data_list)
    return results
"""
            ),
            ConcurrencyModel(
                name="ThreadPoolExecutor",
                workload_type=WorkloadType.BLOCKING_WITH_ASYNCIO,
                rationale="Prevents blocking the asyncio event loop when using synchronous, blocking libraries.",
                key_libraries=["anyio.to_thread.run_sync", "asyncio.to_thread"],
                example_code="""
import asyncio
from PIL import Image  # A blocking library

async def process_image(image_path: str):
    # Use asyncio.to_thread to run the blocking operation in a thread
    image = await asyncio.to_thread(Image.open, image_path)
    # More processing...
    return image
"""
            )
        ]
        
        # Celery best practices
        self.celery_best_practices = [
            "Tasks must be designed to be idempotent.",
            "Implement robust retry mechanisms with exponential backoff.",
            "Enable late acknowledgement (acks_late=True) so tasks are re-queued if a worker crashes.",
            "Guard against runaway tasks with soft_time_limit and time_limit.",
            "Emit task events for monitoring and observability.",
            "Use json serializer for broad compatibility."
        ]
        
        # Celery broker recommendations
        self.celery_brokers = {
            "development": ["Redis 7+"],
            "production": ["RabbitMQ 3.13+", "Google Cloud Pub/Sub", "Amazon SQS"]
        }
        
        # Task queue configuration examples
        self.task_queue_configs = {
            "development": TaskQueueConfig(
                broker="redis://localhost:6379/0",
                backend="redis://localhost:6379/1"
            ),
            "production": TaskQueueConfig(
                broker="amqp://user:password@rabbitmq:5672//",
                backend="redis://redis:6379/0",
                max_retries=10,
                soft_time_limit=120,
                time_limit=150
            ),
            "cloud": TaskQueueConfig(
                broker="pubsub://",
                backend=None,  # Results stored in database or disabled
                max_retries=15,
                soft_time_limit=300,
                time_limit=360
            )
        }
        
        # Messaging systems
        self.messaging_systems = [
            MessagingSystem(
                name="Google Cloud Pub/Sub",
                url="https://cloud.google.com/pubsub",
                key_use_cases=[
                    "Cloud-native, highly scalable (10k+ msg/s)",
                    "Global fan-out",
                    "At-least-once delivery"
                ],
                notes="Excellent for serverless functions, HTTP push subscriptions for near-real-time callbacks. Managed service reduces operational overhead.",
                python_libraries=["google-cloud-pubsub"],
                is_cloud_native=True
            ),
            MessagingSystem(
                name="Apache Kafka",
                url="https://kafka.apache.org/",
                key_use_cases=[
                    "High-volume ordered event streams",
                    "Log-based auditing",
                    "Stream processing",
                    "Event sourcing"
                ],
                notes="Powerful but complex to operate self-hosted. Prefer managed services like Confluent Cloud, Amazon MSK, or Aiven for Apache Kafka.",
                python_libraries=["confluent-kafka", "aiokafka"],
                is_cloud_native=False
            ),
            MessagingSystem(
                name="NATS.io",
                url="https://nats.io/",
                key_use_cases=[
                    "Ultra-lightweight",
                    "Very low latency (<1 ms)",
                    "Request-reply patterns",
                    "Simple pub/sub"
                ],
                notes="Good for internal microservice communication within Kubernetes. Supports various messaging patterns including JetStream for persistence.",
                python_libraries=["nats-py"],
                is_cloud_native=False
            ),
            MessagingSystem(
                name="RabbitMQ",
                url="https://www.rabbitmq.com/",
                key_use_cases=[
                    "Flexible routing",
                    "Multiple protocol support (AMQP, MQTT, STOMP)",
                    "Mature ecosystem"
                ],
                notes="Can be used as a Celery broker or a general-purpose message bus. Requires careful operational management if self-hosted.",
                python_libraries=["pika", "aio-pika"],
                is_cloud_native=False
            )
        ]
        
        # Testing strategies
        self.testing_strategies = [
            TestingStrategy(
                component_type="Celery",
                testing_tools=["pytest-celery"],
                description="Manages an embedded Celery worker during integration tests",
                example_code="""
# Example pytest fixture for Celery testing
@pytest.fixture
def celery_app():
    app = Celery("test_app")
    app.conf.update(
        broker_url="memory://",
        result_backend="cache+memory://",
        task_always_eager=True,  # Tasks execute synchronously for testing
        task_eager_propagates=True  # Exceptions are propagated
    )
    return app

def test_celery_task(celery_app):
    # Register the task with the test app
    @celery_app.task
    def add(x, y):
        return x + y
    
    # Execute the task
    result = add.delay(4, 4)
    assert result.get() == 8
"""
            ),
            TestingStrategy(
                component_type="Google Pub/Sub",
                testing_tools=["google-cloud-pubsub-emulator"],
                description="Uses the official Google Pub/Sub emulator for local testing",
                example_code="""
# Start the emulator before tests:
# $ gcloud beta emulators pubsub start --project=test-project

# In your test code:
import os
os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"

from google.cloud import pubsub_v1

def test_pubsub_subscription():
    # Create client with emulator
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    
    # Create topic and subscription for testing
    topic_path = publisher.topic_path("test-project", "test-topic")
    sub_path = subscriber.subscription_path("test-project", "test-sub")
    
    # Test publishing and receiving
    # ...
"""
            ),
            TestingStrategy(
                component_type="Kafka",
                testing_tools=["testcontainers-python"],
                description="Spins up a Kafka container for testing",
                example_code="""
from testcontainers.kafka import KafkaContainer
import pytest

@pytest.fixture(scope="session")
def kafka_container():
    with KafkaContainer() as kafka:
        yield kafka

def test_kafka_producer(kafka_container):
    from confluent_kafka import Producer
    
    # Configure producer with container address
    bootstrap_servers = kafka_container.get_bootstrap_server()
    producer = Producer({"bootstrap.servers": bootstrap_servers})
    
    # Test producing messages
    # ...
"""
            )
        ]
        
        # Documentation template
        self.doc_template = {
            "component_name": "",
            "purpose": "",
            "schema": "",
            "idempotency_strategy": "",
            "producers": [],
            "consumers": [],
            "error_handling": "",
            "monitoring": "",
            "performance_expectations": ""
        }
        
        # General guidelines
        self.general_guidelines = [
            "Avoid blocking in async def: Never call blocking I/O operations directly within an async function.",
            "Thread Pool Sizing: For ThreadPoolExecutor, keep the pool size to CPU_CORES * 2 or CPU_CORES + 4.",
            "FastAPI Routes: For quick work (<20ms), keep it synchronous. For I/O-bound work up to ~200ms, use async def.",
            "For operations taking >200ms, use Celery or other background task systems."
        ]
        
        # Messaging practices
        self.messaging_practices = [
            "Schematized Payloads: Use well-defined schemas (Avro, Protocol Buffers) or JSON with Pydantic models.",
            "Traceability: Include distributed tracing headers in messages for correlation.",
            "Consumer Logic Location: Organize consumer code in /app/subscribers/ or /app/consumers/ directories.",
            "Dead-Letter Queues: Configure DLQs to handle messages that fail after multiple retries."
        ]
    
    def get_concurrency_model(self, workload_type: WorkloadType) -> ConcurrencyModel:
        """Return the recommended concurrency model for a specific workload type"""
        for model in self.concurrency_models:
            if model.workload_type == workload_type:
                return model
        raise ValueError(f"No concurrency model found for workload type: {workload_type}")
    
    def get_celery_task_decorator(self, task_type: str = "default") -> str:
        """
        Generate a Celery task decorator with recommended settings
        based on the task type.
        """
        if task_type == "cpu_bound":
            return "@app.task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3, soft_time_limit=120, time_limit=150)"
        elif task_type == "io_bound":
            return "@app.task(acks_late=True, autoretry_for=(IOError,), retry_backoff=True, retry_jitter=True, max_retries=5)"
        else:  # default
            return "@app.task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3, soft_time_limit=60, time_limit=70)"
    
    def get_celery_example(self) -> str:
        """Return the Celery minimal example code"""
        return """
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
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ensure Celery accepts JSON
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

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
"""
    
    def get_docker_compose_celery(self) -> str:
        """Return a Docker Compose example for Celery"""
        return """
# compose.celery.yml
version: '3.8'

services:
  worker:
    build: .
    command: celery -A project.tasks worker -l INFO
    volumes:
      - .:/app
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://user:password@db:5432/app
    depends_on:
      - redis
      - db
  
  beat:
    build: .
    command: celery -A project.tasks beat -l INFO
    volumes:
      - .:/app
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - worker
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
  
  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  redis-data:
  postgres-data:
"""
    
    def generate_docker_compose(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Generate a Docker Compose file from a Jinja2 template with the provided context.
        
        Args:
            template_name: The name of the template to use
            context: Dictionary of values to render in the template
            
        Returns:
            The rendered Docker Compose YAML as a string
        """
        templates = {
            "celery": """
# {{ filename }}
version: '{{ version }}'

services:
  worker:
    build: {% if build_context %}{{ build_context }}{% else %}.{% endif %}
    {% if worker_image %}image: {{ worker_image }}
    {% endif %}command: celery -A {{ celery_app }} worker -l {{ log_level }}
    volumes:
      - .:/app
    environment:
      - REDIS_URL={{ redis_url }}
      {% if database_url %}- DATABASE_URL={{ database_url }}{% endif %}
    depends_on:
      - redis
      {% if use_database %}- db{% endif %}
  
  {% if include_beat %}
  beat:
    {% if worker_image %}image: {{ worker_image }}
    {% else %}build: {% if build_context %}{{ build_context }}{% else %}.{% endif %}{% endif %}
    command: celery -A {{ celery_app }} beat -l {{ log_level }}
    volumes:
      - .:/app
    environment:
      - REDIS_URL={{ redis_url }}
    depends_on:
      - redis
      - worker
  {% endif %}
  
  redis:
    image: {{ redis_image }}
    ports:
      - "{{ redis_port }}:6379"
    volumes:
      - redis-data:/data
  
  {% if use_database %}
  db:
    image: {{ db_image }}
    environment:
      - POSTGRES_USER={{ db_user }}
      - POSTGRES_PASSWORD={{ db_password }}
      - POSTGRES_DB={{ db_name }}
    volumes:
      - postgres-data:/var/lib/postgresql/data
  {% endif %}

volumes:
  redis-data:
  {% if use_database %}postgres-data:{% endif %}
""",
            "kafka": """
# {{ filename }}
version: '{{ version }}'

services:
  zookeeper:
    image: {{ zookeeper_image }}
    ports:
      - "{{ zookeeper_port }}:2181"
    environment:
      - ZOOKEEPER_CLIENT_PORT=2181
      - ZOOKEEPER_TICK_TIME=2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-log:/var/lib/zookeeper/log

  kafka:
    image: {{ kafka_image }}
    ports:
      - "{{ kafka_port }}:9092"
    environment:
      - KAFKA_BROKER_ID=1
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
      - KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1
    volumes:
      - kafka-data:/var/lib/kafka/data
    depends_on:
      - zookeeper
      
  {% if include_schema_registry %}
  schema-registry:
    image: {{ schema_registry_image }}
    ports:
      - "{{ schema_registry_port }}:8081"
    environment:
      - SCHEMA_REGISTRY_HOST_NAME=schema-registry
      - SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - kafka
  {% endif %}
  
  {% if include_kafka_ui %}
  kafka-ui:
    image: {{ kafka_ui_image }}
    ports:
      - "{{ kafka_ui_port }}:8080"
    environment:
      - KAFKA_CLUSTERS_0_NAME={{ cluster_name }}
      - KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=kafka:9092
      {% if include_schema_registry %}- KAFKA_CLUSTERS_0_SCHEMAREGISTRY=http://schema-registry:8081{% endif %}
    depends_on:
      - kafka
      {% if include_schema_registry %}- schema-registry{% endif %}
  {% endif %}

volumes:
  zookeeper-data:
  zookeeper-log:
  kafka-data:
""",
            "rabbitmq": """
# {{ filename }}
version: '{{ version }}'

services:
  rabbitmq:
    image: {{ rabbitmq_image }}
    ports:
      - "{{ rabbitmq_port }}:5672"
      {% if management_enabled %}- "{{ management_port }}:15672"{% endif %}
    environment:
      - RABBITMQ_DEFAULT_USER={{ rabbitmq_user }}
      - RABBITMQ_DEFAULT_PASS={{ rabbitmq_password }}
      {% if management_enabled %}- RABBITMQ_MANAGEMENT_ENABLE=true{% endif %}
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
      
volumes:
  rabbitmq-data:
"""
        }
        
        # Set default values if not provided in the context
        defaults = {
            "version": "3.8",
            "filename": f"docker-compose-{template_name}.yml",
            "log_level": "INFO",
        }
        
        # Add template-specific defaults
        if template_name == "celery":
            defaults.update({
                "redis_image": "redis:7-alpine",
                "redis_port": "6379", 
                "redis_url": "redis://redis:6379/0",
                "celery_app": "project.tasks",
                "use_database": True,
                "db_image": "postgres:14-alpine",
                "db_user": "user",
                "db_password": "password",
                "db_name": "app",
                "include_beat": True,
            })
        elif template_name == "kafka":
            defaults.update({
                "zookeeper_image": "confluentinc/cp-zookeeper:7.3.0",
                "kafka_image": "confluentinc/cp-kafka:7.3.0",
                "zookeeper_port": "2181",
                "kafka_port": "9092",
                "include_schema_registry": False,
                "schema_registry_image": "confluentinc/cp-schema-registry:7.3.0",
                "schema_registry_port": "8081",
                "include_kafka_ui": False,
                "kafka_ui_image": "provectuslabs/kafka-ui:latest",
                "kafka_ui_port": "8080",
                "cluster_name": "local-kafka",
            })
        elif template_name == "rabbitmq":
            defaults.update({
                "rabbitmq_image": "rabbitmq:3.13-management",
                "rabbitmq_port": "5672",
                "management_enabled": True,
                "management_port": "15672",
                "rabbitmq_user": "guest",
                "rabbitmq_password": "guest",
            })
        
        # Merge the provided context with defaults
        for key, value in defaults.items():
            if key not in context:
                context[key] = value
                
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' not found. Available templates: {', '.join(templates.keys())}")
        
        # Render the template
        template = jinja2.Template(templates[template_name])
        return template.render(**context)
    
    def create_async_component_doc(self, **kwargs) -> AsyncComponentDoc:
        """
        Create documentation for an asynchronous component following
        the required format.
        """
        # Validate that all required fields are present
        required_fields = ["component_name", "purpose", "schema", "idempotency_strategy", 
                           "producers", "consumers", "error_handling", "monitoring"]
        
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(f"Missing required field: {field}")
        
        return AsyncComponentDoc(**kwargs)
    
    def get_async_component_doc_template(self) -> str:
        """Return a Markdown template for documenting async components"""
        return """
# Asynchronous Component Documentation

## {component_name}

**Purpose:** {purpose}

**Message/Task Schema:**
```json
{schema}
```

**Idempotency Strategy:**
{idempotency_strategy}

**Producers:**
{producers}

**Consumers:**
{consumers}

**Error Handling & Retry Policy:**
{error_handling}

**Monitoring & Alerting:**
{monitoring}

{performance_section}
"""
    
    def render_async_component_doc(self, doc: AsyncComponentDoc) -> str:
        """Render documentation for an async component as Markdown"""
        # Format producers and consumers as bullet points
        producers_md = "\n".join([f"- {producer}" for producer in doc.producers])
        consumers_md = "\n".join([f"- {consumer}" for consumer in doc.consumers])
        
        # Add performance section if available
        performance_section = ""
        if doc.performance_expectations:
            performance_section = f"**Performance Expectations:**\n{doc.performance_expectations}"
        
        template = self.get_async_component_doc_template()
        return template.format(
            component_name=doc.component_name,
            purpose=doc.purpose,
            schema=doc.schema,
            idempotency_strategy=doc.idempotency_strategy,
            producers=producers_md,
            consumers=consumers_md,
            error_handling=doc.error_handling,
            monitoring=doc.monitoring,
            performance_section=performance_section
        )
    
    def get_recommended_messaging_system(self, use_case: str) -> List[MessagingSystem]:
        """Find messaging systems suitable for a specific use case"""
        recommendations = []
        for system in self.messaging_systems:
            if any(use_case.lower() in case.lower() for case in system.key_use_cases):
                recommendations.append(system)
        
        return recommendations if recommendations else self.messaging_systems
    
    def __str__(self) -> str:
        """String representation of background tasks and concurrency guidelines"""
        return f"{self.name}: Strategies for managing concurrency, background tasks, and messaging systems"


# Example usage
if __name__ == "__main__":
    bg_tasks = BackgroundTasksAndConcurrency()
    
    print(f"🔄 {bg_tasks}")
    
    print("\n⚡ Concurrency Models:")
    for model in bg_tasks.concurrency_models:
        print(f"- {model.name}: For {model.workload_type.value}")
        print(f"  Rationale: {model.rationale}")
        print(f"  Key Libraries: {', '.join(model.key_libraries)}")
    
    print("\n🧵 General Concurrency Guidelines:")
    for i, guideline in enumerate(bg_tasks.general_guidelines, 1):
        print(f"{i}. {guideline}")
    
    print("\n🎯 Celery Best Practices:")
    for i, practice in enumerate(bg_tasks.celery_best_practices, 1):
        print(f"{i}. {practice}")
    
    print("\n📨 Messaging Systems:")
    for system in bg_tasks.messaging_systems:
        print(f"- {system.name}")
        print(f"  URL: {system.url}")
        print(f"  Use Cases: {', '.join(system.key_use_cases)}")
    
    print("\n🧪 Testing Strategies:")
    for strategy in bg_tasks.testing_strategies:
        print(f"- Testing {strategy.component_type} with {', '.join(strategy.testing_tools)}")
        print(f"  {strategy.description}")
    
    print("\n📝 Documentation Requirements:")
    doc_example = bg_tasks.create_async_component_doc(
        component_name="order_processing_queue",
        purpose="Process new customer orders asynchronously to ensure fast API responses",
        schema='{"order_id": "string", "items": [{"product_id": "string", "quantity": "integer"}], "customer_id": "string", "timestamp": "string"}',
        idempotency_strategy="Orders are processed exactly once using the order_id as a unique key in the database",
        producers=["API Order Service", "Batch Import Service"],
        consumers=["Order Processing Worker"],
        error_handling="Automatic retry with exponential backoff, max 5 retries. Failed orders moved to dead-letter queue and flagged for manual intervention.",
        monitoring="Queue depth, processing time, and error rate are monitored via Prometheus and Grafana dashboards",
        performance_expectations="Expected to handle up to 1000 orders per minute with processing time < 2 seconds per order"
    )
    
    print(bg_tasks.render_async_component_doc(doc_example))
