## 6. Data Validation & Configuration — **Pydantic v2**

[Pydantic](https://docs.pydantic.dev/latest/) (v2, ensure version ≥ 2.0, preferably latest stable) is **mandatory** for defining and validating all structured data within the codebase. This includes domain models, API request/response schemas, event payloads, and runtime configuration.

> **🔗 Cross-References:**
> - [Section 9: API Development with FastAPI](api.md) leverages Pydantic extensively for request/response modeling
> - [Section 11: Data Persistence & Storage](persistence.md) integrates with Pydantic models for data validation and serialization

### 6.1 Core Principles & Rules

1.  **Model Everything:** Replace raw `dict` or `typing.TypedDict` at function/method boundaries and for internal state with Pydantic [`BaseModel`](https://docs.pydantic.dev/latest/api/base_model/) subclasses. This provides runtime validation and static analysis benefits.
2.  **Configuration via Settings:** Centralize runtime configuration (environment variables, `.env` files, secrets) using a single `Settings` class inheriting from Pydantic's [`BaseSettings`](https://docs.pydantic.dev/latest/usage/settings/).
3.  **Immutability by Default:** Configure models as immutable (`model_config = {"frozen": True}`) unless there's a compelling reason for instances to be mutable. This prevents accidental state changes.
4.  **Validate Early:** Construct Pydantic models as the *first step* when ingesting external data (e.g., from HTTP requests, CLI arguments, database rows). This ensures invalid data is rejected immediately at the system boundary.
5.  **Controlled Serialization:** Use Pydantic's built-in methods like [`.model_dump()`](https://docs.pydantic.dev/latest/usage/serialization/#model_dump) and [`.model_dump_json()`](https://docs.pydantic.dev/latest/usage/serialization/#model_dump_json) for generating outbound data payloads. Avoid manual `dict()` creation or manipulation, which bypasses validation and field processing.

**Model Versioning Tip:** For evolving API schemas non-destructively, consider including a version field (e.g., `model_version: Literal["v1"] = "v1"`). When introducing breaking changes (`v2`, `v3`, ...), create new model versions. In frameworks like FastAPI, manage different API versions using separate routers (e.g., `router.include_router(v1_router, prefix="/v1")`, `router.include_router(v2_router, prefix="/v2")`).

### 6.2 Recommended Layout (`src/` structure)

```text
<root>/
└── src/
    └── <app_name>/         # Your application package
        ├── __init__.py
        ├── models.py       # Core domain models (internal representation)
        ├── schemas.py      # Data transfer objects (API request/response models)
        └── config.py       # Application settings management (Settings class)
```
*(Adjust based on the chosen project structure from Section 4.3)*

### 6.3 Minimal Example

```python
# src/<app_name>/models.py
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

class User(BaseModel):
    model_config = {"frozen": True} # Immutable by default

    id: int = Field(..., gt=0, description="Unique user identifier")
    email: str
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def email_must_contain_at_symbol(cls, v: str) -> str:
        if "@" not in v:
            # Use PydanticCustomError for specific error types
            raise PydanticCustomError(
                "value_error",
                "Email address must contain an '@' symbol",
                {"value": v}
            )
        return v.lower() # Example: Normalize email to lowercase

# src/<app_name>/config.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn

class Settings(BaseSettings):
    # Define application settings, reading from environment variables
    model_config = SettingsConfigDict(
        env_file=".env",         # Load .env file if present
        case_sensitive=False,    # Environment variable names are case-insensitive
        extra="ignore"           # Ignore extra fields from environment
    )

    debug: bool = Field(default=False, description="Enable debug mode")
    # Example: Using a specific Pydantic type for validation
    database_url: PostgresDsn = Field(..., description="DSN for the primary database")
    # Example: Optional setting with default
    redis_url: str | None = Field(default=None, description="URL for Redis cache (optional)")

# Use lru_cache for efficient access to the settings singleton
@lru_cache()
def get_settings() -> Settings:
    """Returns the application settings instance."""
    # Settings automatically reads from environment variables / .env file on instantiation
    return Settings()

# Example usage:
# settings = get_settings()
# print(settings.database_url)
```

### 6.4 Tooling & CI Enforcement

Ensure correct Pydantic usage and type safety using static analysis tools configured in `pyproject.toml`.

| Tool         | Configuration Snippet (`pyproject.toml`)                | Purpose                                                                    |
| :----------- | :------------------------------------------------------ | :------------------------------------------------------------------------- |
| **mypy**     | ```toml\n[tool.mypy]\nplugins = ["pydantic.mypy"]\n# ... other mypy settings ...\n``` | Enables static type checking correctness. The [Pydantic Mypy plugin](https://docs.pydantic.dev/latest/integrations/mypy/) is crucial for validating model types, validators, and generic models. |
| **ruff**     | *(Rule sets like `B` (flake8-bugbear), `ARG` (flake8-unused-arguments), `PTH` (flake8-use-pathlib) are generally recommended)* | Lints for general Python best practices, which often overlap with good Pydantic usage (e.g., flagging unused fields, incorrect exception handling). Configure specific Pydantic-related checks if available/needed. |

### 6.5 FastAPI Integration Quick Reference

[FastAPI](https://fastapi.tiangolo.com/) leverages Pydantic extensively for request/response validation and serialization. For a more comprehensive guide on FastAPI, see [Section 9: API Development — FastAPI](api.md).

```python
from fastapi import FastAPI, HTTPException, Path, Query, Depends
from typing import List, Optional, Annotated
# Assume schemas.py defines UserRequest (for input) and UserResponse (for output)
from .schemas import UserRequest, UserResponse, ErrorResponse
from .models import User
from .config import get_settings

app = FastAPI()
settings = get_settings()

# FastAPI automatically validates the request body against UserRequest
# and serializes the return value using UserResponse.model_dump()
@app.post(
    "/users", 
    response_model=UserResponse, 
    status_code=201,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        409: {"model": ErrorResponse, "description": "User already exists"}
    }
)
async def create_user(user_payload: UserRequest) -> UserResponse:
    # user_payload is a validated Pydantic model instance
    # ... (process the user_payload, e.g., save to database) ...
    created_user_data = {"id": 123, **user_payload.model_dump()}
    # Return data that conforms to UserResponse
    return UserResponse(**created_user_data)

# Path and query parameters with Pydantic validation
@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_user(
    user_id: Annotated[int, Path(gt=0, description="The ID of the user to retrieve")],
    include_details: Annotated[bool, Query(default=False)] = False
) -> UserResponse:
    # Path validation happens automatically
    # ... fetch user from database ...
    return UserResponse(id=user_id, email="user@example.com", is_active=True)

# Using a dependency to inject settings
def get_db_session(settings = Depends(get_settings)):
    # Use settings.database_url to establish connection
    # ...
    try:
        db = DatabaseSession(settings.database_url)
        yield db
    finally:
        db.close()

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: Annotated[int, Query(ge=0, default=0)],
    limit: Annotated[int, Query(ge=1, le=100, default=10)],
    db: DatabaseSession = Depends(get_db_session)
) -> List[UserResponse]:
    # Both API parameters and dependencies leverage Pydantic validation
    # ...
    return [UserResponse(id=1, email="user@example.com", is_active=True)]
```

### 6.6 Advanced Pydantic Patterns

#### 6.6.1 Nested Models and Relationships

```python
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import datetime
from uuid import UUID, uuid4

class Address(BaseModel):
    model_config = {"frozen": True}
    
    street: str
    city: str
    country: str
    postal_code: str
    is_primary: bool = False

class UserProfile(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: dict[str, str] = Field(default_factory=dict)

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)
    profile: UserProfile = Field(default_factory=UserProfile)
    addresses: List[Address] = Field(default_factory=list)
    
    @model_validator(mode='after')
    def ensure_primary_address(self) -> 'User':
        if not self.addresses:
            return self
            
        primary_addresses = [addr for addr in self.addresses if addr.is_primary]
        if not primary_addresses:
            # Make the first address primary if none are marked
            self.addresses[0] = Address(**{**self.addresses[0].model_dump(), "is_primary": True})
        elif len(primary_addresses) > 1:
            raise ValueError("Only one address can be marked as primary")
        
        return self
```

#### 6.6.2 Handling Database Models and API DTOs

```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field, ConfigDict

SQLBase = declarative_base()

# SQLAlchemy database model
class UserDB(SQLBase):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

# Pydantic models for API layer
class UserBase(BaseModel):
    email: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str  # Clear-text only for request
    
    model_config = ConfigDict(extra="forbid")  # Reject extra fields

class UserUpdate(BaseModel):
    email: str | None = None
    is_active: bool | None = None
    
    model_config = ConfigDict(extra="forbid")

class UserInDB(UserBase):
    id: int
    hashed_password: str
    
    # Configure model to work with SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    
    # Configure model to work with SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
```

> **🔗 Note:** For comprehensive database integration patterns, refer to [Section 11: Data Persistence & Storage](persistence.md), which covers SQLAlchemy ORM, driver selection, and integration patterns with Pydantic models.

#### 6.6.3 Error Handling for FastAPI

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Any, Dict, List

app = FastAPI()

class ErrorDetail(BaseModel):
    loc: List[str]  # Location of the error
    msg: str        # Error message
    type: str       # Error type

class ErrorResponse(BaseModel):
    detail: List[ErrorDetail]

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, str):
        # Convert simple string error to structured format
        detail = [{"loc": ["body"], "msg": exc.detail, "type": "request_validation"}]
    else:
        detail = exc.detail
        
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
    )
```

> **Remember:** If a data structure can be represented by a Pydantic model, it **must** be, unless there is a specific, documented reason approved during code review. This consistency is key to maintainability and robustness.

> **🔗 Related Sections:**
> - For API security using these models, see [Section 12: Security](security.md)
> - For testing strategies with Pydantic models, see [Section 8: Testing](testing.md)

---