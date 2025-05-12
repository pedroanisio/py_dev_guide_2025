## 8. Containerization & Docker Usage  
### 8.1 Dockerfile Guidelines  
* Write **multi‑stage builds** to keep images lean and secure.
* Use official, slim base images and **pin explicit tags** inside the Dockerfile (`python:3.13-slim`, `node:20-alpine`, etc.).  
**Vulnerability Scan**  
```yaml
- name: Trivy scan
run: trivy fs --exit-code 1 --severity CRITICAL,HIGH .
```  
### 8.2 Compose Files  
| File              | Purpose                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| `compose.yml`     | Production‑oriented service definitions (minimal, safe defaults).                                     |
| `compose-dev.yml` | Development overrides ‑ mounts source, enables hot‑reload, adds optional helpers (db, mailhog, etc.). |  
#### Mandatory Rules  
1. **Do *not* declare a `version:` key** in any Compose file—Compose V2 infers the schema automatically.
2. Extension or local tweaks must go into **`compose-dev.yml`** (or another `*-dev.yml`) rather than editing `compose.yml` directly.  
#### Minimal Example: `compose-dev.yml`  
```yaml
services:
api:
build:
context: .
dockerfile: Dockerfile
command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
volumes:
- ./:/app:ro
environment:
- PYTHONUNBUFFERED=1
ports:
- "8000:8000"
```  
Run locally with both files:  
```bash
docker compose -f compose.yml -f compose-dev.yml up --build
```  
> **Rule:** Add databases, message brokers, or mock services needed for local hacking to **`compose-dev.yml`**, keep **`compose.yml`** production‑ready, and **never add the `version` property**.  
### 8.3 Compose Recipe Library (Mix & Match)  
Below are **modular compose snippets** you can combine with `docker compose -f ... -f ... up` to assemble the stack you need. All images have explicit tags and omit a top-level `version:` key.  
#### 8.3.1 Database + Admin (`compose.db.yml`)  
```yaml
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
test: ["CMD", "pg_isready", "-U", "dev"]
interval: 10s
retries: 5

pgadmin:
image: dpage/pgadmin4:8.6
environment:
PGADMIN_DEFAULT_EMAIL: admin@example.com
PGADMIN_DEFAULT_PASSWORD: admin
ports:
- "5050:80"
depends_on:
- postgres

volumes:
postgres_data:
```  
#### 8.3.2 Cache (`compose.cache.yml`)  
```yaml
services:
redis:
image: redis:7.2-alpine
ports:
- "6379:6379"
```  
#### 8.3.3 API Service (`compose.api.yml`)  
```yaml
services:
api:
build:
context: .
dockerfile: Dockerfile
environment:
DATABASE_URL: postgresql+asyncpg://dev:devpass@postgres/app_db
REDIS_URL: redis://redis:6379/0
depends_on:
- postgres
- redis
labels:
- "traefik.http.routers.api.rule=Host(`api.localhost`)"
- "traefik.http.services.api.loadbalancer.server.port=8000"
```  
#### 8.3.4 Front‑End (`compose.front.yml`)  
```yaml
services:
frontend:
build:
context: ./frontend
dockerfile: Dockerfile
environment:
VITE_API_URL: http://api.localhost
depends_on:
- api
labels:
- "traefik.http.routers.front.rule=Host(`app.localhost`)"
- "traefik.http.services.front.loadbalancer.server.port=3000"
```  
#### 8.3.5 Routing (`compose.proxy.yml`)  
```yaml
services:
traefik:
image: traefik:v2.11
command:
- "--providers.docker=true"
- "--api.insecure=true"
- "--entrypoints.web.address=:80"
ports:
- "80:80"
- "8080:8080"  # dashboard
volumes:
- "/var/run/docker.sock:/var/run/docker.sock:ro"
```  
#### 8.3.6 Static Assets (`compose.nginx.yml`)  
```yaml
services:
nginx:
image: nginx:1.25-alpine
volumes:
- ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
- ./static:/usr/share/nginx/html:ro
ports:
- "8081:80"
```  
#### 8.3.7 Observability (`compose.observability.yml`)  
```yaml
services:
prometheus:
image: prom/prometheus:v2.52.0
volumes:
- ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
ports:
- "9090:9090"

grafana:
image: grafana/grafana:11.0.0
environment:
- GF_SECURITY_ADMIN_PASSWORD: admin
ports:
- "3001:3000"
depends_on:
- prometheus
```  
#### Using the Recipes  
Spin up API + DB + Redis + Traefik for local dev:  
```bash
docker compose \
-f compose.yml \
-f compose.db.yml \
-f compose.cache.yml \
-f compose.api.yml \
-f compose.proxy.yml \
up --build
```  
Add the React front‑end and observability stack:  
```bash
docker compose \
-f compose.yml \
-f compose.db.yml \
-f compose.cache.yml \
-f compose.api.yml \
-f compose.front.yml \
-f compose.proxy.yml \
-f compose.observability.yml \
up --build
```  
> **Tip:** Keep `compose.yml` minimal (network/volumes + any global defaults) and layer these recipe files as needed. Remember **never to include a `version` key**.  
### 8.4 Docker Command Cheat‑Sheet for Dev & Debug  
| Situation                         | Command                                       | What it does                                                |
| --------------------------------- | --------------------------------------------- | ----------------------------------------------------------- |
| **Build images**                  | `docker compose build`                        | Rebuilds service images without starting containers.        |
| **Start stack**                   | `docker compose up -d`                        | Launches all services in detached mode.                     |
| **Follow logs (all)**             | `docker compose logs -f --tail=50`            | Streams last 50 lines and follows logs.                     |
| **Follow logs (one svc)**         | `docker compose logs -f api`                  | Tail just the `api` container.                              |
| **Interactive shell**             | `docker compose exec api bash`                | Open bash inside the running `api` container.               |
| **Run one‑off cmd**               | `docker compose run --rm api pytest -k quick` | Execute ad‑hoc command in throwaway container.              |
| **List running containers**       | `docker compose ps`                           | Show status table.                                          |
| **Stop stack**                    | `docker compose stop`                         | Gracefully stop all containers (preserve volumes/networks). |
| **Remove stack**                  | `docker compose down -v`                      | Stop and remove containers **and** named volumes.           |
| **Prune dangling images/volumes** | `docker system prune -f`                      | Free disk space (dangling only).                            |
| **View Docker resource usage**    | `docker stats`                                | Live CPU/mem/IO stats per container.                        |
| **Inspect container**             | `docker inspect <container_id>`               | Full JSON metadata—mounts, env, IPs.                        |
| **Copy file from container**      | `docker cp api:/app/log.txt ./log.txt`        | Extract files without volume mounts.                        |
| **Open a Python REPL**            | `docker compose exec api python`              | Access project venv inside container.                       |
| **Rebuild & restart changed svc** | `docker compose up -d --build api`            | Hot‑rebuild changed Dockerfile + restart service.           |  
> **Shortcut:** Add `alias dcd='docker compose down -v'` in your shell for quick full‑reset during heavy iteration.  
### 8.5 Deployment Recipes (Public‑Facing & Internal)  
> These recipes assume you have built images with explicit tags (e.g., `myapp-api:1.0.0`) and pushed them to a registry (ghcr.io / gcr.io / registry.digitalocean.com). Adjust resource names to match your project.  
#### 8.5.1 Stand‑Alone VPS (DigitalOcean Droplet + Cloudflare DNS)  
```bash
# On a fresh Ubuntu 24.04 droplet (root)
adduser deploy
usermod -aG sudo,docker deploy
ssh deploy@droplet

# Clone repo & pull env vars
git clone https://github.com/your‑org/myapp.git && cd myapp
cp .env.prod.example .env

# Export Cloudflare credentials for Traefik DNS‑01 challenge
export CF_DNS_API_TOKEN=cf‑token‑here

# Launch API + Traefik + Postgres
sudo docker compose \
-f compose.yml \
-f compose.db.yml \
-f compose.api.yml \
-f compose.cache.yml \
-f compose.proxy.yml \
up -d
```  
Traefik `dynamic/cloudflare.yaml` (inside repo):  
```yaml
tls:
certificatesResolvers:
letsencrypt:
acme:
email: dev@example.com
storage: /etc/traefik/acme.json
dnsChallenge:
provider: cloudflare
delayBeforeCheck: 0
```  
*DNS setup*: create an **`A`** record `api.example.com` → droplet IP in Cloudflare. Traefik will issue/renew TLS via Let's Encrypt automatically.  
---  
#### 8.5.2 Google Cloud Run (Public HTTPS, No Server Ops)  
1. **Build & push**  
```bash
gcloud builds submit --tag gcr.io/$GOOGLE_PROJECT/myapp-api:1.0.0
```  
2. **Deploy**  
```bash
gcloud run deploy myapp-api \
--image gcr.io/$GOOGLE_PROJECT/myapp-api:1.0.0 \
--platform managed \
--region us-central1 \
--allow-unauthenticated \
--set-env-vars "DATABASE_URL=$(cat prod_secrets.txt)"
```  
3. **Map domain** – In Cloud Run console, map `api.example.com` and add the suggested CNAME in Cloudflare → full TLS chain handled by Google.  
To keep **internal‑only**, omit `--allow-unauthenticated` and place Cloud Armor or IAP in front.  
---  
#### 8.5.3 Google Kubernetes Engine (Multi‑Service, Internal & External)  
*Simplified YAML snippets*  
```yaml
apiVersion: v1
kind: Namespace
metadata:
name: myapp
---
apiVersion: apps/v1
kind: Deployment
metadata:
name: api
namespace: myapp
spec:
replicas: 3
selector:
matchLabels: {app: api}
template:
metadata: {labels: {app: api}}
spec:
containers:
- name: api
image: gcr.io/$PROJECT/myapp-api:1.0.0
env:
- name: DATABASE_URL
valueFrom: {secretKeyRef: {name: db-url, key: url}}
---
apiVersion: v1
kind: Service
metadata:
name: api-int
namespace: myapp
spec:
type: ClusterIP        # internal only
selector: {app: api}
ports: [{port: 8000, targetPort: 8000}]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
name: api-public
namespace: myapp
annotations:
kubernetes.io/ingress.global-static-ip-name: myapp-ip
networking.gke.io/managed-certificates: api-cert
spec:
rules:
- host: api.example.com
http:
paths:
- path: /
pathType: Prefix
backend:
service:
name: api-int
port: {number: 8000}
```  
GKE Ingress controller provisions Cloud Load Balancer + certs automatically.  
For a *private TLD* (e.g., `api.internal`), use an **Internal Load Balancer** (`cloud.google.com/neg: "true"`, `networking.gke.io/internal-load-balancer-allow-global-access: "true"`) and route via Cloud DNS‑private zones.  
---  
#### 8.5.4 Private‑Only Stack in Corp VPC (No Internet)  
Combine internal DNS (`*.corp.local`) with Traefik + self‑signed or internal CA certs.  
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
-keyout tls.key -out tls.crt -subj "/CN=*.corp.local"

kubectl create secret tls internal-tls \
--cert=tls.crt --key=tls.key -n myapp
```  
Traefik `ingressRoute` references `internal-tls`; only corp network can resolve DNS.  
---  
> **Note:** Stick to the same environment variables and `uv.lock` across deploy targets to guarantee reproducibility.