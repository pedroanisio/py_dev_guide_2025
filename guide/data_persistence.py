#!/usr/bin/env python3
"""
Data Persistence & Storage - Living Documentation

This module demonstrates data persistence best practices (§11 in our guide) through
active examples and clear explanations. It shows proper database usage patterns,
migrations, connection pooling, and various storage options.

Key concepts demonstrated:
- Database choice and selection criteria
- Connection management and pooling
- Migration strategies
- ORM patterns and best practices
- Vector databases for AI applications
- Polyglot persistence in microservices

Run this file directly to see a narrated demonstration of data persistence best practices.
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
import contextlib
import threading
from enum import Enum
import random
import inspect

# Try importing database libraries for demonstration
try:
    import sqlalchemy
    from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    # Create mock classes for SQLAlchemy
    class sqlalchemy:
        @staticmethod
        def create_engine(*args, **kwargs):
            return MockEngine()
    
    class Column:
        def __init__(self, *args, **kwargs):
            pass
    
    Integer = String = Boolean = ForeignKey = DateTime = object()
    
    def declarative_base():
        return type('Base', (), {})
    
    def sessionmaker(*args, **kwargs):
        return lambda: MockSession()
    
    def relationship(*args, **kwargs):
        return lambda: None
    
    class MockEngine:
        def connect(self):
            return self
        
        def close(self):
            pass
        
        def execute(self, *args, **kwargs):
            return []
    
    class MockSession:
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def close(self):
            pass
        
        def commit(self):
            pass
        
        def rollback(self):
            pass
        
        def query(self, *args, **kwargs):
            return self
        
        def filter(self, *args, **kwargs):
            return self
        
        def all(self):
            return []
        
        def first(self):
            return None
        
        def one_or_none(self):
            return None

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False


@dataclass
class DatabaseEngine:
    """
    Represents a database engine with its characteristics and use cases.
    """
    name: str
    version: str
    use_cases: List[str]
    async_driver: str
    migration_tool: str
    image_tag: str


class DatabaseType(Enum):
    """Types of databases by data model"""
    RELATIONAL = "Relational (SQL)"
    DOCUMENT = "Document (NoSQL)"
    GRAPH = "Graph"
    KEY_VALUE = "Key-Value"
    SEARCH = "Search Engine"
    VECTOR = "Vector Database"
    TIME_SERIES = "Time Series"


class DataPersistenceAndStorage:
    """
    Data Persistence & Storage
    
    This class demonstrates best practices for database management and data persistence
    as defined in §11 of our guide.
    """
    
    def __init__(self):
        """Initialize with data persistence practices from §11 of our guide."""
        self.name = "Data Persistence & Storage"
        
        # Set up logger
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Database engines from §11.2
        self.database_engines = [
            DatabaseEngine(
                name="PostgreSQL",
                version="16",
                use_cases=["OLTP", "JSONB", "analytical queries", "extensions (PostGIS, TimescaleDB)"],
                async_driver="asyncpg, psycopg[pool]",
                migration_tool="Alembic",
                image_tag="postgres:16.2-alpine"
            ),
            DatabaseEngine(
                name="SQLite",
                version="3.45",
                use_cases=["Simple CLI apps", "embedded tests", "edge devices"],
                async_driver="aiosqlite",
                migration_tool="sqlite-utils, Alembic (offline)",
                image_tag="Bundled"
            ),
            DatabaseEngine(
                name="MongoDB",
                version="7",
                use_cases=["High-write schemaless docs", "rapid prototyping"],
                async_driver="motor",
                migration_tool="Mongo-Migrate / Mongock",
                image_tag="mongodb/mongodb-community-server:7.0-ubi8"
            ),
            DatabaseEngine(
                name="Neo4j",
                version="5",
                use_cases=["Deep graph traversals", "recommendation", "fraud detection"],
                async_driver="neo4j-driver (asyncio mode)",
                migration_tool="Liquibase-Neo4j",
                image_tag="neo4j:5.20"
            ),
            DatabaseEngine(
                name="Elasticsearch",
                version="8",
                use_cases=["Full-text search", "log analytics", "observability"],
                async_driver="elasticsearch[async]",
                migration_tool="Index template JSONs + ILM",
                image_tag="elastic/elasticsearch:8.13.0"
            ),
            DatabaseEngine(
                name="Chroma",
                version="0.4",
                use_cases=["Lightweight local vector DB (in-proc / server) for semantic RAG"],
                async_driver="chromadb",
                migration_tool="n/a (implicit collections)",
                image_tag="ghcr.io/chroma-core/chroma:0.4.24"
            ),
            DatabaseEngine(
                name="Qdrant",
                version="1.9",
                use_cases=["Production vector search", "HNSW", "filtering"],
                async_driver="qdrant-client[async]",
                migration_tool="Collection schema JSON",
                image_tag="qdrant/qdrant:v1.9.0"
            )
        ]
    
    def demonstrate_database_selection(self):
        """
        Demonstrate database selection criteria.
        
        This method explains how to choose the right database for different use cases.
        """
        print("\n" + "=" * 80)
        print("📊 DATABASE SELECTION CRITERIA")
        print("=" * 80)
        print("✨ Following §11.2: 'Database Matrix'")
        
        # Display database matrix from the guide
        print("\n📋 Database Selection Matrix:")
        print("\n{:<12} {:<10} {:<50} {:<20} {:<25} {:<30}".format(
            "Engine", "Version", "Use-Case Sweet Spot", "Async Driver", "Migration Tool", "Recommended Image Tag"
        ))
        print("-" * 150)
        
        for engine in self.database_engines:
            use_cases = ", ".join(engine.use_cases)
            if len(use_cases) > 50:
                use_cases = use_cases[:47] + "..."
            
            print("{:<12} {:<10} {:<50} {:<20} {:<25} {:<30}".format(
                engine.name, engine.version, use_cases, engine.async_driver.split(",")[0], 
                engine.migration_tool.split(",")[0], engine.image_tag
            ))
        
        # Decision tree for database selection
        print("\n🌳 Database Selection Decision Tree:")
        print("""
1. Do you need full SQL query capabilities?
   ├── YES: Consider SQL databases
   │   ├── Need scalability: PostgreSQL
   │   ├── Need embedded: SQLite
   │   └── Need time-series: TimescaleDB (PostgreSQL extension)
   └── NO: Consider specialized databases
       ├── Need document flexibility: MongoDB
       ├── Need graph relationships: Neo4j
       ├── Need full-text search: Elasticsearch
       ├── Need vector search: Qdrant or Chroma
       └── Need pure key-value: Redis

2. What's your primary access pattern?
   ├── Complex queries with joins: PostgreSQL
   ├── Document-oriented access: MongoDB
   ├── Graph traversals: Neo4j
   ├── Text search: Elasticsearch
   ├── Vector similarity: Qdrant/Chroma
   └── Simple key lookups: Redis

3. Scale considerations:
   ├── Small-to-medium: Any of the above
   ├── Large (TB+): Consider cloud-managed versions
   └── Edge/embedded: SQLite
""")
        
        # Postgres + pgvector tip
        print("\n💡 TIP: For combined relational + vector search, use PostgreSQL with pgvector extension.")
        print("This is perfect for applications that need both structured data and similarity search.")
        
        print("\n📝 Key Database Selection Principles:")
        print("  • Choose based on data access patterns, not just popularity")
        print("  • Consider operational complexity (managed vs. self-hosted)")
        print("  • Evaluate scaling requirements (vertical vs. horizontal)")
        print("  • Think about query flexibility needs")
        print("  • Consider developer familiarity and ecosystem support")
    
    def demonstrate_connection_pooling(self):
        """
        Demonstrate connection pooling best practices.
        
        This method shows how to properly manage database connections.
        """
        print("\n" + "=" * 80)
        print("🔄 CONNECTION POOLING & MANAGEMENT")
        print("=" * 80)
        print("✨ Following §11.3: 'Connection Pooling'")
        
        # Connection pooling with SQLAlchemy
        print("\n📄 SQLAlchemy Connection Pool:")
        sqlalchemy_pool = """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment (following §0 Security practices)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")

# Create engine with connection pooling (§11.3)
engine = create_engine(
    DATABASE_URL,
    # Pool size recommendation from §11.3: min(32, CPU×2)
    pool_size=10,  # Adjust based on CPU cores
    max_overflow=20,  # Allow additional connections under load
    pool_timeout=30,  # Wait up to 30 seconds for connection
    pool_recycle=1800,  # Recycle connections every 30 minutes
    echo=False  # Set to True for query logging (development only)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
        print(sqlalchemy_pool)
        
        # Connection pooling with asyncpg
        print("\n📄 Async Connection Pool with asyncpg:")
        asyncpg_pool = """
import asyncpg
import asyncio
import os
from contextlib import asynccontextmanager

# Get database URL from environment (following §0 Security practices)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost/app")

# Global pool variable
pool = None

async def create_pool():
    global pool
    # Create connection pool, following §11.3 recommendations
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,  # Minimum connections in pool
        max_size=10,  # Maximum connections in pool (adjust based on CPU cores)
        command_timeout=60.0,  # Command timeout in seconds
        max_inactive_connection_lifetime=1800.0,  # 30 minutes
        ssl="require"  # Force SSL for security (§0 Transport Encryption)
    )
    return pool

@asynccontextmanager
async def get_connection():
    global pool
    if pool is None:
        pool = await create_pool()
    
    # Acquire connection from pool
    async with pool.acquire() as connection:
        yield connection

# Application startup (integrate with FastAPI lifespan)
async def startup():
    await create_pool()

# Application shutdown
async def shutdown():
    global pool
    if pool:
        await pool.close()
"""
        print(asyncpg_pool)
        
        # Practical example
        print("\n📄 Complete FastAPI Example with Connection Pool:")
        fastapi_example = """
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncpg
import os

app = FastAPI()

# Setup connection pool on startup, close on shutdown
@app.on_event("startup")
async def startup():
    await create_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_pool()

# Dependency for database access
async def get_db_connection():
    async with get_connection() as conn:
        yield conn

@app.get("/users/{user_id}")
async def get_user(user_id: int, conn = Depends(get_db_connection)):
    # Use connection from pool
    user = await conn.fetchrow(
        "SELECT id, username, email FROM users WHERE id = $1",
        user_id
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return dict(user)
"""
        print(fastapi_example)
        
        print("\n📝 Connection Pooling Best Practices:")
        print("  • Size pool based on CPU cores: min(32, CPU×2)")
        print("  • Set sensible timeouts and max_overflow")
        print("  • Recycle connections periodically to prevent stale connections")
        print("  • Use a context manager or dependency to ensure connections return to pool")
        print("  • Monitor pool metrics in production")
        print("  • Consider PgBouncer for high-connection PostgreSQL workloads")
    
    def demonstrate_sqlalchemy_models(self):
        """
        Demonstrate SQLAlchemy ORM models.
        
        This method shows how to define and use SQLAlchemy models following best practices.
        """
        print("\n" + "=" * 80)
        print("🔄 SQLALCHEMY ORM PATTERNS")
        print("=" * 80)
        print("✨ Implementing ORM patterns for relational databases")
        
        # SQLAlchemy base models
        print("\n📄 SQLAlchemy Model Definitions:")
        sqlalchemy_models = """
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Create base class for models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    # Primary key - always define explicitly
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic fields with constraints
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    
    # Default values for fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Audit timestamps - always include these!
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships - use lazy="joined" for eager loading when appropriate
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    # Use table's own primary key instead of user_id as PK
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Back reference
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile {self.user_id}>"

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Foreign keys - always include index for performance
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content status
    is_published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary="post_tags", back_populates="posts")
    
    def __repr__(self):
        return f"<Post {self.title}>"

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relationships
    posts = relationship("Post", secondary="post_tags", back_populates="tags")
    
    def __repr__(self):
        return f"<Tag {self.name}>"

# Association table for many-to-many relationship
class PostTag(Base):
    __tablename__ = "post_tags"
    
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    
    # Optional: Add additional fields to the association
    created_at = Column(DateTime, default=datetime.utcnow)
"""
        print(sqlalchemy_models)
        
        # Repository pattern
        print("\n📄 Repository Pattern for Data Access:")
        repository_pattern = """
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from pydantic import BaseModel

# Generic type for the model
T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository for database operations."""
    
    def __init__(self, db_session: Session, model: Type[T]):
        self.db = db_session
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, data: Dict[str, Any]) -> T:
        """Create a new record."""
        db_obj = self.model(**data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update an existing record."""
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in data.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

class UserRepository(BaseRepository[User]):
    """User-specific repository with specialized methods."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(self.model).filter(self.model.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.db.query(self.model).filter(self.model.username == username).first()
    
    def get_active_superusers(self) -> List[User]:
        """Get all active superusers."""
        return (self.db.query(self.model)
                .filter(and_(self.model.is_active == True, self.model.is_superuser == True))
                .all())
"""
        print(repository_pattern)
        
        # Usage example
        print("\n📄 Using the Repository Pattern:")
        repository_usage = """
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Repository dependency
def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

# FastAPI route using repository
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository)
):
    db_user = user_repo.get_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Creating a user
@app.post("/users/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    # Check if user exists
    existing_user = user_repo.get_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    hashed_password = hash_password(user.password)
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    
    return user_repo.create(user_data)
"""
        print(repository_usage)
        
        print("\n📝 SQLAlchemy ORM Best Practices:")
        print("  • Use declarative base for model definitions")
        print("  • Include standard audit fields (created_at, updated_at)")
        print("  • Define explicit primary keys and indexes")
        print("  • Use proper cascades for relationships")
        print("  • Implement the repository pattern to encapsulate data access logic")
        print("  • Separate database models from API schemas")
        print("  • Use proper typing for better IDE support")
        print("  • Set appropriate relationship loading strategies")
    
    def demonstrate_migrations(self):
        """
        Demonstrate database migration strategies.
        
        This method shows how to handle schema migrations with Alembic.
        """
        print("\n" + "=" * 80)
        print("🔄 DATABASE MIGRATIONS")
        print("=" * 80)
        print("✨ Following §11.3: 'Migrations'")
        
        # Alembic setup
        print("\n📄 Alembic Setup:")
        alembic_setup = """
# Install Alembic
# pip install alembic

# Initialize Alembic in your project
# alembic init migrations

# The command creates a migrations directory with this structure:
# migrations/
# ├── env.py
# ├── README
# ├── script.py.mako
# └── versions/

# Edit alembic.ini to set the database URL (or use env variables)
# sqlalchemy.url = postgresql://user:pass@localhost/dbname

# Edit migrations/env.py to import your models
# from myapp.models import Base
# target_metadata = Base.metadata
"""
        print(alembic_setup)
        
        # Generate migration
        print("\n📄 Creating and Running Migrations:")
        alembic_usage = """
# Generate a new migration
# alembic revision --autogenerate -m "Create users table"

# This creates a file in migrations/versions/ like:
# 3c5d8e6f1abc_create_users_table.py

# Review the migration before applying!
# Make sure the generated migration does what you expect

# Apply the migration
# alembic upgrade head

# Rollback one migration
# alembic downgrade -1

# Show current migration
# alembic current

# Show migration history
# alembic history --verbose
"""
        print(alembic_usage)
        
        # Example migration script
        print("\n📄 Example Migration Script:")
        migration_script = """
# migrations/versions/3c5d8e6f1abc_create_users_table.py
\"\"\"Create users table

Revision ID: 3c5d8e6f1abc
Revises: 
Create Date: 2025-05-12 13:45:00.123456

\"\"\"
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '3c5d8e6f1abc'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    
    # Drop table
    op.drop_table('users')
"""
        print(migration_script)
        
        # CI integration
        print("\n📄 CI/CD Pipeline Integration:")
        ci_example = """
# .github/workflows/migrations-check.yml
name: DB Migrations Check

on:
  pull_request:
    paths:
      - 'app/models/**'
      - 'migrations/**'
      - 'alembic.ini'

jobs:
  check-migrations:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16.2-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Check migrations
        run: |
          # Generate a dry run SQL script to verify migrations
          alembic upgrade head --sql | tee migration.sql
          
          # Fail if the script is empty (no migrations)
          test -s migration.sql
      
      - name: Apply migrations to test DB
        run: |
          # Actually run migrations against test DB
          alembic upgrade head
      
      - name: Verify downgrade works
        run: |
          # Test that downgrades work correctly
          alembic downgrade base
"""
        print(ci_example)
        
        print("\n📝 Migration Best Practices:")
        print("  • Always use a migration tool (Alembic for SQLAlchemy)")
        print("  • Never modify production schemas manually")
        print("  • Review auto-generated migrations before applying")
        print("  • Test migrations in CI/CD pipeline")
        print("  • Include both upgrade and downgrade paths")
        print("  • Use transactions for safety")
        print("  • For large tables, consider batched migrations")
        print("  • Create database backup before applying migrations")
    
    def demonstrate_vector_databases(self):
        """
        Demonstrate vector database usage.
        
        This method shows how to work with vector databases for AI applications.
        """
        print("\n" + "=" * 80)
        print("🧠 VECTOR DATABASES")
        print("=" * 80)
        print("✨ Following §11.2: 'Chroma, Qdrant, pgvector'")
        
        # Vector database explanation
        print("\n📋 Vector Database Overview:")
        print("""
Vector databases store high-dimensional vector embeddings and enable efficient similarity search.
They are essential for:
- Semantic search
- Recommendation systems
- Retrieval-Augmented Generation (RAG)
- Image similarity
- Anomaly detection
""")
        
        # Vector database options
        print("\n📋 Vector Database Options:")
        print("""
1. Chroma (0.4+)
   - Lightweight, in-process or server mode
   - Easy to set up for development
   - Python native

2. Qdrant (1.9+)
   - Production-ready vector database
   - High-performance HNSW algorithm
   - Rich filtering capabilities
   - Horizontal scaling

3. pgvector (PostgreSQL extension)
   - Add vector capabilities to PostgreSQL
   - Combine relational and vector data
   - Good for existing PostgreSQL users
   - Less specialized than dedicated vector DBs
""")
        
        # Chroma example
        print("\n📄 Chroma Example:")
        chroma_example = """
import chromadb
from chromadb.config import Settings

# Initialize Chroma client
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",  # For persistent storage
    persist_directory="./chroma_db"    # Where data will be stored
))

# Create a collection
collection = client.create_collection(
    name="documents",
    metadata={"description": "Document embeddings"}
)

# Add documents with embeddings
collection.add(
    documents=["Document about Python", "Document about databases", "Document about AI"],
    embeddings=[
        [0.1, 0.2, 0.3, 0.4, 0.5],  # Simplified embeddings (usually 768-1536 dimensions)
        [0.2, 0.3, 0.4, 0.5, 0.6],
        [0.3, 0.4, 0.5, 0.6, 0.7]
    ],
    ids=["doc1", "doc2", "doc3"],
    metadatas=[
        {"source": "book", "page": 42},
        {"source": "article", "date": "2025-05-12"},
        {"source": "website", "url": "https://example.com"}
    ]
)

# Query for similar documents
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3, 0.4, 0.5]],
    n_results=2  # Return top 2 matches
)

# Use the results
documents = results['documents'][0]  # List of matching documents
distances = results['distances'][0]  # List of distances/similarity scores
metadatas = results['metadatas'][0]  # List of metadata for matching documents
"""
        print(chroma_example)
        
        # Qdrant example
        print("\n📄 Qdrant Example:")
        qdrant_example = """
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialize Qdrant client
client = QdrantClient(
    url="http://localhost:6333",  # For local Qdrant
    # url="https://your-qdrant-instance.cloud",  # For cloud
    # api_key="your-api-key",  # If using cloud with auth
)

# Create a collection
client.create_collection(
    collection_name="documents",
    vectors_config=models.VectorParams(
        size=768,  # Vector dimension (e.g., 768 for bert-base embeddings)
        distance=models.Distance.COSINE  # Similarity metric
    )
)

# Add documents with vectors
client.upload_points(
    collection_name="documents",
    points=[
        models.PointStruct(
            id=1,
            vector=[0.1, 0.2, ...],  # 768-dimensional vector
            payload={"text": "Document about Python", "source": "book", "page": 42}
        ),
        models.PointStruct(
            id=2,
            vector=[0.2, 0.3, ...],
            payload={"text": "Document about databases", "source": "article", "date": "2025-05-12"}
        ),
        models.PointStruct(
            id=3,
            vector=[0.3, 0.4, ...],
            payload={"text": "Document about AI", "source": "website", "url": "https://example.com"}
        )
    ]
)

# Search for similar documents
search_result = client.search(
    collection_name="documents",
    query_vector=[0.1, 0.2, ...],  # Query vector
    limit=2,  # Top 2 results
    # Optional: Filter results
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="source",
                match=models.MatchValue(value="book")
            )
        ]
    )
)

# Process results
for result in search_result:
    print(f"ID: {result.id}, Score: {result.score}")
    print(f"Text: {result.payload['text']}")
"""
        print(qdrant_example)
        
        # pgvector example
        print("\n📄 pgvector with SQLAlchemy Example:")
        pgvector_example = """
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np

# For pgvector, first install the extension in PostgreSQL:
# CREATE EXTENSION IF NOT EXISTS vector;

# Then add SQLAlchemy support:
# pip install pgvector sqlalchemy-utils

from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    
    # Vector column for embeddings
    embedding = Column(Vector(768), nullable=False)  # 768-dimensional vector

# Create engine and tables
engine = create_engine("postgresql+psycopg2://user:pass@localhost/vectordb")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Add documents
db = Session()
db.add(Document(
    content="Document about Python",
    source="book",
    embedding=np.random.rand(768).astype(np.float32)  # Random vector for demo
))
db.commit()

# Search for similar documents using cosine distance
from sqlalchemy import select, func

# Query vector (random for demo)
query_vector = np.random.rand(768).astype(np.float32)

# Perform vector similarity search
stmt = (
    select(Document)
    .order_by(Document.embedding.cosine_distance(query_vector))
    .limit(5)
)

results = db.execute(stmt).scalars().all()

# Process results
for doc in results:
    print(f"ID: {doc.id}, Content: {doc.content}")
"""
        print(pgvector_example)
        
        print("\n📝 Vector Database Best Practices:")
        print("  • Choose the right vector DB for your use case:")
        print("    - Chroma for development and small-scale applications")
        print("    - Qdrant for production and larger-scale applications")
        print("    - pgvector when you need to combine with relational data")
        print("  • Use appropriate vector dimensions for your model (usually 768-4096)")
        print("  • Store metadata alongside vectors for filtering and display")
        print("  • Use batched operations for efficiency")
        print("  • Consider indexing methods (HNSW, IVF) for large collections")
        print("  • Monitor performance and scale horizontally if needed")
    
    def demonstrate_data_patterns(self):
        """
        Demonstrate data access patterns in microservices.
        
        This method shows different approaches to data management in microservices.
        """
        print("\n" + "=" * 80)
        print("🏗️ DATA PATTERNS IN MICROSERVICES")
        print("=" * 80)
        print("✨ Following §11.4: 'Patterns in Microservices'")
        
        # Microservice data patterns table
        print("\n📋 Microservice Data Patterns:")
        patterns = [
            {
                "pattern": "Database-per-Service",
                "when_to_use": "Default pattern",
                "description": "Each microservice owns its data completely; joins happen in application layer or via events"
            },
            {
                "pattern": "Event-Sourcing + Snapshot",
                "when_to_use": "Audit requirements, temporal queries",
                "description": "Store all state changes as immutable events; build projections for queries"
            },
            {
                "pattern": "Polyglot Persistence",
                "when_to_use": "One service needs multiple data models",
                "description": "Use different databases for different aspects (e.g., PostgreSQL for CRUD, Neo4j for graph, Elasticsearch for search)"
            },
            {
                "pattern": "Shared Read Replica",
                "when_to_use": "Complex cross-domain reporting",
                "description": "Analytics/reporting service reads from read-only replicas, never writes back"
            }
        ]
        
        print("{:<25} {:<30} {:<50}".format("Pattern", "When to Use", "Description"))
        print("-" * 105)
        
        for pattern in patterns:
            print("{:<25} {:<30} {:<50}".format(
                pattern["pattern"], 
                pattern["when_to_use"], 
                pattern["description"]
            ))
        
        # Database-per-Service example
        print("\n📄 Database-per-Service Example:")
        db_per_service = """
# services/user_service/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# services/order_service/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Just a reference, not a ForeignKey!
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Instead of foreign key constraints, use API calls or events:
# services/order_service/api.py
@app.post("/orders/")
async def create_order(order: OrderCreate, user_service: UserService = Depends(get_user_service)):
    # Validate user exists via API call to user service
    user = await user_service.get_user(order.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create order in local database
    db_order = create_order_in_db(order)
    
    # Publish event
    await event_bus.publish(
        "order.created",
        {"order_id": db_order.id, "user_id": db_order.user_id}
    )
    
    return db_order
"""
        print(db_per_service)
        
        # Event sourcing pattern
        print("\n📄 Event Sourcing Pattern:")
        event_sourcing = """
# Event store table
class EventStore(Base):
    __tablename__ = "event_store"
    
    id = Column(Integer, primary_key=True)
    aggregate_id = Column(String(50), nullable=False, index=True)  # e.g., "order-123"
    aggregate_type = Column(String(50), nullable=False, index=True)  # e.g., "order"
    event_type = Column(String(50), nullable=False)  # e.g., "order_created"
    event_data = Column(JSONB, nullable=False)  # Event payload
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Optimistic concurrency control
    sequence_number = Column(Integer, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('aggregate_id', 'sequence_number', name='uq_event_sequence'),
    )

# Event sourcing service
class OrderEventService:
    def __init__(self, session):
        self.session = session
    
    async def create_order(self, order_data):
        # Generate new order ID
        order_id = str(uuid.uuid4())
        aggregate_id = f"order-{order_id}"
        
        # Create the event
        event = EventStore(
            aggregate_id=aggregate_id,
            aggregate_type="order",
            event_type="order_created",
            event_data=order_data,
            sequence_number=1  # First event for this aggregate
        )
        
        self.session.add(event)
        await self.session.commit()
        
        # Update the read model (projection)
        await self.update_order_projection(order_id, order_data)
        
        return order_id
    
    async def update_order_status(self, order_id, status):
        aggregate_id = f"order-{order_id}"
        
        # Get the current sequence number
        last_event = await self.session.execute(
            select(EventStore)
            .where(EventStore.aggregate_id == aggregate_id)
            .order_by(EventStore.sequence_number.desc())
            .limit(1)
        ).scalar_one_or_none()
        
        if not last_event:
            raise ValueError(f"Order {order_id} not found")
        
        # Create the status change event
        event = EventStore(
            aggregate_id=aggregate_id,
            aggregate_type="order",
            event_type="order_status_changed",
            event_data={"status": status},
            sequence_number=last_event.sequence_number + 1
        )
        
        self.session.add(event)
        await self.session.commit()
        
        # Update the read model
        await self.update_order_projection(order_id, {"status": status})
        
        return order_id
    
    async def rebuild_projection(self, order_id):
        """Rebuild the order projection from events."""
        aggregate_id = f"order-{order_id}"
        
        # Get all events for this order
        events = await self.session.execute(
            select(EventStore)
            .where(EventStore.aggregate_id == aggregate_id)
            .order_by(EventStore.sequence_number)
        ).scalars().all()
        
        if not events:
            raise ValueError(f"Order {order_id} not found")
        
        # Start with empty order state
        order_state = {}
        
        # Apply each event in sequence
        for event in events:
            if event.event_type == "order_created":
                order_state.update(event.event_data)
            elif event.event_type == "order_status_changed":
                order_state["status"] = event.event_data["status"]
            # ... handle other event types
        
        # Save the rebuilt projection
        await self.save_order_projection(order_id, order_state)
"""
        print(event_sourcing)
        
        # Polyglot persistence
        print("\n📄 Polyglot Persistence Example:")
        polyglot = """
# Product service using multiple databases
class ProductService:
    def __init__(self, pg_session, es_client, neo4j_driver, redis_client):
        self.pg_session = pg_session            # PostgreSQL for CRUD
        self.es_client = es_client              # Elasticsearch for search
        self.neo4j_driver = neo4j_driver        # Neo4j for recommendation
        self.redis_client = redis_client        # Redis for caching
    
    async def create_product(self, product_data):
        # 1. Store core data in PostgreSQL
        db_product = Product(**product_data)
        self.pg_session.add(db_product)
        await self.pg_session.commit()
        
        # 2. Index in Elasticsearch for search
        es_product = {
            "id": str(db_product.id),
            "name": db_product.name,
            "description": db_product.description,
            "category": db_product.category,
            "tags": db_product.tags,
            "price": float(db_product.price)
        }
        await self.es_client.index(
            index="products",
            id=str(db_product.id),
            document=es_product
        )
        
        # 3. Add to Neo4j for graph relationships
        query = '''
        CREATE (p:Product {id: $id, name: $name, category: $category})
        WITH p
        UNWIND $tags AS tag
        MERGE (t:Tag {name: tag})
        CREATE (p)-[:HAS_TAG]->(t)
        '''
        with self.neo4j_driver.session() as session:
            session.run(query, {
                "id": str(db_product.id),
                "name": db_product.name,
                "category": db_product.category,
                "tags": db_product.tags
            })
        
        # 4. Cache the product in Redis
        product_cache_key = f"product:{db_product.id}"
        await self.redis_client.set(
            product_cache_key,
            json.dumps(es_product),
            ex=3600  # 1 hour expiration
        )
        
        return db_product
    
    async def search_products(self, query, filters=None):
        # Use Elasticsearch for search
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["name^3", "description", "tags"]
                            }
                        }
                    ]
                }
            }
        }
        
        # Add filters if provided
        if filters:
            for field, value in filters.items():
                search_body["query"]["bool"].setdefault("filter", []).append(
                    {"term": {field: value}}
                )
        
        results = await self.es_client.search(
            index="products",
            body=search_body
        )
        
        return [hit["_source"] for hit in results["hits"]["hits"]]
    
    async def get_similar_products(self, product_id):
        # Use Neo4j for graph-based recommendations
        query = '''
        MATCH (p:Product {id: $id})-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(similar:Product)
        WHERE similar.id <> $id
        RETURN similar.id, similar.name, COUNT(t) AS shared_tags
        ORDER BY shared_tags DESC
        LIMIT 5
        '''
        
        with self.neo4j_driver.session() as session:
            result = session.run(query, {"id": str(product_id)})
            similar_products = [record for record in result]
        
        # Fetch full product details for the similar products
        # (either from cache or database)
        return [await self.get_product(record["similar.id"]) for record in similar_products]
"""
        print(polyglot)
        
        print("\n📝 Microservice Data Pattern Best Practices:")
        print("  • Own your data: Each service controls its own datastore")
        print("  • Use the right database for each access pattern")
        print("  • Consider eventual consistency between services")
        print("  • Use events for cross-service data updates")
        print("  • Implement proper error handling and retries")
        print("  • Design for resilience to database failures")
        print("  • Consider read replicas for reporting")
        print("  • Document data ownership boundaries clearly")
    
    def create_demo_compose(self):
        """
        Create a Docker Compose file for databases.
        
        This method generates a Docker Compose file for setting up various databases.
        """
        print("\n" + "=" * 80)
        print("🐳 DOCKER COMPOSE FOR DATABASES")
        print("=" * 80)
        print("✨ Following §11.5: 'Example Compose Snippets'")
        
        # Create a directory for the demo
        demo_dir = Path("./data_persistence_demo")
        demo_dir.mkdir(exist_ok=True)
        
        # Create a Docker Compose file
        compose_content = """
# No version: property - follows §8.1 mandatory rules
services:
  # PostgreSQL with pgvector (§11.2)
  postgres:
    image: ankane/pgvector:0.8.1-pg16  # pgvector baked in
    environment:
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: devdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "devuser"]
      interval: 10s
      retries: 5

  # MongoDB (§11.2)
  mongodb:
    image: mongodb/mongodb-community-server:7.0-ubi8
    ports:
      - "27017:27017"
    volumes:
      - mongodata:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=devuser
      - MONGO_INITDB_ROOT_PASSWORD=devpassword

  # Redis for caching (§11.4 Polyglot Persistence)
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

  # Qdrant vector database (§11.2)
  qdrant:
    image: qdrant/qdrant:v1.9.0
    ports:
      - "6333:6333"  # API
      - "6334:6334"  # Web UI
    volumes:
      - qdrantdata:/qdrant/storage

  # Admin tools
  adminer:
    image: adminer:4.8
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  mongo-express:
    image: mongo-express:latest
    ports:
      - "8081:8081"
    environment:
      - ME_CONFIG_MONGODB_ADMINUSERNAME=devuser
      - ME_CONFIG_MONGODB_ADMINPASSWORD=devpassword
      - ME_CONFIG_MONGODB_URL=mongodb://devuser:devpassword@mongodb:27017/
    depends_on:
      - mongodb

volumes:
  pgdata:
  mongodata:
  redisdata:
  qdrantdata:
"""
        
        compose_file = demo_dir / "compose.yml"
        with open(compose_file, "w") as f:
            f.write(compose_content)
        
        print(f"\n📄 Created Docker Compose file at {compose_file}")
        
        # Create README with instructions
        readme_content = """# Database Demo Environment

This directory contains Docker Compose configuration for setting up various databases
recommended in §11 of the Python Best Practices guide.

## Databases Included

- **PostgreSQL with pgvector**: Relational database with vector search capabilities
- **MongoDB**: Document-oriented database
- **Redis**: Key-value store and cache
- **Qdrant**: Vector database for AI applications

## Admin Tools

- **Adminer**: Web-based database management for PostgreSQL (http://localhost:8080)
- **Mongo Express**: Web-based MongoDB management (http://localhost:8081)

## Usage

Start all databases:

```bash
docker compose up -d
```

Start specific database:

```bash
docker compose up -d postgres
```

Check status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop all databases:

```bash
docker compose down
```

## Connection Information

### PostgreSQL

- Host: localhost
- Port: 5432
- Username: devuser
- Password: devpassword
- Database: devdb
- Connection string: `postgresql://devuser:devpassword@localhost:5432/devdb`

### MongoDB

- Host: localhost
- Port: 27017
- Username: devuser
- Password: devpassword
- Connection string: `mongodb://devuser:devpassword@localhost:27017`

### Redis

- Host: localhost
- Port: 6379
- Connection string: `redis://localhost:6379`

### Qdrant

- Host: localhost
- REST API Port: 6333
- Web UI Port: 6334
- URL: `http://localhost:6333`
- Web UI: `http://localhost:6334`
"""
        
        readme_file = demo_dir / "README.md"
        with open(readme_file, "w") as f:
            f.write(readme_content)
        
        print(f"\n📄 Created README with instructions at {readme_file}")
        
        print("\n📝 Docker Compose Best Practices:")
        print("  • No version: property (follows §8.1)")
        print("  • Explicitly pin image tags")
        print("  • Include healthchecks")
        print("  • Use named volumes for data persistence")
        print("  • Set specific ports to avoid conflicts")
        print("  • Include admin tools for easier management")
        print("  • Document connection information")
        
        return demo_dir
    
    def run_demo(self):
        """Run a comprehensive demonstration of data persistence best practices."""
        print("\n" + "=" * 80)
        print("🚀 DATA PERSISTENCE & STORAGE DEMONSTRATION")
        print(f"✨ Demonstrating §11 of the Python Development Best Practices")
        print("=" * 80)
        
        print("\n📋 This demonstration will show you:")
        print("  1. Database Selection Criteria")
        print("  2. Connection Pooling & Management")
        print("  3. SQLAlchemy ORM Patterns")
        print("  4. Database Migrations")
        print("  5. Vector Databases")
        print("  6. Data Patterns in Microservices")
        print("  7. Docker Compose Setup")
        
        # Demonstrate each component
        self.demonstrate_database_selection()
        self.demonstrate_connection_pooling()
        self.demonstrate_sqlalchemy_models()
        self.demonstrate_migrations()
        self.demonstrate_vector_databases()
        self.demonstrate_data_patterns()
        
        # Ask if the user wants to create a Docker Compose demo
        print("\n📁 Would you like to create a Docker Compose demo for databases?")
        print("  1. Yes - Create the demo")
        print("  2. No - Skip this step")
        
        try:
            choice = input("Enter your choice (1-2): ").strip()
            if choice == "1":
                self.create_demo_compose()
            else:
                print("Skipping Docker Compose demo creation.")
        except Exception as e:
            print(f"Error: {e}")
            print("Skipping Docker Compose demo creation.")
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nRecommended next steps:")
        print("  1. Choose the right database for your use case")
        print("  2. Implement proper connection pooling")
        print("  3. Set up migrations for your database schema")
        print("  4. Consider using the repository pattern")
        print("  5. Explore vector databases for AI applications")
        print("  6. Apply microservice data patterns")
        print("  7. Use Docker Compose for local development")
    
    def generate_markdown(self) -> str:
        """
        Generate markdown documentation for the Data Persistence section
        of our best practices guide.
        """
        return f"""
## Data Persistence & Storage

### Core Principles

1. **Own your data**: Each micro-service controls its own datastore; cross-service queries flow through APIs or async events—never through shared DB tables.
2. **Right tool for the job**: Pick the engine that matches access patterns (OLTP, graph traversals, vector similarity, full-text search).
3. **Schema-first**: Maintain schema definitions in Git (SQL migrations, OpenAPI-backed event payloads, GraphQL SDL, etc.). Apply via automated CI/CD.
4. **Observability & backups**: Metrics, slow-query logs, and nightly off-site backups are non-negotiable—even in dev/staging.

### Database Matrix

| Engine              | Use-Case Sweet Spot                                                 | Async Driver                    | Migration Tool                    | Recommended Image Tag                       |
| ------------------- | ------------------------------------------------------------------- | ------------------------------- | --------------------------------- | ------------------------------------------- |
| **PostgreSQL 16**   | OLTP, JSONB, analytical queries, extensions (PostGIS, TimescaleDB). | `asyncpg`, `psycopg[pool]`      | Alembic                           | `postgres:16.2-alpine`                      |
| **SQLite 3.45**     | Simple CLI apps, embedded tests, edge devices.                      | `aiosqlite`                     | `sqlite-utils`, Alembic (offline) | Bundled                                     |
| **MongoDB 7**       | High-write schemaless docs, rapid prototyping.                      | `motor`                         | Mongo-Migrate / Mongock           | `mongodb/mongodb-community-server:7.0-ubi8` |
| **Neo4j 5**         | Deep graph traversals, recommendation, fraud detection.             | `neo4j-driver` (`asyncio` mode) | Liquibase-Neo4j                   | `neo4j:5.20`                                |
| **Elasticsearch 8** | Full-text search, log analytics, observability.                     | `elasticsearch[async]`          | Index template JSONs + ILM        | `elastic/elasticsearch:8.13.0`              |
| **Chroma 0.4**      | Lightweight local vector DB (in-proc / server) for semantic RAG.    | `chromadb`                      | n/a (implicit collections)        | `ghcr.io/chroma-core/chroma:0.4.24`         |
| **Qdrant 1.9**      | Production vector search, HNSW, filtering.                          | `qdrant-client[async]`          | Collection schema JSON            | `qdrant/qdrant:v1.9.0`                      |

> **Tip:** Pair Postgres with the [pgvector](https://github.com/pgvector/pgvector) extension when you need both relational and vector similarity in the same dataset.

### Operational Best Practices

* **Connection Pooling**: Use `asyncpg.create_pool()` (FastAPI startup) or PgBouncer for Postgres; configure pool size = (min(32, CPU×2)).
* **Migrations**: Auto-generate with Alembic—review SQL diff before merge; CI runs `alembic upgrade head --sql` to lint.
* **Backups**: Nightly `pg_dump` or WAL-archiving to S3; MongoDB Atlas continuous backup; Neo4j `neo4j-admin dump`.
* **Monitoring**: Export metrics (`pg_exporter`, `mongodb_exporter`, `qdrant_exporter`) to Prometheus; set SLOs on p95 latency and error-rate.
* **Security**: Least-privileged DB accounts; rotate secrets via Doppler/Vault; enable TLS in transit.

### Patterns in Microservices

| Pattern                       | When to Pick                            | Notes                                                     |
| ----------------------------- | --------------------------------------- | --------------------------------------------------------- |
| **Database-per-Service**      | Default                                 | Avoids tight coupling; join data in app layer or via async saga / CQRS.    |
| **Event-Sourcing + Snapshot** | Auditability, temporal queries          | Store immutable events (Kafka) + projections in Postgres/Elastic.          |
| **Polyglot Persistence**      | One service needs graph + search + OLTP | Keep write canonical in Postgres, index into Neo4j/Elastic asynchronously. |
| **Shared Read Replica**       | Complex cross-domain reporting          | Expose read-only replica to analytics service—never write.                 |

### Example Connection Pool Initialization

```python
async def create_pool():
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=min(32, os.cpu_count() * 2),
        command_timeout=60.0,
        ssl="require"  # Force TLS for security
    )
```

> **Rule:** Declare every database/collection/graph index in `m2m/README.md`—include purpose, schema/version table, backup plan, and retention policy.
"""
    
    def __str__(self):
        """String representation"""
        return f"{self.name}: Strategies for database management and storage in Python applications"


# Run the demo if this file is executed directly
if __name__ == "__main__":
    data_persistence = DataPersistenceAndStorage()
    data_persistence.run_demo()#!/usr/bin/env python3
"""
Data Persistence & Storage - Living Documentation

This module demonstrates data persistence best practices (§11 in our guide) through
active examples and clear explanations. It shows proper database usage patterns,
migrations, connection pooling, and various storage options.

Key concepts demonstrated:
- Database choice and selection criteria
- Connection management and pooling
- Migration strategies
- ORM patterns and best practices
- Vector databases for AI applications
- Polyglot persistence in microservices

Run this file directly to see a narrated demonstration of data persistence best practices.
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
import contextlib
import threading
from enum import Enum
import random
import inspect

# Try importing database libraries for demonstration
try:
    import sqlalchemy
    from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    # Create mock classes for SQLAlchemy
    class sqlalchemy:
        @staticmethod
        def create_engine(*args, **kwargs):
            return MockEngine()
    
    class Column:
        def __init__(self, *args, **kwargs):
            pass
    
    Integer = String = Boolean = ForeignKey = DateTime = object()
    
    def declarative_base():
        return type('Base', (), {})
    
    def sessionmaker(*args, **kwargs):
        return lambda: MockSession()
    
    def relationship(*args, **kwargs):
        return lambda: None
    
    class MockEngine:
        def connect(self):
            return self
        
        def close(self):
            pass
        
        def execute(self, *args, **kwargs):
            return []
    
    class MockSession:
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def close(self):
            pass
        
        def commit(self):
            pass
        
        def rollback(self):
            pass
        
        def query(self, *args, **kwargs):
            return self
        
        def filter(self, *args, **kwargs):
            return self
        
        def all(self):
            return []
        
        def first(self):
            return None
        
        def one_or_none(self):
            return None

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False


@dataclass
class DatabaseEngine:
    """
    Represents a database engine with its characteristics and use cases.
    """
    name: str
    version: str
    use_cases: List[str]
    async_driver: str
    migration_tool: str
    image_tag: str


class DatabaseType(Enum):
    """Types of databases by data model"""
    RELATIONAL = "Relational (SQL)"
    DOCUMENT = "Document (NoSQL)"
    GRAPH = "Graph"
    KEY_VALUE = "Key-Value"
    SEARCH = "Search Engine"
    VECTOR = "Vector Database"
    TIME_SERIES = "Time Series"


class DataPersistenceAndStorage:
    """
    Data Persistence & Storage
    
    This class demonstrates best practices for database management and data persistence
    as defined in §11 of our guide.
    """
    
    def __init__(self):
        """Initialize with data persistence practices from §11 of our guide."""
        self.name = "Data Persistence & Storage"
        
        # Set up logger
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Database engines from §11.2
        self.database_engines = [
            DatabaseEngine(
                name="PostgreSQL",
                version="16",
                use_cases=["OLTP", "JSONB", "analytical queries", "extensions (PostGIS, TimescaleDB)"],
                async_driver="asyncpg, psycopg[pool]",
                migration_tool="Alembic",
                image_tag="postgres:16.2-alpine"
            ),
            DatabaseEngine(
                name="SQLite",
                version="3.45",
                use_cases=["Simple CLI apps", "embedded tests", "edge devices"],
                async_driver="aiosqlite",
                migration_tool="sqlite-utils, Alembic (offline)",
                image_tag="Bundled"
            ),
            DatabaseEngine(
                name="MongoDB",
                version="7",
                use_cases=["High-write schemaless docs", "rapid prototyping"],
                async_driver="motor",
                migration_tool="Mongo-Migrate / Mongock",
                image_tag="mongodb/mongodb-community-server:7.0-ubi8"
            ),
            DatabaseEngine(
                name="Neo4j",
                version="5",
                use_cases=["Deep graph traversals", "recommendation", "fraud detection"],
                async_driver="neo4j-driver (asyncio mode)",
                migration_tool="Liquibase-Neo4j",
                image_tag="neo4j:5.20"
            ),
            DatabaseEngine(
                name="Elasticsearch",
                version="8",
                use_cases=["Full-text search", "log analytics", "observability"],
                async_driver="elasticsearch[async]",
                migration_tool="Index template JSONs + ILM",
                image_tag="elastic/elasticsearch:8.13.0"
            ),
            DatabaseEngine(
                name="Chroma",
                version="0.4",
                use_cases=["Lightweight local vector DB (in-proc / server) for semantic RAG"],
                async_driver="chromadb",
                migration_tool="n/a (implicit collections)",
                image_tag="ghcr.io/chroma-core/chroma:0.4.24"
            ),
            DatabaseEngine(
                name="Qdrant",
                version="1.9",
                use_cases=["Production vector search", "HNSW", "filtering"],
                async_driver="qdrant-client[async]",
                migration_tool="Collection schema JSON",
                image_tag="qdrant/qdrant:v1.9.0"
            )
        ]
    
    def demonstrate_database_selection(self):
        """
        Demonstrate database selection criteria.
        
        This method explains how to choose the right database for different use cases.
        """
        print("\n" + "=" * 80)
        print("📊 DATABASE SELECTION CRITERIA")
        print("=" * 80)
        print("✨ Following §11.2: 'Database Matrix'")
        
        # Display database matrix from the guide
        print("\n📋 Database Selection Matrix:")
        print("\n{:<12} {:<10} {:<50} {:<20} {:<25} {:<30}".format(
            "Engine", "Version", "Use-Case Sweet Spot", "Async Driver", "Migration Tool", "Recommended Image Tag"
        ))
        print("-" * 150)
        
        for engine in self.database_engines:
            use_cases = ", ".join(engine.use_cases)
            if len(use_cases) > 50:
                use_cases = use_cases[:47] + "..."
            
            print("{:<12} {:<10} {:<50} {:<20} {:<25} {:<30}".format(
                engine.name, engine.version, use_cases, engine.async_driver.split(",")[0], 
                engine.migration_tool.split(",")[0], engine.image_tag
            ))
        
        # Decision tree for database selection
        print("\n🌳 Database Selection Decision Tree:")
        print("""
1. Do you need full SQL query capabilities?
   ├── YES: Consider SQL databases
   │   ├── Need scalability: PostgreSQL
   │   ├── Need embedded: SQLite
   │   └── Need time-series: TimescaleDB (PostgreSQL extension)
   └── NO: Consider specialized databases
       ├── Need document flexibility: MongoDB
       ├── Need graph relationships: Neo4j
       ├── Need full-text search: Elasticsearch
       ├── Need vector search: Qdrant or Chroma
       └── Need pure key-value: Redis

2. What's your primary access pattern?
   ├── Complex queries with joins: PostgreSQL
   ├── Document-oriented access: MongoDB
   ├── Graph traversals: Neo4j
   ├── Text search: Elasticsearch
   ├── Vector similarity: Qdrant/Chroma
   └── Simple key lookups: Redis

3. Scale considerations:
   ├── Small-to-medium: Any of the above
   ├── Large (TB+): Consider cloud-managed versions
   └── Edge/embedded: SQLite
""")
        
        # Postgres + pgvector tip
        print("\n💡 TIP: For combined relational + vector search, use PostgreSQL with pgvector extension.")
        print("This is perfect for applications that need both structured data and similarity search.")
        
        print("\n📝 Key Database Selection Principles:")
        print("  • Choose based on data access patterns, not just popularity")
        print("  • Consider operational complexity (managed vs. self-hosted)")
        print("  • Evaluate scaling requirements (vertical vs. horizontal)")
        print("  • Think about query flexibility needs")
        print("  • Consider developer familiarity and ecosystem support")
    
    def demonstrate_connection_pooling(self):
        """
        Demonstrate connection pooling best practices.
        
        This method shows how to properly manage database connections.
        """
        print("\n" + "=" * 80)
        print("🔄 CONNECTION POOLING & MANAGEMENT")
        print("=" * 80)
        print("✨ Following §11.3: 'Connection Pooling'")
        
        # Connection pooling with SQLAlchemy
        print("\n📄 SQLAlchemy Connection Pool:")
        sqlalchemy_pool = """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment (following §0 Security practices)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")

# Create engine with connection pooling (§11.3)
engine = create_engine(
    DATABASE_URL,
    # Pool size recommendation from §11.3: min(32, CPU×2)
    pool_size=10,  # Adjust based on CPU cores
    max_overflow=20,  # Allow additional connections under load
    pool_timeout=30,  # Wait up to 30 seconds for connection
    pool_recycle=1800,  # Recycle connections every 30 minutes
    echo=False  # Set to True for query logging (development only)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
        print(sqlalchemy_pool)
        
        # Connection pooling with asyncpg
        print("\n📄 Async Connection Pool with asyncpg:")
        asyncpg_pool = """
import asyncpg
import asyncio
import os
from contextlib import asynccontextmanager

# Get database URL from environment (following §0 Security practices)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@localhost/app")

# Global pool variable
pool = None

async def create_pool():
    global pool
    # Create connection pool, following §11.3 recommendations
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,  # Minimum connections in pool
        max_size=10,  # Maximum connections in pool (adjust based on CPU cores)
        command_timeout=60.0,  # Command timeout in seconds
        max_inactive_connection_lifetime=1800.0,  # 30 minutes
        ssl="require"  # Force SSL for security (§0 Transport Encryption)
    )
    return pool

@asynccontextmanager
async def get_connection():
    global pool
    if pool is None:
        pool = await create_pool()
    
    # Acquire connection from pool
    async with pool.acquire() as connection:
        yield connection

# Application startup (integrate with FastAPI lifespan)
async def startup():
    await create_pool()

# Application shutdown
async def shutdown():
    global pool
    if pool:
        await pool.close()
"""
        print(asyncpg_pool)
        
        # Practical example
        print("\n📄 Complete FastAPI Example with Connection Pool:")
        fastapi_example = """
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncpg
import os

app = FastAPI()

# Setup connection pool on startup, close on shutdown
@app.on_event("startup")
async def startup():
    await create_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_pool()

# Dependency for database access
async def get_db_connection():
    async with get_connection() as conn:
        yield conn

@app.get("/users/{user_id}")
async def get_user(user_id: int, conn = Depends(get_db_connection)):
    # Use connection from pool
    user = await conn.fetchrow(
        "SELECT id, username, email FROM users WHERE id = $1",
        user_id
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return dict(user)
"""
        print(fastapi_example)
        
        print("\n📝 Connection Pooling Best Practices:")
        print("  • Size pool based on CPU cores: min(32, CPU×2)")
        print("  • Set sensible timeouts and max_overflow")
        print("  • Recycle connections periodically to prevent stale connections")
        print("  • Use a context manager or dependency to ensure connections return to pool")
        print("  • Monitor pool metrics in production")
        print("  • Consider PgBouncer for high-connection PostgreSQL workloads")
    
    def demonstrate_sqlalchemy_models(self):
        """
        Demonstrate SQLAlchemy ORM models.
        
        This method shows how to define and use SQLAlchemy models following best practices.
        """
        print("\n" + "=" * 80)
        print("🔄 SQLALCHEMY ORM PATTERNS")
        print("=" * 80)
        print("✨ Implementing ORM patterns for relational databases")
        
        # SQLAlchemy base models
        print("\n📄 SQLAlchemy Model Definitions:")
        sqlalchemy_models = """
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Create base class for models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    # Primary key - always define explicitly
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic fields with constraints
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    
    # Default values for fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Audit timestamps - always include these!
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships - use lazy="joined" for eager loading when appropriate
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    # Use table's own primary key instead of user_id as PK
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Back reference
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile {self.user_id}>"

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Foreign keys - always include index for performance
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content status
    is_published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary="post_tags", back_populates="posts")
    
    def __repr__(self):
        return f"<Post {self.title}>"

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relationships
    posts = relationship("Post", secondary="post_tags", back_populates="tags")
    
    def __repr__(self):
        return f"<Tag {self.name}>"

# Association table for many-to-many relationship
class PostTag(Base):
    __tablename__ = "post_tags"
    
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    
    # Optional: Add additional fields to the association
    created_at = Column(DateTime, default=datetime.utcnow)
"""
        print(sqlalchemy_models)
        
        # Repository pattern
        print("\n📄 Repository Pattern for Data Access:")
        repository_pattern = """
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from pydantic import BaseModel

# Generic type for the model
T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository for database operations."""
    
    def __init__(self, db_session: Session, model: Type[T]):
        self.db = db_session
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, data: Dict[str, Any]) -> T:
        """Create a new record."""
        db_obj = self.model(**data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """Update an existing record."""
        db_obj = self.get_by_id(id)
        if db_obj:
            for key, value in data.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

class UserRepository(BaseRepository[User]):
    """User-specific repository with specialized methods."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(self.model).filter(self.model.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.db.query(self.model).filter(self.model.username == username).first()
    
    def get_active_superusers(self) -> List[User]:
        """Get all active superusers."""
        return (self.db.query(self.model)
                .filter(and_(self.model.is_active == True, self.model.is_superuser == True))
                .all())
"""
        print(repository_pattern)
        
        # Usage example
        print("\n📄 Using the Repository Pattern:")
        repository_usage = """
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Repository dependency
def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

# FastAPI route using repository
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository)
):
    db_user = user_repo.get_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Creating a user
@app.post("/users/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    # Check if user exists
    existing_user = user_repo.get_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    hashed_password = hash_password(user.password)
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    
    return user_repo.create(user_data)
"""
        print(repository_usage)
        
        print("\n📝 SQLAlchemy ORM Best Practices:")
        print("  • Use declarative base for model definitions")
        print("  • Include standard audit fields (created_at, updated_at)")
        print("  • Define explicit primary keys and indexes")
        print("  • Use proper cascades for relationships")
        print("  • Implement the repository pattern to encapsulate data access logic")
        print("  • Separate database models from API schemas")
        print("  • Use proper typing for better IDE support")
        print("  • Set appropriate relationship loading strategies")
    
    def demonstrate_migrations(self):
        """
        Demonstrate database migration strategies.
        
        This method shows how to handle schema migrations with Alembic.
        """
        print("\n" + "=" * 80)
        print("🔄 DATABASE MIGRATIONS")
        print("=" * 80)
        print("✨ Following §11.3: 'Migrations'")
        
        # Alembic setup
        print("\n📄 Alembic Setup:")
        alembic_setup = """
# Install Alembic
# pip install alembic

# Initialize Alembic in your project
# alembic init migrations

# The command creates a migrations directory with this structure:
# migrations/
# ├── env.py
# ├── README
# ├── script.py.mako
# └── versions/

# Edit alembic.ini to set the database URL (or use env variables)
# sqlalchemy.url = postgresql://user:pass@localhost/dbname

# Edit migrations/env.py to import your models
# from myapp.models import Base
# target_metadata = Base.metadata
"""
        print(alembic_setup)
        
        # Generate migration
        print("\n📄 Creating and Running Migrations:")
        alembic_usage = """
# Generate a new migration
# alembic revision --autogenerate -m "Create users table"

# This creates a file in migrations/versions/ like:
# 3c5d8e6f1abc_create_users_table.py

# Review the migration before applying!
# Make sure the generated migration does what you expect

# Apply the migration
# alembic upgrade head

# Rollback one migration
# alembic downgrade -1

# Show current migration
# alembic current

# Show migration history
# alembic history --verbose
"""
        print(alembic_usage)
        
        # Example migration script
        print("\n📄 Example Migration Script:")
        migration_script = """
# migrations/versions/3c5d8e6f1abc_create_users_table.py
\"\"\"Create users table

Revision ID: 3c5d8e6f1abc
Revises: 
Create Date: 2025-05-12 13:45:00.123456

\"\"\"
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '3c5d8e6f1abc'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    
    # Drop table
    op.drop_table('users')
"""
        print(migration_script)
        
        # CI integration
        print("\n📄 CI/CD Pipeline Integration:")
        ci_example = """
# .github/workflows/migrations-check.yml
name: DB Migrations Check

on:
  pull_request:
    paths:
      - 'app/models/**'
      - 'migrations/**'
      - 'alembic.ini'

jobs:
  check-migrations:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16.2-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Check migrations
        run: |
          # Generate a dry run SQL script to verify migrations
          alembic upgrade head --sql | tee migration.sql
          
          # Fail if the script is empty (no migrations)
          test -s migration.sql
      
      - name: Apply migrations to test DB
        run: |
          # Actually run migrations against test DB
          alembic upgrade head
      
      - name: Verify downgrade works
        run: |
          # Test that downgrades work correctly
          alembic downgrade base
"""
        print(ci_example)
        
        print("\n📝 Migration Best Practices:")
        print("  • Always use a migration tool (Alembic for SQLAlchemy)")
        print("  • Never modify production schemas manually")
        print("  • Review auto-generated migrations before applying")
        print("  • Test migrations in CI/CD pipeline")
        print("  • Include both upgrade and downgrade paths")
        print("  • Use transactions for safety")
        print("  • For large tables, consider batched migrations")
        print("  • Create database backup before applying migrations")
    
    def demonstrate_vector_databases(self):
        """
        Demonstrate vector database usage.
        
        This method shows how to work with vector databases for AI applications.
        """
        print("\n" + "=" * 80)
        print("🧠 VECTOR DATABASES")
        print("=" * 80)
        print("✨ Following §11.2: 'Chroma, Qdrant, pgvector'")
        
        # Vector database explanation
        print("\n📋 Vector Database Overview:")
        print("""
Vector databases store high-dimensional vector embeddings and enable efficient similarity search.
They are essential for:
- Semantic search
- Recommendation systems
- Retrieval-Augmented Generation (RAG)
- Image similarity
- Anomaly detection
""")
        
        # Vector database options
        print("\n📋 Vector Database Options:")
        print("""
1. Chroma (0.4+)
   - Lightweight, in-process or server mode
   - Easy to set up for development
   - Python native

2. Qdrant (1.9+)
   - Production-ready vector database
   - High-performance HNSW algorithm
   - Rich filtering capabilities
   - Horizontal scaling

3. pgvector (PostgreSQL extension)
   - Add vector capabilities to PostgreSQL
   - Combine relational and vector data
   - Good for existing PostgreSQL users
   - Less specialized than dedicated vector DBs
""")
        
        # Chroma example
        print("\n📄 Chroma Example:")
        chroma_example = """
import chromadb
from chromadb.config import Settings

# Initialize Chroma client
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",  # For persistent storage
    persist_directory="./chroma_db"    # Where data will be stored
))

# Create a collection
collection = client.create_collection(
    name="documents",
    metadata={"description": "Document embeddings"}
)

# Add documents with embeddings
collection.add(
    documents=["Document about Python", "Document about databases", "Document about AI"],
    embeddings=[
        [0.1, 0.2, 0.3, 0.4, 0.5],  # Simplified embeddings (usually 768-1536 dimensions)
        [0.2, 0.3, 0.4, 0.5, 0.6],
        [0.3, 0.4, 0.5, 0.6, 0.7]
    ],
    ids=["doc1", "doc2", "doc3"],
    metadatas=[
        {"source": "book", "page": 42},
        {"source": "article", "date": "2025-05-12"},
        {"source": "website", "url": "https://example.com"}
    ]
)

# Query for similar documents
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3, 0.4, 0.5]],
    n_results=2  # Return top 2 matches
)

# Use the results
documents = results['documents'][0]  # List of matching documents
distances = results['distances'][0]  # List of distances/similarity scores
metadatas = results['metadatas'][0]  # List of metadata for matching documents
"""
        print(chroma_example)
        
        # Qdrant example
        print("\n📄 Qdrant Example:")
        qdrant_example = """
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialize Qdrant client
client = QdrantClient(
    url="http://localhost:6333",  # For local Qdrant
    # url="https://your-qdrant-instance.cloud",  # For cloud
    # api_key="your-api-key",  # If using cloud with auth
)

# Create a collection
client.create_collection(
    collection_name="documents",
    vectors_config=models.VectorParams(
        size=768,  # Vector dimension (e.g., 768 for bert-base embeddings)
        distance=models.Distance.COSINE  # Similarity metric
    )
)

# Add documents with vectors
client.upload_points(
    collection_name="documents",
    points=[
        models.PointStruct(
            id=1,
            vector=[0.1, 0.2, ...],  # 768-dimensional vector
            payload={"text": "Document about Python", "source": "book", "page": 42}
        ),
        models.PointStruct(
            id=2,
            vector=[0.2, 0.3, ...],
            payload={"text": "Document about databases", "source": "article", "date": "2025-05-12"}
        ),
        models.PointStruct(
            id=3,
            vector=[0.3, 0.4, ...],
            payload={"text": "Document about AI", "source": "website", "url": "https://example.com"}
        )
    ]
)

# Search for similar documents
search_result = client.search(
    collection_name="documents",
    query_vector=[0.1, 0.2, ...],  # Query vector
    limit=2,  # Top 2 results
    # Optional: Filter results
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="source",
                match=models.MatchValue(value="book")
            )
        ]
    )
)

# Process results
for result in search_result:
    print(f"ID: {result.id}, Score: {result.score}")
    print(f"Text: {result.payload['text']}")
"""
        print(qdrant_example)
        
        # pgvector example
        print("\n📄 pgvector with SQLAlchemy Example:")
        pgvector_example = """
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np

# For pgvector, first install the extension in PostgreSQL:
# CREATE EXTENSION IF NOT EXISTS vector;

# Then add SQLAlchemy support:
# pip install pgvector sqlalchemy-utils

from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    
    # Vector column for embeddings
    embedding = Column(Vector(768), nullable=False)  # 768-dimensional vector

# Create engine and tables
engine = create_engine("postgresql+psycopg2://user:pass@localhost/vectordb")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Add documents
db = Session()
db.add(Document(
    content="Document about Python",
    source="book",
    embedding=np.random.rand(768).astype(np.float32)  # Random vector for demo
))
db.commit()

# Search for similar documents using cosine distance
from sqlalchemy import select, func

# Query vector (random for demo)
query_vector = np.random.rand(768).astype(np.float32)

# Perform vector similarity search
stmt = (
    select(Document)
    .order_by(Document.embedding.cosine_distance(query_vector))
    .limit(5)
)

results = db.execute(stmt).scalars().all()

# Process results
for doc in results:
    print(f"ID: {doc.id}, Content: {doc.content}")
"""
        print(pgvector_example)
        
        print("\n📝 Vector Database Best Practices:")
        print("  • Choose the right vector DB for your use case:")
        print("    - Chroma for development and small-scale applications")
        print("    - Qdrant for production and larger-scale applications")
        print("    - pgvector when you need to combine with relational data")
        print("  • Use appropriate vector dimensions for your model (usually 768-4096)")
        print("  • Store metadata alongside vectors for filtering and display")
        print("  • Use batched operations for efficiency")
        print("  • Consider indexing methods (HNSW, IVF) for large collections")
        print("  • Monitor performance and scale horizontally if needed")
    
    def demonstrate_data_patterns(self):
        """
        Demonstrate data access patterns in microservices.
        
        This method shows different approaches to data management in microservices.
        """
        print("\n" + "=" * 80)
        print("🏗️ DATA PATTERNS IN MICROSERVICES")
        print("=" * 80)
        print("✨ Following §11.4: 'Patterns in Microservices'")
        
        # Microservice data patterns table
        print("\n📋 Microservice Data Patterns:")
        patterns = [
            {
                "pattern": "Database-per-Service",
                "when_to_use": "Default pattern",
                "description": "Each microservice owns its data completely; joins happen in application layer or via events"
            },
            {
                "pattern": "Event-Sourcing + Snapshot",
                "when_to_use": "Audit requirements, temporal queries",
                "description": "Store all state changes as immutable events; build projections for queries"
            },
            {
                "pattern": "Polyglot Persistence",
                "when_to_use": "One service needs multiple data models",
                "description": "Use different databases for different aspects (e.g., PostgreSQL for CRUD, Neo4j for graph, Elasticsearch for search)"
            },
            {
                "pattern": "Shared Read Replica",
                "when_to_use": "Complex cross-domain reporting",
                "description": "Analytics/reporting service reads from read-only replicas, never writes back"
            }
        ]
        
        print("{:<25} {:<30} {:<50}".format("Pattern", "When to Use", "Description"))
        print("-" * 105)
        
        for pattern in patterns:
            print("{:<25} {:<30} {:<50}".format(
                pattern["pattern"], 
                pattern["when_to_use"], 
                pattern["description"]
            ))
        
        # Database-per-Service example
        print("\n📄 Database-per-Service Example:")
        db_per_service = """
# services/user_service/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# services/order_service/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Just a reference, not a ForeignKey!
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Instead of foreign key constraints, use API calls or events:
# services/order_service/api.py
@app.post("/orders/")
async def create_order(order: OrderCreate, user_service: UserService = Depends(get_user_service)):
    # Validate user exists via API call to user service
    user = await user_service.get_user(order.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create order in local database
    db_order = create_order_in_db(order)
    
    # Publish event
    await event_bus.publish(
        "order.created",
        {"order_id": db_order.id, "user_id": db_order.user_id}
    )
    
    return db_order
"""
        print(db_per_service)
        
        # Event sourcing pattern
        print("\n📄 Event Sourcing Pattern:")
        event_sourcing = """
# Event store table
class EventStore(Base):
    __tablename__ = "event_store"
    
    id = Column(Integer, primary_key=True)
    aggregate_id = Column(String(50), nullable=False, index=True)  # e.g., "order-123"
    aggregate_type = Column(String(50), nullable=False, index=True)  # e.g., "order"
    event_type = Column(String(50), nullable=False)  # e.g., "order_created"
    event_data = Column(JSONB, nullable=False)  # Event payload
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Optimistic concurrency control
    sequence_number = Column(Integer, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('aggregate_id', 'sequence_number', name='uq_event_sequence'),
    )

# Event sourcing service
class OrderEventService:
    def __init__(self, session):
        self.session = session
    
    async def create_order(self, order_data):
        # Generate new order ID
        order_id = str(uuid.uuid4())
        aggregate_id = f"order-{order_id}"
        
        # Create the event
        event = EventStore(
            aggregate_id=aggregate_id,
            aggregate_type="order",
            event_type="order_created",
            event_data=order_data,
            sequence_number=1  # First event for this aggregate
        )
        
        self.session.add(event)
        await self.session.commit()
        
        # Update the read model (projection)
        await self.update_order_projection(order_id, order_data)
        
        return order_id
    
    async def update_order_status(self, order_id, status):
        aggregate_id = f"order-{order_id}"
        
        # Get the current sequence number
        last_event = await self.session.execute(
            select(EventStore)
            .where(EventStore.aggregate_id == aggregate_id)
            .order_by(EventStore.sequence_number.desc())
            .limit(1)
        ).scalar_one_or_none()
        
        if not last_event:
            raise ValueError(f"Order {order_id} not found")
        
        # Create the status change event
        event = EventStore(
            aggregate_id=aggregate_id,
            aggregate_type="order",
            event_type="order_status_changed",
            event_data={"status": status},
            sequence_number=last_event.sequence_number + 1
        )
        
        self.session.add(event)
        await self.session.commit()
        
        # Update the read model
        await self.update_order_projection(order_id, {"status": status})
        
        return order_id
    
    async def rebuild_projection(self, order_id):
        """Rebuild the order projection from events."""
        aggregate_id = f"order-{order_id}"
        
        # Get all events for this order
        events = await self.session.execute(
            select(EventStore)
            .where(EventStore.aggregate_id == aggregate_id)
            .order_by(EventStore.sequence_number)
        ).scalars().all()
        
        if not events:
            raise ValueError(f"Order {order_id} not found")
        
        # Start with empty order state
        order_state = {}
        
        # Apply each event in sequence
        for event in events:
            if event.event_type == "order_created":
                order_state.update(event.event_data)
            elif event.event_type == "order_status_changed":
                order_state["status"] = event.event_data["status"]
            # ... handle other event types
        
        # Save the rebuilt projection
        await self.save_order_projection(order_id, order_state)
"""
        print(event_sourcing)
        
        # Polyglot persistence
        print("\n📄 Polyglot Persistence Example:")
        polyglot = """
# Product service using multiple databases
class ProductService:
    def __init__(self, pg_session, es_client, neo4j_driver, redis_client):
        self.pg_session = pg_session            # PostgreSQL for CRUD
        self.es_client = es_client              # Elasticsearch for search
        self.neo4j_driver = neo4j_driver        # Neo4j for recommendation
        self.redis_client = redis_client        # Redis for caching
    
    async def create_product(self, product_data):
        # 1. Store core data in PostgreSQL
        db_product = Product(**product_data)
        self.pg_session.add(db_product)
        await self.pg_session.commit()
        
        # 2. Index in Elasticsearch for search
        es_product = {
            "id": str(db_product.id),
            "name": db_product.name,
            "description": db_product.description,
            "category": db_product.category,
            "tags": db_product.tags,
            "price": float(db_product.price)
        }
        await self.es_client.index(
            index="products",
            id=str(db_product.id),
            document=es_product
        )
        
        # 3. Add to Neo4j for graph relationships
        query = '''
        CREATE (p:Product {id: $id, name: $name, category: $category})
        WITH p
        UNWIND $tags AS tag
        MERGE (t:Tag {name: tag})
        CREATE (p)-[:HAS_TAG]->(t)
        '''
        with self.neo4j_driver.session() as session:
            session.run(query, {
                "id": str(db_product.id),
                "name": db_product.name,
                "category": db_product.category,
                "tags": db_product.tags
            })
        
        # 4. Cache the product in Redis
        product_cache_key = f"product:{db_product.id}"
        await self.redis_client.set(
            product_cache_key,
            json.dumps(es_product),
            ex=3600  # 1 hour expiration
        )
        
        return db_product
    
    async def search_products(self, query, filters=None):
        # Use Elasticsearch for search
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["name^3", "description", "tags"]
                            }
                        }
                    ]
                }
            }
        }
        
        # Add filters if provided
        if filters:
            for field, value in filters.items():
                search_body["query"]["bool"].setdefault("filter", []).append(
                    {"term": {field: value}}
                )
        
        results = await self.es_client.search(
            index="products",
            body=search_body
        )
        
        return [hit["_source"] for hit in results["hits"]["hits"]]
    
    async def get_similar_products(self, product_id):
        # Use Neo4j for graph-based recommendations
        query = '''
        MATCH (p:Product {id: $id})-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(similar:Product)
        WHERE similar.id <> $id
        RETURN similar.id, similar.name, COUNT(t) AS shared_tags
        ORDER BY shared_tags DESC
        LIMIT 5
        '''
        
        with self.neo4j_driver.session() as session:
            result = session.run(query, {"id": str(product_id)})
            similar_products = [record for record in result]
        
        # Fetch full product details for the similar products
        # (either from cache or database)
        return [await self.get_product(record["similar.id"]) for record in similar_products]
"""
        print(polyglot)
        
        print("\n📝 Microservice Data Pattern Best Practices:")
        print("  • Own your data: Each service controls its own datastore")
        print("  • Use the right database for each access pattern")
        print("  • Consider eventual consistency between services")
        print("  • Use events for cross-service data updates")
        print("  • Implement proper error handling and retries")
        print("  • Design for resilience to database failures")
        print("  • Consider read replicas for reporting")
        print("  • Document data ownership boundaries clearly")
    
    def create_demo_compose(self):
        """
        Create a Docker Compose file for databases.
        
        This method generates a Docker Compose file for setting up various databases.
        """
        print("\n" + "=" * 80)
        print("🐳 DOCKER COMPOSE FOR DATABASES")
        print("=" * 80)
        print("✨ Following §11.5: 'Example Compose Snippets'")
        
        # Create a directory for the demo
        demo_dir = Path("./data_persistence_demo")
        demo_dir.mkdir(exist_ok=True)
        
        # Create a Docker Compose file
        compose_content = """
# No version: property - follows §8.1 mandatory rules
services:
  # PostgreSQL with pgvector (§11.2)
  postgres:
    image: ankane/pgvector:0.8.1-pg16  # pgvector baked in
    environment:
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: devdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "devuser"]
      interval: 10s
      retries: 5

  # MongoDB (§11.2)
  mongodb:
    image: mongodb/mongodb-community-server:7.0-ubi8
    ports:
      - "27017:27017"
    volumes:
      - mongodata:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=devuser
      - MONGO_INITDB_ROOT_PASSWORD=devpassword

  # Redis for caching (§11.4 Polyglot Persistence)
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

  # Qdrant vector database (§11.2)
  qdrant:
    image: qdrant/qdrant:v1.9.0
    ports:
      - "6333:6333"  # API
      - "6334:6334"  # Web UI
    volumes:
      - qdrantdata:/qdrant/storage

  # Admin tools
  adminer:
    image: adminer:4.8
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  mongo-express:
    image: mongo-express:latest
    ports:
      - "8081:8081"
    environment:
      - ME_CONFIG_MONGODB_ADMINUSERNAME=devuser
      - ME_CONFIG_MONGODB_ADMINPASSWORD=devpassword
      - ME_CONFIG_MONGODB_URL=mongodb://devuser:devpassword@mongodb:27017/
    depends_on:
      - mongodb

volumes:
  pgdata:
  mongodata:
  redisdata:
  qdrantdata:
"""
        
        compose_file = demo_dir / "compose.yml"
        with open(compose_file, "w") as f:
            f.write(compose_content)
        
        print(f"\n📄 Created Docker Compose file at {compose_file}")
        
        # Create README with instructions
        readme_content = """# Database Demo Environment

This directory contains Docker Compose configuration for setting up various databases
recommended in §11 of the Python Best Practices guide.

## Databases Included

- **PostgreSQL with pgvector**: Relational database with vector search capabilities
- **MongoDB**: Document-oriented database
- **Redis**: Key-value store and cache
- **Qdrant**: Vector database for AI applications

## Admin Tools

- **Adminer**: Web-based database management for PostgreSQL (http://localhost:8080)
- **Mongo Express**: Web-based MongoDB management (http://localhost:8081)

## Usage

Start all databases:

```bash
docker compose up -d
```

Start specific database:

```bash
docker compose up -d postgres
```

Check status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop all databases:

```bash
docker compose down
```

## Connection Information

### PostgreSQL

- Host: localhost
- Port: 5432
- Username: devuser
- Password: devpassword
- Database: devdb
- Connection string: `postgresql://devuser:devpassword@localhost:5432/devdb`

### MongoDB

- Host: localhost
- Port: 27017
- Username: devuser
- Password: devpassword
- Connection string: `mongodb://devuser:devpassword@localhost:27017`

### Redis

- Host: localhost
- Port: 6379
- Connection string: `redis://localhost:6379`

### Qdrant

- Host: localhost
- REST API Port: 6333
- Web UI Port: 6334
- URL: `http://localhost:6333`
- Web UI: `http://localhost:6334`
"""
        
        readme_file = demo_dir / "README.md"
        with open(readme_file, "w") as f:
            f.write(readme_content)
        
        print(f"\n📄 Created README with instructions at {readme_file}")
        
        print("\n📝 Docker Compose Best Practices:")
        print("  • No version: property (follows §8.1)")
        print("  • Explicitly pin image tags")
        print("  • Include healthchecks")
        print("  • Use named volumes for data persistence")
        print("  • Set specific ports to avoid conflicts")
        print("  • Include admin tools for easier management")
        print("  • Document connection information")
        
        return demo_dir
    
    def run_demo(self):
        """Run a comprehensive demonstration of data persistence best practices."""
        print("\n" + "=" * 80)
        print("🚀 DATA PERSISTENCE & STORAGE DEMONSTRATION")
        print(f"✨ Demonstrating §11 of the Python Development Best Practices")
        print("=" * 80)
        
        print("\n📋 This demonstration will show you:")
        print("  1. Database Selection Criteria")
        print("  2. Connection Pooling & Management")
        print("  3. SQLAlchemy ORM Patterns")
        print("  4. Database Migrations")
        print("  5. Vector Databases")
        print("  6. Data Patterns in Microservices")
        print("  7. Docker Compose Setup")
        
        # Demonstrate each component
        self.demonstrate_database_selection()
        self.demonstrate_connection_pooling()
        self.demonstrate_sqlalchemy_models()
        self.demonstrate_migrations()
        self.demonstrate_vector_databases()
        self.demonstrate_data_patterns()
        
        # Ask if the user wants to create a Docker Compose demo
        print("\n📁 Would you like to create a Docker Compose demo for databases?")
        print("  1. Yes - Create the demo")
        print("  2. No - Skip this step")
        
        try:
            choice = input("Enter your choice (1-2): ").strip()
            if choice == "1":
                self.create_demo_compose()
            else:
                print("Skipping Docker Compose demo creation.")
        except Exception as e:
            print(f"Error: {e}")
            print("Skipping Docker Compose demo creation.")
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nRecommended next steps:")
        print("  1. Choose the right database for your use case")
        print("  2. Implement proper connection pooling")
        print("  3. Set up migrations for your database schema")
        print("  4. Consider using the repository pattern")
        print("  5. Explore vector databases for AI applications")
        print("  6. Apply microservice data patterns")
        print("  7. Use Docker Compose for local development")
    
    def generate_markdown(self) -> str:
        """
        Generate markdown documentation for the Data Persistence section
        of our best practices guide.
        """
        return f"""
## Data Persistence & Storage

### Core Principles

1. **Own your data**: Each micro-service controls its own datastore; cross-service queries flow through APIs or async events—never through shared DB tables.
2. **Right tool for the job**: Pick the engine that matches access patterns (OLTP, graph traversals, vector similarity, full-text search).
3. **Schema-first**: Maintain schema definitions in Git (SQL migrations, OpenAPI-backed event payloads, GraphQL SDL, etc.). Apply via automated CI/CD.
4. **Observability & backups**: Metrics, slow-query logs, and nightly off-site backups are non-negotiable—even in dev/staging.

### Database Matrix

| Engine              | Use-Case Sweet Spot                                                 | Async Driver                    | Migration Tool                    | Recommended Image Tag                       |
| ------------------- | ------------------------------------------------------------------- | ------------------------------- | --------------------------------- | ------------------------------------------- |
| **PostgreSQL 16**   | OLTP, JSONB, analytical queries, extensions (PostGIS, TimescaleDB). | `asyncpg`, `psycopg[pool]`      | Alembic                           | `postgres:16.2-alpine`                      |
| **SQLite 3.45**     | Simple CLI apps, embedded tests, edge devices.                      | `aiosqlite`                     | `sqlite-utils`, Alembic (offline) | Bundled                                     |
| **MongoDB 7**       | High-write schemaless docs, rapid prototyping.                      | `motor`                         | Mongo-Migrate / Mongock           | `mongodb/mongodb-community-server:7.0-ubi8` |
| **Neo4j 5**         | Deep graph traversals, recommendation, fraud detection.             | `neo4j-driver` (`asyncio` mode) | Liquibase-Neo4j                   | `neo4j:5.20`                                |
| **Elasticsearch 8** | Full-text search, log analytics, observability.                     | `elasticsearch[async]`          | Index template JSONs + ILM        | `elastic/elasticsearch:8.13.0`              |
| **Chroma 0.4**      | Lightweight local vector DB (in-proc / server) for semantic RAG.    | `chromadb`                      | n/a (implicit collections)        | `ghcr.io/chroma-core/chroma:0.4.24`         |
| **Qdrant 1.9**      | Production vector search, HNSW, filtering.                          | `qdrant-client[async]`          | Collection schema JSON            | `qdrant/qdrant:v1.9.0`                      |

> **Tip:** Pair Postgres with the [pgvector](https://github.com/pgvector/pgvector) extension when you need both relational and vector similarity in the same dataset.

### Operational Best Practices

* **Connection Pooling**: Use `asyncpg.create_pool()` (FastAPI startup) or PgBouncer for Postgres; configure pool size = (min(32, CPU×2)).
* **Migrations**: Auto-generate with Alembic—review SQL diff before merge; CI runs `alembic upgrade head --sql` to lint.
* **Backups**: Nightly `pg_dump` or WAL-archiving to S3; MongoDB Atlas continuous backup; Neo4j `neo4j-admin dump`.
* **Monitoring**: Export metrics (`pg_exporter`, `mongodb_exporter`, `qdrant_exporter`) to Prometheus; set SLOs on p95 latency and error-rate.
* **Security**: Least-privileged DB accounts; rotate secrets via Doppler/Vault; enable TLS in transit.

### Patterns in Microservices

| Pattern                       | When to Pick                            | Notes                                                     |
| ----------------------------- | --------------------------------------- | --------------------------------------------------------- |
| **Database-per-Service**      | Default                                 | Avoids tight coupling; join data in app layer or via async saga / CQRS.    |
| **Event-Sourcing + Snapshot** | Auditability, temporal queries          | Store immutable events (Kafka) + projections in Postgres/Elastic.          |
| **Polyglot Persistence**      | One service needs graph + search + OLTP | Keep write canonical in Postgres, index into Neo4j/Elastic asynchronously. |
| **Shared Read Replica**       | Complex cross-domain reporting          | Expose read-only replica to analytics service—never write.                 |

### Example Connection Pool Initialization

```python
async def create_pool():
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=min(32, os.cpu_count() * 2),
        command_timeout=60.0,
        ssl="require"  # Force TLS for security
    )
```

> **Rule:** Declare every database/collection/graph index in `m2m/README.md`—include purpose, schema/version table, backup plan, and retention policy.
"""
    
    def __str__(self):
        """String representation"""
        return f"{self.name}: Strategies for database management and storage in Python applications"


# Run the demo if this file is executed directly
if __name__ == "__main__":
    data_persistence = DataPersistenceAndStorage()
    data_persistence.run_demo()