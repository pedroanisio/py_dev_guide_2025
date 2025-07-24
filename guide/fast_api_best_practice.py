#!/usr/bin/env python3
"""
FastAPI Best Practices - Living Documentation

This module demonstrates best practices for building APIs with FastAPI through
narrative-driven, executable examples. It serves as both working code and 
educational documentation.

Key concepts demonstrated:
- API design and organization
- Authentication and security
- Dependency injection
- Validation with Pydantic
- Documentation and OpenAPI
- Error handling
- Performance optimization

Run this file directly to see a narrated demonstration of FastAPI in action.
"""

import logging
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any, Union, Annotated

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request, Path, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator
from jose import JWTError, jwt
import contextlib

# Import our own modules for integration
try:
    from validation import DataValidationAndConfiguration
    from observability import LoggingObservabilityStandards
except ImportError:
    # When running standalone, create mock objects
    class DataValidationAndConfiguration:
        def __init__(self):
            pass
        
    class LoggingObservabilityStandards:
        def __init__(self):
            pass
        def create_basic_jsonl_logger(self):
            return logging.getLogger("fastapi_demo")


class FastAPIBestPractices:
    """
    Demonstrates FastAPI best practices through narrative explanation and working code.
    
    This class implements a demonstration FastAPI application that showcases
    recommended patterns and approaches. Each method is documented to explain
    not just what it does, but why it follows best practices.
    """
    
    def __init__(self):
        """
        Initialize the FastAPI demonstration application.
        
        Best practices shown:
        - Configurable title and version
        - Custom documentation URLs
        - Structured logging setup
        """
        print("=" * 80)
        print("🚀 FASTAPI BEST PRACTICES DEMONSTRATION")
        print("=" * 80)
        print("This module demonstrates recommended patterns for FastAPI applications")
        print("while explaining the reasoning behind each practice.")
        
        self.secret_key = "demo-secret-key-replace-in-production"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # Integrate with the logging module
        self.logging_module = LoggingObservabilityStandards()
        self.logger = self.logging_module.create_basic_jsonl_logger()
        self.logger.info("Initializing FastAPI application")
        
        # Integrate with the validation module
        self.validation_module = DataValidationAndConfiguration()
        
        # Configure application-wide settings
        print("\n📋 Initializing FastAPI application...")
        self.app = FastAPI(
            title="Demo API",
            description="API showcasing FastAPI best practices",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )
        
        print("  ✅ Application initialized with title, description, and version")
        print("  ✅ Documentation configured at /docs and /redoc endpoints")
        
        # Set up authentication
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        print("  ✅ OAuth2 authentication scheme configured")
        
        # Configure CORS
        self._setup_cors()
        
        # Set up error handling
        self._setup_error_handling()
        
        # Set up routes
        self._setup_routes()
        
        # Set up the logging middleware (integrated with our logging module)
        self.setup_logging_middleware()
        
        print("  ✅ Application configuration complete")
        self.logger.info("FastAPI application initialized successfully")
    
    def _setup_cors(self):
        """
        Configure Cross-Origin Resource Sharing (CORS) middleware.
        
        Best practices shown:
        - Restricting origins to trusted domains
        - Environment-based configuration
        - Configuring allowed methods and headers
        """
        print("\n🔒 Configuring CORS (Cross-Origin Resource Sharing)...")
        print("  • CORS prevents websites from making unauthorized requests to your API")
        print("  • In production, restrict origins to trusted domains")
        
        # In a real app, this would come from environment variables
        is_development = True
        
        allowed_origins = ["*"] if is_development else [
            "https://app.example.com", 
            "https://api.example.com"
        ]
        
        if is_development:
            print("  ⚠️ DEVELOPMENT MODE: Allowing all origins (*)")
            print("  ⚠️ This should NEVER be done in production")
        else:
            print(f"  ✅ PRODUCTION MODE: Restricting origins to: {', '.join(allowed_origins)}")
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )
        
        print("  ✅ CORS middleware configured")
    
    def _setup_error_handling(self):
        """
        Configure global exception handling.
        
        Best practices shown:
        - Consistent error responses
        - Structured error logging
        - Hiding implementation details from clients
        """
        print("\n🛠️ Setting up global error handling...")
        print("  • Centralizes error handling across the application")
        print("  • Provides consistent error responses")
        print("  • Logs exceptions while hiding sensitive details from client")
        
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            """Global exception handler for all unhandled exceptions."""
            # Here we would log to a structured logging system
            print(f"  ❌ [ERROR] Unhandled exception: {str(exc)}")
            print(f"  ❌ [ERROR] Path: {request.url.path}, Method: {request.method}")
            
            # Return a sanitized response to the client
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
        
        print("  ✅ Global exception handler configured")
    
    def _setup_routes(self):
        """
        Configure API routes.
        
        Best practices shown:
        - Logical route organization
        - Health check endpoint
        - Authentication endpoints
        - Resource endpoints with proper HTTP methods
        """
        print("\n🔌 Setting up API routes...")
        print("  • Organized by resource and purpose")
        print("  • Using appropriate HTTP methods for actions")
        print("  • Including monitoring endpoints")
        
        # Health check endpoint
        @self.app.get("/health", tags=["monitoring"])
        async def health_check():
            """Health check endpoint for monitoring."""
            return {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
        
        # Authentication endpoints
        @self.app.post("/token", response_model=self.Token, tags=["auth"])
        async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
            """OAuth2 compatible token login, returns JWT token."""
            user = self._authenticate_user(form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            access_token = self._create_access_token(
                data={"sub": user.username}
            )
            return self.Token(access_token=access_token)
        
        # User endpoints
        @self.app.get("/users/me", response_model=self.User, tags=["users"])
        async def read_users_me(current_user: Annotated[self.User, Depends(self.get_current_user)]):
            """Get current user information."""
            return current_user
        
        # Item endpoints
        @self.app.get("/items", response_model=List[self.Item], tags=["items"])
        async def list_items(
            current_user: Annotated[self.User, Depends(self.get_current_user)],
            skip: Annotated[int, Query(ge=0, description="Skip N items")] = 0,
            limit: Annotated[int, Query(ge=1, le=100, description="Limit to N items")] = 10,
            tag: Optional[str] = None
        ):
            """
            Get a list of items with pagination support.
            
            - **skip**: Number of items to skip (for pagination)
            - **limit**: Maximum number of items to return
            - **tag**: Optional filter by tag
            """
            items = self._get_items(skip=skip, limit=limit, tag=tag)
            return items
        
        @self.app.post("/items", response_model=self.Item, status_code=201, tags=["items"])
        async def create_item(
            item: self.ItemCreate,
            current_user: Annotated[self.User, Depends(self.get_current_user)]
        ):
            """Create a new item (requires authentication)."""
            return self._create_item(item=item, user_id=current_user.id)
        
        @self.app.get(
            "/items/{item_id}", 
            response_model=self.Item, 
            tags=["items"],
            responses={404: {"description": "Item not found"}}
        )
        async def get_item(
            item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)]
        ):
            """Get a specific item by ID."""
            item = self._get_item_by_id(item_id=item_id)
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return item
        
        @self.app.put("/items/{item_id}", response_model=self.Item, tags=["items"])
        async def update_item(
            item_id: int,
            item: self.ItemCreate,
            current_user: Annotated[self.User, Depends(self.get_current_user)]
        ):
            """Update an item (requires authentication)."""
            existing_item = self._get_item_by_id(item_id=item_id)
            if existing_item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            
            # Check ownership (optional)
            if existing_item.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
                
            return self._update_item(item_id=item_id, item=item)
        
        @self.app.delete("/items/{item_id}", status_code=204, tags=["items"])
        async def delete_item(
            item_id: int,
            current_user: Annotated[self.User, Depends(self.get_current_user)]
        ):
            """
            Delete an item (requires authentication).
            
            Returns 204 No Content on success.
            """
            existing_item = self._get_item_by_id(item_id=item_id)
            if existing_item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            
            # Check ownership (optional)
            if existing_item.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
                
            self._delete_item(item_id=item_id)
            return None  # 204 No Content
        
        print("  ✅ API routes configured")
        print("  • GET /health - Health check endpoint")
        print("  • POST /token - Authentication endpoint")
        print("  • GET /users/me - Current user information")
        print("  • GET /items - List items with pagination")
        print("  • POST /items - Create a new item")
        print("  • GET /items/{item_id} - Get a specific item")
        print("  • PUT /items/{item_id} - Update an item")
        print("  • DELETE /items/{item_id} - Delete an item")
    
    # --- Pydantic Models ---
    
    class Token(BaseModel):
        """JWT token response model."""
        access_token: str
        token_type: str = "bearer"
    
    class User(BaseModel):
        """User model with basic information."""
        id: int
        username: str
        email: EmailStr
        is_active: bool = True
        
        class Config:
            from_attributes = True
    
    class UserCreate(BaseModel):
        """Model for creating a new user."""
        username: str = Field(..., min_length=3, max_length=50)
        email: EmailStr
        password: str = Field(..., min_length=8)
    
    class ItemBase(BaseModel):
        """Base item information."""
        name: str = Field(..., min_length=1, max_length=100, description="Name of the item")
        description: Optional[str] = Field(None, max_length=1000, description="Optional item description")
        price: float = Field(..., gt=0, description="Price must be greater than zero")
        tags: List[str] = Field(default_factory=list, description="List of item tags")
    
    class ItemCreate(ItemBase):
        """Model for creating a new item."""
        pass
    
    class Item(ItemBase):
        """Model for item responses."""
        id: int
        owner_id: int
        created_at: datetime
        
        class Config:
            from_attributes = True
    
    # --- Authentication methods ---
    
    def _authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.
        
        In a real application, this would check against a database.
        For this demo, we use a hardcoded user.
        """
        # Mock database lookup - in a real app, this would query a database
        if username == "testuser" and password == "password":
            return self.User(
                id=1,
                username="testuser",
                email="test@example.com",
                is_active=True
            )
        return None
    
    def _create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token with an expiration time.
        
        Best practices shown:
        - Token expiration
        - Secure signing algorithm
        - Claims-based token content
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        # In a real app, SECRET_KEY would be loaded from an environment variable
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
        """
        Validate the access token and return the current user.
        
        Best practices shown:
        - Token validation
        - Specific error messages
        - Authentication headers in exceptions
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decode the JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            
            # In a real app, this would lookup the user in a database
            if username == "testuser":
                return self.User(
                    id=1,
                    username="testuser",
                    email="test@example.com",
                    is_active=True
                )
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
    
    # --- Demo data methods ---
    
    def _get_items(self, skip: int = 0, limit: int = 10, tag: Optional[str] = None) -> List[Item]:
        """Mock database query for items."""
        # This would query a database in a real application
        items = [
            self.Item(
                id=1,
                name="Item 1",
                description="Description for Item 1",
                price=19.99,
                tags=["electronics", "gadgets"],
                owner_id=1,
                created_at=datetime.now() - timedelta(days=5)
            ),
            self.Item(
                id=2,
                name="Item 2",
                description="Description for Item 2",
                price=29.99,
                tags=["clothing", "accessories"],
                owner_id=1,
                created_at=datetime.now() - timedelta(days=3)
            ),
            self.Item(
                id=3,
                name="Item 3",
                description="Description for Item 3",
                price=39.99,
                tags=["electronics", "accessories"],
                owner_id=1,
                created_at=datetime.now() - timedelta(days=1)
            )
        ]
        
        # Apply tag filter if specified
        if tag:
            items = [item for item in items if tag in item.tags]
        
        # Apply pagination
        return items[skip:skip+limit]
    
    def _get_item_by_id(self, item_id: int) -> Optional[Item]:
        """Mock database query for a specific item."""
        items = self._get_items(limit=100)
        for item in items:
            if item.id == item_id:
                return item
        return None
    
    def _create_item(self, item: ItemCreate, user_id: int) -> Item:
        """Mock database creation for an item."""
        # In a real app, this would insert into a database
        return self.Item(
            id=4,  # Would be generated by the database
            **item.dict(),
            owner_id=user_id,
            created_at=datetime.now()
        )
    
    def _update_item(self, item_id: int, item: ItemCreate) -> Item:
        """Mock database update for an item."""
        # In a real app, this would update a database record
        existing_item = self._get_item_by_id(item_id)
        if existing_item:
            # Update fields
            updated_item = self.Item(
                id=existing_item.id,
                **item.dict(),
                owner_id=existing_item.owner_id,
                created_at=existing_item.created_at
            )
            return updated_item
        raise HTTPException(status_code=404, detail="Item not found")
    
    def _delete_item(self, item_id: int) -> None:
        """Mock database deletion for an item."""
        # In a real app, this would delete from a database
        pass
    
    # --- Logging middleware ---
    
    def setup_logging_middleware(self):
        """
        Configure request logging middleware with structured logging.
        
        Best practices shown:
        - Structured logging for every request
        - Performance timing
        - Correlation IDs for request tracing
        - Exception capturing
        """
        print("\n📝 Setting up request logging middleware...")
        print("  • Logs every request with structured data")
        print("  • Includes timing information")
        print("  • Generates correlation IDs for request tracing")
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            """Log request details, timing, and response status."""
            # Generate a unique ID for this request
            request_id = str(uuid.uuid4())
            
            # Store in the request state for access in route handlers
            request.state.request_id = request_id
            
            # Log the start of the request using our structured logger
            self.logger.info(
                "Request started",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                client=request.client.host if request.client else None
            )
            
            # Time the request
            start_time = time.time()
            
            try:
                # Process the request
                response = await call_next(request)
                
                # Calculate processing time
                process_time = time.time() - start_time
                
                # Add timing header
                response.headers["X-Process-Time"] = str(process_time)
                
                # Log the completed request
                self.logger.info(
                    "Request completed",
                    request_id=request_id,
                    method=request.method,
                    url=str(request.url),
                    status_code=response.status_code,
                    process_time=process_time
                )
                
                return response
                
            except Exception as e:
                # Log exceptions
                process_time = time.time() - start_time
                self.logger.error(
                    "Request failed",
                    request_id=request_id,
                    method=request.method,
                    url=str(request.url),
                    error=str(e),
                    process_time=process_time,
                    exc_info=True
                )
                raise
                
        print("  ✅ Request logging middleware configured")
    
    def start_server(self, host: str = "127.0.0.1", port: int = 8000):
        """
        Start the FastAPI server for demonstration purposes.
        
        Best practices shown:
        - Configurable host and port
        - Proper uvicorn configuration
        - Graceful shutdown
        """
        print("\n🚀 Starting FastAPI server...")
        print(f"  • Host: {host}")
        print(f"  • Port: {port}")
        print("  • OpenAPI documentation will be available at /docs")
        print("  • ReDoc documentation will be available at /redoc")
        print("\n  Press Ctrl+C to stop the server")
        
        # Set up the logging middleware before starting
        self.setup_logging_middleware()
        
        # In a real application, this would use a proper production server setup
        uvicorn.run(self.app, host=host, port=port)
    
    def run_demo(self):
        """
        Run a demo showcasing various FastAPI features.
        
        This method demonstrates:
        - API structure and organization
        - Authentication flow
        - Request/response cycle
        - Error handling
        """
        print("\n" + "=" * 80)
        print("🎮 FASTAPI INTERACTIVE DEMO")
        print("=" * 80)
        print("\nThis demo will guide you through the key features of FastAPI")
        print("and showcase best practices for building robust APIs.")
        
        print("\n📋 FEATURES OVERVIEW:")
        print("  • Automatic OpenAPI documentation")
        print("  • Pydantic model validation")
        print("  • Dependency injection system")
        print("  • JWT authentication")
        print("  • Type hints throughout")
        print("  • Automatic serialization/deserialization")
        
        print("\n🔄 TYPICAL API FLOWS:")
        
        print("\n1. AUTHENTICATION FLOW")
        print("   ↓ Client sends credentials to /token endpoint")
        print("   ↓ Server validates credentials and generates JWT")
        print("   ↓ Client includes JWT in Authorization header")
        print("   ↓ Server validates JWT for protected endpoints")
        
        print("\n2. RESOURCE CREATION FLOW")
        print("   ↓ Client sends authenticated POST request with data")
        print("   ↓ Server validates request data with Pydantic")
        print("   ↓ Server creates resource and returns 201 Created")
        print("   ↓ Response includes the created resource with ID")
        
        print("\n3. ERROR HANDLING FLOW")
        print("   ↓ Client sends invalid request")
        print("   ↓ Server validates and returns appropriate error")
        print("   ↓ Response includes status code and error details")
        print("   ↓ Client can use error information to fix request")
        
        print("\n🔍 To explore the full API:")
        print("  1. Start the server with .start_server()")
        print("  2. Open http://localhost:8000/docs in your browser")
        print("  3. Use the interactive documentation to test endpoints")
        print("  4. Try authenticating with username 'testuser' and password 'password'")
        
        print("\n" + "=" * 80)
        print("FastAPI makes it easy to build production-ready APIs with Python")
        print("For more information, visit: https://fastapi.tiangolo.com/")
        print("=" * 80)
        
        # Optionally start the server automatically
        start_server = input("\nStart the demo server now? (y/n): ").strip().lower()
        if start_server == 'y':
            self.start_server()


if __name__ == "__main__":
    # Create and run the demo
    demo = FastAPIBestPractices()
    demo.run_demo()