## 10. API Development — FastAPI **(Mandatory)**  🚀  

> **🔗 Cross-References:**
> - For detailed guidance on Pydantic models for API validation, see [Section 7: Data Validation & Configuration](validation.md)
> - For database integration with your API, see [Section 12: Data Persistence & Storage](persistence.md)
> - For standard project structure, see [Section 4.3: Recommended Project Structures](design.md#43-recommended-project-structures)

### Why FastAPI?  
* First‑class **async** support (built on Starlette) → **handles concurrent requests efficiently for I/O-bound operations** (DB queries, HTTP calls)
* **OpenAPI** docs auto‑generated → contract‑driven dev with **interactive documentation that simplifies client integration and testing**
* Pydantic integration = zero‑boilerplate validation → **catches errors early at system boundaries and improves type safety**
* **High performance** comparable to Node.js and Go → consistently ranks among the fastest Python frameworks
* **Developer-friendly** with intuitive syntax and excellent IDE support (type hints throughout)

### Quick‑start Skeleton  
```python
# app/main.py ★ HDR required in actual project files
from fastapi import FastAPI, Depends, HTTPException, status, Query, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Annotated
import uvicorn
import logging
from datetime import datetime, timedelta

# --- Models ---
class Health(BaseModel):
    """Health check response model"""
    status: str = "ok"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ItemBase(BaseModel):
    """Base item information"""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the item")
    description: Optional[str] = Field(None, max_length=1000, description="Optional item description")
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    tags: List[str] = Field(default_factory=list, description="List of item tags")

class ItemCreate(ItemBase):
    """Model for creating a new item"""
    pass

class Item(ItemBase):
    """Model for item responses"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"

# --- App Configuration ---
app = FastAPI(
    title="My API", 
    version="1.0.0",
    description="API for managing items and users",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-site.com"],  # List allowed origins (use ["*"] for development)
    allow_credentials=True,
    allow_methods=["*"],  # Or restrict: ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],
)

# Configure authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Dependencies ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to validate token and return current user"""
    try:
        # Replace with actual token validation (e.g., JWT decode)
        user = verify_token(token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                              detail="Invalid authentication credentials",
                              headers={"WWW-Authenticate": "Bearer"})
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                          detail="Invalid authentication credentials",
                          headers={"WWW-Authenticate": "Bearer"})

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---
@app.get("/health", response_model=Health, tags=["meta"])
async def health() -> Health:
    """Health check endpoint for monitoring"""
    return Health(status="ok")

@app.post("/token", response_model=Token, tags=["auth"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """OAuth2 compatible token login, returns JWT token"""
    # Replace with actual authentication logic
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with expiration (replace with actual JWT implementation)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    return Token(access_token=access_token)

@app.get("/items", response_model=List[Item], tags=["items"])
async def list_items(
    skip: Annotated[int, Query(ge=0, description="Skip N items")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Limit to N items")] = 10,
    tag: Optional[str] = None,
    db = Depends(get_db)
) -> List[Item]:
    """
    Get a list of items with pagination support.
    
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return
    - **tag**: Optional filter by tag
    """
    items = get_items(db, skip=skip, limit=limit, tag=tag)
    return items

@app.post("/items", response_model=Item, status_code=201, tags=["items"])
async def create_item(
    item: ItemCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
) -> Item:
    """
    Create a new item (requires authentication).
    """
    return create_db_item(db=db, item=item, user_id=current_user.id)

@app.get("/items/{item_id}", response_model=Item, tags=["items"],
        responses={404: {"description": "Item not found"}})
async def get_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)],
    db = Depends(get_db)
) -> Item:
    """
    Get a specific item by ID.
    """
    item = get_item_by_id(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=Item, tags=["items"])
async def update_item(
    item_id: int,
    item: ItemCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
) -> Item:
    """
    Update an item (requires authentication).
    """
    existing_item = get_item_by_id(db, item_id=item_id)
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check ownership (optional)
    if existing_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return update_db_item(db=db, item_id=item_id, item=item)

@app.delete("/items/{item_id}", status_code=204, tags=["items"])
async def delete_item(
    item_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete an item (requires authentication).
    
    Returns 204 No Content on success.
    """
    existing_item = get_item_by_id(db, item_id=item_id)
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check ownership (optional)
    if existing_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    delete_db_item(db=db, item_id=item_id)
    return None  # 204 No Content
```

> **💡 Note:** For comprehensive examples of Pydantic models for request/response schemas, validators, and error handling with FastAPI, see [Section 6.5: FastAPI Integration](validation.md#65-fastapi-integration-quick-reference) and [Section 6.6: Advanced Pydantic Patterns](validation.md#66-advanced-pydantic-patterns).

### Production Guidelines  

| Concern       | Mandate                                                                  |
| ------------- | ------------------------------------------------------------------------ |
| Workers       | **uvicorn\[standard]** via Gunicorn (`-k uvicorn.workers.UvicornWorker`) |
| Timeouts      | 60 s hard, 30 s read.                                                    |
| CORS          | Restrict origins in `CORSMiddleware`.                                    |
| Rate Limiting | Deploy Traefik plugin or Redis‑based SlowAPI.                            |

### Structuring Larger Applications

For projects beyond a single file, organize your API using the following structure:

```text
app/
├── main.py                # Application entry point
├── core/
│   ├── config.py          # Settings and configuration
│   ├── dependencies.py    # Shared dependencies
│   └── security.py        # Authentication and security
├── api/
│   ├── __init__.py
│   ├── deps.py            # API-specific dependencies
│   └── v1/                # Version 1 of your API
│       ├── __init__.py
│       ├── router.py      # Main router for v1
│       ├── endpoints/
│       │   ├── users.py   # User-related endpoints
│       │   └── items.py   # Item-related endpoints
├── models/                # Database models (SQLAlchemy)
├── schemas/               # Pydantic models
├── crud/                  # Database operations
├── utils/                 # Utility functions
└── tests/                 # Test suite
```

Example of a modular router setup:

```python
# app/api/v1/router.py
from fastapi import APIRouter
from .endpoints import users, items

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(items.router, prefix="/items", tags=["items"])

# app/main.py
from fastapi import FastAPI
from .api.v1 import router as api_v1_router

app = FastAPI(title="My API", version="1.0.0")
app.include_router(api_v1_router, prefix="/v1")
```

### Best Practices for FastAPI Projects

#### Versioning
- Use path-based versioning (e.g., `/v1/users`) for API stability.
- Maintain backward compatibility within version paths.
- Document deprecation timelines for outdated endpoints.

#### Logging
```python
# app/main.py
import logging
from fastapi import FastAPI, Request
import time
import uuid

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | %(asctime)s | %(message)s | %(name)s',
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    request_id = str(uuid.uuid4())
    logger.info(f"start request | {request.method} {request.url.path} | {request_id}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"end request | {request.method} {request.url.path} | {request_id} | "
        f"status={response.status_code} | time={process_time:.4f}s"
    )
    
    # Add request ID header to response
    response.headers["X-Request-ID"] = request_id
    return response
```

#### Testing
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_create_item():
    # Setup: authenticate and get token
    token_response = client.post("/token", data={"username": "test", "password": "test"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    
    # Test item creation
    headers = {"Authorization": f"Bearer {token}"}
    item_data = {"name": "Test Item", "price": 9.99, "description": "Test description"}
    
    response = client.post("/items", json=item_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["price"] == item_data["price"]
    assert "id" in data
```

#### Documentation
Enhance OpenAPI documentation with detailed descriptions:

```python
@app.get(
    "/users/{user_id}",
    response_model=User,
    responses={
        200: {
            "description": "Successful response with user details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "is_active": True
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
async def read_user(user_id: int):
    """
    Get user information by ID.
    
    This endpoint retrieves a specific user's details including:
    - User ID
    - Email address
    - Active status
    
    Authentication required: **Bearer token**
    Permissions required: **Admin or same user**
    """
    # ...implementation
```

#### Performance Optimization

- **Caching**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache:")

@app.get("/items/{item_id}")
@cache(expire=60)  # Cache for 60 seconds
async def get_item(item_id: int):
    # Expensive operation like database query
    return get_item_by_id(item_id)
```

- **Background Tasks**
```python
from fastapi import BackgroundTasks

@app.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email_notification, email, subject="New Update")
    return {"message": "Notification will be sent in the background"}
```

### Security Checklist

- ✅ **HTTPS Only**: Configure production servers to redirect HTTP to HTTPS
- ✅ **Authentication**: Use industry-standard authentication (OAuth2, JWT)
- ✅ **Rate Limiting**: Protect endpoints from abuse with rate limiting
- ✅ **Input Validation**: Use Pydantic models for all input validation
- ✅ **CORS**: Restrict Cross-Origin Resource Sharing to trusted domains
- ✅ **Dependency Scanning**: Regularly scan dependencies for vulnerabilities
- ✅ **Security Headers**: Set appropriate security headers (X-XSS-Protection, Content-Security-Policy)
- ✅ **Request Timeouts**: Configure timeouts to prevent resource exhaustion

### Further Reading

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Starlette Documentation](https://www.starlette.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [REST API Design Best Practices](https://restfulapi.net/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

## 9. FastAPI Best Practices

### 9.1 Project Structure

```
app/
├── __init__.py
├── main.py                 # Application entry point
├── config.py               # Configuration handling
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── security.py         # Authentication & authorization
│   ├── logging_config.py   # Logging configuration
│   └── exceptions.py       # Exception handlers
├── api/                    # API endpoints
│   ├── __init__.py
│   ├── deps.py             # Dependency injections
│   └── v1/                 # API version 1
│       ├── __init__.py
│       ├── endpoints/      # Route handlers
│       │   ├── __init__.py
│       │   ├── users.py
│       │   └── items.py
│       └── router.py       # Router aggregation
├── models/                 # Pydantic models
│   ├── __init__.py
│   ├── user.py
│   └── item.py
├── schemas/                # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   └── item.py
├── services/               # Business logic
│   ├── __init__.py
│   ├── user_service.py
│   └── item_service.py
├── db/                     # Database
│   ├── __init__.py
│   ├── session.py
│   └── crud/
│       ├── __init__.py
│       ├── base.py
│       ├── user.py
│       └── item.py
└── tests/                  # Tests
    ├── __init__.py
    ├── conftest.py
    └── api/
        ├── __init__.py
        ├── test_users.py
        └── test_items.py
```

### 9.2 Basic Application Skeleton

```python
"""
HDR-DESCRIPTION: FastAPI application entry point
HDR-FILENAME: main.py
HDR-FILEPATH: app/main.py
HDR-VERSION: 1.0.0
"""
import logging
from typing import Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from app.api.v1.router import api_router
from app.core.logging_config import configure_logging, get_logger
from app.core.security import get_current_user
from app.middleware.logging_middleware import add_logging_middleware

# Configure logging with jsonl format
log_level = os.environ.get("LOG_LEVEL", "INFO")
configure_logging(
    level=getattr(logging, log_level),
    service_name="api-service"
)

logger = get_logger("app.main")
logger.info("Starting application")

app = FastAPI(
    title="MyApp API",
    description="API for MyApp service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware with proper origins management
def get_allowed_origins():
    # In development, allow all origins for testing
    if os.getenv("ENVIRONMENT") == "development":
        return ["*"]
    
    # In production, restrict to specific domains
    origins_str = os.getenv("ALLOWED_ORIGINS", "")
    if not origins_str:
        # Fallback to secure defaults
        return ["https://app.example.com", "https://api.example.com"]
    return origins_str.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
add_logging_middleware(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        context={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 9.3 Authentication Implementation

#### 9.3.1 Security Module

```python
"""
HDR-DESCRIPTION: Authentication and authorization utilities
HDR-FILENAME: security.py
HDR-FILEPATH: app/core/security.py
HDR-VERSION: 1.0.0
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Any, TypeVar, cast

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, validator, Field

from app.models.user import User
from app.core.logging_config import get_logger

# Configuration
SECRET_KEY = "your-secret-key-in-env-var"  # IMPORTANT: Use an environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger = get_logger("app.core.security")

# Token and user models
class TokenData(BaseModel):
    sub: str
    scopes: List[str] = Field(default_factory=list)
    exp: Optional[datetime] = None
    
    @validator("scopes", pre=True)
    def ensure_scopes_list(cls, v: Union[str, List[str]]) -> List[str]:
        """Ensure scopes are a list, even if the token contains a space-separated string"""
        if isinstance(v, str):
            return v.split()
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

# Password handling
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

# JWT token creation/validation
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with claims and expiration."""
    to_encode = data.copy()
    expires_delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """Verify a JWT token and return the decoded data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract required fields
        sub: str = payload.get("sub", "")
        if not sub:
            raise JWTError("Missing subject claim")
            
        # Get scopes (either as list or space-separated string)
        scopes_raw = payload.get("scopes", [])
        
        # Create token data
        token_data = TokenData(
            sub=sub,
            scopes=scopes_raw,
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc)
        )
        return token_data
    except JWTError as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency for requiring a valid user
T = TypeVar('T', bound=User)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = verify_token(token)
        user = await get_user_by_username(token_data.sub)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

async def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username from the database."""
    # Implementation would fetch from your database
    # This is a placeholder
    from app.db.crud.user import get_user_by_username as db_get_user
    return await db_get_user(username)

# Scope-based authorization
def requires_scopes(*required_scopes: str):
    """Dependency to check if the user has the required scopes."""
    async def _check_scopes(token: str = Depends(oauth2_scheme)) -> bool:
        token_data = verify_token(token)
        for scope in required_scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not authorized for scope: {scope}",
                )
        return True
    return _check_scopes
```

#### 9.3.2 Authentication Router

```python
"""
HDR-DESCRIPTION: Authentication routes
HDR-FILENAME: auth.py
HDR-FILEPATH: app/api/v1/endpoints/auth.py
HDR-VERSION: 1.0.0
"""
from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import (
    Token, verify_password, create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
)
from app.models.user import User, UserCreate
from app.services.user_service import UserService
from app.core.logging_config import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("app.api.auth")

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate user
    user_service = UserService()
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        logger.warning(
            "Failed login attempt", 
            context={"username": form_data.username}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with user info and scopes
    token_data = {
        "sub": user.username,
        "scopes": user.scopes,
        # Add any additional claims here
    }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, 
        expires_delta=access_token_expires
    )
    
    logger.info(
        "User logged in successfully", 
        context={"username": user.username}
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    user_service = UserService()
    
    # Check if username already exists
    existing_user = await user_service.get_user_by_username(user_data.username)
    if existing_user:
        logger.warning(
            "Registration failed - username already exists", 
            context={"username": user_data.username}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Create new user
    try:
        user = await user_service.create_user(user_data)
        logger.info(
            "User registered successfully", 
            context={"username": user.username}
        )
        return user
    except Exception as e:
        logger.exception(
            "Error registering user", 
            context={"username": user_data.username, "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    logger.info(
        "User accessed profile", 
        context={"username": current_user.username}
    )
    return current_user
```

#### 9.3.3 Protected Route Example

```python
"""
HDR-DESCRIPTION: User endpoints
HDR-FILENAME: users.py
HDR-FILEPATH: app/api/v1/endpoints/users.py
HDR-VERSION: 1.0.0
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from app.models.user import User, UserUpdate
from app.core.security import get_current_user, requires_scopes
from app.services.user_service import UserService
from app.core.logging_config import get_logger

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger("app.api.users")

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(requires_scopes("users:read"))
):
    """Get list of users (requires users:read scope)"""
    user_service = UserService()
    users = await user_service.get_users(skip=skip, limit=limit)
    
    logger.info(
        f"Retrieved {len(users)} users",
        context={"requester": current_user.username, "skip": skip, "limit": limit}
    )
    
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: UUID4,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(requires_scopes("users:read"))
):
    """Get user by ID (requires users:read scope)"""
    user_service = UserService()
    user = await user_service.get_user(user_id)
    
    if not user:
        logger.warning(
            f"User not found",
            context={"user_id": str(user_id), "requester": current_user.username}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(
        f"Retrieved user",
        context={"user_id": str(user_id), "requester": current_user.username}
    )
    
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID4,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(requires_scopes("users:write"))
):
    """Update user (requires users:write scope)"""
    # Check if the current user is updating themselves or has admin privileges
    if str(user_id) != str(current_user.id) and "admin" not in current_user.scopes:
        logger.warning(
            "Unauthorized user update attempt",
            context={
                "requester": current_user.username,
                "target_user_id": str(user_id)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update other users"
        )
    
    user_service = UserService()
    user = await user_service.update_user(user_id, user_update)
    
    if not user:
        logger.warning(
            f"User not found for update",
            context={"user_id": str(user_id), "requester": current_user.username}
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(
        f"Updated user",
        context={"user_id": str(user_id), "requester": current_user.username}
    )
    
    return user
```

### 9.4 Database Connection

```python
"""
HDR-DESCRIPTION: Database session management
HDR-FILENAME: session.py
HDR-FILEPATH: app/db/session.py
HDR-VERSION: 1.0.0
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from app.core.logging_config import get_logger

logger = get_logger("app.db.session")

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/app")

# Create engine with proper pool size settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    pool_size=20,  # Depends on your worker count (typically 2-4x workers)
    max_overflow=10,
    pool_pre_ping=True,  # Verify connection before using from pool
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create sessionmaker
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncSession:
    """Dependency to get a database session."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.exception("Database session error", context={"error": str(e)})
        raise
    finally:
        await session.close()
```

### 9.5 Testing Asynchronous Code

```python
"""
HDR-DESCRIPTION: Tests for user endpoints
HDR-FILENAME: test_users.py
HDR-FILEPATH: app/tests/api/test_users.py
HDR-VERSION: 1.0.0
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import UserCreate, User
from app.core.security import create_access_token

# Synchronous client
client = TestClient(app)

# Test data
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword"
}

def create_test_token(username: str, scopes: list[str] = None):
    """Create a test JWT token with specified scopes"""
    scopes = scopes or ["users:read", "users:write"]
    token_data = {
        "sub": username,
        "scopes": scopes
    }
    return create_access_token(token_data)

# Test fixtures
@pytest.fixture
async def db_session():
    """Create a test database session"""
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session
        # Clean up test data
        await session.rollback()

@pytest.fixture
async def test_user_in_db(db_session: AsyncSession):
    """Create a test user in the database"""
    from app.services.user_service import UserService
    
    service = UserService(db_session)
    user_create = UserCreate(**test_user)
    user = await service.create_user(user_create)
    return user

@pytest.fixture
def auth_headers(test_user_in_db: User):
    """Create authorization headers with JWT token"""
    token = create_test_token(test_user_in_db.username)
    return {"Authorization": f"Bearer {token}"}

# Asynchronous tests
@pytest.mark.asyncio
async def test_get_users(auth_headers):
    """Test getting all users"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/users/", headers=auth_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_user(test_user_in_db: User, auth_headers):
    """Test getting a specific user"""
    user_id = test_user_in_db.id
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]

@pytest.mark.asyncio
async def test_update_user(test_user_in_db: User, auth_headers):
    """Test updating a user"""
    user_id = test_user_in_db.id
    update_data = {"email": "updated@example.com"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            f"/api/v1/users/{user_id}", 
            json=update_data, 
            headers=auth_headers
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == update_data["email"]

@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test accessing endpoint without token"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/users/")
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_insufficient_scope(test_user_in_db: User):
    """Test accessing endpoint with insufficient scope"""
    # Create token with insufficient scopes
    token = create_test_token(test_user_in_db.username, scopes=["profile:read"])
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/users/", headers=headers)
    
    assert response.status_code == 403
```

### 9.6 API Documentation

```python
"""
HDR-DESCRIPTION: API router aggregation
HDR-FILENAME: router.py
HDR-FILEPATH: app/api/v1/router.py
HDR-VERSION: 1.0.0
"""
from fastapi import APIRouter

from app.api.v1.endpoints import users, items, auth

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(items.router, tags=["items"])

# Add tags metadata for Swagger UI
tags_metadata = [
    {
        "name": "auth",
        "description": "Authentication and authorization operations",
    },
    {
        "name": "users",
        "description": "Operations with users",
    },
    {
        "name": "items",
        "description": "Operations with items",
    },
]
```

### 9.7 Production Guidelines

1. **Environment Configuration**
   - Use environment variables for all configuration
   - Store secrets in Doppler, HashiCorp Vault, or AWS Secrets Manager
   - Apply different settings per environment (dev/staging/prod)

2. **Security**
   - Always use HTTPS in production
   - Set restrictive CORS rules
   - Implement rate limiting
   - Use proper authentication (OAuth2 with JWT)
   - Validate all inputs
   - Set security headers

3. **Performance**
   - Run with multiple Gunicorn workers (2-4x CPU cores)
   - Use async workers (uvicorn.workers.UvicornWorker)
   - Optimize database queries
   - Use connection pooling
   - Implement caching where appropriate

4. **Monitoring & Observability**
   - Structured logging in JSON format
   - Metrics collection (Prometheus)
   - Distributed tracing (OpenTelemetry)
   - Health checks for load balancers
   - Error tracking (Sentry)

5. **Deployment**
   - Deploy as Docker containers
   - Use CI/CD pipelines
   - Implement rolling updates
   - Back by load balancer
   - Set appropriate resource limits

---