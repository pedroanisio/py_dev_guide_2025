## 11. Data Persistence & Storage Choices  
### 11.1 Core Principles  
1. **Own your data**: Each micro‑service controls its own datastore; cross‑service queries flow through APIs or async events—never through shared DB tables.
2. **Right tool for the job**: Pick the engine that matches access patterns (OLTP, graph traversals, vector similarity, full‑text search).
3. **Schema‑first**: Maintain schema definitions in Git (SQL migrations, OpenAPI‑backed event payloads, GraphQL SDL, etc.). Apply via automated CI/CD.
4. **Observability & backups**: Metrics, slow‑query logs, and nightly off‑site backups are non‑negotiable—even in dev/staging.  
### 11.2 Database Matrix  
| Engine              | Use‑Case Sweet Spot                                                 | Async Driver                    | Migration Tool                    | Recommended Image Tag                       |
| ------------------- | ------------------------------------------------------------------- | ------------------------------- | --------------------------------- | ------------------------------------------- |
| **PostgreSQL 16**   | OLTP, JSONB, analytical queries, extensions (PostGIS, TimescaleDB). | `asyncpg`, `psycopg[pool]`      | Alembic                           | `postgres:16.2-alpine`                      |
| **SQLite 3.45**     | Simple CLI apps, embedded tests, edge devices.                      | `aiosqlite`                     | `sqlite-utils`, Alembic (offline) | Bundled                                     |
| **MongoDB 7**       | High‑write schemaless docs, rapid prototyping.                      | `motor`                         | Mongo‑Migrate / Mongock           | `mongodb/mongodb-community-server:7.0-ubi8` |
| **Neo4j 5**         | Deep graph traversals, recommendation, fraud detection.             | `neo4j-driver` (`asyncio` mode) | Liquibase‑Neo4j                   | `neo4j:5.20`                                |
| **Elasticsearch 8** | Full‑text search, log analytics, observability.                     | `elasticsearch[async]`          | Index template JSONs + ILM        | `elastic/elasticsearch:8.13.0`              |
| **Chroma 0.4**      | Lightweight local vector DB (in‑proc / server) for semantic RAG.    | `chromadb`                      | n/a (implicit collections)        | `ghcr.io/chroma-core/chroma:0.4.24`         |
| **Qdrant 1.9**      | Production vector search, HNSW, filtering.                          | `qdrant-client[async]`          | Collection schema JSON            | `qdrant/qdrant:v1.9.0`                      |  
> **Tip:** Pair Postgres with the [pgvector](https://github.com/pgvector/pgvector) extension when you need both relational and vector similarity in the same dataset.  
### 11.3 Operational Best Practices  
* **Connection Pooling**: Use `asyncpg.create_pool()` (FastAPI startup) or PgBouncer for Postgres; configure pool size = (min(32, CPU×2)).
* **Migrations**: Auto‑generate with Alembic—review SQL diff before merge; CI runs `alembic upgrade head --sql` to lint.
* **Backups**: Nightly `pg_dump` or WAL‑archiving to S3; MongoDB Atlas continuous backup; Neo4j `neo4j-admin dump`.
* **Monitoring**: Export metrics (`pg_exporter`, `mongodb_exporter`, `qdrant_exporter`) to Prometheus; set SLOs on p95 latency and error‑rate.
* **Security**: Least‑privileged DB accounts; rotate secrets via Doppler/Vault; enable TLS in transit.  
### 11.4 Patterns in Microservices  
| Pattern                       | When to Pick                            | Notes                                                                      |
| ----------------------------- | --------------------------------------- | -------------------------------------------------------------------------- |
| **Database‑per‑Service**      | Default                                 | Avoids tight coupling; join data in app layer or via async saga / CQRS.    |
| **Event‑Sourcing + Snapshot** | Auditability, temporal queries          | Store immutable events (Kafka) + projections in Postgres/Elastic.          |
| **Polyglot Persistence**      | One service needs graph + search + OLTP | Keep write canonical in Postgres, index into Neo4j/Elastic asynchronously. |
| **Shared Read Replica**       | Complex cross‑domain reporting          | Expose read‑only replica to analytics service—never write.                 |  
### 11.5 Example Compose Snippets  
*Postgres + pgvector + adminer (`compose.db.vector.yml`)*  
```yaml
services:
postgres:
image: ankane/pgvector:0.8.1-pg16   # pgvector baked in
environment:
POSTGRES_PASSWORD: devpass
volumes: [pgdata:/var/lib/postgresql/data]

adminer:
image: adminer:4.8
ports: ["8082:8080"]
depends_on: [postgres]

volumes:
pgdata:
```  
*Qdrant + Grafana dashboard (`compose.vector.yml`)*  
```yaml
services:
qdrant:
image: qdrant/qdrant:v1.9.0
ports: ["6333:6333", "6334:6334"]

grafana:
image: grafana/grafana:11.0.0
ports: ["3002:3000"]
environment:
GF_SECURITY_ADMIN_PASSWORD: admin
```  
> **Rule:** Declare every database/collection/graph index in `m2m/README.md`—include purpose, schema/version table, backup plan, and retention policy.  
### 11.6 CI Migration Stage  
```yaml
- name: Alembic dry‑run migration
run: |
alembic upgrade head --sql | tee migration.sql
test -s migration.sql  # fail if empty
```  
---