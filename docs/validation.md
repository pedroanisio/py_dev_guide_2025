## 6. Data Validation & Configuration — **Pydantic v2**

[Pydantic](https://docs.pydantic.dev/latest/) (v2, ensure version ≥ 2.0, preferably latest stable) is **mandatory** for defining and validating all structured data within the codebase. This includes domain models, API request/response schemas, event payloads, and runtime configuration.

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

[FastAPI](https://fastapi.tiangolo.com/) leverages Pydantic extensively for request/response validation and serialization.

```python
from fastapi import FastAPI
# Assume schemas.py defines UserRequest (for input) and UserResponse (for output)
from .schemas import UserRequest, UserResponse

app = FastAPI()

# FastAPI automatically validates the request body against UserRequest
# and serializes the return value using UserResponse.model_dump()
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_payload: UserRequest) -> UserResponse:
    # user_payload is a validated Pydantic model instance
    # ... (process the user_payload, e.g., save to database) ...
    created_user_data = {"id": 123, **user_payload.model_dump()}
    # Return data that conforms to UserResponse
    return UserResponse(**created_user_data)

```

> **Remember:** If a data structure can be represented by a Pydantic model, it **must** be, unless there is a specific, documented reason approved during code review. This consistency is key to maintainability and robustness.

---