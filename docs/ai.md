## 12. AI & Data‑Science Practices  
### 12.1 Model Serving & Local LLMs  
| Tool                                        | Use Case                                                                                          | Notes                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Ollama**                                  | Quickly spin up local LLMs (Mistral, Llama 3) for prototypes, private inference, or edge devices. | Mount `~/.ollama` as a volume in Docker; bind GPU with `--gpus all` if available. |
| **vLLM**                                    | High‑throughput, GPU‑optimized serving for production.                                            | Pair with Triton or FastAPI adapter; use CUDA 12 base image.                      |
| **HuggingFace `text-generation-inference`** | Multi‑GPU distributed serving of bigger models.                                                   | Requires Nvidia A100/H100; run behind Traefik.                                    |
| **OpenAI-compatible API Servers**            | Drop-in replacement for OpenAI with local models                                                 | Use LiteLLM, vLLM with OpenAI-compatible mode, or FastAPI with pydantic validation    |
| **Ray Serve**                               | Scalable multi-model deployments with resource management                                        | Use for complex pipelines with multiple models working together                    |

Guidelines:  
* **Tag images by model + version** (`ollama/llama3:70b‑q4_1`).
* Store model configs (`model‑config.yaml`) in `m2m/` and load via entrypoint.
* For CPU‑only nodes, pick quantized variants (`q4_K_M`) or distilled models (TinyLlama).
* Use OpenAI-compatible API servers to enable easy switching between local and cloud models.
* Implement graceful fallbacks for expensive models with timeouts.

**Example Containerized LLM Serving:**
```dockerfile
FROM ollama/ollama:0.1.27

# Copy model configuration
COPY ./m2m/llama3-config.yaml /etc/ollama/models/

# Set up health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:11434/api/health || exit 1

# Expose API port
EXPOSE 11434

# Run with 4 workers and model preloading
ENTRYPOINT ["ollama", "serve", "--workers=4", "--preload=llama3:70b-q4"]
```

### 12.2 NLP Stack (Python)  
| Layer        | Preferred Lib                                      | Alternatives                              | Example                                                                 |
| ------------ | -------------------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------------- |
| Tokenization | `tokenizers` (HF)                                  | `spaCy` tokenizers                        | `from tokenizers import Tokenizer; t = Tokenizer.from_pretrained("gpt2")` |
| Core NLP     | **spaCy v3** for POS/NER; `en_core_web_trf` model. | NLTK for teaching / quick regex grammars. | `import spacy; nlp = spacy.load("en_core_web_trf")`                        |
| Embeddings   | `sentence-transformers`                            | `transformers` + manual mean‑pooling      | `from sentence_transformers import SentenceTransformer; model = SentenceTransformer("all-MiniLM-L6-v2")` |
| Vector DB    | **Qdrant** (prod), **Chroma** (dev)                | pgvector extension                        | `from qdrant_client import QdrantClient; client = QdrantClient("localhost", port=6333)` |
| RAG Framework| **LlamaIndex** or **LangChain**                     | Custom implementation                        | `from llama_index import VectorStoreIndex, SimpleDirectoryReader`            |
| Eval & Bench | `langchain‑bench`, `lm‑eval‑harness`, `RAGAS`       | custom pytest harness                     | `from lm_eval import tasks, evaluator; results = evaluator.evaluate(model, tasks=["hellaswag"])` |

> **Rule:** New NLP pipelines must expose a **pure‑function endpoint** (`/v1/ner`), accept JSON, and return Pydantic models for entities.  

**Standard Vector Pipeline:**
```python
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from pydantic import BaseModel, Field
from typing import List

class Document(BaseModel):
    id: str
    text: str
    metadata: dict = Field(default_factory=dict)

class VectorService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.client = QdrantClient("localhost", port=6333)
        
    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()
        
    def index(self, docs: List[Document], collection: str):
        embeddings = self.embed([doc.text for doc in docs])
        self.client.upsert(
            collection_name=collection,
            points=[
                {"id": doc.id, "vector": emb, "payload": {"text": doc.text, **doc.metadata}}
                for doc, emb in zip(docs, embeddings)
            ]
        )
        
    def search(self, query: str, collection: str, limit: int = 5) -> List[Document]:
        vector = self.embed([query])[0]
        results = self.client.search(collection, vector, limit=limit)
        return [Document(id=hit.id, text=hit.payload["text"], 
                        metadata={k:v for k,v in hit.payload.items() if k != "text"}) 
                for hit in results]
```

### 12.3 GPU vs CPU Guidelines  
| Case                        | Hardware                | Settings                                                           | Optimization                                                                 |
| --------------------------- | ----------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| Training small (<1B) models | Consumer GPU (RTX 4090) | `torch.set_float32_matmul_precision("high")`, `bf16` if supported. | DeepSpeed ZeRO Stage 2, gradient accumulation                              |
| Serving quantized 7B LLM    | Single GPU (24–48 GB)   | vLLM + Flash‑Attention 2; `--gpu-memory-utilization 0.85`.         | Continuous batching, KV cache management                                     |
| Batch inference embeddings  | CPU cluster             | `sentence-transformers` with `torch.set_num_threads($CPU)`.        | Thread pinning, vectorized operations (SIMD)                                      |
| Vector search >100M vectors | Server with AVX‑512     | Qdrant `hnsw_16` + disk cache.                                     | HNSW index with filter optimization                                               |
| Multimodal models (vision+text)| Mixed GPU (A10/A100) | Use model sharding and pipeline parallelism                            | Efficient prefetching, mixed precision                                           |

**Performance Monitoring Tools:**
- **PyTorch Profiler** - For detailed operation timing and memory tracking
- **NVIDIA NSight** - For GPU kernel analysis
- **Prometheus + Grafana** - For production monitoring of latency/throughput

**Example GPU Resource Allocation in Kubernetes:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: llm-inference
spec:
  containers:
  - name: llm-service
    image: your-registry/vllm-service:latest
    resources:
      limits:
        nvidia.com/gpu: 1
        memory: 64Gi
      requests:
        nvidia.com/gpu: 1
        memory: 48Gi
    env:
    - name: PYTORCH_CUDA_ALLOC_CONF
      value: "max_split_size_mb:128"
    - name: VLLM_GPU_MEMORY_UTILIZATION
      value: "0.85"
```

### 12.4 Data Pipelines  
| Stage          | Tooling                        | Comment                                                         | Example                                                                 |
| -------------- | ------------------------------ | --------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Orchestration  | **Apache Airflow 2.9**         | DAGs stored in `pipelines/` folder; deploy via Docker Operator. | `from airflow import DAG; from airflow.operators.python import PythonOperator` |
| Pythonic flows | **Prefect 2**                  | Great for local dev; run agent in K8s.                          | `from prefect import flow, task; @flow(name="etl")`                        |
| Streaming ETL  | **Apache Beam** on Dataflow    | Use for terabyte‑scale transforms.                              | `import apache_beam as beam; with beam.Pipeline() as p:`                     |
| Feature Store  | **Feast** with Postgres/Qdrant | Keep feature definitions versioned.                             | `from feast import FeatureStore; store = FeatureStore(repo_path=".")`         |
| Data Validation| **Great Expectations**         | Validate data schemas and quality                                | `import great_expectations as ge; context = ge.get_context()`                 |
| Data Version Control| **DVC**                        | Track data alongside code                                        | `dvc add data/training_set.csv`                                             |

**Guidelines:**
* DAG code must pass `ruff` and unit tests (`pytest pipelines/tests`).
* Schedule stored in `pipelines/schedules.yaml`, validated at CI time.
* All pipelines should have monitoring, alerting, and failure handling.
* Implement idempotent pipelines that can safely re-run from any step.

**Example Data Pipeline with Error Handling:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external import ExternalTaskSensor
from datetime import datetime, timedelta
import great_expectations as ge
import pandas as pd

default_args = {
    'owner': 'data-science',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'train_embeddings_pipeline',
    default_args=default_args,
    description='Pipeline to process data and train embeddings',
    schedule_interval='0 2 * * *',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['ml', 'embeddings'],
)

def extract_data(**kwargs):
    # Extraction logic
    df = pd.read_csv('s3://bucket/data.csv')
    # Validation with Great Expectations
    context = ge.get_context()
    validator = context.get_validator(
        batch_request=context.build_batch_request(df, "my_datasource"),
        expectation_suite_name="data.basic.expectations"
    )
    validation_result = validator.validate()
    if not validation_result.success:
        raise ValueError("Data validation failed")
    return df.to_dict()

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

# Define additional tasks for transform, load, train, etc.
```

### 12.5 Experiment Tracking & Reproducibility  
| Aspect | Tool | Mandatory Config | Integration |
| ------------------------------------------------------ | | 💾 Artifacts |
**MLflow** | Track params + metrics; log models as `mlflow.pyfunc`. | | 📊
Dashboards | **Weights & Biases** | Link run URL in PR description. | | 🧪 Data
Versioning | **DVC** | Store datasets in S3 bucket; lockfile in Git. | | 📝 Model Cards
| 🔍 A/B Testing | **Statsig** or **GrowthBook** | Feature flags with automatic statistical analysis | |

> **Rule:** All experiments must have a unique run ID, parameter snapshot, and random seed. Without these, results are non‑reviewable.  
Integrate MLflow client in FastAPI `/experiments` router for quick lookup.  

**Standard Experiment Tracking Pattern:**
```python
import mlflow
from mlflow.tracking import MlflowClient
import numpy as np
import json
from datetime import datetime
from pathlib import Path

def log_experiment(config, model, data_version, metrics, artifacts=None):
    """Standardized experiment logging with full reproducibility"""
    # Set random seeds from config
    np.random.seed(config.get("seed", 42))
    torch.manual_seed(config.get("seed", 42))
    
    # Start run with standardized naming
    run_name = f"{config['model_name']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    with mlflow.start_run(run_name=run_name):
        # Log parameters
        mlflow.log_params(config)
        mlflow.log_param("data_version", data_version)
        
        # Log git info
        try:
            repo = git.Repo(search_parent_directories=True)
            mlflow.log_param("git_commit", repo.head.object.hexsha)
            mlflow.log_param("git_branch", repo.active_branch.name)
        except:
            pass
            
        # Log metrics
        for name, value in metrics.items():
            mlflow.log_metric(name, value)
        
        # Log model
        if hasattr(model, 'save_pretrained'):
            model_path = Path("./model_checkpoint")
            model.save_pretrained(model_path)
            mlflow.log_artifacts(model_path)
        else:
            mlflow.pytorch.log_model(model, "model")
            
        # Log additional artifacts
        if artifacts:
            for name, path in artifacts.items():
                mlflow.log_artifact(path, name)
                
        return mlflow.active_run().info.run_id
```

**FastAPI Experiment Endpoint:**
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from mlflow.tracking import MlflowClient

router = APIRouter(prefix="/experiments", tags=["Experiments"])
client = MlflowClient()

class ExperimentRun(BaseModel):
    run_id: str
    name: str
    status: str
    metrics: Dict[str, float]
    params: Dict[str, str]
    artifacts: List[str]

@router.get("/runs", response_model=List[ExperimentRun])
async def get_recent_runs(experiment_name: str, limit: int = 10):
    """Get recent experiment runs for a given experiment"""
    try:
        experiment = client.get_experiment_by_name(experiment_name)
        if experiment is None:
            raise HTTPException(status_code=404, detail=f"Experiment {experiment_name} not found")
            
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=limit,
            order_by=["attributes.start_time DESC"]
        )
        
        return [
            ExperimentRun(
                run_id=run.info.run_id,
                name=run.info.run_name,
                status=run.info.status,
                metrics={k: v for k, v in run.data.metrics.items()},
                params={k: v for k, v in run.data.params.items()},
                artifacts=[a.path for a in client.list_artifacts(run.info.run_id)]
            )
            for run in runs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 12.6 Ollama Quick‑Serve  
```bash
# Pull model & run REST service
ollama pull mistral:7b-instruct
ollama serve -m mistral:7b-instruct -p 11434
```  
Query:  
```python
import requests, json
resp = requests.post("http://localhost:11434/api/generate", json={"prompt": "Hello"})
print(json.loads(resp.text)["response"])
```  
### 12.7 MLflow Tracking Example  
```python
import mlflow, sklearn
with mlflow.start_run(run_name="clf_v1"):
model.fit(X_train, y_train)
mlflow.sklearn.log_model(model, "model")
mlflow.log_metric("accuracy", acc)
```  
### 12.8 Model Deployment & Serving

| Component | Recommended Approach | Alternative | Key Metrics |
|-----------|---------------------|-------------|------------|
| Model Registry | MLflow Model Registry with versioning | HuggingFace Hub | Model size, latency profiles, memory usage |
| Inference API | FastAPI with async endpoints | TorchServe, BentoML | p95/p99 latency, throughput, error rate |
| Horizontal Scaling | K8s HPA based on CPU/GPU usage | Manual replica management | Queue depth, batch efficiency, resource utilization |
| Model Monitoring | Prometheus + Grafana dashboards | Seldon Core metrics | Drift detection, accuracy regression |
| Canary Deployments | Istio or ArgoRollouts | K8s native blue/green | Success rate delta, user impact metrics |

**Example Model Serving Architecture:**
```python
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
import time
import logging
from prometheus_client import Counter, Histogram, start_http_server

# Define API models
class InferenceRequest(BaseModel):
    input: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
class InferenceResponse(BaseModel):
    output: str
    processing_time: float
    model_version: str

# Metrics
REQUEST_COUNT = Counter('model_requests_total', 'Total model inference requests', ['status', 'model'])
LATENCY = Histogram('model_inference_seconds', 'Model inference latency', ['model'])

# Application
app = FastAPI(title="ML Model API", version="1.0.0")

# Start metrics server on a separate port
start_http_server(8000)

class ModelService:
    def __init__(self):
        self.model = None
        self.version = "v1.0.0"
        self.ready = False
        self.load_model()
        
    def load_model(self):
        # Simulate model loading
        logging.info("Loading model...")
        time.sleep(2)  # Simulate loading time
        self.model = "loaded_model"  # Replace with actual model loading
        self.ready = True
        logging.info("Model loaded successfully")
        
    async def predict(self, text: str, params: Dict[str, Any]) -> str:
        if not self.ready:
            raise RuntimeError("Model not ready")
        
        # Simulate inference
        await asyncio.sleep(0.1)  # Simulate processing time
        return f"Processed: {text}"

model_service = ModelService()

@app.post("/v1/predict", response_model=InferenceResponse)
async def predict(request: InferenceRequest, background_tasks: BackgroundTasks):
    start_time = time.time()
    
    try:
        output = await model_service.predict(request.input, request.parameters)
        processing_time = time.time() - start_time
        
        # Record metrics
        REQUEST_COUNT.labels(status="success", model=model_service.version).inc()
        LATENCY.labels(model=model_service.version).observe(processing_time)
        
        return InferenceResponse(
            output=output,
            processing_time=processing_time,
            model_version=model_service.version
        )
    except Exception as e:
        REQUEST_COUNT.labels(status="error", model=model_service.version).inc()
        raise HTTPException(status_code=500, detail=str(e))
```

---