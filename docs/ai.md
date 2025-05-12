## 12. AI & Data‑Science Practices  
### 12.1 Model Serving & Local LLMs  
| Tool                                        | Use Case                                                                                          | Notes                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Ollama**                                  | Quickly spin up local LLMs (Mistral, Llama 3) for prototypes, private inference, or edge devices. | Mount `~/.ollama` as a volume in Docker; bind GPU with `--gpus all` if available. |
| **vLLM**                                    | High‑throughput, GPU‑optimized serving for production.                                            | Pair with Triton or FastAPI adapter; use CUDA 12 base image.                      |
| **HuggingFace `text-generation-inference`** | Multi‑GPU distributed serving of bigger models.                                                   | Requires Nvidia A100/H100; run behind Traefik.                                    |  
Guidelines:  
* **Tag images by model + version** (`ollama/llama3:70b‑q4_1`).
* Store model configs (`model‑config.yaml`) in `m2m/` and load via entrypoint.
* For CPU‑only nodes, pick quantized variants (`q4_K_M`) or distilled models (TinyLlama).  
### 12.2 NLP Stack (Python)  
| Layer        | Preferred Lib                                      | Alternatives                              |
| ------------ | -------------------------------------------------- | ----------------------------------------- |
| Tokenization | `tokenizers` (HF)                                  | `spaCy` tokenizers                        |
| Core NLP     | **spaCy v3** for POS/NER; `en_core_web_trf` model. | NLTK for teaching / quick regex grammars. |
| Embeddings   | `sentence-transformers`                            | `transformers` + manual mean‑pooling      |
| Vector DB    | **Qdrant** (prod), **Chroma** (dev)                | pgvector extension                        |
| Eval & Bench | `langchain‑bench`, `lm‑eval‑harness`               | custom pytest harness                     |  
> **Rule:** New NLP pipelines must expose a **pure‑function endpoint** (`/v1/ner`), accept JSON, and return Pydantic models for entities.  
### 12.3 GPU vs CPU Guidelines  
| Case                        | Hardware                | Settings                                                           |
| --------------------------- | ----------------------- | ------------------------------------------------------------------ |
| Training small (<1B) models | Consumer GPU (RTX 4090) | `torch.set_float32_matmul_precision("high")`, `bf16` if supported. |
| Serving quantized 7B LLM    | Single GPU (24–48 GB)   | vLLM + Flash‑Attention 2; `--gpu-memory-utilization 0.85`.         |
| Batch inference embeddings  | CPU cluster             | `sentence-transformers` with `torch.set_num_threads($CPU)`.        |
| Vector search >100M vectors | Server with AVX‑512     | Qdrant `hnsw_16` + disk cache.                                     |  
### 12.4 Data Pipelines  
| Stage          | Tooling                        | Comment                                                         |
| -------------- | ------------------------------ | --------------------------------------------------------------- |
| Orchestration  | **Apache Airflow 2.9**         | DAGs stored in `pipelines/` folder; deploy via Docker Operator. |
| Pythonic flows | **Prefect 2**                  | Great for local dev; run agent in K8s.                          |
| Streaming ETL  | **Apache Beam** on Dataflow    | Use for terabyte‑scale transforms.                              |
| Feature Store  | **Feast** with Postgres/Qdrant | Keep feature definitions versioned.                             |  
Guidelines:  
* DAG code must pass `ruff` and unit tests (`pytest pipelines/tests`).
* Schedule stored in `pipelines/schedules.yaml`, validated at CI time.  
### 12.5 Experiment Tracking & Reproducibility  
| Aspect | Tool | Mandatory Config | | ------------------ | --------------------
| ------------------------------------------------------ | | 💾 Artifacts |
**MLflow** | Track params + metrics; log models as `mlflow.pyfunc`. | | 📊
Dashboards | **Weights & Biases** | Link run URL in PR description. | | 🧪 Data
Versioning | **DVC** | Store datasets in S3 bucket; lockfile in Git. |  
> **Rule:** All experiments must have a unique run ID, parameter snapshot, and random seed. Without these, results are non‑reviewable.  
Integrate MLflow client in FastAPI `/experiments` router for quick lookup.  
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
---