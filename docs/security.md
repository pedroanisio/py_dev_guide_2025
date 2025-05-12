## 0. Security Practices (NEW)  
| Concern | Mandate |
| ------- | ------- |
| **Secret Management** | *Never* commit secrets. Load via **python‑dotenv** in *dev* and Vault/Doppler/SM in *prod*. |
| **Configuration** | Use `Settings(BaseSettings)`; map secret env vars (`DB_URL`, `JWT_KEY`). |
| **Dependency Scanning** | CI runs **trivy fs . --exit-code 1** and `uv pip audit`. |
| **Auth & AuthZ** | FastAPI routes use **OAuth2 Bearer** with scopes; enforce with `Depends(get_current_user)`. See §9. |
| **Input Sanitization** | Pydantic validates all inbound data; never `eval()` untrusted strings. |
| **HTTPS Everywhere** | Traefik or Cloud LB terminates TLS; internal networks may allow mTLS. |
| **Security Headers** | Add `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` through Traefik middleware. |
| **Transport Encryption** | Databases use TLS (`sslmode=require`), Redis with `--tls`. |
| **Static Analysis** | Enable **Bandit** in pre‑commit (`bandit -ll -r src`). |  
**Example: Loading environment variables**  
```python
from dotenv import load_dotenv; load_dotenv()
```  
!!! tip "Golden Rule"
    If you touch credentials, crypto, or user data, open a **SECURITY.md** threat‑model PR.  
---  
<a id="1-environment-management--setup"></a>