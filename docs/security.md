## 0. Security Practices

Security is a foundational aspect of modern Python application development. This section provides comprehensive guidance on securing your applications at every level.

### 0.1 Security Quick Reference

| Concern | Mandate |
| ------- | ------- |
| **Secret Management** | *Never* commit secrets. Load via **python‑dotenv** in *dev* and Vault/Doppler/SM in *prod*. |
| **Configuration** | Use `Settings(BaseSettings)`; map secret env vars (`DB_URL`, `JWT_KEY`). |
| **Dependency Scanning** | CI runs **trivy fs . --exit-code 1** and `uv pip audit`. |
| **Auth & AuthZ** | FastAPI routes use **OAuth2 Bearer** with scopes; enforce with `Depends(get_current_user)`. See §10. |
| **Input Sanitization** | Pydantic validates all inbound data; never `eval()` untrusted strings. |
| **HTTPS Everywhere** | Traefik or Cloud LB terminates TLS; internal networks may allow mTLS. |
| **Security Headers** | Add `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` through Traefik middleware. |
| **Transport Encryption** | Databases use TLS (`sslmode=require`), Redis with `--tls`. |
| **Static Analysis** | Enable **Bandit** in pre‑commit (`bandit -ll -r src`). |

### 0.2 Environment Variables and Configuration

Never store sensitive information directly in your codebase. Use environment variables and secure vaults.

**Local Development Example using python-dotenv:**
```python
# app/core/config.py
"""
HDR-DESCRIPTION: Application configuration management
HDR-FILENAME: config.py
HDR-FILEPATH: app/core/config.py
HDR-VERSION: 1.0.0
"""
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, PostgresDsn, validator, AnyHttpUrl

# Load .env file for local development
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    """Application settings with secure defaults"""
    PROJECT_NAME: str = "MyApp"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[AnyHttpUrl]:
        """Parse CORS origins from string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Construct database URI from components"""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create global settings instance
settings = Settings()
```

### 0.3 Authentication and Authorization

Implement modern authentication using JWT tokens with proper scope checking:

```python
# app/core/security.py
"""
HDR-DESCRIPTION: Security utilities
HDR-FILENAME: security.py
HDR-FILEPATH: app/core/security.py
HDR-VERSION: 1.0.0
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare plain password with hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate secure password hash"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with expiration"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    
    # Include scopes if provided
    if "scopes" not in to_encode and "scope" in to_encode:
        to_encode["scopes"] = to_encode["scope"].split()
    
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )

def validate_token(token: str) -> Dict[str, Any]:
    """Validate and decode JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """FastAPI dependency to get current authenticated user"""
    payload = validate_token(token)
    
    # In a real implementation, fetch user from database
    # based on the subject claim (sub)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return user object (should be fetched from database)
    # In this example, we just return user_id
    return {"id": user_id}

def require_scopes(*required_scopes: str):
    """Create a dependency that checks for required scopes"""
    async def check_scopes(token: str = Depends(oauth2_scheme)):
        payload = validate_token(token)
        
        # Get token scopes (either as list or space-delimited string)
        token_scopes_raw = payload.get("scopes", payload.get("scope", ""))
        
        # Convert to a list if it's a string
        if isinstance(token_scopes_raw, str):
            token_scopes = token_scopes_raw.split()
        else:
            token_scopes = token_scopes_raw
        
        # Check if all required scopes are present
        for scope in required_scopes:
            if scope not in token_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: missing required scope '{scope}'",
                )
        
        return True
    
    return check_scopes
```

### 0.4 Input Validation and Sanitization

Always validate and sanitize all user-provided input:

```python
# app/schemas/user.py
"""
HDR-DESCRIPTION: User validation schemas
HDR-FILENAME: user.py
HDR-FILEPATH: app/schemas/user.py
HDR-VERSION: 1.0.0
"""
from pydantic import BaseModel, EmailStr, validator, Field
import re

class UserBase(BaseModel):
    """Base model with common user attributes"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    
    @validator("username")
    def username_alphanumeric(cls, v):
        """Validate username contains only alphanumeric chars and underscore"""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric")
        return v

class UserCreate(UserBase):
    """Schema for user creation with password validation"""
    password: str = Field(..., min_length=8)
    
    @validator("password")
    def password_strength(cls, v):
        """Enforce strong password requirements"""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain a special character")
        return v
```

### 0.5 API Security Headers

Add security headers to your FastAPI application:

```python
# app/main.py middleware setup
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response
```

### 0.6 Secure Database Connections

Always use encrypted connections to your databases:

```python
# Example SQLAlchemy connection with SSL
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# PostgreSQL with SSL
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username="user",
    password="password",
    host="dbhost",
    port=5432,
    database="mydb",
    query={"sslmode": "require"}  # Requires SSL
)

engine = create_engine(db_url)

# Redis with TLS
import redis

redis_client = redis.Redis(
    host="redis.example.com",
    port=6379,
    ssl=True,
    ssl_cert_reqs="required",
    password="your_password"
)
```

### 0.7 OWASP Top 10 Mitigations

Address the OWASP Top 10 vulnerabilities:

1. **Broken Access Control**: Implement proper authorization with scope checking
2. **Cryptographic Failures**: Use modern algorithms (bcrypt for passwords, HTTPS for transport)
3. **Injection**: Use parameterized queries with SQLAlchemy, validate inputs with Pydantic
4. **Insecure Design**: Follow secure by design principles in architecture
5. **Security Misconfiguration**: Use secure defaults, minimize exposed services
6. **Vulnerable Components**: Regularly scan dependencies with `uv pip audit` and Trivy
7. **Authentication Failures**: Implement proper JWT authentication with expiration
8. **Software and Data Integrity Failures**: Verify dependencies with integrity checks
9. **Security Logging and Monitoring Failures**: Implement proper logging (see Section 8)
10. **Server-Side Request Forgery**: Validate and sanitize all URLs before making requests

### 0.8 CI/CD Security Integration

Add security scanning to your CI pipeline:

```yaml
# .github/workflows/security.yml
name: Security Checks

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install --system bandit safety
          
      - name: Run Bandit
        run: bandit -r src/ -ll
        
      - name: Check dependencies
        run: uv pip audit
        
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
```

!!! tip "Golden Rule"
    If you touch credentials, crypto, or user data, open a **SECURITY.md** threat‑model PR.  

---
<a id="1-environment-management--setup"></a>