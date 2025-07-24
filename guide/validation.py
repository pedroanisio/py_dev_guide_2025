from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Union, Type
from enum import Enum
import textwrap
import os
from pathlib import Path


class ModelType(Enum):
    """Types of Pydantic models"""
    DOMAIN = "Domain Model"
    DTO = "Data Transfer Object"
    SETTINGS = "Settings"
    REQUEST = "Request Model"
    RESPONSE = "Response Model"
    ERROR = "Error Model"


@dataclass
class PydanticModel:
    """Represents a Pydantic model definition"""
    name: str
    model_type: ModelType
    description: str
    code: str
    related_models: List[str] = field(default_factory=list)
    immutable: bool = True


@dataclass
class CorePrinciple:
    """Core principle for data validation"""
    name: str
    description: str
    example: Optional[str] = None


class ValidationPattern(Enum):
    """Common validation patterns"""
    FIELD_VALIDATOR = "Field Validator"
    MODEL_VALIDATOR = "Model Validator"
    ROOT_VALIDATOR = "Root Validator (v1 compatibility)"
    CONSTRAINT = "Field Constraint"
    TYPE_VALIDATION = "Type Validation"


@dataclass
class ToolingConfig:
    """Configuration for Pydantic-related tools"""
    tool: str
    config_snippet: str
    purpose: str


class DataValidationAndConfiguration:
    """
    Data Validation & Configuration
    
    A class representing best practices for using Pydantic for data validation
    and configuration management in Python applications.
    """
    
    def __init__(self):
        self.name = "Data Validation & Configuration"
        self.required_package = "pydantic"
        self.min_version = "2.0"
        
        # Core principles
        self.core_principles = [
            CorePrinciple(
                "Model Everything", 
                "Replace raw dict or typing.TypedDict at function/method boundaries and for internal state with Pydantic BaseModel subclasses.",
                """
# Instead of this:
def process_user(user_data: dict) -> dict:
    # Validation mixed with business logic
    if "email" not in user_data:
        raise ValueError("Email is required")
    # ...
    return {"id": 123, **user_data}

# Use this:
class UserInput(BaseModel):
    email: str
    name: str
    age: int | None = None

class UserOutput(BaseModel):
    id: int
    email: str
    name: str
    age: int | None = None

def process_user(user: UserInput) -> UserOutput:
    # Validation already handled by Pydantic
    # Business logic only
    return UserOutput(id=123, **user.model_dump())
"""
            ),
            CorePrinciple(
                "Configuration via Settings",
                "Centralize runtime configuration (environment variables, .env files, secrets) using a single Settings class inheriting from Pydantic's BaseSettings.",
                """
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    debug: bool = False
    database_url: str
    api_key: str
"""
            ),
            CorePrinciple(
                "Immutability by Default",
                "Configure models as immutable (model_config = {'frozen': True}) unless there's a compelling reason for instances to be mutable.",
                """
class User(BaseModel):
    model_config = {"frozen": True}
    
    id: int
    name: str
    
# This will raise an error:
# user = User(id=1, name="Alice")
# user.name = "Bob"  # Error: instance is frozen
"""
            ),
            CorePrinciple(
                "Validate Early",
                "Construct Pydantic models as the first step when ingesting external data (e.g., from HTTP requests, CLI arguments, database rows).",
                """
def api_endpoint(request_data: dict):
    # Validate immediately at the boundary
    try:
        user_request = UserCreate(**request_data)
    except ValidationError as e:
        return {"error": e.errors()}
    
    # Now work with validated data
    process_user(user_request)
"""
            ),
            CorePrinciple(
                "Controlled Serialization",
                "Use Pydantic's built-in methods like .model_dump() and .model_dump_json() for generating outbound data payloads.",
                """
def get_user_response(user: User) -> dict:
    # Instead of manually creating a dict
    # return {"id": user.id, "name": user.name}
    
    # Use controlled serialization
    return user.model_dump(exclude={"password_hash"})
"""
            )
        ]
        
        # Folder structure recommendation
        self.recommended_layout = {
            "<root>/": {
                "src/": {
                    "<app_name>/": [
                        "__init__.py",
                        "models.py",  # Core domain models (internal representation)
                        "schemas.py", # Data transfer objects (API request/response models)
                        "config.py",  # Application settings management (Settings class)
                    ]
                }
            }
        }
        
        # Example models
        self.example_models = [
            PydanticModel(
                name="User",
                model_type=ModelType.DOMAIN,
                description="Basic domain model with field validation",
                code="""
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
""",
                related_models=["Address", "UserProfile"]
            ),
            PydanticModel(
                name="Settings",
                model_type=ModelType.SETTINGS,
                description="Application settings with environment variable loading",
                code="""
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
"""
            ),
            PydanticModel(
                name="Address",
                model_type=ModelType.DOMAIN,
                description="Nested model for use in relationships",
                code="""
from pydantic import BaseModel, Field

class Address(BaseModel):
    model_config = {"frozen": True}
    
    street: str
    city: str
    country: str
    postal_code: str
    is_primary: bool = False
""",
                related_models=["User"]
            ),
            PydanticModel(
                name="UserProfile",
                model_type=ModelType.DOMAIN,
                description="Related model with default values",
                code="""
from pydantic import BaseModel, Field
from typing import Optional, Dict

class UserProfile(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Dict[str, str] = Field(default_factory=dict)
""",
                related_models=["User"]
            ),
            PydanticModel(
                name="ErrorDetail",
                model_type=ModelType.ERROR,
                description="Error detail for API responses",
                code="""
from pydantic import BaseModel
from typing import List

class ErrorDetail(BaseModel):
    loc: List[str]  # Location of the error
    msg: str        # Error message
    type: str       # Error type
""",
                related_models=["ErrorResponse"]
            ),
            PydanticModel(
                name="ErrorResponse",
                model_type=ModelType.RESPONSE,
                description="Standardized error response for APIs",
                code="""
from pydantic import BaseModel
from typing import List
from .schemas import ErrorDetail

class ErrorResponse(BaseModel):
    detail: List[ErrorDetail]
""",
                related_models=["ErrorDetail"]
            )
        ]
        # End of example_models
        
        # Tooling config
        self.tooling_configs = [
            ToolingConfig(
                tool="mypy",
                config_snippet="""
[tool.mypy]
plugins = ["pydantic.mypy"]
follow_imports = "silent"
strict_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_reexport = true
disallow_untyped_defs = true
""",
                purpose="Enables static type checking correctness. The Pydantic Mypy plugin is crucial for validating model types, validators, and generic models."
            ),
            ToolingConfig(
                tool="ruff",
                config_snippet="""
[tool.ruff]
select = ["E", "F", "B", "I", "ARG", "PTH"]
ignore = []
line-length = 88
target-version = "py39"
""",
                purpose="Lints for general Python best practices, which often overlap with good Pydantic usage."
            )
        ]
        
        # Advanced patterns
        self.advanced_patterns = {
            "nested_models": """
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
            addresses = list(self.addresses)  # Create a mutable copy
            addresses[0] = Address(**{**addresses[0].model_dump(), "is_primary": True})
            object.__setattr__(self, 'addresses', addresses)
        elif len(primary_addresses) > 1:
            raise ValueError("Only one address can be marked as primary")
        
        return self
""",
            "database_models": """
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
""",
            "error_handling": """
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
"""
        }
        
        # FastAPI integration example
        self.fastapi_integration = """
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
"""
    
    def get_model_by_name(self, name: str) -> Optional[PydanticModel]:
        """Find a model by name"""
        for model in self.example_models:
            if model.name == name:
                return model
        return None
    
    def get_related_models(self, model_name: str) -> List[PydanticModel]:
        """Find all models related to the specified model"""
        model = self.get_model_by_name(model_name)
        if not model:
            return []
            
        related = []
        for related_name in model.related_models:
            related_model = self.get_model_by_name(related_name)
            if related_model:
                related.append(related_model)
                
        return related
    
    def get_model_by_type(self, model_type: ModelType) -> List[PydanticModel]:
        """Find all models of a specific type"""
        return [model for model in self.example_models if model.model_type == model_type]
    
    def generate_settings_example(self, include_env_vars: bool = True) -> str:
        """Generate a settings example with environment variables"""
        settings_model = self.get_model_by_name("Settings")
        if not settings_model:
            return ""
            
        result = settings_model.code
        
        if include_env_vars:
            result += "\n\n# Example .env file:\n"
            result += "DATABASE_URL=postgresql://user:password@localhost:5432/app\n"
            result += "DEBUG=false\n"
            result += "# REDIS_URL=redis://localhost:6379/0  # Optional\n"
            
        return result
    
    def render_folder_structure(self, structure: Dict, indent: int = 0) -> str:
        """Render the recommended folder structure as a string"""
        result = []
        for key, value in structure.items():
            if isinstance(value, dict):
                result.append(" " * indent + key)
                result.append(self.render_folder_structure(value, indent + 2))
            elif isinstance(value, list):
                result.append(" " * indent + key)
                for item in value:
                    result.append(" " * (indent + 2) + item)
                    
        return "\n".join(result)
    
    def generate_project_template(self, base_dir: Path, app_name: str) -> Dict[str, Path]:
        """
        Generate a basic project structure with Pydantic models.
        Returns a dictionary of created files.
        """
        # Create the directory structure
        src_dir = base_dir / "src" / app_name
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the __init__.py
        init_file = src_dir / "__init__.py"
        with open(init_file, "w") as f:
            f.write(f'"""Core package for {app_name}."""\n\n')
            f.write(f'__version__ = "0.1.0"\n')
        
        # Create models.py with the User model example
        models_file = src_dir / "models.py"
        user_model = self.get_model_by_name("User")
        with open(models_file, "w") as f:
            f.write(f'"""Core domain models for {app_name}."""\n\n')
            f.write('from pydantic import BaseModel, Field, field_validator\n')
            f.write('from pydantic_core import PydanticCustomError\n\n')
            f.write(textwrap.dedent(user_model.code.strip() if user_model else ""))
        
        # Create config.py with Settings model
        config_file = src_dir / "config.py"
        settings_model = self.get_model_by_name("Settings")
        with open(config_file, "w") as f:
            f.write(f'"""Configuration management for {app_name}."""\n\n')
            f.write(textwrap.dedent(settings_model.code.strip() if settings_model else ""))
        
        # Create schemas.py with API models
        schemas_file = src_dir / "schemas.py"
        with open(schemas_file, "w") as f:
            f.write(f'"""API schema models for {app_name}."""\n\n')
            f.write('from pydantic import BaseModel, Field, EmailStr\n')
            f.write('from typing import List, Optional\n\n')
            f.write('class UserBase(BaseModel):\n')
            f.write('    """Base user attributes shared across schemas."""\n')
            f.write('    email: str\n')
            f.write('    is_active: bool = True\n\n')
            f.write('class UserCreate(UserBase):\n')
            f.write('    """Schema for creating a new user."""\n')
            f.write('    password: str\n\n')
            f.write('class UserResponse(UserBase):\n')
            f.write('    """Schema for user responses."""\n')
            f.write('    id: int\n\n')
            f.write('class ErrorDetail(BaseModel):\n')
            f.write('    """Details of a validation error."""\n')
            f.write('    loc: List[str]  # Location of the error\n')
            f.write('    msg: str        # Error message\n')
            f.write('    type: str       # Error type\n\n')
            f.write('class ErrorResponse(BaseModel):\n')
            f.write('    """Standard error response."""\n')
            f.write('    detail: List[ErrorDetail]\n')
        
        # Create .env file
        env_file = base_dir / ".env"
        with open(env_file, "w") as f:
            f.write('# Environment variables for development\n')
            f.write('DEBUG=true\n')
            f.write('DATABASE_URL=postgresql://user:password@localhost:5432/dev\n')
        
        # Create pyproject.toml with tool configs
        pyproject_file = base_dir / "pyproject.toml"
        with open(pyproject_file, "w") as f:
            f.write('[build-system]\n')
            f.write('requires = ["hatchling"]\n')
            f.write('build-backend = "hatchling.build"\n\n')
            f.write(f'[project]\n')
            f.write(f'name = "{app_name}"\n')
            f.write('version = "0.1.0"\n')
            f.write(f'description = "{app_name} project"\n')
            f.write('requires-python = ">=3.9"\n')
            f.write('dependencies = [\n')
            f.write('    "pydantic>=2.0",\n')
            f.write('    "pydantic-settings",\n')
            f.write(']\n\n')
            
            # Add mypy config
            mypy_config = next((tc for tc in self.tooling_configs if tc.tool == "mypy"), None)
            if mypy_config:
                f.write(textwrap.dedent(mypy_config.config_snippet.strip()) + '\n\n')
            
            # Add ruff config
            ruff_config = next((tc for tc in self.tooling_configs if tc.tool == "ruff"), None)
            if ruff_config:
                f.write(textwrap.dedent(ruff_config.config_snippet.strip()) + '\n')
        
        return {
            "init": init_file,
            "models": models_file,
            "config": config_file,
            "schemas": schemas_file,
            "env": env_file,
            "pyproject": pyproject_file
        }
    
    def __str__(self) -> str:
        """String representation of data validation standards"""
        return f"{self.name}: Using Pydantic {self.min_version}+ for data validation and configuration"


# Example usage
if __name__ == "__main__":
    validation = DataValidationAndConfiguration()
    
    print(f"📊 {validation}")
    
    print("\n🔑 Core Principles:")
    for i, principle in enumerate(validation.core_principles, 1):
        print(f"{i}. {principle.name}: {principle.description}")
    
    print("\n📁 Recommended Project Layout:")
    print("```")
    print(validation.render_folder_structure(validation.recommended_layout))
    print("```")
    
    print("\n📋 Example Models:")
    for model in validation.example_models:
        print(f"- {model.name} ({model.model_type.value}): {model.description}")
    
    print("\n⚙️ Tooling Configuration:")
    for tool_config in validation.tooling_configs:
        print(f"- {tool_config.tool}: {tool_config.purpose}")
    
    print("\n🔍 Example Usage:")
    user_model = validation.get_model_by_name("User")
    if user_model:
        print(f"User Model Example:\n```python\n{textwrap.dedent(user_model.code)}\n```")
    
    print("\n🧩 Advanced Patterns:")
    print("1. Nested Models and Relationships")
    print("2. Database Model Integration")
    print("3. Error Handling")
    
    print("\n💡 Try running the `.generate_project_template()` method to create a starter project structure.")