#!/usr/bin/env python3
"""
Pydantic Data Validation & Configuration - Living Documentation

This module demonstrates best practices for data validation and configuration 
management using Pydantic. It serves as both working code and educational
documentation with interactive examples.

Key concepts demonstrated:
- Model definition and validation
- Configuration management
- Field constraints and validators
- Serialization and deserialization
- Error handling
- Integration patterns

Run this file directly to see a narrated demonstration of Pydantic in action.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any, TypeVar, Literal, Annotated
from uuid import UUID, uuid4
from pathlib import Path
import contextlib


class PydanticBestPractices:
    """
    Demonstrates Pydantic best practices through narrative explanation and working code.
    
    This class implements a series of examples that showcase recommended patterns
    for using Pydantic to validate and manage data in Python applications.
    """
    
    def __init__(self):
        """Initialize the demonstration."""
        print("=" * 80)
        print("🔍 PYDANTIC DATA VALIDATION & CONFIGURATION BEST PRACTICES")
        print("=" * 80)
        print("\nThis module demonstrates how to effectively use Pydantic for")
        print("data validation, configuration management, and ensuring type safety.")
        
        # Check Pydantic version to ensure we're using v2+
        try:
            import pydantic
            version = pydantic.__version__
            major_version = int(version.split('.')[0])
            if major_version < 2:
                print(f"\n⚠️ WARNING: You are using Pydantic v{version}.")
                print("This demonstration requires Pydantic v2.0.0 or higher.")
                print("Please upgrade with: pip install -U pydantic>=2.0.0")
                sys.exit(1)
            else:
                print(f"\n✅ Using Pydantic v{version}")
        except ImportError:
            print("\n❌ ERROR: Pydantic is not installed.")
            print("Please install with: pip install pydantic>=2.0.0")
            sys.exit(1)

    def demonstrate_basic_models(self):
        """
        Demonstrate the definition and usage of basic Pydantic models.
        
        Best practices shown:
        - Type annotations for automatic validation
        - Field constraints for data integrity
        - Custom validators for complex rules
        - Immutable models to prevent accidental state changes
        """
        from pydantic import BaseModel, Field, field_validator, EmailStr
        from pydantic_core import PydanticCustomError
        
        print("\n" + "-" * 80)
        print("📘 BASIC MODEL DEFINITION & VALIDATION")
        print("-" * 80)
        print("Best Practice: Use Pydantic models instead of dictionaries for all structured data")
        print("Benefits: Runtime validation, type safety, self-documenting code")
        
        # Define a basic user model
        class User(BaseModel):
            """User model with validation."""
            # Best Practice: Make models immutable by default
            model_config = {"frozen": True}
            
            id: int = Field(..., gt=0, description="Unique user identifier")
            email: str
            is_active: bool = True
            created_at: datetime = Field(default_factory=datetime.utcnow)
            
            # Custom validator to ensure email format
            @field_validator("email")
            @classmethod
            def validate_email(cls, value: str) -> str:
                if "@" not in value:
                    # Use PydanticCustomError for specific error types
                    raise PydanticCustomError(
                        "value_error",
                        "Email address must contain an '@' symbol",
                        {"value": value}
                    )
                return value.lower()  # Normalize email to lowercase
        
        print("\n📝 Example Model: User")
        print(f"Fields:")
        print(f"  • id: int (required, > 0)")
        print(f"  • email: str (required, must contain @)")
        print(f"  • is_active: bool (default: True)")
        print(f"  • created_at: datetime (default: current UTC time)")
        
        print("\n🔍 Demonstration: Creating valid model instances")
        # Valid user creation
        try:
            user = User(id=1, email="user@example.com")
            print(f"  ✅ Valid user created: {user}")
            
            # Try to modify the immutable model
            try:
                user.email = "new@example.com"
                print(f"  ❌ This line should not execute - model is mutable!")
            except Exception as e:
                print(f"  ✅ Cannot modify frozen model: {type(e).__name__}: {str(e)}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {type(e).__name__}: {str(e)}")
        
        print("\n🔍 Demonstration: Validation prevents invalid data")
        # Invalid ID (must be > 0)
        try:
            User(id=0, email="user@example.com")
            print(f"  ❌ This line should not execute - id validation failed!")
        except Exception as e:
            print(f"  ✅ Validation caught invalid ID: {str(e)}")
        
        # Invalid email (must contain @)
        try:
            User(id=1, email="invalid-email")
            print(f"  ❌ This line should not execute - email validation failed!")
        except Exception as e:
            print(f"  ✅ Validation caught invalid email: {str(e)}")
        
        # Next, demonstrate serialization
        print("\n🔄 Demonstration: Model serialization")
        user = User(id=1, email="user@example.com")
        
        # Proper way to serialize to dict
        user_dict = user.model_dump()
        print(f"  ✅ Serialized to dict: {json.dumps(user_dict, default=str)}")
        
        # Proper way to serialize to JSON
        user_json = user.model_dump_json()
        print(f"  ✅ Serialized to JSON: {user_json}")
        
        # Best practices for model serialization
        print("\n⭐ Best Practices for Serialization:")
        print("  • Always use .model_dump() instead of dict(model)")
        print("  • Always use .model_dump_json() for JSON serialization")
        print("  • Configure model_dump with include/exclude for field filtering")
        print("  • Use exclude_none=True to omit None values when appropriate")
        
        print("\n⚠️ Common Pitfalls to Avoid:")
        print("  • Manually creating dictionaries from model attributes")
        print("  • Using json.dumps() directly on model instances")
        print("  • Bypassing validation with direct dictionary manipulation")
        
        return User  # Return for use in later examples

    def demonstrate_config_management(self):
        """
        Demonstrate configuration management using Pydantic Settings.
        
        Best practices shown:
        - Centralized configuration with environment variables
        - Validation of configuration values
        - Type conversion and defaults
        - .env file support
        """
        from pydantic import BaseModel, Field, PostgresDsn
        from pydantic_settings import BaseSettings, SettingsConfigDict
        from functools import lru_cache
        
        print("\n" + "-" * 80)
        print("⚙️ CONFIGURATION MANAGEMENT")
        print("-" * 80)
        print("Best Practice: Use Pydantic Settings for all application configuration")
        print("Benefits: Environment variable integration, type validation, centralized config")
        
        # Create a temporary .env file for demonstration
        env_content = """
        # Application settings
        DEBUG=true
        API_KEY=demo-api-key
        DATABASE_URL=postgresql://user:password@localhost:5432/demo
        LOG_LEVEL=INFO
        MAX_CONNECTIONS=10
        ALLOWED_HOSTS=localhost,127.0.0.1
        """
        
        env_file = Path(".env.demo")
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print(f"\n📝 Created demo .env file: {env_file}")
        print("Contents (would normally contain sensitive information):")
        for line in env_content.strip().split("\n"):
            if line.strip() and not line.strip().startswith("#"):
                print(f"  {line.strip()}")
        
        # Define a settings class
        class LogLevel(str, Enum):
            """Valid log levels."""
            DEBUG = "DEBUG"
            INFO = "INFO"
            WARNING = "WARNING"
            ERROR = "ERROR"
            CRITICAL = "CRITICAL"
        
        class Settings(BaseSettings):
            """Application settings with validation."""
            model_config = SettingsConfigDict(
                env_file=".env.demo",      # Load from custom .env file
                case_sensitive=False,      # Environment variables are case-insensitive
                extra="ignore",            # Ignore extra fields from environment
                env_file_encoding="utf-8", # Specify file encoding
            )
            
            # Basic settings with validation
            debug: bool = Field(default=False, description="Enable debug mode")
            api_key: str = Field(..., description="API key for external services")
            log_level: LogLevel = Field(default=LogLevel.INFO, description="Application log level")
            
            # Database connection using special Pydantic types
            database_url: PostgresDsn = Field(
                ..., 
                description="Database connection string"
            )
            
            # Numeric value with constraints
            max_connections: int = Field(
                default=5, 
                ge=1, 
                le=100, 
                description="Maximum number of database connections"
            )
            
            # List from comma-separated string
            allowed_hosts: List[str] = Field(
                default_factory=lambda: ["localhost"],
                description="List of allowed hosts"
            )
            
            # Computed property based on other settings
            @property
            def is_production(self) -> bool:
                """Determine if this is a production environment."""
                return not self.debug and "localhost" not in self.allowed_hosts
        
        # Use lru_cache for efficient access to the settings
        @lru_cache
        def get_settings() -> Settings:
            """Returns cached application settings."""
            return Settings()
        
        print("\n🔍 Demonstration: Loading settings from environment")
        try:
            settings = get_settings()
            print("  ✅ Settings loaded successfully")
            print(f"  • Debug mode: {settings.debug}")
            print(f"  • API key: {settings.api_key}")
            print(f"  • Database URL: {settings.database_url}")
            print(f"  • Log level: {settings.log_level}")
            print(f"  • Max connections: {settings.max_connections}")
            print(f"  • Allowed hosts: {settings.allowed_hosts}")
            print(f"  • Is production: {settings.is_production}")
        except Exception as e:
            print(f"  ❌ Error loading settings: {type(e).__name__}: {str(e)}")
        
        # Clean up the demo .env file
        env_file.unlink()
        print(f"\n🧹 Removed demo .env file")
        
        print("\n⭐ Best Practices for Configuration:")
        print("  • Create a single Settings class for all application configuration")
        print("  • Use environment variables for deployment-specific settings")
        print("  • Validate configuration values at application startup")
        print("  • Use lru_cache to avoid repeatedly parsing environment variables")
        print("  • Handle sensitive values carefully (don't log them)")
        
        return Settings  # Return for use in later examples

    def demonstrate_nested_models(self):
        """
        Demonstrate nested models and relationships.
        
        Best practices shown:
        - Model composition
        - List fields with validators
        - Default factories for complex defaults
        - Cross-field validation
        """
        from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
        
        print("\n" + "-" * 80)
        print("🧩 NESTED MODELS & RELATIONSHIPS")
        print("-" * 80)
        print("Best Practice: Use model composition for complex data structures")
        print("Benefits: Better organization, reusable components, structured validation")
        
        # Define nested models for a richer domain model
        class Address(BaseModel):
            """Physical address model."""
            model_config = {"frozen": True}
            
            street: str
            city: str
            state: Optional[str] = None
            country: str
            postal_code: str
            is_primary: bool = False
        
        class Contact(BaseModel):
            """Contact information model."""
            email: str
            phone: Optional[str] = None
            
            @field_validator("email")
            @classmethod
            def validate_email(cls, value: str) -> str:
                if "@" not in value:
                    raise ValueError("Email must contain @ symbol")
                return value.lower()
            
            @field_validator("phone")
            @classmethod
            def validate_phone(cls, value: Optional[str]) -> Optional[str]:
                if value is None:
                    return None
                    
                # Remove common formatting characters
                digits_only = re.sub(r'[^0-9]', '', value)
                if len(digits_only) < 10:
                    raise ValueError("Phone number must have at least 10 digits")
                return digits_only
        
        class UserProfile(BaseModel):
            """Extended user profile information."""
            bio: Optional[str] = None
            avatar_url: Optional[str] = None
            preferences: Dict[str, str] = Field(default_factory=dict)
        
        class User(BaseModel):
            """User model with nested components."""
            id: UUID = Field(default_factory=uuid4)
            username: str
            created_at: datetime = Field(default_factory=datetime.utcnow)
            contact: Contact
            profile: UserProfile = Field(default_factory=UserProfile)
            addresses: List[Address] = Field(default_factory=list)
            
            @model_validator(mode='after')
            def ensure_primary_address(self) -> 'User':
                """Ensure there is exactly one primary address if addresses exist."""
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
            
            @computed_field
            @property
            def primary_address(self) -> Optional[Address]:
                """Return the primary address if it exists."""
                for addr in self.addresses:
                    if addr.is_primary:
                        return addr
                return None
        
        print("\n📝 Example Model Hierarchy:")
        print("User")
        print("├── id: UUID (auto-generated)")
        print("├── username: str")
        print("├── created_at: datetime (auto-generated)")
        print("├── contact: Contact")
        print("│   ├── email: str (validated)")
        print("│   └── phone: Optional[str] (validated)")
        print("├── profile: UserProfile")
        print("│   ├── bio: Optional[str]")
        print("│   ├── avatar_url: Optional[str]")
        print("│   └── preferences: Dict[str, str]")
        print("└── addresses: List[Address]")
        print("    ├── street: str")
        print("    ├── city: str")
        print("    ├── state: Optional[str]")
        print("    ├── country: str")
        print("    ├── postal_code: str")
        print("    └── is_primary: bool")
        
        print("\n🔍 Demonstration: Creating a user with nested models")
        
        # Create a user with nested models
        try:
            user = User(
                username="johndoe",
                contact=Contact(
                    email="john.doe@example.com",
                    phone="(555) 123-4567"
                ),
                addresses=[
                    Address(
                        street="123 Main St",
                        city="Anytown",
                        state="CA",
                        country="US",
                        postal_code="12345",
                        is_primary=True
                    ),
                    Address(
                        street="456 Market St",
                        city="Othertown",
                        state="NY",
                        country="US",
                        postal_code="67890"
                    )
                ]
            )
            
            print("  ✅ User created successfully")
            print(f"  • Username: {user.username}")
            print(f"  • Contact email: {user.contact.email}")
            print(f"  • Contact phone: {user.contact.phone}")
            print(f"  • Number of addresses: {len(user.addresses)}")
            print(f"  • Primary address: {user.primary_address.city}, {user.primary_address.state}" if user.primary_address else "None")
        except Exception as e:
            print(f"  ❌ Error creating user: {type(e).__name__}: {str(e)}")
        
        print("\n🔍 Demonstration: Cross-field validation")
        
        # Create a user with multiple primary addresses (should fail)
        try:
            user = User(
                username="janedoe",
                contact=Contact(
                    email="jane.doe@example.com"
                ),
                addresses=[
                    Address(
                        street="123 Main St",
                        city="Anytown",
                        country="US",
                        postal_code="12345",
                        is_primary=True
                    ),
                    Address(
                        street="456 Market St",
                        city="Othertown",
                        country="US",
                        postal_code="67890",
                        is_primary=True  # Second primary address - should fail
                    )
                ]
            )
            print("  ❌ This line should not execute - validation should fail!")
        except Exception as e:
            print(f"  ✅ Validation caught multiple primary addresses: {type(e).__name__}: {str(e)}")
        
        print("\n🔍 Demonstration: Automatic primary address selection")
        
        # Create a user with no primary address (first should be marked as primary)
        try:
            user = User(
                username="samsmith",
                contact=Contact(
                    email="sam.smith@example.com"
                ),
                addresses=[
                    Address(
                        street="123 Main St",
                        city="Anytown",
                        country="US",
                        postal_code="12345",
                        is_primary=False  # Not primary
                    ),
                    Address(
                        street="456 Market St",
                        city="Othertown",
                        country="US",
                        postal_code="67890",
                        is_primary=False  # Not primary
                    )
                ]
            )
            
            print("  ✅ User created successfully")
            print(f"  • First address is now primary: {user.addresses[0].is_primary}")
            print(f"  • Second address is still not primary: {user.addresses[1].is_primary}")
            print(f"  • Primary address: {user.primary_address.city}, {user.primary_address.country}")
        except Exception as e:
            print(f"  ❌ Error creating user: {type(e).__name__}: {str(e)}")
        
        print("\n⭐ Best Practices for Nested Models:")
        print("  • Break complex models into smaller, focused components")
        print("  • Use model composition to build rich domain models")
        print("  • Implement cross-field validation with model_validator")
        print("  • Use default_factory for complex default values")
        print("  • Add computed_field properties for derived values")
        
        return User  # Return for use in later examples

    def demonstrate_model_evolution(self):
        """
        Demonstrate model evolution and versioning strategies.
        
        Best practices shown:
        - Model versioning for backward compatibility
        - Creating new model versions while maintaining old ones
        - Migration between model versions
        """
        from pydantic import BaseModel, Field, root_validator
        from typing import Literal, Optional, List, Dict, Union, Any
        
        print("\n" + "-" * 80)
        print("🔄 MODEL EVOLUTION & VERSIONING")
        print("-" * 80)
        print("Best Practice: Version your models for API stability")
        print("Benefits: Backward compatibility, controlled evolution, clear client expectations")
        
        # Define a versioned model hierarchy
        class ProductBase(BaseModel):
            """Base product fields common to all versions."""
            id: int
            name: str
        
        class ProductV1(ProductBase):
            """Version 1 of the Product model."""
            model_version: Literal["v1"] = "v1"
            price: float
            description: Optional[str] = None
            
            class Config:
                extra = "forbid"  # Prevent extra fields
        
        class ProductV2(ProductBase):
            """Version 2 of the Product model with extended fields."""
            model_version: Literal["v2"] = "v2"
            price: Dict[str, float]  # Now a dictionary of currency -> price
            description: str  # Now required
            category: str  # New field
            tags: List[str] = Field(default_factory=list)  # New field
            
            class Config:
                extra = "forbid"
        
        # Define a version-agnostic product type
        ProductAny = Union[ProductV1, ProductV2]
        
        # Migration function to upgrade from v1 to v2
        def migrate_product_v1_to_v2(product_v1: ProductV1) -> ProductV2:
            """Migrate a v1 product to v2 format."""
            # Extract base fields
            base_data = product_v1.model_dump()
            
            # Remove v1-specific fields
            base_data.pop("model_version")
            price = base_data.pop("price")
            
            # Add v2-specific fields
            return ProductV2(
                **base_data,
                price={"USD": price},  # Convert price to dictionary
                description=product_v1.description or "No description available",  # Ensure description is not None
                category="Uncategorized"  # Default category for migrated products
            )
        
        print("\n📝 Versioned Model Example: Product")
        print("\nProductV1:")
        print("├── id: int")
        print("├── name: str")
        print("├── model_version: Literal['v1']")
        print("├── price: float")
        print("└── description: Optional[str]")
        
        print("\nProductV2:")
        print("├── id: int")
        print("├── name: str")
        print("├── model_version: Literal['v2']")
        print("├── price: Dict[str, float]")
        print("├── description: str (now required)")
        print("├── category: str (new field)")
        print("└── tags: List[str] (new field)")
        
        print("\n🔍 Demonstration: Creating models of different versions")
        
        # Create a v1 product
        product_v1 = ProductV1(
            id=1,
            name="Basic Widget",
            price=19.99
        )
        print(f"  ✅ ProductV1 created: {product_v1.model_dump_json()}")
        
        # Create a v2 product
        product_v2 = ProductV2(
            id=2,
            name="Advanced Widget",
            price={"USD": 29.99, "EUR": 26.99},
            description="An advanced widget with multiple features",
            category="Widgets",
            tags=["advanced", "featured"]
        )
        print(f"  ✅ ProductV2 created: {product_v2.model_dump_json()}")
        
        print("\n🔍 Demonstration: Migrating from v1 to v2")
        
        # Migrate a v1 product to v2
        migrated_product = migrate_product_v1_to_v2(product_v1)
        print(f"  ✅ Migrated product: {migrated_product.model_dump_json()}")
        
        print("\n🔍 Demonstration: API versioning strategy")
        
        print("\nIn a REST API, you would typically use URL versioning:")
        print("  • /api/v1/products - Returns ProductV1 objects")
        print("  • /api/v2/products - Returns ProductV2 objects")
        
        print("\nOr set up version-specific routes in FastAPI:")
        print("  v1_router = APIRouter(prefix='/v1')")
        print("  v2_router = APIRouter(prefix='/v2')")
        print("  app.include_router(v1_router)")
        print("  app.include_router(v2_router)")
        
        print("\n⭐ Best Practices for Model Versioning:")
        print("  • Include explicit version field in models (model_version)")
        print("  • Never modify existing model versions in breaking ways")
        print("  • Create new model versions for significant changes")
        print("  • Provide migration utilities between versions")
        print("  • Version your APIs to match model versions")
        print("  • Set appropriate deprecation timelines for old versions")
        
        return {
            "v1": ProductV1,
            "v2": ProductV2,
            "migrate": migrate_product_v1_to_v2
        }  # Return for use in later examples

    def demonstrate_error_handling(self):
        """
        Demonstrate proper error handling with Pydantic.
        
        Best practices shown:
        - Custom error types
        - Structured error responses
        - Validation errors
        - Error formatting
        """
        from pydantic import BaseModel, Field, field_validator, ValidationError
        
        print("\n" + "-" * 80)
        print("⚠️ ERROR HANDLING & VALIDATION")
        print("-" * 80)
        print("Best Practice: Use structured error handling with Pydantic ValidationError")
        print("Benefits: Consistent error responses, detailed validation feedback, easier debugging")
        
        # Define a model with various validation rules
        class Product(BaseModel):
            """Product model with validation rules."""
            name: str = Field(..., min_length=3, max_length=50)
            price: float = Field(..., gt=0)
            sku: str = Field(..., pattern=r'^[A-Z]{2}\d{6}$')  # Format: XX123456
            stock: int = Field(..., ge=0)
            
            @field_validator("name")
            @classmethod
            def validate_name(cls, value: str) -> str:
                if value.lower() == "test":
                    raise ValueError("'test' is not a valid product name")
                return value.strip()
        
        # Define an error response model
        class ErrorDetail(BaseModel):
            """Details about a validation error."""
            loc: List[str]
            msg: str
            type: str
        
        class ErrorResponse(BaseModel):
            """Structured error response."""
            detail: List[ErrorDetail]
        
        print("\n📝 Example Model: Product with Validation Rules")
        print("├── name: str (3-50 chars, cannot be 'test')")
        print("├── price: float (must be > 0)")
        print("├── sku: str (must match pattern XX123456)")
        print("└── stock: int (must be >= 0)")
        
        print("\n🔍 Demonstration: Handling validation errors")
        
        # Function to create a product with error handling
        def create_product(data: Dict[str, Any]) -> Union[Product, ErrorResponse]:
            """Create a product with validation error handling."""
            try:
                return Product(**data)
            except ValidationError as e:
                return ErrorResponse(detail=[
                    ErrorDetail(
                        loc=list(map(str, error["loc"])),
                        msg=error["msg"],
                        type=error["type"]
                    )
                    for error in e.errors()
                ])
        
        # Valid product
        valid_data = {
            "name": "Wireless Headphones",
            "price": 99.99,
            "sku": "HX123456",
            "stock": 100
        }
        
        result = create_product(valid_data)
        if isinstance(result, Product):
            print(f"  ✅ Valid product created: {result.model_dump_json()}")
        else:
            print(f"  ❌ Unexpected validation error: {result.model_dump_json()}")
        
        # Invalid product with multiple errors
        invalid_data = {
            "name": "t",  # Too short
            "price": -10,  # Negative price
            "sku": "invalid",  # Invalid SKU format
            "stock": -5  # Negative stock
        }
        
        result = create_product(invalid_data)
        if isinstance(result, ErrorResponse):
            print(f"  ✅ Validation errors caught:")
            for error in result.detail:
                print(f"    • Field: {'.'.join(error.loc)}: {error.msg} ({error.type})")
        else:
            print(f"  ❌ Validation should have failed but didn't!")
        
        # Processing validation errors
        print("\n🔍 Demonstration: Structured error handling in API context")
        
        def api_create_product(data: Dict[str, Any]) -> Dict[str, Any]:
            """Simulate API endpoint with proper error handling."""
            try:
                product = Product(**data)
                # In a real API, you would save to database here
                return {
                    "status": "success",
                    "data": product.model_dump(),
                    "code": 201  # Created
                }
            except ValidationError as e:
                return {
                    "status": "error",
                    "detail": e.errors(),
                    "code": 422  # Unprocessable Entity
                }
        
        # Invalid product
        response = api_create_product({
            "name": "test",  # Invalid name
            "price": 99.99,
            "sku": "HX123456",
            "stock": 100
        })
        
        print(f"  API Response Status: {response['status']}")
        print(f"  HTTP Status Code: {response['code']}")
        if response["status"] == "error":
            print("  Validation Errors:")
            for error in response["detail"]:
                print(f"    • Field: {'.'.join(map(str, error['loc']))}: {error['msg']}")
        
        print("\n⭐ Best Practices for Error Handling:")
        print("  • Use try/except blocks around model creation")
        print("  • Create structured error responses with ValidationError.errors()")
        print("  • Return appropriate HTTP status codes (422 for validation errors)")
        print("  • Keep a consistent error format across your API")
        print("  • Include enough detail to help clients fix their requests")
        
        return ErrorResponse  # Return for use in later examples

    def demonstrate_integration_patterns(self):
        """
        Demonstrate integration patterns with other systems.
        
        Best practices shown:
        - Integration with FastAPI
        - Integration with SQLAlchemy
        - Converting between different model types
        """
        from pydantic import BaseModel, Field, EmailStr, ConfigDict
        from typing import List, Optional, Dict, Any, ClassVar, Type
        from datetime import datetime
        
        print("\n" + "-" * 80)
        print("🔌 INTEGRATION PATTERNS")
        print("-" * 80)
        print("Best Practice: Use consistent patterns for integrating with other systems")
        print("Benefits: Clean boundaries, type safety, centralized validation")
        
        # Mock SQLAlchemy model (simulated)
        class UserDB:
            """Simulated SQLAlchemy model."""
            __tablename__ = "users"
            
            id: int
            email: str
            is_active: bool
            hashed_password: str
            created_at: datetime
            
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # Pydantic models for the API layer
        class UserBase(BaseModel):
            """Base user fields."""
            email: EmailStr
            is_active: bool = True
        
        class UserCreate(UserBase):
            """Model for creating a new user."""
            password: str  # Plain text password only for request
            
            model_config = ConfigDict(extra="forbid")  # Reject extra fields
        
        class UserUpdate(BaseModel):
            """Model for updating an existing user."""
            email: Optional[EmailStr] = None
            is_active: Optional[bool] = None
            
            model_config = ConfigDict(extra="forbid")
        
        class UserInDB(UserBase):
            """Internal user model with hashed password."""
            id: int
            hashed_password: str
            created_at: datetime
            
            # Configure for ORM mode
            model_config = ConfigDict(from_attributes=True)
        
        class UserResponse(UserBase):
            """User model returned in API responses."""
            id: int
            created_at: datetime
            
            # Configure for ORM mode
            model_config = ConfigDict(from_attributes=True)
        
        # Service layer for user operations
        class UserService:
            """Service for user operations."""
            
            @staticmethod
            def create_user(user_create: UserCreate) -> UserInDB:
                """Create a new user."""
                # Hash the password (simulated)
                hashed_password = f"hashed_{user_create.password}"
                
                # Create the database model (simulated)
                db_user = UserDB(
                    id=1,  # In a real app, this would be generated by the database
                    email=user_create.email,
                    is_active=user_create.is_active,
                    hashed_password=hashed_password,
                    created_at=datetime.utcnow()
                )
                
                # Return as Pydantic model
                return UserInDB.model_validate(db_user)
            
            @staticmethod
            def update_user(user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
                """Update an existing user."""
                # Simulate fetching user from database
                db_user = UserDB(
                    id=user_id,
                    email="existing@example.com",
                    is_active=True,
                    hashed_password="hashed_password",
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
                
                # Apply updates
                update_data = user_update.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_user, key, value)
                
                # Return as Pydantic model
                return UserInDB.model_validate(db_user)
        
        print("\n📝 User Model Hierarchy for FastAPI & Database Integration")
        print("UserBase (Base class with common fields)")
        print("├── UserCreate (API input for user creation)")
        print("│   └── + password field")
        print("├── UserUpdate (API input for user updates)")
        print("│   ├── Optional email")
        print("│   └── Optional is_active")
        print("├── UserInDB (Internal model with hashed password)")
        print("│   ├── + id field")
        print("│   ├── + hashed_password field")
        print("│   └── + created_at field")
        print("└── UserResponse (API output model)")
        print("    ├── + id field")
        print("    └── + created_at field")
        
        print("\n🔍 Demonstration: User creation flow")
        
        # Create a new user
        user_create = UserCreate(
            email="newuser@example.com",
            password="securepassword"
        )
        
        user_service = UserService()
        db_user = user_service.create_user(user_create)
        
        print("  ✅ User created in database:")
        print(f"  • ID: {db_user.id}")
        print(f"  • Email: {db_user.email}")
        print(f"  • Active: {db_user.is_active}")
        print(f"  • Hashed Password: {db_user.hashed_password}")
        print(f"  • Created At: {db_user.created_at}")
        
        # Convert to response model (using model_dump to exclude hashed_password)
        user_response = UserResponse.model_validate(db_user)
        print("\n  API Response (excludes sensitive fields):")
        print(f"  {user_response.model_dump_json()}")
        
        print("\n🔍 Demonstration: User update flow")
        
        # Update an existing user
        user_update = UserUpdate(email="updated@example.com")
        updated_user = user_service.update_user(1, user_update)
        
        if updated_user:
            print("  ✅ User updated in database:")
            print(f"  • Email: {updated_user.email} (was: existing@example.com)")
            print(f"  • Other fields preserved")
            
            # Convert to response model
            response = UserResponse.model_validate(updated_user)
            print("\n  API Response:")
            print(f"  {response.model_dump_json()}")
        else:
            print("  ❌ User not found")
        
        print("\n🔍 Demonstration: Mock FastAPI endpoint handlers")
        
        # Mock FastAPI handlers (pseudocode)
        print("\n  Example FastAPI endpoint handlers:")
        print("  ```python")
        print("  @app.post('/users', response_model=UserResponse)")
        print("  async def create_user(user: UserCreate):")
        print("      # FastAPI automatically validates against UserCreate")
        print("      db_user = user_service.create_user(user)")
        print("      # FastAPI automatically serializes using UserResponse")
        print("      return db_user")
        print("      ")
        print("  @app.put('/users/{user_id}', response_model=UserResponse)")
        print("  async def update_user(user_id: int, user: UserUpdate):")
        print("      # FastAPI automatically validates against UserUpdate")
        print("      db_user = user_service.update_user(user_id, user)")
        print("      if not db_user:")
        print("          raise HTTPException(404, 'User not found')")
        print("      # FastAPI automatically serializes using UserResponse")
        print("      return db_user")
        print("  ```")
        
        print("\n⭐ Best Practices for Integration:")
        print("  • Create different model types for different purposes")
        print("  • Use inheritance for common fields")
        print("  • Configure models with from_attributes=True for ORM integration")
        print("  • Keep sensitive data out of response models")
        print("  • Use the service layer pattern to separate business logic")
        print("  • Always validate input data at system boundaries")
        
        return {
            "base": UserBase,
            "create": UserCreate,
            "update": UserUpdate,
            "in_db": UserInDB,
            "response": UserResponse,
            "service": UserService
        }  # Return for use in later examples

    def run_demo(self):
        """
        Run a complete demonstration of Pydantic best practices.
        """
        print("\n" + "=" * 80)
        print("🚀 RUNNING PYDANTIC BEST PRACTICES DEMO")
        print("=" * 80)
        
        # Run all demonstrations
        basic_model = self.demonstrate_basic_models()
        settings = self.demonstrate_config_management()
        nested_model = self.demonstrate_nested_models()
        versioned_models = self.demonstrate_model_evolution()
        error_handling = self.demonstrate_error_handling()
        integration = self.demonstrate_integration_patterns()
        
        print("\n" + "=" * 80)
        print("✅ PYDANTIC BEST PRACTICES SUMMARY")
        print("=" * 80)
        
        print("\n🔑 Key Principles:")
        print("  1. Model Everything: Replace dictionaries with validated models")
        print("  2. Configuration via Settings: Centralize application configuration")
        print("  3. Immutability by Default: Prevent accidental state changes")
        print("  4. Validate Early: Reject invalid data at system boundaries")
        print("  5. Controlled Serialization: Use model_dump() and model_dump_json()")
        
        print("\n📚 Common Patterns Demonstrated:")
        print("  • Basic model definition and validation")
        print("  • Environment-based configuration")
        print("  • Nested models and relationships")
        print("  • Model versioning for API evolution")
        print("  • Error handling and validation")
        print("  • Integration with other systems")
        
        print("\n🛠️ Tools for Enforcement:")
        print("  • mypy with pydantic plugin for static type checking")
        print("  • ruff for linting and code quality")
        print("  • pytest with pydantic-factories for testing")
        print("  • Pre-commit hooks for validation before commits")
        
        print("\n" + "=" * 80)
        print("For more information, visit: https://docs.pydantic.dev/")
        print("=" * 80)


if __name__ == "__main__":
    # Run the demo
    demo = PydanticBestPractices()
    demo.run_demo()