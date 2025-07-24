#!/usr/bin/env python3
"""
Sample Application Demonstrating Integrated Best Practices

This module shows how to use the different best practice modules together
in a real application. It demonstrates:

1. Project initialization following best practices
2. Modern Python syntax and validation
3. An API with proper logging and error handling
4. Background tasks integration

This is a concrete example of the principles taught in this repository.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager

# Import our best practice modules
from dry import DRY
from environment import EnvironmentManagement
from observability import LoggingObservabilityStandards
from validation import DataValidationAndConfiguration, ModelType, PydanticModel
from tasks import BackgroundTasksAndConcurrency
from fast_api_best_practice import FastAPIBestPractices

# Import other required libraries
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field, EmailStr


class SampleApp:
    """
    Demonstrates integration of best practice modules in a real application.
    
    This class implements a sample todo app that uses:
    - Pydantic for data validation (validation.py)
    - Structured logging (logging.py)
    - Background tasks (tasks.py)
    - FastAPI best practices (fast_api_best_practice.py)
    """
    
    def __init__(self):
        """
        Initialize the sample application with integrated best practices.
        """
        # Initialize logging first (foundation for all other components)
        self.logger_module = LoggingObservabilityStandards()
        self.logger = self.logger_module.create_basic_jsonl_logger()
        self.logger.info("Initializing sample application")
        
        # Initialize environment management
        self.env_manager = EnvironmentManagement() 
        
        # Initialize data validation module
        self.validation = DataValidationAndConfiguration()
        
        # Initialize background tasks module
        self.tasks = BackgroundTasksAndConcurrency()
        
        # Define Pydantic models for our application
        self.define_models()
        
        # Setup API with lifespan to handle startup/shutdown
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup actions
            self.logger.info("Application startup")
            
            # For demonstration purposes, we'll initialize some todo items
            self.todos = [
                {"id": 1, "title": "Learn Python Best Practices", "completed": True},
                {"id": 2, "title": "Build a FastAPI application", "completed": False},
                {"id": 3, "title": "Implement background tasks", "completed": False}
            ]
            
            yield
            
            # Shutdown actions
            self.logger.info("Application shutdown")
        
        # Create the FastAPI app
        self.app = FastAPI(
            title="Sample Todo App",
            description="Sample application demonstrating integrated best practices",
            version="1.0.0",
            lifespan=lifespan
        )
        
        # Set up routes
        self.setup_routes()
        
        self.logger.info("Sample application initialized successfully")
    
    def define_models(self):
        """Define Pydantic models for the application using our validation best practices."""
        # We'll create these inline, but the validation module helps us identify patterns
        class TodoBase(BaseModel):
            """Base todo model with shared attributes"""
            title: str = Field(..., min_length=1, max_length=100, description="Title of the todo item")
            completed: bool = Field(default=False, description="Whether the item is completed")
        
        class TodoCreate(TodoBase):
            """Model for creating a new todo item"""
            pass
        
        class Todo(TodoBase):
            """Model for todo responses including the ID"""
            id: int = Field(..., gt=0, description="Unique identifier for the todo item")
            
            class Config:
                from_attributes = True
        
        # Store models for use in routes
        self.TodoBase = TodoBase
        self.TodoCreate = TodoCreate
        self.Todo = Todo
    
    def setup_routes(self):
        """Set up the API routes following best practices."""
        
        @self.app.get("/todos", response_model=List[self.Todo], tags=["todos"])
        async def get_todos():
            """Get all todo items."""
            self.logger.info("Retrieving all todos", count=len(self.todos))
            return self.todos
        
        @self.app.get("/todos/{todo_id}", response_model=self.Todo, tags=["todos"])
        async def get_todo(todo_id: int):
            """Get a specific todo item by ID."""
            todo = next((t for t in self.todos if t["id"] == todo_id), None)
            if not todo:
                self.logger.warning("Todo not found", todo_id=todo_id)
                raise HTTPException(status_code=404, detail="Todo not found")
            
            self.logger.info("Retrieved todo", todo_id=todo_id)
            return todo
        
        @self.app.post("/todos", response_model=self.Todo, status_code=201, tags=["todos"])
        async def create_todo(todo: self.TodoCreate, background_tasks: BackgroundTasks):
            """Create a new todo item."""
            # Generate ID (in a real app, this would be handled by the database)
            new_id = max(t["id"] for t in self.todos) + 1 if self.todos else 1
            
            # Create the new todo
            new_todo = {
                "id": new_id,
                **todo.model_dump()
            }
            
            # Add to our list
            self.todos.append(new_todo)
            
            # Log using structured logging
            self.logger.info("Todo created", todo_id=new_id, title=todo.title)
            
            # Add a background task to demonstrate task integration
            background_tasks.add_task(self.process_new_todo, new_todo)
            
            return new_todo
        
        @self.app.put("/todos/{todo_id}", response_model=self.Todo, tags=["todos"])
        async def update_todo(todo_id: int, todo: self.TodoCreate):
            """Update an existing todo item."""
            # Find the todo
            index = next((i for i, t in enumerate(self.todos) if t["id"] == todo_id), None)
            if index is None:
                self.logger.warning("Todo not found for update", todo_id=todo_id)
                raise HTTPException(status_code=404, detail="Todo not found")
            
            # Update the todo
            updated_todo = {
                "id": todo_id,
                **todo.model_dump()
            }
            self.todos[index] = updated_todo
            
            self.logger.info("Todo updated", todo_id=todo_id, title=todo.title)
            return updated_todo
        
        @self.app.delete("/todos/{todo_id}", status_code=204, tags=["todos"])
        async def delete_todo(todo_id: int):
            """Delete a todo item."""
            # Find the todo
            index = next((i for i, t in enumerate(self.todos) if t["id"] == todo_id), None)
            if index is None:
                self.logger.warning("Todo not found for deletion", todo_id=todo_id)
                raise HTTPException(status_code=404, detail="Todo not found")
            
            # Remove the todo
            self.todos.pop(index)
            
            self.logger.info("Todo deleted", todo_id=todo_id)
    
    async def process_new_todo(self, todo: Dict[str, Any]):
        """
        Process a new todo item in the background.
        
        This demonstrates a background task that would typically do something like:
        - Send notifications
        - Update search indices
        - Generate reports
        """
        await asyncio.sleep(2)  # Simulate some processing time
        self.logger.info("Background processing of todo complete", todo_id=todo["id"])
    
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the sample application."""
        import uvicorn
        self.logger.info("Starting sample application", host=host, port=port)
        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    app = SampleApp()
    app.run() 