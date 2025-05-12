## 6. Data Validation & Configuration — **Pydantic v2**  
Pydantic (≥ 2.11.4) is **mandatory** for all structured data exchanged inside the codebase—domain models, API schemas, event payloads, and runtime configuration.  
### 6.1 Core Rules  
1. **Model everything**: Replace raw `dict`/`TypedDict` at module boundaries with `BaseModel` subclasses.
2. **Settings pattern**: Centralize runtime/env config in a single `Settings` class that extends `BaseSettings` (reads from env, `.env`, `secrets/`).
3. **No implicit mutation**: Models are immutable by default (`model_config = {"frozen": True}`) unless mutability is essential.
4. **Validation first**: Construct models as the first step when ingesting external data (HTTP, CLI, DB rows) to reject bad input early.
5. **Serialization**: Use `.model_dump()` / `.model_dump_json()` for outbound payloads—never manual `dict()` manipulation.  
**Model Versioning Tip**: include `model_version: Literal["v1"]` in schemas to evolve breaking changes (`v2`, `v3`, …) without downtime. Deprecate via **router.include_router(v1_router, prefix="/v1")**.  
### 6.2 Recommended Layout  
```text
<root>/
├── app/
│   ├── models.py        # domain DTOs (BaseModel)
│   ├── schemas.py       # API request / response models
│   └── config.py        # Settings(BaseSettings) singleton
```  
### 6.3 Minimal Example  
```python
# app/models.py
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
id: int = Field(gt=0)
email: str
is_active: bool = True

@field_validator("email")
def email_must_have_at(cls, v: str) -> str:
if "@" not in v:
raise ValueError("invalid email")
return v

# app/config.py
from functools import lru_cache
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
debug: bool = Field(False, env="DEBUG")
database_url: str = Field(..., env="DATABASE_URL")

class Config:
env_file = ".env"
case_sensitive = True

@lru_cache
def get_settings() -> Settings:
return Settings()
```  
### 6.4 Tooling & CI Enforcement  
| Tool                         | Config Snippet | Purpose |
| ---------------------------- | -------------- | ------- |
| **mypy**                     | \\\n```toml\n[tool.mypy]\nplugins = ["pydantic.mypy"]\n```\n\\\n                     | Static-typing correctness, Pydantic plugin for generics & validators. |
| **ruff** | Rule set `B0`, `ARG`, `PTH` enabled by default. | Flags unused fields, wrong exception style, etc. |  
### 6.5 FastAPI Integration Quick‑Ref  
```python
from fastapi import FastAPI
from app.schemas import User

app = FastAPI()

@app.post("/users", response_model=User)
async def create_user(user: User):
# user is already validated ✅
return user
```  
> **Remember**: if a structure could be represented by a Pydantic model, it **must** be—unless explicitly instructed otherwise.  
---