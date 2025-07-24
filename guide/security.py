#!/usr/bin/env python3
"""
Security Practices - Living Documentation

This module demonstrates Python security best practices (§0 in our guide) through
active examples and clear explanations. It shows proper techniques for handling
secrets, securing applications, and preventing common security vulnerabilities.

Key concepts demonstrated:
- Secret management with environment variables
- Configuration security with Pydantic
- Dependency scanning with safety and Trivy
- Authentication and authorization patterns
- Input sanitization
- Secure transport practices
- Static analysis with Bandit

Run this file directly to see a narrated demonstration of security best practices.
"""

import os
import sys
import json
import hashlib
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import re
import secrets
import hmac
import base64

# Try to import external libraries
try:
    from dotenv import load_dotenv
    from pydantic import BaseModel, Field, SecretStr
except ImportError:
    # Create minimal placeholder for demo purposes
    load_dotenv = lambda: None
    
    class BaseModel:
        pass
    
    def Field(*args, **kwargs):
        return None
    
    class SecretStr:
        def __init__(self, value):
            self._value = value
        
        def get_secret_value(self):
            return self._value


class SecurityPractices:
    """
    Security Practices
    
    This class demonstrates security best practices for Python applications
    as defined in §0 of our guide.
    """
    
    def __init__(self):
        """Initialize with security practices from §0 of our guide."""
        self.name = "Security Practices"
        
        # Set up logger
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Security concerns matrix from the guide
        self.security_concerns = {
            "Secret Management": {
                "mandate": "Never commit secrets. Load via python-dotenv in dev and Vault/Doppler/SM in prod.",
                "implementation": "Use SecretStr in Pydantic models and environment variables",
                "risk_level": "Critical"
            },
            "Configuration": {
                "mandate": "Use Settings(BaseSettings); map secret env vars (DB_URL, JWT_KEY).",
                "implementation": "Pydantic Settings with SecretStr fields",
                "risk_level": "High"
            },
            "Dependency Scanning": {
                "mandate": "CI runs trivy fs . --exit-code 1 and uv pip audit.",
                "implementation": "Regular dependency scanning and updates",
                "risk_level": "High"
            },
            "Auth & AuthZ": {
                "mandate": "FastAPI routes use OAuth2 Bearer with scopes; enforce with Depends(get_current_user).",
                "implementation": "JWT-based authentication with scoped permissions",
                "risk_level": "Critical"
            },
            "Input Sanitization": {
                "mandate": "Pydantic validates all inbound data; never eval() untrusted strings.",
                "implementation": "Input validation at system boundaries",
                "risk_level": "Critical"
            },
            "HTTPS Everywhere": {
                "mandate": "Traefik or Cloud LB terminates TLS; internal networks may allow mTLS.",
                "implementation": "TLS for all external communications",
                "risk_level": "High"
            },
            "Security Headers": {
                "mandate": "Add X-Content-Type-Options: nosniff, X-Frame-Options: DENY through Traefik middleware.",
                "implementation": "Security headers in all responses",
                "risk_level": "Medium"
            },
            "Transport Encryption": {
                "mandate": "Databases use TLS (sslmode=require), Redis with --tls.",
                "implementation": "Encrypted communication with databases",
                "risk_level": "High"
            },
            "Static Analysis": {
                "mandate": "Enable Bandit in pre-commit (bandit -ll -r src).",
                "implementation": "Regular security-focused code scanning",
                "risk_level": "Medium"
            }
        }
    
    def demonstrate_secret_management(self):
        """
        Demonstrate proper secret management using environment variables.
        
        This method shows how to handle secrets securely in Python applications.
        """
        print("\n" + "=" * 80)
        print("🔒 SECRET MANAGEMENT")
        print("=" * 80)
        print("✨ Following §0: 'Never commit secrets. Load via python-dotenv in dev and Vault/Doppler/SM in prod.'")
        
        # Create a .env.sample file
        env_sample_content = """
# Sample .env file - NEVER commit the actual .env file with real values
# Copy this file to .env and fill in your values

# Database credentials
DB_HOST=localhost
DB_NAME=mydatabase
DB_USER=dbuser
DB_PASSWORD=  # Add your password here

# API credentials
API_KEY=  # Add your API key here
STRIPE_SECRET_KEY=  # Add your Stripe key here

# JWT settings
JWT_SECRET_KEY=  # Add a strong random key here
JWT_ALGORITHM=HS256
"""
        env_sample_path = Path(".env.sample")
        with open(env_sample_path, "w") as f:
            f.write(env_sample_content)
        
        print(f"\n📄 Created .env.sample template at {env_sample_path}")
        print("  • This template shows required environment variables WITHOUT actual values")
        print("  • Real values should only exist in the .env file which is .gitignored")
        
        # ANTI-PATTERN: Hard-coded secrets
        print("\n❌ ANTI-PATTERN: Hard-coded secrets in source code")
        bad_example = """
# DO NOT DO THIS!
DATABASE_URL = "postgresql://admin:SuperSecret123!@db.example.com/app"
API_KEY = "sk_live_a1b2c3d4e5f6g7h8i9j0"
JWT_SECRET = "my-super-secret-jwt-key-that-no-one-will-guess"

def connect_to_db():
    # Using hard-coded credentials directly in source code
    connection = psycopg2.connect(DATABASE_URL)
    return connection

def make_api_request(endpoint):
    # Embedding API key directly in the code
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return requests.get(f"https://api.example.com/{endpoint}", headers=headers)
"""
        print(bad_example)
        
        # BETTER PATTERN: Using environment variables
        print("\n✅ BETTER PATTERN: Loading secrets from environment variables")
        good_example = """
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get secrets from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

def connect_to_db():
    # Using environment variables
    if not DATABASE_URL:
        raise EnvironmentError("DATABASE_URL environment variable is not set")
    connection = psycopg2.connect(DATABASE_URL)
    return connection

def make_api_request(endpoint):
    # Using environment variables
    if not API_KEY:
        raise EnvironmentError("API_KEY environment variable is not set")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return requests.get(f"https://api.example.com/{endpoint}", headers=headers)
"""
        print(good_example)
        
        # BEST PATTERN: Using Pydantic with SecretStr
        print("\n✅✅ BEST PATTERN: Pydantic Settings with SecretStr")
        best_example = """
from pydantic import BaseSettings, SecretStr, PostgresDsn

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: PostgresDsn
    
    # API credentials
    API_KEY: SecretStr
    
    # JWT settings
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

def connect_to_db():
    # Using settings with validation
    connection = psycopg2.connect(str(settings.DATABASE_URL))
    return connection

def make_api_request(endpoint):
    # SecretStr prevents accidental logging of the secret
    api_key = settings.API_KEY.get_secret_value()
    headers = {"Authorization": f"Bearer {api_key}"}
    return requests.get(f"https://api.example.com/{endpoint}", headers=headers)
"""
        print(best_example)
        
        # Create gitignore entry
        gitignore_content = """
# Security-related files
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
credentials/
"""
        gitignore_path = Path(".gitignore-security")
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)
        
        print(f"\n📄 Created .gitignore-security template at {gitignore_path}")
        print("  • Make sure these patterns are in your project's .gitignore")
        
        print("\n📝 Secret Management Best Practices:")
        print("  • NEVER commit secrets to version control")
        print("  • Use environment variables for configuration")
        print("  • Load variables from .env file in development")
        print("  • Use a secret manager (AWS Secrets Manager, HashiCorp Vault, etc.) in production")
        print("  • Use Pydantic's SecretStr type to prevent accidental exposure in logs")
        print("  • Include basic secrets validation (not empty, proper format, etc.)")
        print("  • Create a .env.sample file with the structure but not actual values")
        print("  • Add .env to .gitignore")
    
    def demonstrate_security_headers(self):
        """
        Demonstrate security headers for web applications.
        
        This method explains important security headers and how to implement them.
        """
        print("\n" + "=" * 80)
        print("🛡️ SECURITY HEADERS")
        print("=" * 80)
        print("✨ Following §0: 'Add X-Content-Type-Options: nosniff, X-Frame-Options: DENY through Traefik middleware'")
        
        # Security headers table
        security_headers = [
            {
                "header": "X-Content-Type-Options",
                "value": "nosniff",
                "purpose": "Prevents MIME type sniffing, ensuring browsers respect declared content types"
            },
            {
                "header": "X-Frame-Options",
                "value": "DENY",
                "purpose": "Prevents your site from being embedded in frames, protecting against clickjacking"
            },
            {
                "header": "Content-Security-Policy",
                "value": "default-src 'self'",
                "purpose": "Restricts sources of content, preventing XSS and data injection attacks"
            },
            {
                "header": "Strict-Transport-Security",
                "value": "max-age=31536000; includeSubDomains",
                "purpose": "Enforces HTTPS connections, preventing downgrade attacks"
            },
            {
                "header": "X-XSS-Protection",
                "value": "1; mode=block",
                "purpose": "Enables browser's built-in XSS filters"
            },
            {
                "header": "Referrer-Policy",
                "value": "strict-origin-when-cross-origin",
                "purpose": "Controls information in the Referer header to protect user privacy"
            }
        ]
        
        print("\n📋 Essential Security Headers:")
        for header in security_headers:
            print(f"  • {header['header']}: {header['value']}")
            print(f"    Purpose: {header['purpose']}")
        
        # FastAPI implementation example
        print("\n📄 FastAPI Implementation:")
        fastapi_example = """
from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

app = FastAPI()

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["api.example.com", "*.example.com"]
)

# Add CORS middleware with restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com", "https://www.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
"""
        print(fastapi_example)
        
        # Traefik implementation example
        print("\n📄 Traefik Implementation:")
        traefik_example = """
# docker-compose.yml or compose.yml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--providers.file.directory=/etc/traefik/dynamic"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik:/etc/traefik/dynamic
    ports:
      - "80:80"
      - "443:443"

# traefik/security-headers.yml
http:
  middlewares:
    security-headers:
      headers:
        customResponseHeaders:
          X-Content-Type-Options: "nosniff"
          X-Frame-Options: "DENY"
          Content-Security-Policy: "default-src 'self'"
          Strict-Transport-Security: "max-age=31536000; includeSubDomains"
          X-XSS-Protection: "1; mode=block"
          Referrer-Policy: "strict-origin-when-cross-origin"

# Apply the middleware to your services
  routers:
    myapp:
      rule: "Host(`app.example.com`)"
      middlewares:
        - "security-headers"
      service: "myapp"
"""
        print(traefik_example)
        
        print("\n📝 Security Headers Best Practices:")
        print("  • Always include essential security headers in all responses")
        print("  • Use middleware to ensure consistent application across all endpoints")
        print("  • Set appropriate Content Security Policy to restrict content sources")
        print("  • Force HTTPS with Strict-Transport-Security")
        print("  • Regularly test your security headers with online tools like securityheaders.com")
        print("  • Consider using a web application firewall (WAF) for additional protection")
    
    def demonstrate_auth_patterns(self):
        """
        Demonstrate authentication and authorization patterns.
        
        This method explains secure authentication patterns for web applications.
        """
        print("\n" + "=" * 80)
        print("🔐 AUTHENTICATION & AUTHORIZATION")
        print("=" * 80)
        print("✨ Following §0: 'FastAPI routes use OAuth2 Bearer with scopes; enforce with Depends(get_current_user)'")
        
        # JWT token generation with proper security
        print("\n📄 Secure JWT Implementation:")
        jwt_example = """
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, SecretStr

# Security models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class User(BaseModel):
    username: str
    email: str
    disabled: bool = False
    scopes: List[str] = []

class UserInDB(User):
    hashed_password: str

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "users:read": "Read user information",
        "users:write": "Create or modify users",
        "admin": "Admin actions"
    }
)

# Settings class for secrets
class Settings(BaseModel):
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

# Verify password helper
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create access token with proper security
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add expiration to payload
    to_encode.update({"exp": expire})
    
    # Create token with secure algorithm
    secret_key = settings.SECRET_KEY.get_secret_value()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

# Dependency for getting the current user
async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and verify token
        secret_key = settings.SECRET_KEY.get_secret_value()
        payload = jwt.decode(
            token, 
            secret_key, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user data from token
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception
        
    # Get user from database
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
        
    return user

# Check required scopes
def require_scopes(required_scopes: List[str]):
    async def scope_validator(user: User = Depends(get_current_user)):
        for scope in required_scopes:
            if scope not in user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required scope: {scope}",
                )
        return user
    return scope_validator

# API route that requires authentication and specific scope
@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(require_scopes(["users:read"]))
):
    return current_user

# API route that requires admin scope
@app.post("/users", response_model=User)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_scopes(["admin"]))
):
    # Admin-only operation
    return create_new_user(user_data)
"""
        print(jwt_example)
        
        # Password hashing
        print("\n📄 Secure Password Handling:")
        password_example = """
from passlib.context import CryptContext

# Create password context with strong hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

# Usage example
def register_user(username: str, password: str):
    # Hash the password before storing
    hashed_password = hash_password(password)
    
    # Store in database
    db.execute(
        "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
        (username, hashed_password)
    )
    
def authenticate_user(username: str, password: str) -> bool:
    # Get user from database
    user = db.execute(
        "SELECT username, hashed_password FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    
    if not user:
        return False
        
    # Verify password using constant-time comparison
    if not verify_password(password, user["hashed_password"]):
        return False
        
    return True
"""
        print(password_example)
        
        print("\n📝 Authentication & Authorization Best Practices:")
        print("  • Use secure password hashing with bcrypt or Argon2")
        print("  • Implement JWT tokens with proper expiration and secure algorithms")
        print("  • Apply the principle of least privilege with scopes/roles")
        print("  • Enforce scope validation for sensitive operations")
        print("  • Use constant-time comparison for password verification")
        print("  • Include JTI (JWT ID) for token revocation capability")
        print("  • Implement refresh token rotation for long-lived sessions")
        print("  • Store sensitive settings like SECRET_KEY in environment variables")
        print("  • Return appropriate 401/403 status codes for auth failures")
    
    def demonstrate_input_sanitization(self):
        """
        Demonstrate input sanitization and validation.
        
        This method shows how to properly validate and sanitize user input.
        """
        print("\n" + "=" * 80)
        print("🧹 INPUT SANITIZATION")
        print("=" * 80)
        print("✨ Following §0: 'Pydantic validates all inbound data; never eval() untrusted strings'")
        
        # BAD EXAMPLE: Unsafe input handling
        print("\n❌ ANTI-PATTERN: Unsafe input handling with eval()")
        bad_example = """
def calculate(expression):
    # EXTREMELY DANGEROUS! Never do this with user input
    return eval(expression)  # Allows arbitrary code execution

def search_users(query):
    # SQL Injection vulnerability
    sql = f"SELECT * FROM users WHERE username LIKE '%{query}%'"
    return db.execute(sql)

def render_user_content(html_content):
    # Cross-site scripting vulnerability
    return f"<div>{html_content}</div>"
"""
        print(bad_example)
        
        # GOOD EXAMPLE: Safe input handling
        print("\n✅ BETTER PATTERN: Safe input handling")
        good_example = """
import ast
import re
from markupsafe import escape
from typing import List, Optional
from pydantic import BaseModel, Field, validator

class MathExpression(BaseModel):
    expression: str
    
    @validator("expression")
    def validate_math_expression(cls, v):
        # Only allow safe math operations
        allowed_chars = set("0123456789+-*/() .")
        if not all(c in allowed_chars for c in v):
            raise ValueError("Expression contains forbidden characters")
        return v

def calculate_safe(expr_model: MathExpression):
    # Use safe evaluation with ast.literal_eval for simple math
    # or a proper math parser like sympy
    expr = expr_model.expression.replace(" ", "")
    
    # Simple case for demonstration:
    # Convert to abstract syntax tree and check for safe operations
    try:
        node = ast.parse(expr, mode='eval')
        
        # Check if the AST contains only safe operations
        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Call):
                raise ValueError("Function calls are not allowed")
        
        # Use a safer alternative to eval
        return eval(compile(node, '<string>', 'eval'))
    except (SyntaxError, ValueError) as e:
        raise ValueError(f"Invalid expression: {e}")

class UserQuery(BaseModel):
    username_filter: Optional[str] = None
    
    @validator("username_filter")
    def sanitize_username_filter(cls, v):
        if v is None:
            return v
        # Remove any special SQL characters
        return re.sub(r'[\\;\'"/]', '', v)

def search_users_safe(query: UserQuery):
    # Use parameterized queries to prevent SQL injection
    sql = "SELECT * FROM users WHERE 1=1"
    params = []
    
    if query.username_filter:
        sql += " AND username LIKE ?"
        params.append(f"%{query.username_filter}%")
    
    return db.execute(sql, params)

class UserContent(BaseModel):
    html_content: str

def render_user_content_safe(content: UserContent):
    # Escape HTML to prevent XSS
    safe_content = escape(content.html_content)
    return f"<div>{safe_content}</div>"
"""
        print(good_example)
        
        # BEST EXAMPLE: Comprehensive validation with Pydantic
        print("\n✅✅ BEST PATTERN: Comprehensive validation with Pydantic")
        best_example = """
from pydantic import BaseModel, Field, validator, EmailStr, HttpUrl
from typing import List, Optional
import re
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.VIEWER
    website: Optional[HttpUrl] = None
    
    @validator("password")
    def password_strength(cls, v):
        # Check password strength
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    model_config = {
        "extra": "forbid",  # Reject extra fields
        "json_schema_extra": {
            "examples": [
                {
                    "username": "johndoe",
                    "email": "john@example.com",
                    "password": "SecurePass123!",
                    "full_name": "John Doe",
                    "role": "viewer"
                }
            ]
        }
    }

# API route with validated input
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    # All input is now validated:
    # - username has correct length and characters
    # - email is a valid email format
    # - password meets complexity requirements
    # - role is one of the allowed values
    # - website is a valid URL if provided
    # - no unexpected fields are included
    
    # Safe to use the data
    db_user = create_user_in_db(user)
    return db_user
"""
        print(best_example)
        
        print("\n📝 Input Sanitization Best Practices:")
        print("  • Validate all user input at system boundaries using Pydantic or similar")
        print("  • NEVER use eval() or exec() with user-supplied data")
        print("  • Use parameterized queries for all database operations")
        print("  • Escape output to prevent cross-site scripting (XSS)")
        print("  • Apply proper Content Security Policy headers")
        print("  • Validate both data type AND content (e.g., regex patterns)")
        print("  • Set appropriate constraints (min/max length, allowed values)")
        print("  • Reject unexpected fields with extra='forbid'")
    
    def demonstrate_dependency_scanning(self):
        """
        Demonstrate dependency scanning and vulnerability management.
        
        This method shows how to keep dependencies secure.
        """
        print("\n" + "=" * 80)
        print("🔍 DEPENDENCY SCANNING")
        print("=" * 80)
        print("✨ Following §0: 'CI runs trivy fs . --exit-code 1 and uv pip audit'")
        
        # Create a requirements file for demonstration
        req_content = """
# Example requirements.txt with pinned versions
fastapi==0.100.0
pydantic==2.1.1
uvicorn==0.22.0
sqlalchemy==2.0.15
psycopg2-binary==2.9.6
python-jose==3.3.0
passlib==1.7.4
"""
        req_path = Path("requirements-secure.txt")
        with open(req_path, "w") as f:
            f.write(req_content)
        
        print(f"\n📄 Created requirements file at {req_path}")
        
        # Check if safety is installed
        try:
            result = subprocess.run(["uv", "pip", "audit", "--help"], capture_output=True, text=True)
            has_uv_audit = result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            has_uv_audit = False
        
        # GitHub Actions workflow
        print("\n📄 GitHub Actions Workflow for Dependency Scanning:")
        github_actions = """
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run weekly to catch new vulnerabilities
    - cron: '0 2 * * 1'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip uv
          uv pip install -r requirements.txt
      
      - name: Run uv pip audit
        run: |
          uv pip audit
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          security-checks: 'vuln,secret,config'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
          ignore-unfixed: true
"""
        print(github_actions)
        
        # Local pre-commit hook
        print("\n📄 Pre-commit Hook for Dependency Scanning:")
        pre_commit = """
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.272
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/Lucas-C/pre-commit-hooks-bandit
    rev: v1.0.6
    hooks:
      - id: python-bandit-vulnerability-check
        args: ['-r', 'src', '-ll']

  - repo: local
    hooks:
      - id: uv-pip-audit
        name: uv-pip-audit
        entry: uv pip audit
        language: system
        pass_filenames: false
        always_run: true
"""
        print(pre_commit)
        
        # Show examples of how to run tools if installed
        if has_uv_audit:
            print("\n🔍 Running uv pip audit:")
            result = subprocess.run(["uv", "pip", "audit"], capture_output=True, text=True)
            print(result.stdout)
        else:
            print("\n📝 To run dependency scanning locally:")
            print("  • Install uv: pip install uv")
            print("  • Run: uv pip audit")
        
        print("\n📝 Dependency Scanning Best Practices:")
        print("  • Pin all dependency versions in requirements.txt")
        print("  • Use uv pip audit to check for known vulnerabilities")
        print("  • Set up automated scanning in CI/CD pipelines")
        print("  • Schedule regular scans to catch new vulnerabilities")
        print("  • Update dependencies promptly when vulnerabilities are found")
        print("  • Use pre-commit hooks for local dependency scanning")
        print("  • Consider Dependabot or similar services for automated updates")
    
    def demonstrate_bandit(self):
        """
        Demonstrate static analysis with Bandit.
        
        This method shows how to use Bandit to find security issues in code.
        """
        print("\n" + "=" * 80)
        print("🔎 STATIC ANALYSIS WITH BANDIT")
        print("=" * 80)
        print("✨ Following §0: 'Enable Bandit in pre-commit (bandit -ll -r src)'")
        
        # Create a Python file with security issues
        bad_code = """#!/usr/bin/env python3
import pickle
import yaml
import subprocess
import tempfile
import os

def insecure_function(user_input):
    # B102: exec() used with variable input
    exec(user_input)  # Insecure!
    
    # B201: Use of flask_accept_large_json without size limit
    app.config['MAX_CONTENT_LENGTH'] = None
    
    # B301: pickle deserialization (can lead to RCE)
    data = pickle.loads(user_input)  # Insecure!
    
    # B506: Use of unsafe yaml load
    config = yaml.load(user_input)  # Insecure!
    
    # B602: subprocess with shell=True
    subprocess.call(f"ls {user_input}", shell=True)  # Insecure!
    
    # B108: Hardcoded temp file
    temp = open('/tmp/file.txt', 'w')
    
    # B105: Hardcoded password
    password = "SuperSecret123"
    
    # B110: try-except-pass pattern
    try:
        do_something()
    except Exception:
        pass  # Security issue might be hidden
"""
        bad_code_path = Path("insecure_code.py")
        with open(bad_code_path, "w") as f:
            f.write(bad_code)
        
        print(f"\n📄 Created code with security issues at {bad_code_path}")
        
        # Check if bandit is installed
        try:
            result = subprocess.run(["bandit", "--help"], capture_output=True, text=True)
            has_bandit = result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            has_bandit = False
        
        # Run bandit if installed
        if has_bandit:
            print("\n🔍 Running Bandit analysis:")
            result = subprocess.run(["bandit", "-r", str(bad_code_path)], capture_output=True, text=True)
            print(result.stdout)
        else:
            print("\n📝 To run Bandit static analysis:")
            print("  • Install bandit: pip install bandit")
            print("  • Run: bandit -r your_code_directory")
        
        # Create a fixed version
        good_code = """#!/usr/bin/env python3
import json
import yaml
import subprocess
import tempfile
import os
from ast import literal_eval

def secure_function(user_input):
    # Instead of exec(), use a safer approach
    # like a command pattern or specific allowed functions
    allowed_commands = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y
    }
    command, *args = user_input.split()
    if command in allowed_commands:
        result = allowed_commands[command](*map(int, args))
    
    # Set a reasonable size limit
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB
    
    # Use json instead of pickle for serialization
    data = json.loads(user_input)
    
    # Use safe_load for YAML
    config = yaml.safe_load(user_input)
    
    # Use list arguments instead of shell=True
    subprocess.call(["ls", user_input], shell=False)
    
    # Use tempfile for secure temporary files
    with tempfile.NamedTemporaryFile(mode='w') as temp:
        temp.write('data')
    
    # Use environment variables or a secure vault for sensitive data
    password = os.environ.get('APP_PASSWORD')
    
    # Properly handle exceptions
    try:
        do_something()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
"""
        good_code_path = Path("secure_code.py")
        with open(good_code_path, "w") as f:
            f.write(good_code)
        
        print(f"\n📄 Created fixed code at {good_code_path}")
        
        # Run bandit on the fixed code if installed
        if has_bandit:
            print("\n🔍 Running Bandit analysis on fixed code:")
            result = subprocess.run(["bandit", "-r", str(good_code_path)], capture_output=True, text=True)
            print(result.stdout)
        
        print("\n📝 Bandit Static Analysis Best Practices:")
        print("  • Run bandit as part of your CI/CD pipeline")
        print("  • Add bandit to pre-commit hooks")
        print("  • Set appropriate severity levels (Low/Medium/High)")
        print("  • Review and fix all high-severity issues")
        print("  • Document any false positives with inline comments")
        print("  • Use a .bandit configuration file for project-specific settings")
        print("  • Combine with other static analysis tools (mypy, ruff)")
    
    def run_demo(self):
        """Run a comprehensive demonstration of security best practices."""
        print("\n" + "=" * 80)
        print("🚀 SECURITY PRACTICES DEMONSTRATION")
        print(f"✨ Demonstrating §0 of the Python Development Best Practices")
        print("=" * 80)
        
        print("\n📋 This demonstration will show you:")
        print("  1. Secret Management")
        print("  2. Security Headers")
        print("  3. Authentication & Authorization")
        print("  4. Input Sanitization")
        print("  5. Dependency Scanning")
        print("  6. Static Analysis with Bandit")
        
        # Demonstrate each component
        self.demonstrate_secret_management()
        self.demonstrate_security_headers()
        self.demonstrate_auth_patterns()
        self.demonstrate_input_sanitization()
        self.demonstrate_dependency_scanning()
        self.demonstrate_bandit()
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        
        print("\n🛡️ Security is a continuous process, not a one-time task.")
        print("Remember the golden rule from §0:")
        print("  If you touch credentials, crypto, or user data, open a SECURITY.md threat-model PR.")
        
        print("\nRecommended next steps:")
        print("  1. Conduct a security audit of your current codebase")
        print("  2. Implement proper secret management")
        print("  3. Add dependency scanning to your CI/CD pipeline")
        print("  4. Use static analysis tools to identify security issues")
        print("  5. Apply the principle of least privilege")
        print("  6. Create a security.md file with a threat model")
    
    def generate_markdown(self) -> str:
        """
        Generate markdown documentation for the Security Practices section
        of our best practices guide.
        """
        return """
## Security Practices

| Concern | Mandate |
| ------- | ------- |
| **Secret Management** | *Never* commit secrets. Load via **python-dotenv** in *dev* and Vault/Doppler/SM in *prod*. |
| **Configuration** | Use `Settings(BaseSettings)`; map secret env vars (`DB_URL`, `JWT_KEY`). |
| **Dependency Scanning** | CI runs **trivy fs . --exit-code 1** and `uv pip audit`. |
| **Auth & AuthZ** | FastAPI routes use **OAuth2 Bearer** with scopes; enforce with `Depends(get_current_user)`. See §9. |
| **Input Sanitization** | Pydantic validates all inbound data; never `eval()` untrusted strings. |
| **HTTPS Everywhere** | Traefik or Cloud LB terminates TLS; internal networks may allow mTLS. |
| **Security Headers** | Add `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` through Traefik middleware. |
| **Transport Encryption** | Databases use TLS (`sslmode=require`), Redis with `--tls`. |
| **Static Analysis** | Enable **Bandit** in pre-commit (`bandit -ll -r src`). |

**Example: Loading environment variables**
```python
from dotenv import load_dotenv; load_dotenv()
```

> **Golden Rule:** If you touch credentials, crypto, or user data, open a **SECURITY.md** threat-model PR.
"""
    
    def __str__(self):
        """String representation"""
        return f"{self.name}: Critical practices for secure Python applications"


# Run the demo if this file is executed directly
if __name__ == "__main__":
    security = SecurityPractices()
    security.run_demo()