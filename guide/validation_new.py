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
