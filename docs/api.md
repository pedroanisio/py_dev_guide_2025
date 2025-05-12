## 9. API Development — FastAPI **(Mandatory)**  🚀  

> **🔗 Cross-References:**
> - For detailed guidance on Pydantic models for API validation, see [Section 6: Data Validation & Configuration](validation.md)
> - For database integration with your API, see [Section 11: Data Persistence & Storage](persistence.md)

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