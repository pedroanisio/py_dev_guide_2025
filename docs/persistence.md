## 11. Data Persistence & Storage Choices

Choosing the right data persistence strategy and technology is fundamental to building scalable and maintainable applications. This section outlines core principles, recommended tools, operational practices, common patterns, and examples.

### 11.1 Core Principles

These principles guide all persistence-related decisions:

1.  **Data Ownership (Microservices):** Each microservice must own and control its datastore. Cross-service data access occurs via well-defined APIs or asynchronous events, never through direct access to another service's database. This promotes loose coupling and independent evolution.
2.  **Right Tool for the Job:** Select database engines based on specific data characteristics and access patterns (e.g., OLTP, graph traversals, vector similarity search, full-text search, time-series, document storage).
3.  **Schema-First & Version Controlled:** Maintain all schema definitions (SQL DDL, OpenAPI-backed event schemas, GraphQL SDL, NoSQL validation rules) in Git. Apply schema changes automatically via CI/CD using robust migration tools.
4.  **Observability & Backups:** Comprehensive monitoring (metrics, logs) and automated, regularly tested backup/restore procedures are non-negotiable for all datastores, including non-production environments.

### 11.2 Technology Choices: Database Matrix

This matrix provides a quick reference for common database options. Evaluate against specific project needs.

| Engine                 | Use-Case Sweet Spot                                                     | Recommended Async Driver(s)                                    | Migration Tool(s)                                   | Example Docker Image Tag                      |
| :--------------------- | :---------------------------------------------------------------------- | :------------------------------------------------------------- | :---------------------------------------------- | :-------------------------------------------- |
| **PostgreSQL 16+**     | General OLTP, JSONB storage, analytical queries, GIS ([PostGIS](https://postgis.net/)), Time-Series ([TimescaleDB](https://www.timescale.com/)), Vector ([pgvector](https://github.com/pgvector/pgvector)). | [`asyncpg`](https://magicstack.github.io/asyncpg/current/), [`psycopg[pool]`](https://www.psycopg.org/psycopg3/docs/basic/pool.html) | [Alembic](https://alembic.sqlalchemy.org/)        | `postgres:16-alpine`                          |
| **SQLite 3.45+**       | Simple CLI apps, embedded systems, local testing (e.g., `pytest` fixtures), edge devices. | [`aiosqlite`](https://github.com/omnilib/aiosqlite)            | [sqlite-utils](https://sqlite-utils.datasette.io/), Alembic (offline mode) | Bundled with Python                           |
| **MongoDB 7+**         | High-write schemaless/flexible-schema documents, rapid prototyping, content management. | [`motor`](https://motor.readthedocs.io/)                       | [Mongo-Migrate](https://github.com/kofrasa/mongo-migrate), [Mongock](https://www.mongock.io/) | `mongodb/mongodb-community-server:7.0-ubi8`   |
| **Neo4j 5+**           | Deep graph traversals, recommendation engines, fraud detection, knowledge graphs. | [`neo4j-driver`](https://neo4j.com/docs/python-manual/current/driver/) (asyncio mode) | [Liquibase-Neo4j](https://github.com/liquibase/liquibase-neo4j) | `neo4j:5` (use specific minor version)        |
| **Elasticsearch 8+**   | Full-text search, log analytics, observability data, complex aggregations. | [`elasticsearch[async]`](https://elasticsearch-py.readthedocs.io/) | Index template JSONs, [Index Lifecycle Management (ILM)](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html) | `docker.elastic.co/elasticsearch/elasticsearch:8.x.y` |
| **Chroma 0.4+**        | Lightweight local vector database (in-process or server mode) for semantic search and RAG applications. | [`chromadb`](https://docs.trychroma.com/usage-guide)           | Schema managed implicitly by collection creation. | `ghcr.io/chroma-core/chroma:0.4.x`              |
| **Qdrant 1.9+**        | Production-grade vector search, HNSW/Scalar Quantization, advanced filtering, high-cardinality metadata. | [`qdrant-client[async]`](https://github.com/qdrant/qdrant_client) | Collection schema managed via API/JSON.         | `qdrant/qdrant:v1.9.x`                        |

#### 11.2.1 Tip: Combining Relational and Vector Search

For projects requiring both strong relational capabilities and vector similarity search on the same dataset, consider PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension. It allows leveraging Postgres's mature ecosystem while adding efficient vector operations.

### 11.3 Implementation & Operational Practices

Effective data management involves robust operational procedures.

#### 11.3.1 Schema Management & Migrations

*   **Tooling:** Use tools like [Alembic](https://alembic.sqlalchemy.org/) for SQL databases. Auto-generate migration scripts but **always review the generated SQL diff** before merging.
*   **CI/CD Integration:** The CI pipeline must validate migrations (e.g., dry-run) before deployment.
    ```yaml
    # Example CI Step (Alembic)
    - name: Alembic Dry-Run Migration Check
      run: |
        echo "Generating SQL for pending migrations..."
        # Assumes Alembic is configured and environment variables for DB connection are set
        alembic upgrade head --sql > migration_diff.sql

        echo "Checking if migration_diff.sql is non-empty..."
        # Adapt this check based on whether migrations are always expected or optional
        if [ -s migration_diff.sql ]; then
          echo "Migration SQL generated:"
          cat migration_diff.sql
          # Add linting or policy checks here if needed
        else
          echo "No pending migrations or no SQL generated."
        fi
        # Example: Fail build if migration SQL was expected but not generated
        # test -s migration_diff.sql
    ```

#### 11.3.2 Connection Management

*   **Pooling:** Essential for performance. Use driver-provided pools (e.g., `asyncpg.create_pool()`) or external poolers ([PgBouncer](https://www.pgbouncer.org/) for Postgres). Size appropriately based on workload and resources (e.g., `min(32, (CPU_CORES * 2) + EFFECTIVE_SPINDLE_COUNT)` as a starting point for Postgres).

#### 11.3.3 Backup & Recovery

*   **Automation:** Implement automated nightly backups (e.g., `pg_dump`, WAL archiving, cloud provider snapshots, `neo4j-admin dump`).
*   **Testing:** **Regularly test your restore procedures** to verify data integrity and meet Recovery Time Objectives (RTO).

#### 11.3.4 Monitoring & Alerting

*   **Metrics:** Export database metrics using specific exporters (e.g., [`pg_exporter`](https://github.com/prometheus-community/postgres_exporter), `mongodb_exporter`, `qdrant_exporter`) to a monitoring system ([Prometheus](https://prometheus.io/)).
*   **SLOs & Alerts:** Define Service Level Objectives (SLOs) for key metrics (p95 latency, error rates, availability) and configure alerts for breaches.
*   **Logging:** Monitor slow query logs and database error logs.

#### 11.3.5 Security Considerations

*   **Permissions:** Use least-privileged database accounts.
*   **Secrets Management:** Rotate credentials regularly using tools like [HashiCorp Vault](https://www.vaultproject.io/) or [Doppler](https://doppler.com/).
*   **Encryption:** Enforce TLS/SSL for data in transit. Consider encryption at rest for sensitive data.

### 11.4 Architectural Patterns (Microservices)

Common patterns for data management in a microservices architecture:

| Pattern                             | When to Use                                         | Notes                                                                                                                               |
| :---------------------------------- | :-------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| **Database-per-Service**            | **Default pattern.**                                | Promotes loose coupling and independent scaling. Joins across services are handled at the application layer or via asynchronous patterns like Sagas or [CQRS](https://martinfowler.com/bliki/CQRS.html). |
| **Event Sourcing + Snapshots**      | High auditability, temporal queries, complex state transitions. | Store state changes as immutable events (e.g., in [Apache Kafka](https://kafka.apache.org/)). Maintain read-optimized projections (snapshots) in a suitable database (e.g., Postgres, Elasticsearch). |
| **Polyglot Persistence**            | A single service has diverse data needs (e.g., relational, graph, and full-text search). | Use the most appropriate database for each data type/access pattern within the service boundary. Often, one DB is canonical for writes, with data asynchronously replicated to others. |
| **Shared Read Replica (Cautiously)** | Complex, cross-domain analytical reporting where API aggregation is too slow/complex. | Expose a read-only replica of one or more service databases to a dedicated analytics service. **Strictly for reads.** Manage carefully to avoid tight coupling. |

### 11.5 Development Environment Examples (Docker Compose)

These snippets illustrate setting up databases for local development.

*PostgreSQL with pgvector and [Adminer](https://www.adminer.org/) (e.g., `compose.db.vector.yml`)*

```yaml
services:
  postgres-pgvector:
    image: ankane/pgvector:pg16 # Specific pgvector image with PostgreSQL 16
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mysecretpassword
      POSTGRES_DB: mydatabase
    ports:
      - "5432:5432"
    volumes:
      - postgres_pgvector_data:/var/lib/postgresql/data
    restart: unless-stopped

  adminer:
    image: adminer:latest
    ports:
      - "8082:8080"
    depends_on:
      - postgres-pgvector
    restart: unless-stopped

volumes:
  postgres_pgvector_data: {}
```

*Qdrant vector database and [Grafana](https://grafana.com/) (e.g., `compose.vector.monitoring.yml`)*

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.9.0 # Use a specific stable version
    ports:
      - "6333:6333" # gRPC
      - "6334:6334" # HTTP REST API
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

  grafana:
    image: grafana/grafana-oss:latest
    ports:
      - "3002:3000"
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: mygrafanapassword
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - qdrant # Optional: For dashboards querying Qdrant or its exporter
    restart: unless-stopped

volumes:
  qdrant_data: {}
  grafana_data: {}
```

### 11.6 Documentation Requirements

> **Rule:** For every primary datastore (database, collection, graph, index), document its purpose, schema definition location, backup strategy, and data retention policy in `m2m/README.md` or a dedicated `docs/data/<datastore_name>.md` file. This ensures critical operational knowledge is captured and accessible.

---