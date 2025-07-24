#!/usr/bin/env python3
"""
Application Design & Structure - Living Documentation

This module demonstrates best practices for Python application design and structure
(§4 in our guide) through active examples and clear explanations. It shows how to
organize code into logical packages, manage configuration, handle errors, and
implement design principles.

Key concepts demonstrated:
- Project structure organization
- DRY (Don't Repeat Yourself) principle
- SOLID principles
- Error handling patterns
- Command-line interface design
- Configuration management

Run this file directly to see a narrated demonstration of application design.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Try to import our other modules for integration
try:
    from dry import DRY
    from solid import SOLID
except ImportError:
    # Create minimal placeholder classes
    class DRY:
        def __init__(self):
            self.name = "DRY"
            self.full_name = "Don't Repeat Yourself"
            self.core_idea = "Every piece of knowledge must have a single, unambiguous representation within the codebase."
    
    class SOLID:
        def __init__(self):
            self.name = "SOLID"
            self.core_idea = "Five principles that promote maintainable, extensible OOP designs."


@dataclass
class ProjectStructure:
    """
    Represents a recommended project structure following §4.3 guidelines.
    """
    name: str
    description: str
    directories: Dict[str, Any]
    files: List[str]


@dataclass
class DesignPattern:
    """
    Represents a design pattern useful in Python applications.
    """
    name: str
    purpose: str
    example: str


class ApplicationDesignAndStructure:
    """
    Application Design & Structure
    
    A class demonstrating best practices for Python application design and structure
    as defined in §4 of our guide.
    """
    
    def __init__(self):
        """Initialize with design principles from §4 of our guide."""
        self.name = "Application Design & Structure"
        
        # Set up logger
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Load core principles
        self.dry_principle = DRY()
        self.solid_principles = SOLID()
        
        # Define recommended project structures
        self.project_structures = [
            ProjectStructure(
                name="Web Application (FastAPI)",
                description="Structure for web applications built with FastAPI",
                directories={
                    "src/": {
                        "<app_name>/": {
                            "__init__.py": "Package marker",
                            "api/": {
                                "__init__.py": "Package marker",
                                "routers/": "API endpoint routers",
                                "dependencies.py": "Dependency injection functions"
                            },
                            "core/": {
                                "__init__.py": "Package marker",
                                "config.py": "Configuration management",
                                "security.py": "Authentication and security"
                            },
                            "models/": {
                                "__init__.py": "Package marker",
                                "domain.py": "Domain models",
                                "schemas.py": "Pydantic schemas"
                            },
                            "services/": "Business logic layer",
                            "db/": "Database models and queries",
                            "main.py": "Application entry point"
                        }
                    },
                    "tests/": {
                        "conftest.py": "Pytest fixtures",
                        "unit/": "Unit tests",
                        "integration/": "Integration tests"
                    },
                    "docs/": "Documentation files",
                    "migrations/": "Database migrations"
                },
                files=[
                    "README.md",
                    "pyproject.toml",
                    ".gitignore",
                    ".env.example",
                    "LICENSE"
                ]
            ),
            ProjectStructure(
                name="CLI Application",
                description="Structure for command-line applications",
                directories={
                    "src/": {
                        "<cli_name>/": {
                            "__init__.py": "Package marker",
                            "cli.py": "Command-line interface",
                            "commands/": "Command implementations",
                            "core/": "Core functionality"
                        }
                    },
                    "tests/": {
                        "test_cli.py": "CLI tests",
                        "test_commands.py": "Command tests"
                    }
                },
                files=[
                    "README.md",
                    "pyproject.toml",
                    ".gitignore",
                    "LICENSE"
                ]
            ),
            ProjectStructure(
                name="Library Package",
                description="Structure for reusable library packages",
                directories={
                    "src/": {
                        "<library_name>/": {
                            "__init__.py": "Package marker with version",
                            "module1.py": "Core functionality",
                            "module2.py": "Additional functionality"
                        }
                    },
                    "tests/": "Test files",
                    "examples/": "Example usage"
                },
                files=[
                    "README.md",
                    "pyproject.toml",
                    ".gitignore",
                    "LICENSE"
                ]
            )
        ]
        
        # Common design patterns
        self.design_patterns = [
            DesignPattern(
                name="Factory",
                purpose="Create objects without specifying their exact class",
                example="""
class UserFactory:
    @staticmethod
    def create_user(user_type, **kwargs):
        if user_type == 'admin':
            return AdminUser(**kwargs)
        elif user_type == 'customer':
            return CustomerUser(**kwargs)
        else:
            return RegularUser(**kwargs)
"""
            ),
            DesignPattern(
                name="Singleton",
                purpose="Ensure a class has only one instance",
                example="""
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize the instance
            cls._instance.connect()
        return cls._instance
        
    def connect(self):
        # Connection logic
        pass
"""
            ),
            DesignPattern(
                name="Repository",
                purpose="Separate data access logic from business logic",
                example="""
class UserRepository:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def get_by_id(self, user_id):
        return self.db_session.query(User).filter(User.id == user_id).first()
    
    def create(self, user_data):
        user = User(**user_data)
        self.db_session.add(user)
        self.db_session.commit()
        return user
"""
            ),
            DesignPattern(
                name="Strategy",
                purpose="Define a family of algorithms and make them interchangeable",
                example="""
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paying ${amount} with credit card")
        
class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paying ${amount} with PayPal")
        
class PaymentProcessor:
    def __init__(self, strategy):
        self.strategy = strategy
        
    def process_payment(self, amount):
        self.strategy.pay(amount)
"""
            )
        ]
    
    def demonstrate_project_structure(self):
        """
        Demonstrate recommended project structures.
        
        This method explains and visualizes different project structures
        for various types of Python applications.
        """
        print("\n" + "=" * 80)
        print("📁 RECOMMENDED PROJECT STRUCTURES")
        print("=" * 80)
        print("✨ Following §4.3: 'Recommended Project Structures'")
        
        # Show each project structure
        for i, structure in enumerate(self.project_structures, 1):
            print(f"\n{i}. {structure.name}: {structure.description}")
            self._print_tree(structure.directories, indent=3)
            
            print("\n   Root files:")
            for file in structure.files:
                print(f"   - {file}")
        
        print("\n📝 Key structure principles:")
        print("  • Each file has a well-defined purpose")
        print("  • Related functionality is grouped into packages")
        print("  • Clear separation of concerns between modules")
        print("  • Tests are organized alongside the code")
        print("  • Configuration is separated from code")
    
    def _print_tree(self, tree, indent=0, is_last=True, prefix=""):
        """Helper method to print a directory tree structure."""
        if isinstance(tree, str):
            print(f"{' ' * indent}{prefix}{'└── ' if is_last else '├── '}{tree}")
            return
            
        for i, (key, value) in enumerate(tree.items()):
            is_last_item = i == len(tree) - 1
            print(f"{' ' * indent}{prefix}{'└── ' if is_last_item else '├── '}{key}")
            
            if isinstance(value, dict):
                new_prefix = prefix + ("    " if is_last_item else "│   ")
                self._print_tree(value, indent + 4, is_last_item, new_prefix)
            elif isinstance(value, str):
                print(f"{' ' * (indent + 4)}{prefix}{'    ' if is_last_item else '│   '}└── {value}")
    
    def demonstrate_dry_principle(self):
        """
        Demonstrate the DRY (Don't Repeat Yourself) principle.
        
        This method shows good and bad examples of DRY implementation.
        """
        print("\n" + "=" * 80)
        print("🔄 DRY PRINCIPLE")
        print("=" * 80)
        print(f"✨ Following §4.1: '{self.dry_principle.full_name}'")
        print(f"  • {self.dry_principle.core_idea}")
        
        # BAD example - violating DRY
        print("\n❌ ANTI-PATTERN: Repeated code")
        bad_example = """
def process_customer_order(customer_id, items):
    # Connect to the database (repeated code)
    conn = connect_to_database("localhost", "mydb", "user", "pass")
    
    # Process order
    cursor = conn.cursor()
    # ... order processing logic ...
    conn.close()

def update_customer_profile(customer_id, data):
    # Connect to the database (same code repeated)
    conn = connect_to_database("localhost", "mydb", "user", "pass")
    
    # Update profile
    cursor = conn.cursor()
    # ... profile update logic ...
    conn.close()

def get_customer_orders(customer_id):
    # Connect to the database (same code again)
    conn = connect_to_database("localhost", "mydb", "user", "pass")
    
    # Get orders
    cursor = conn.cursor()
    # ... query logic ...
    conn.close()
"""
        print(bad_example)
        
        # GOOD example - following DRY
        print("\n✅ BETTER PATTERN: Centralized shared logic")
        good_example = """
def get_database_connection():
    \"\"\"Centralized database connection function.\"\"\"
    return connect_to_database("localhost", "mydb", "user", "pass")

def process_customer_order(customer_id, items):
    conn = get_database_connection()
    # Process order
    cursor = conn.cursor()
    # ... order processing logic ...
    conn.close()

def update_customer_profile(customer_id, data):
    conn = get_database_connection()
    # Update profile
    cursor = conn.cursor()
    # ... profile update logic ...
    conn.close()

def get_customer_orders(customer_id):
    conn = get_database_connection()
    # Get orders
    cursor = conn.cursor()
    # ... query logic ...
    conn.close()
"""
        print(good_example)
        
        # BEST example - with context manager
        print("\n✅✅ BEST PATTERN: Context manager for resource handling")
        best_example = """
@contextmanager
def database_connection():
    \"\"\"Context manager for database connections.\"\"\"
    conn = connect_to_database("localhost", "mydb", "user", "pass")
    try:
        yield conn
    finally:
        conn.close()

def process_customer_order(customer_id, items):
    with database_connection() as conn:
        cursor = conn.cursor()
        # ... order processing logic ...
        # No need to close the connection manually

def update_customer_profile(customer_id, data):
    with database_connection() as conn:
        cursor = conn.cursor()
        # ... profile update logic ...
        # No need to close the connection manually

def get_customer_orders(customer_id):
    with database_connection() as conn:
        cursor = conn.cursor()
        # ... query logic ...
        # No need to close the connection manually
"""
        print(best_example)
        
        print("\n📝 DRY Benefits:")
        print("  • Reduced code maintenance overhead")
        print("  • Fewer bugs due to inconsistent updates")
        print("  • Easier refactoring and code evolution")
        print("  • Better reusability of components")
    
    def demonstrate_solid_principles(self):
        """
        Demonstrate the SOLID principles.
        
        This method explains and shows examples of the five SOLID principles.
        """
        print("\n" + "=" * 80)
        print("📏 SOLID PRINCIPLES")
        print("=" * 80)
        print(f"✨ Following §4.1: '{self.solid_principles.name}'")
        print(f"  • {self.solid_principles.core_idea}")
        
        # S: Single Responsibility Principle
        print("\n1️⃣ Single Responsibility Principle")
        print("  • Each class should have only one reason to change")
        print("  • Separate concerns into different classes")
        print("\n❌ ANTI-PATTERN: Class with multiple responsibilities")
        bad_srp = """
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def validate_email(self):
        # Email validation logic
        return "@" in self.email
    
    def save_to_database(self):
        # Database logic
        db.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                 (self.name, self.email))
    
    def send_welcome_email(self):
        # Email sending logic
        email_service.send(
            to=self.email,
            subject="Welcome!",
            body=f"Welcome, {self.name}!"
        )
"""
        print(bad_srp)
        
        print("\n✅ BETTER PATTERN: Separated responsibilities")
        good_srp = """
class User:
    \"\"\"User entity - just holds data.\"\"\"
    def __init__(self, name, email):
        self.name = name
        self.email = email

class EmailValidator:
    \"\"\"Validates email addresses.\"\"\"
    @staticmethod
    def is_valid(email):
        return "@" in email

class UserRepository:
    \"\"\"Handles user database operations.\"\"\"
    def save(self, user):
        db.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
                 (user.name, user.email))

class EmailService:
    \"\"\"Handles email sending.\"\"\"
    def send_welcome_email(self, user):
        email_service.send(
            to=user.email,
            subject="Welcome!",
            body=f"Welcome, {user.name}!"
        )
"""
        print(good_srp)
        
        # O: Open/Closed Principle
        print("\n2️⃣ Open/Closed Principle")
        print("  • Classes should be open for extension but closed for modification")
        print("  • Add new functionality by adding new code, not changing existing code")
        print("\n❌ ANTI-PATTERN: Need to modify existing class for new shapes")
        bad_ocp = """
class AreaCalculator:
    def calculate_area(self, shape):
        if isinstance(shape, Rectangle):
            return shape.width * shape.height
        elif isinstance(shape, Circle):
            return 3.14 * shape.radius ** 2
        # Need to modify this class for each new shape
"""
        print(bad_ocp)
        
        print("\n✅ BETTER PATTERN: Using polymorphism")
        good_ocp = """
class Shape:
    def area(self):
        pass  # Abstract method

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class AreaCalculator:
    def calculate_area(self, shape):
        return shape.area()  # Polymorphic call
"""
        print(good_ocp)
        
        # L: Liskov Substitution Principle
        print("\n3️⃣ Liskov Substitution Principle")
        print("  • Subtypes must be substitutable for their base types")
        print("  • Derived classes must respect the contracts of base classes")
        print("\n❌ ANTI-PATTERN: Square violates Rectangle's contract")
        bad_lsp = """
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def set_width(self, width):
        self.width = width
    
    def set_height(self, height):
        self.height = height
    
    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)
    
    def set_width(self, width):
        self.width = width
        self.height = width  # Violates Rectangle's behavior
    
    def set_height(self, height):
        self.height = height
        self.width = height  # Violates Rectangle's behavior
"""
        print(bad_lsp)
        
        print("\n✅ BETTER PATTERN: Proper hierarchy with base Shape")
        good_lsp = """
class Shape:
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Square(Shape):  # Not a Rectangle subclass
    def __init__(self, side):
        self.side = side
    
    def area(self):
        return self.side * self.side
"""
        print(good_lsp)
        
        # I: Interface Segregation Principle
        print("\n4️⃣ Interface Segregation Principle")
        print("  • Clients should not depend on interfaces they don't use")
        print("  • Many small, specific interfaces are better than a large, general one")
        print("\n❌ ANTI-PATTERN: Monolithic interface")
        bad_isp = """
class Worker:
    def work(self):
        pass
    
    def eat(self):
        pass
    
    def sleep(self):
        pass

class Robot(Worker):
    def work(self):
        print("Robot working")
    
    def eat(self):
        raise NotImplementedError("Robots don't eat")  # Forced to implement
    
    def sleep(self):
        raise NotImplementedError("Robots don't sleep")  # Forced to implement
"""
        print(bad_isp)
        
        print("\n✅ BETTER PATTERN: Segregated interfaces")
        good_isp = """
class Workable:
    def work(self):
        pass

class Eatable:
    def eat(self):
        pass

class Sleepable:
    def sleep(self):
        pass

class Human(Workable, Eatable, Sleepable):
    def work(self):
        print("Human working")
    
    def eat(self):
        print("Human eating")
    
    def sleep(self):
        print("Human sleeping")

class Robot(Workable):  # Only implements what it needs
    def work(self):
        print("Robot working")
"""
        print(good_isp)
        
        # D: Dependency Inversion Principle
        print("\n5️⃣ Dependency Inversion Principle")
        print("  • High-level modules should not depend on low-level modules")
        print("  • Both should depend on abstractions")
        print("\n❌ ANTI-PATTERN: Direct dependency on concrete implementation")
        bad_dip = """
class MySQLDatabase:
    def save(self, data):
        print(f"Saving {data} to MySQL")

class UserService:
    def __init__(self):
        self.database = MySQLDatabase()  # Direct dependency
    
    def save_user(self, user):
        self.database.save(user)
"""
        print(bad_dip)
        
        print("\n✅ BETTER PATTERN: Dependency injection through abstraction")
        good_dip = """
class Database:  # Abstract interface
    def save(self, data):
        pass

class MySQLDatabase(Database):
    def save(self, data):
        print(f"Saving {data} to MySQL")

class PostgreSQLDatabase(Database):
    def save(self, data):
        print(f"Saving {data} to PostgreSQL")

class UserService:
    def __init__(self, database):  # Dependency injection
        self.database = database
    
    def save_user(self, user):
        self.database.save(user)
"""
        print(good_dip)
        
        print("\n📝 SOLID Benefits:")
        print("  • More maintainable and extensible code")
        print("  • Fewer bugs and easier debugging")
        print("  • Better testability")
        print("  • Improved code reuse")
        print("  • Reduced coupling between components")
    
    def demonstrate_error_handling(self):
        """
        Demonstrate proper error handling patterns.
        
        This method shows best practices for handling errors in Python applications.
        """
        print("\n" + "=" * 80)
        print("⚠️ ERROR HANDLING PATTERNS")
        print("=" * 80)
        print("✨ Following §4: 'Write robust error handling'")
        
        # BAD example - poor error handling
        print("\n❌ ANTI-PATTERN: Bare except and silent failures")
        bad_error = """
def process_file(filename):
    try:
        # Open file and process
        file = open(filename, 'r')
        data = file.read()
        result = process_data(data)
        return result
    except:  # Bare except - catches ALL exceptions, including KeyboardInterrupt
        # Silent failure - no logging, no re-raising
        return None  # Returns None on ANY error
"""
        print(bad_error)
        
        # GOOD example - proper error handling
        print("\n✅ BETTER PATTERN: Specific exceptions and proper handling")
        good_error = """
def process_file(filename):
    try:
        with open(filename, 'r') as file:  # Use context manager
            data = file.read()
            result = process_data(data)
            return result
    except FileNotFoundError:
        # Specific exception handling
        logger.error(f"File not found: {filename}")
        raise FileProcessingError(f"File not found: {filename}")
    except PermissionError:
        logger.error(f"Permission denied: {filename}")
        raise FileProcessingError(f"Permission denied: {filename}")
    except Exception as e:
        # General exception as a last resort, with logging and re-raising
        logger.error(f"Error processing file {filename}: {str(e)}")
        raise FileProcessingError(f"Error processing file: {str(e)}") from e
"""
        print(good_error)
        
        # BEST example - with custom exception
        print("\n✅✅ BEST PATTERN: Custom exceptions and contextual errors")
        best_error = """
class FileProcessingError(Exception):
    \"\"\"Custom exception for file processing errors.\"\"\"
    pass

def process_file(filename):
    \"\"\"
    Process a file, with robust error handling.
    
    Args:
        filename: The path to the file
        
    Returns:
        The processed data
        
    Raises:
        FileProcessingError: If the file cannot be processed
    \"\"\"
    try:
        with open(filename, 'r') as file:
            data = file.read()
            try:
                result = process_data(data)
                return result
            except ValueError as e:
                # Wrap the low-level exception with context
                logger.error(f"Invalid data in {filename}: {str(e)}")
                raise FileProcessingError(f"Invalid data in file: {str(e)}") from e
    except (FileNotFoundError, PermissionError) as e:
        # Handle file access errors
        logger.error(f"Cannot access file {filename}: {str(e)}")
        raise FileProcessingError(f"Cannot access file: {str(e)}") from e
"""
        print(best_error)
        
        print("\n📝 Error Handling Best Practices:")
        print("  • Use specific exception types, not bare except")
        print("  • Always log exceptions with context (filename, user, etc.)")
        print("  • Use custom exception classes for domain-specific errors")
        print("  • Use context managers (with) for resource cleanup")
        print("  • Document exceptions in docstrings")
        print("  • Use 'raise ... from exception' to preserve the traceback")
    
    def demonstrate_cli_design(self):
        """
        Demonstrate command-line interface design.
        
        This method shows how to create well-designed CLI applications.
        """
        print("\n" + "=" * 80)
        print("💻 COMMAND-LINE INTERFACE DESIGN")
        print("=" * 80)
        print("✨ Following §4: 'For CLI apps, use argparse, typer, or click'")
        
        # Basic argparse example
        print("\n📄 ARGPARSE EXAMPLE (Standard Library):")
        argparse_example = """
import argparse

def create_parser():
    \"\"\"Create the command-line argument parser.\"\"\"
    parser = argparse.ArgumentParser(
        description="Sample command-line application",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("filename", help="File to process")
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "-o", "--output", 
        default="output.txt", 
        help="Output file"
    )
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Processing {args.filename}")
    
    # Process the file
    with open(args.filename, 'r') as infile, open(args.output, 'w') as outfile:
        content = infile.read()
        # Do some processing
        result = content.upper()
        outfile.write(result)
    
    if args.verbose:
        print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()
"""
        print(argparse_example)
        
        # Typer example (modern approach)
        print("\n📄 TYPER EXAMPLE (Modern Approach):")
        typer_example = """
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer(help="Sample command-line application")

@app.command()
def process(
    filename: Path = typer.Argument(..., help="File to process"),
    output: Path = typer.Option("output.txt", "--output", "-o", help="Output file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    \"\"\"Process a file and convert its content to uppercase.\"\"\"
    if verbose:
        typer.echo(f"Processing {filename}")
    
    # Process the file
    content = filename.read_text()
    result = content.upper()
    output.write_text(result)
    
    if verbose:
        typer.echo(f"Output written to {output}")

if __name__ == "__main__":
    app()
"""
        print(typer_example)
        
        print("\n📝 CLI Design Best Practices:")
        print("  • Use a modern CLI library like typer or click")
        print("  • Provide helpful error messages and documentation")
        print("  • Follow Unix conventions (--long-option, -s short option)")
        print("  • Implement proper exit codes")
        print("  • Support verbose/quiet modes")
        print("  • Add support for configuration files")
        print("  • Implement tab completion for complex commands")
    
    def demonstrate_design_patterns(self):
        """
        Demonstrate common design patterns.
        
        This method explains and shows examples of design patterns
        useful in Python applications.
        """
        print("\n" + "=" * 80)
        print("🧩 COMMON DESIGN PATTERNS")
        print("=" * 80)
        print("✨ Following §4: 'Use appropriate design patterns'")
        
        # Show each design pattern
        for i, pattern in enumerate(self.design_patterns, 1):
            print(f"\n{i}. {pattern.name} Pattern")
            print(f"   Purpose: {pattern.purpose}")
            print(f"   Example:")
            
            for line in pattern.example.strip().split("\n"):
                print(f"   {line}")
        
        print("\n📝 Design Pattern Best Practices:")
        print("  • Use patterns to solve common problems with proven solutions")
        print("  • Don't over-engineer by using patterns unnecessarily")
        print("  • Document when and why you're using a pattern")
        print("  • Adapt patterns to fit Python's idioms")
        print("  • Be aware of both Gang of Four patterns and Python-specific patterns")
    
    def create_demo_structure(self, output_dir: Path = None, app_type: str = "web"):
        """
        Create a demo project structure.
        
        This method creates a directory structure following the recommended
        project structure for a given application type.
        """
        if not output_dir:
            output_dir = Path(f"./demo_{app_type}_app")
            output_dir.mkdir(exist_ok=True)
        
        print("\n" + "=" * 80)
        print("📁 CREATING DEMO PROJECT STRUCTURE")
        print("=" * 80)
        print(f"✨ Creating a {app_type} application structure at {output_dir}")
        
        # Choose the appropriate structure
        structure = next((s for s in self.project_structures if app_type.lower() in s.name.lower()), self.project_structures[0])
        
        # Create directories
        created_dirs = []
        created_files = []
        
        def create_structure(directory, tree, parent_path=Path(".")):
            for key, value in tree.items():
                path = parent_path / key
                full_path = directory / path
                
                if isinstance(value, dict):
                    full_path.mkdir(exist_ok=True, parents=True)
                    created_dirs.append(str(path))
                    create_structure(directory, value, path)
                elif isinstance(value, str):
                    # It's a file
                    full_path.parent.mkdir(exist_ok=True, parents=True)
                    with open(full_path, "w") as f:
                        if full_path.name == "__init__.py":
                            f.write('"""Package namespace."""\n\n')
                        else:
                            f.write(f'"""{value}"""\n\n')
                    created_files.append(str(path))
        
        # Create the directory structure
        create_structure(output_dir, structure.directories)
        
        # Create root files
        for file in structure.files:
            file_path = output_dir / file
            with open(file_path, "w") as f:
                if file == "README.md":
                    # Create a proper README
                    app_name = output_dir.name
                    f.write(f"# {app_name}\n\n")
                    f.write(f"{structure.description}\n\n")
                    f.write("## Installation\n\n")
                    f.write("```bash\n")
                    f.write("pip install -e .\n")
                    f.write("```\n\n")
                    f.write("## Usage\n\n")
                    f.write("```python\n")
                    f.write(f"from {app_name} import example\n")
                    f.write("```\n")
                elif file == "pyproject.toml":
                    # Create a basic pyproject.toml
                    f.write("[build-system]\n")
                    f.write('requires = ["hatchling"]\n')
                    f.write('build-backend = "hatchling.build"\n\n')
                    f.write("[project]\n")
                    f.write(f'name = "{output_dir.name}"\n')
                    f.write('version = "0.1.0"\n')
                    f.write(f'description = "{structure.description}"\n')
                    f.write('authors = [{name = "Your Name", email = "your.email@example.com"}]\n')
                    f.write('readme = "README.md"\n')
                    f.write('requires-python = ">=3.10"\n')
                elif file == ".gitignore":
                    # Create a sensible .gitignore
                    f.write("# Python\n")
                    f.write("__pycache__/\n")
                    f.write("*.py[cod]\n")
                    f.write("*$py.class\n")
                    f.write("*.so\n")
                    f.write("dist/\n")
                    f.write("build/\n")
                    f.write("*.egg-info/\n\n")
                    f.write("# Virtual environments\n")
                    f.write("venv/\n")
                    f.write(".env/\n")
                    f.write(".venv/\n\n")
                    f.write("# Environment variables\n")
                    f.write(".env\n\n")
                    f.write("# IDE\n")
                    f.write(".idea/\n")
                    f.write(".vscode/\n")
                elif file == ".env.example":
                    # Create a sample .env file
                    f.write("# Environment variables for development\n")
                    f.write("DEBUG=True\n")
                    f.write("LOG_LEVEL=DEBUG\n")
                    f.write("DATABASE_URL=sqlite:///dev.db\n")
                    f.write("SECRET_KEY=development-secret-key\n")
                elif file == "LICENSE":
                    # Add a minimal MIT license
                    f.write("MIT License\n\n")
                    f.write(f"Copyright (c) {datetime.now().year} Your Name\n\n")
                    f.write("Permission is hereby granted, free of charge, to any person obtaining a copy\n")
                    f.write("of this software and associated documentation files (the \"Software\"), to deal\n")
                    f.write("in the Software without restriction, including without limitation the rights\n")
                    f.write("to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n")
                    f.write("copies of the Software, and to permit persons to whom the Software is\n")
                    f.write("furnished to do so, subject to the following conditions:\n\n")
                    f.write("The above copyright notice and this permission notice shall be included in all\n")
                    f.write("copies or substantial portions of the Software.\n")
            
            created_files.append(file)
        
        # Show what was created
        print("\n📁 Created directories:")
        for directory in created_dirs:
            print(f"  • {directory}")
        
        print("\n📄 Created files:")
        for file in created_files:
            print(f"  • {file}")
        
        print("\n📝 Next steps:")
        print("  1. Initialize a git repository in this directory:")
        print("     $ git init")
        print("  2. Install the project in development mode:")
        print("     $ pip install -e .")
        print("  3. Start implementing your application in the structure provided")
        
        return output_dir
    
    def run_demo(self):
        """Run a comprehensive demonstration of application design best practices."""
        print("\n" + "=" * 80)
        print("🚀 APPLICATION DESIGN & STRUCTURE DEMONSTRATION")
        print(f"✨ Demonstrating §4 of the Python Development Best Practices")
        print("=" * 80)
        
        print("\n📋 This demonstration will show you:")
        print("  1. Recommended Project Structures")
        print("  2. DRY Principle")
        print("  3. SOLID Principles")
        print("  4. Error Handling Patterns")
        print("  5. CLI Design Patterns")
        print("  6. Common Design Patterns")
        print("  7. Creating a Demo Project Structure")
        
        # Demonstrate each component
        self.demonstrate_project_structure()
        self.demonstrate_dry_principle()
        self.demonstrate_solid_principles()
        self.demonstrate_error_handling()
        self.demonstrate_cli_design()
        self.demonstrate_design_patterns()
        
        # Ask if the user wants to create a demo structure
        print("\n📁 Would you like to create a demo project structure?")
        print("  1. Web Application (FastAPI)")
        print("  2. CLI Application")
        print("  3. Library Package")
        print("  4. Skip (don't create any structure)")
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
            if choice == "1":
                self.create_demo_structure(app_type="web")
            elif choice == "2":
                self.create_demo_structure(app_type="cli")
            elif choice == "3":
                self.create_demo_structure(app_type="library")
            else:
                print("Skipping demo structure creation.")
        except Exception as e:
            print(f"Error: {e}")
            print("Skipping demo structure creation.")
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nRecommended next steps:")
        print("  • Review and apply the SOLID principles in your code")
        print("  • Look for violations of the DRY principle in your codebase")
        print("  • Set up a proper project structure for your next project")
        print("  • Improve error handling in your applications")
        print("  • Consider appropriate design patterns for common problems")
    
    def generate_markdown(self) -> str:
        """
        Generate markdown documentation for the Application Design section
        of our best practices guide.
        """
        return f"""
## Application Design & Structure

* Organize code into logical packages; include `__init__.py`.
* **Use `logging`**, not `print()`, for diagnostics and errors.
* Manage configuration via **TOML** (`pyproject.toml`) or environment variables.
* Write robust **error handling** with specific exceptions; avoid bare `except Exception`.
* Follow **DRY** and **Explicit is better than implicit (PEP 20)** principles.
* For CLI apps, use **`argparse`**, **`typer`**, or **`click`**.
* Leverage **`asyncio`** (`async`/`await`) and libraries like `httpx` for I/O-bound concurrency.

### Mandatory Design Principles: DRY & SOLID

| Acronym                        | Core Idea                                                                                    | Practical Enforcement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------ | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DRY**(Don't Repeat Yourself) | Every piece of knowledge must have a single, unambiguous representation within the codebase. | • Centralize shared logic in functions or classes.• Extract common constants/config values.• Use parametrized tests to avoid duplicate cases.• Document conventions in `docs/` to prevent ad-hoc re-implementation.                                                                                                                                                                                                                                                                                                                                                                                            |
| **SOLID**                      | Five principles that promote maintainable, extensible OOP designs.                           | **S** Single-Responsibility: Each module/class handles one concern.**O** Open-Closed: Classes are open for extension, closed for modification—use inheritance or composition instead of editing core.**L** Liskov Substitution: Subclasses should be drop-in replacements for their base types; respect type contracts and Pydantic model invariants.**I** Interface Segregation: Prefer small, focused ABCs or Protocols over monolithic ones.**D** Dependency Inversion: Depend on abstractions (e.g., type-hinted protocols) not concrete details; inject collaborators via constructor or function params. |

Embed DRY/SOLID checks in **code reviews** and **CI lint rules**—e.g., flag duplicate code with Ruff (`RUF013`-series) and enforce complexity thresholds (`flake8-cyclomatic-complexity`).

### CLI Skeleton (typer)

```python
# cli.py
import typer

app = typer.Typer()

@app.command()
def hello(name: str):
    \"\"\"Say hello.\"\"\"
    typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
    app()
```

Run: `python -m cli hello --name Pedro`.

### Recommended Project Structures

A well-defined project structure is crucial for maintainability, collaboration, and scalability. While the specific layout can vary depending on the project type, consistency within a project is key.

**Web Applications (FastAPI / Flask / Django)**

This structure emphasizes separation of application code (`src/`) from tests, scripts, and configuration.

```text
<root>/
├── src/
│   └── <app_name>/     # Main application package
│       ├── __init__.py
│       ├── api/          # API endpoints/routers 
│       ├── core/         # Core logic, configuration loading
│       ├── models/       # Pydantic models / ORM models
│       ├── schemas/      # Pydantic schemas for API validation
│       ├── services/     # Business logic layer
│       └── main.py       # Application entry point
├── tests/              # All tests (unit, integration, e2e)
│   ├── __init__.py
│   ├── conftest.py     # Pytest fixtures
│   ├── integration/
│   └── unit/
├── docs/               # Documentation
├── .env.example        # Example environment variables
├── pyproject.toml      # Project configuration
└── README.md           # Project documentation
```

**CLI Tools (Typer / Click / Argparse)**

Similar to web apps, often using a `src/` layout, but the internal structure reflects CLI commands and logic.

```text
<root>/
├── src/
│   └── <cli_tool_name>/
│       ├── __init__.py
│       ├── cli.py        # Main Typer/Click app definition
│       ├── commands/     # Subcommands module
│       └── core/         # Core logic accessed by commands
├── tests/
├── pyproject.toml
└── README.md
```

Choose the structure that best fits the project's current needs and anticipated future complexity. Adhering to these patterns promotes consistency across projects.
"""
    
    def __str__(self):
        """String representation"""
        return f"{self.name}: Strategies for structuring Python applications and applying design principles"


# Run the demo if this file is executed directly
if __name__ == "__main__":
    app_design = ApplicationDesignAndStructure()
    app_design.run_demo()