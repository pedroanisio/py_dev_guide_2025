## 9. Containerization & Docker Usage

Containerization using [Docker](https://www.docker.com/) is essential for creating consistent, reproducible, and isolated development, testing, and production environments. This section covers best practices for Dockerfiles, structuring Docker Compose files, common recipes, local development workflows, and deployment strategies.

### 9.1 Dockerfile Best Practices

Optimized and secure Dockerfiles are crucial for efficient builds and runtime performance.

*   **Multi-Stage Builds:** Always use [multi-stage builds](https://docs.docker.com/build/building/multi-stage/) to separate build-time dependencies from the final runtime image. This significantly reduces image size and attack surface.
*   **Base Images:** Start from official, minimal base images (e.g., `-slim`, `-alpine`). Avoid using `:latest` tags.
*   **Pin Versions:** Explicitly pin base image tags (e.g., `python:3.13-slim`, `node:20-alpine`) and package versions installed within the Dockerfile to ensure reproducible builds.
*   **Layer Caching:** Structure commands to leverage Docker's layer caching effectively (e.g., copy dependency manifests and install dependencies *before* copying application code).
*   **Non-Root User:** Run application processes as a non-root user for enhanced security.
*   **Security Scanning:** Integrate vulnerability scanning into your CI pipeline.
    *Example using [Trivy](https://github.com/aquasecurity/trivy):*
    ```yaml
    # .github/workflows/ci.yml
    - name: Scan filesystem for vulnerabilities
      run: |
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        trivy fs --exit-code 1 --severity CRITICAL,HIGH .
    ```

### 9.2 Docker Compose Fundamentals

[Docker Compose](https://docs.docker.com/compose/) simplifies the definition and management of multi-container applications.

#### 9.2.1 Layering Configuration (`compose.yml` + Overrides)

We use a layered approach for Compose files:

| File Pattern          | Purpose                                                                                               |
| :-------------------- | :---------------------------------------------------------------------------------------------------- |
| `compose.yml`         | Defines the core, production-like service structure, networks, and volumes. Contains minimal, safe defaults. Should be runnable on its own if possible. |
| `compose-*.yml`       | Provides overrides or additions for specific environments (e.g., `compose-dev.yml`, `compose-test.yml`). |
| `compose.override.yml`| Default override file automatically picked up by Docker Compose if present. Often used for local development tweaks. |

**Key Principle:** Start services using multiple `-f` flags, with later files overriding earlier ones.
`docker compose -f compose.yml -f compose-dev.yml up`

#### 9.2.2 Mandatory Rules

1.  **No `version:` Key:** **Do *not* declare a top-level `version:` key** in any Compose file. Compose V2 (the standard) infers the schema automatically.
2.  **Use Override Files:** Development-specific configurations (source code mounts, hot-reloading commands, debuggers, helper services like `mailhog`) **must** go into override files (e.g., `compose-dev.yml` or `compose.override.yml`), not the base `compose.yml`.
3.  **Keep Base Clean:** The base `compose.yml` should represent a production-ready configuration as closely as possible, using baked-in application code from the Docker image build.

> **Rule Reminder:** Add databases, message brokers, or mock services needed *only* for local development to `compose-dev.yml` or similar override files. Keep `compose.yml` focused on the core application services. **Never add the `version` property.**

#### 9.2.3 Modular Recipe Concept

The following section provides a library of modular `compose.*.yml` snippets. These are designed to be layered onto a base `compose.yml` using the `-f` flag to assemble the specific stack needed for development or testing.

### 9.3 Modular Compose Recipe Library

Combine these snippets with a base `compose.yml` (which might only define networks and volumes) to build your environment.

#### 9.3.1 Database + Admin (`compose.db.yml`)

```yaml
# Provides PostgreSQL + pgAdmin
services:
  postgres:
    image: postgres:16.2-alpine
    environment:
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: devpass
      POSTGRES_DB: app_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev -d app_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      postgres: # Wait for postgres service, not necessarily healthy
        condition: service_started
    restart: unless-stopped

volumes:
  postgres_data: {}
```

#### 9.3.2 Cache (`compose.cache.yml`)

```yaml
# Provides Redis
services:
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

#### 9.3.3 API Service (`compose.api.yml`)

```yaml
# Defines the main Python API service
services:
  api:
    # Assumes image is built separately or defined in base compose.yml/compose-dev.yml
    # build:
    #   context: .
    #   dockerfile: Dockerfile
    image: myapp-api:latest # Replace with your actual image name/tag
    environment:
      # Example environment variables
      DATABASE_URL: postgresql+asyncpg://dev:devpass@postgres/app_db
      REDIS_URL: redis://redis:6379/0
      LOG_LEVEL: INFO
    depends_on:
      postgres: # Wait for postgres service to start
        condition: service_started
      redis:
        condition: service_started
    # ports: # Expose ports if needed directly, often handled by proxy
    #   - "8000:8000"
    labels: # Example labels for Traefik proxy
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.localhost`)"
      - "traefik.http.routers.api.service=api-service"
      - "traefik.http.services.api-service.loadbalancer.server.port=8000"
    restart: unless-stopped
```

#### 9.3.4 Front-End (`compose.front.yml`)

```yaml
# Defines a Node.js/Vite frontend service
services:
  frontend:
    # Assumes image is built separately or defined in base compose.yml/compose-dev.yml
    # build:
    #   context: ./frontend
    #   dockerfile: Dockerfile
    image: myapp-frontend:latest # Replace with your actual image name/tag
    environment:
      # Example environment variable for API endpoint
      VITE_API_URL: http://api.localhost
    depends_on:
      - api # Optional, depends if frontend needs API at build/start time
    # ports: # Expose ports if needed directly, often handled by proxy
    #   - "3000:3000"
    labels: # Example labels for Traefik proxy
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`app.localhost`)"
      - "traefik.http.routers.frontend.service=frontend-service"
      - "traefik.http.services.frontend-service.loadbalancer.server.port=3000"
    restart: unless-stopped
```

#### 9.3.5 Routing Proxy (`compose.proxy.yml`)

```yaml
# Provides Traefik as a reverse proxy and API gateway
services:
  traefik:
    image: traefik:v2.11 # Pin to a specific minor version
    command:
      - "--api.insecure=true" # Enable dashboard (unsafe for production)
      - "--providers.docker=true" # Enable Docker provider
      - "--providers.docker.exposedbydefault=false" # Only expose containers with labels
      - "--entrypoints.web.address=:80" # Define HTTP entrypoint
      # Add command args for HTTPS, Let's Encrypt, etc. for production
    ports:
      - "80:80"       # HTTP
      - "443:443"     # HTTPS (if configured)
      - "8080:8080"   # Traefik Dashboard
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro" # Allow Traefik to access Docker socket
      # - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro # Optional static config
      # - ./traefik/dynamic:/etc/traefik/dynamic:ro       # Optional dynamic config
      # - traefik_certs:/letsencrypt                       # Volume for Let's Encrypt certs
    restart: unless-stopped

# volumes:
#   traefik_certs: {}
```

#### 9.3.6 Static Assets Server (`compose.nginx.yml`)

```yaml
# Provides Nginx for serving static files
services:
  nginx:
    image: nginx:1.25-alpine
    volumes:
      # Mount your Nginx config
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      # Mount your static assets directory
      - ./static:/usr/share/nginx/html:ro
    ports:
      - "8081:80" # Expose on a different host port
    restart: unless-stopped
```

#### 9.3.7 Observability Stack (`compose.observability.yml`)

```yaml
# Provides Prometheus + Grafana
services:
  prometheus:
    image: prom/prometheus:latest # Consider pinning version
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana-oss:latest # Consider pinning version
    environment:
      - GF_SECURITY_ADMIN_PASSWORD__FILE=/run/secrets/grafana_admin_password
      # Add other Grafana config via env vars if needed
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    secrets:
      - grafana_admin_password
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus_data: {}
  grafana_data: {}

secrets:
  grafana_admin_password:
    file: ./grafana/admin_password.txt # Store sensitive data outside compose file
```

> **Recipe Tip:** Keep the base `compose.yml` minimal (perhaps just defining networks and volumes). Layer these recipe files using `-f` as needed for different development or testing scenarios. Remember the mandatory rule: **never include a `version:` key**.

### 9.4 Assembling Development Stacks

Combine the base file and recipe files using `docker compose -f ...` to create your desired local environment.

**Example 1: API + Database + Cache + Proxy**

```bash
# Assumes a base compose.yml defining networks/volumes
docker compose \
  -f compose.yml \
  -f compose.db.yml \
  -f compose.cache.yml \
  -f compose.api.yml \
  -f compose.proxy.yml \
  up --build -d
```

**Example 2: Full Stack (API, Frontend, DB, Cache, Proxy, Observability)**

```bash
docker compose \
  -f compose.yml \
  -f compose.db.yml \
  -f compose.cache.yml \
  -f compose.api.yml \
  -f compose.front.yml \
  -f compose.proxy.yml \
  -f compose.observability.yml \
  up --build -d
```

#### 9.4.1 Development Overrides (`compose-dev.yml`)

Use a `compose-dev.yml` (or `compose.override.yml`) to apply development-specific settings like volume mounts for hot-reloading and different commands, without modifying the core service definitions.

**Minimal Example (`compose-dev.yml`):**

```yaml
# Overrides for the 'api' service defined in compose.api.yml or compose.yml
services:
  api:
    build:
      context: . # Build from local context for dev
      dockerfile: Dockerfile # Use the standard Dockerfile
      # Add build args or cache mounts specific to dev if needed
      # args:
      #   SOME_DEV_ARG: 1
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 # Hot-reload command
    volumes:
      # Mount local source code into the container (read-only recommended)
      - ./:/app:ro
    environment:
      # Override or add environment variables for development
      LOG_LEVEL: DEBUG
      PYTHONUNBUFFERED: "1"
      # Ensure ports are mapped for local access if not using a proxy
    ports:
      - "8000:8000"
```

**Running with Development Overrides:**

```bash
# Base + API recipe + Development overrides
docker compose -f compose.yml -f compose.api.yml -f compose-dev.yml up --build
```

### 9.5 Local Development Workflow & Debugging

Common Docker commands for managing your development stack:

| Situation                         | Command                                       | What it does                                                |
| :-------------------------------- | :-------------------------------------------- | :---------------------------------------------------------- |
| **Build images**                  | `docker compose build [--no-cache]`           | Rebuilds service images (optionally without cache).         |
| **Start stack (detached)**        | `docker compose up -d [--build]`              | Launches all services in background (optionally build first). |
| **Start stack (foreground)**      | `docker compose up [--build]`                 | Launches services in foreground, streaming logs.            |
| **Follow logs (all)**             | `docker compose logs -f --tail=50`            | Streams last 50 lines and follows logs from all services.   |
| **Follow logs (one service)**     | `docker compose logs -f api`                  | Tails logs just for the `api` service.                      |
| **Interactive shell**             | `docker compose exec api bash`                | Opens a bash shell inside the running `api` container.      |
| **Run one-off command**           | `docker compose run --rm api pytest -k quick` | Executes a command in a new, temporary container for the service. |
| **List running services**         | `docker compose ps`                           | Shows the status of services defined in compose files.      |
| **Stop stack**                    | `docker compose stop`                         | Gracefully stops running services (preserves volumes).      |
| **Stop & Remove stack**           | `docker compose down [-v]`                    | Stops and removes containers, networks. Add `-v` to remove named volumes. |
| **Prune unused resources**        | `docker system prune -f [--volumes]`          | Frees disk space by removing dangling images, build cache, networks. Add `--volumes` to remove unused volumes. |
| **View resource usage**           | `docker stats`                                | Shows live CPU/memory/network/IO stats per container.       |
| **Inspect container details**     | `docker inspect <container_id_or_name>`       | Displays low-level JSON information about a container.      |
| **Copy file from container**      | `docker cp api:/app/log.txt ./local_log.txt`  | Copies a file/folder from a container to the host.        |
| **Copy file to container**        | `docker cp ./config.yml api:/app/config.yml`  | Copies a file/folder from the host to a container.        |
| **Open Python REPL in service**   | `docker compose exec api python`              | Accesses the Python environment within the `api` container. |
| **Rebuild & restart specific svc**| `docker compose up -d --build api --no-deps`  | Rebuilds and restarts only the `api` service without restarting its dependencies. |

> **Shortcut Tip:** Add `alias dcd='docker compose down -v'` (or similar) to your shell profile (`.bashrc`, `.zshrc`) for quickly resetting your environment during development iterations.

### 9.6 Deployment Strategies & Recipes

Deploying containerized applications involves packaging them into immutable images and running them on target infrastructure.

> **Assumption:** These recipes assume you have built images with explicit, unique tags (e.g., `myapp-api:1.2.3`, `myapp-frontend:a7b3cde`) and pushed them to a container registry (e.g., GHCR, Docker Hub, GCR, ECR, DigitalOcean Registry). Adjust resource names and registry paths to match your project.

#### 9.6.1 Stand-Alone VPS (e.g., DigitalOcean Droplet + Cloudflare DNS)

Suitable for simpler applications or initial deployments.

```bash
# --- On the Target Server (e.g., Ubuntu 24.04) ---
# 1. Initial Setup (as root or with sudo)
apt update && apt install -y docker.io docker-compose-plugin # Install Docker Engine & Compose
adduser deploy # Create a deployment user
usermod -aG sudo,docker deploy # Add user to sudo and docker groups
su - deploy # Switch to the deployment user

# 2. Clone Repository & Prepare Environment
cd ~/
git clone https://github.com/your-org/myapp.git
cd myapp
cp .env.prod.example .env # Copy template
# vim .env # Edit .env with production secrets/config

# 3. Login to Container Registry (if private)
docker login registry.example.com -u <username> -p <token_or_password>

# 4. Pull latest images defined in compose files
docker compose -f compose.yml -f compose.prod.yml pull # Assuming a compose.prod.yml for prod settings

# 5. Prepare Traefik (if using for TLS via DNS challenge)
# Ensure Traefik dynamic config (e.g., cloudflare.yml) is present
# Set required environment variables for DNS provider API token
export CF_DNS_API_TOKEN="your_cloudflare_api_token"

# 6. Launch the Stack
docker compose \
  -f compose.yml \
  # Include relevant recipes for production (DB, Cache, Proxy, etc.)
  -f compose.db.yml \
  -f compose.api.yml \
  -f compose.cache.yml \
  -f compose.proxy.yml \
  # Optionally add a prod-specific override file
  # -f compose.prod.yml \
  up -d
```

*   **Traefik DNS Challenge:** Configure Traefik with your DNS provider (e.g., Cloudflare) and ACME settings (Let's Encrypt) in its dynamic configuration to handle automated TLS certificate issuance and renewal.
*   **DNS Setup:** Point your domain (e.g., `api.example.com`) via an **`A`** record to the droplet's IP address.

---

#### 9.6.2 Serverless Container Platform (e.g., Google Cloud Run)

Ideal for stateless applications needing auto-scaling and managed infrastructure (including TLS).

1.  **Build & Push Image:**
    ```bash
    # Assuming gcloud SDK is configured
    gcloud builds submit --tag gcr.io/$GOOGLE_PROJECT_ID/myapp-api:1.2.3
    ```
2.  **Deploy Service:**
    ```bash
    gcloud run deploy myapp-api \
      --image gcr.io/$GOOGLE_PROJECT_ID/myapp-api:1.2.3 \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated `# For public access` \
      --port 8000 `# Port container listens on` \
      --min-instances 1 `# Optional: Ensure at least one instance is warm` \
      --max-instances 10 `# Optional: Limit scaling` \
      --cpu 1 \
      --memory 512Mi \
      --set-secrets "DATABASE_URL=db-url-secret:latest" `# Mount secret as env var` \
      --set-env-vars "LOG_LEVEL=INFO,OTHER_CONFIG=value"
    ```
3.  **Map Custom Domain:** Use the Cloud Run console or `gcloud run domain-mappings create` to map your domain (e.g., `api.example.com`). Google provisions and manages the TLS certificate.

*   **Internal Access:** For internal-only services, omit `--allow-unauthenticated` and configure access control using [IAM Invoker roles](https://cloud.google.com/run/docs/securing/managing-access), [VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs/overview), or an [Internal HTTP(S) Load Balancer](https://cloud.google.com/load-balancing/docs/https/internal-https-load-balancing) with [IAP](https://cloud.google.com/iap/docs/concepts-overview).

---

#### 9.6.3 Managed Kubernetes (e.g., Google Kubernetes Engine - GKE)

Suitable for complex, multi-service applications requiring fine-grained control over networking, scaling, and orchestration.

*Simplified Kubernetes Manifest Snippets (`kubernetes/` directory):*

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
---
# kubernetes/secrets.yaml (Manage secrets securely, e.g., via SealedSecrets or Vault)
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: myapp
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:password@host:port/db"
---
# kubernetes/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
  namespace: myapp
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api-container
        image: gcr.io/$GOOGLE_PROJECT_ID/myapp-api:1.2.3
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: DATABASE_URL
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        readinessProbe: # Example probe
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 5
--- 
# kubernetes/api-service-internal.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-internal-service
  namespace: myapp
spec:
  type: ClusterIP # Internal service type
  selector:
    app: api
  ports:
  - protocol: TCP
    port: 80 # Service port
    targetPort: 8000 # Container port
---
# kubernetes/api-ingress-public.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-public-ingress
  namespace: myapp
  annotations:
    # GKE specific annotations for managed resources
    kubernetes.io/ingress.global-static-ip-name: "myapp-static-ip" # Reserved static IP
    networking.gke.io/managed-certificates: "api-managed-cert"     # Managed SSL cert
    # kubernetes.io/ingress.class: "gce" # Specify ingress controller if needed
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: api-internal-service
            port:
              number: 80
```

*   **Deployment:** Apply manifests using `kubectl apply -f kubernetes/`.
*   **GKE Features:** GKE Ingress automatically provisions Google Cloud Load Balancers and integrates with Google-managed SSL certificates.
*   **Internal Load Balancing:** For internal-only endpoints (e.g., `api.internal`), use an Internal Load Balancer Service type (`type: LoadBalancer` with internal annotations) or an Ingress configured with internal annotations, routing via internal DNS.

---

#### 9.6.4 Private-Only Stack (e.g., Corporate VPC without Internet Access)

Requires careful network configuration, internal DNS, and potentially a private container registry.

*   **DNS:** Configure internal DNS servers to resolve private TLDs (e.g., `*.corp.local`).
*   **TLS:** Use certificates issued by an internal Certificate Authority (CA) or generate self-signed certificates.
*   **Proxy:** Deploy Traefik or another ingress controller configured to use the internal CA/self-signed certificates.
    ```bash
    # Example: Generate self-signed cert
    openssl req -x509 -nodes -days 1095 -newkey rsa:4096 \
      -keyout /etc/ssl/private/internal-tls.key \
      -out /etc/ssl/certs/internal-tls.crt \
      -subj "/CN=*.corp.local"

    # Create Kubernetes secret
    kubectl create secret tls internal-tls-secret \
      --cert=/etc/ssl/certs/internal-tls.crt \
      --key=/etc/ssl/private/internal-tls.key \
      -n myapp
    ```
*   **Ingress:** Reference the internal TLS secret in the Ingress or Traefik `IngressRoute` configuration.
*   **Network Policies:** Implement strict Kubernetes Network Policies to control traffic flow within the cluster.

---

> **Reproducibility Note:** Ensure consistency across all deployment targets by using the same tagged container images, managing environment variables securely and consistently (e.g., via secrets management tools or platform integrations), and using the same dependency definitions (`uv.lock`, `package-lock.json`, etc.) used to build the images.