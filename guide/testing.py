#!/usr/bin/env python3
"""
Testing - Living Documentation

This module demonstrates testing best practices (§5 in our guide) through active
examples and clear explanations. It shows how to write effective tests, structure
test suites, and implement test-driven development.

Key concepts demonstrated:
- pytest for testing
- Test organization and structure
- Test-driven development (TDD)
- Mocking and fixtures
- Parameterization
- Coverage measurement

Run this file directly to see a narrated demonstration of testing best practices.
"""

import os
import sys
import json
import re
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
import time
import inspect
import contextlib

# Try importing testing libraries
try:
    import pytest
    import pytest_mock
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    # Create minimal placeholders for demo purposes
    class pytest:
        @staticmethod
        def mark(function=None, **kwargs):
            return function if function else lambda f: f
        
        @staticmethod
        def fixture(**kwargs):
            return lambda f: f
        
        @staticmethod
        def raises(*args, **kwargs):
            @contextlib.contextmanager
            def context_manager():
                try:
                    yield
                except Exception:
                    pass
                else:
                    pass
            return context_manager()
    
    class pytest_mock:
        class MockFixture:
            def patch(self, *args, **kwargs):
                return lambda f: f


@dataclass
class TestingPattern:
    """
    Represents a testing pattern or technique with examples.
    """
    name: str
    description: str
    example: str


class TestingPractices:
    """
    Testing Practices
    
    This class demonstrates best practices for testing Python applications
    as defined in §5 of our guide.
    """
    
    def __init__(self):
        """Initialize with testing practices from §5 of our guide."""
        self.name = "Testing"
        
        # Set up logger
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Testing patterns
        self.testing_patterns = [
            TestingPattern(
                name="Test Function",
                description="Basic test function that verifies a piece of functionality",
                example="""
def test_add():
    \"\"\"Test that the add function works correctly.\"\"\"
    # Arrange
    a = 1
    b = 2
    expected = 3
    
    # Act
    result = add(a, b)
    
    # Assert
    assert result == expected, f"Expected {expected} but got {result}"
"""
            ),
            TestingPattern(
                name="Test Class",
                description="Class-based test organization for related test cases",
                example="""
class TestCalculator:
    \"\"\"Tests for the Calculator class.\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixture before each test method.\"\"\"
        self.calculator = Calculator()
    
    def test_add(self):
        \"\"\"Test addition.\"\"\"
        assert self.calculator.add(1, 2) == 3
    
    def test_subtract(self):
        \"\"\"Test subtraction.\"\"\"
        assert self.calculator.subtract(5, 3) == 2
    
    def test_multiply(self):
        \"\"\"Test multiplication.\"\"\"
        assert self.calculator.multiply(2, 3) == 6
    
    def test_divide(self):
        \"\"\"Test division.\"\"\"
        assert self.calculator.divide(6, 2) == 3
"""
            ),
            TestingPattern(
                name="Fixture",
                description="Reusable test data or setup code",
                example="""
@pytest.fixture
def sample_data():
    \"\"\"Provide sample data for tests.\"\"\"
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
    }

def test_find_user(sample_data):
    \"\"\"Test finding a user by ID.\"\"\"
    user_service = UserService(sample_data["users"])
    user = user_service.find_by_id(1)
    assert user is not None
    assert user["name"] == "Alice"
"""
            ),
            TestingPattern(
                name="Mock",
                description="Replace real objects with test doubles",
                example="""
def test_send_email(mocker):
    \"\"\"Test email sending with a mock.\"\"\"
    # Create a mock for the email service
    mock_email_service = mocker.patch("myapp.services.email_service")
    
    # Setup the notification service with the mock
    notification_service = NotificationService()
    
    # Call the method being tested
    notification_service.notify_user("test@example.com", "Test message")
    
    # Verify the mock was called correctly
    mock_email_service.send_email.assert_called_once_with(
        to="test@example.com",
        subject="Notification",
        body="Test message"
    )
"""
            ),
            TestingPattern(
                name="Parameterization",
                description="Run the same test with different inputs",
                example="""
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 3),    # Test case 1: 1 + 2 = 3
        (0, 0, 0),    # Test case 2: 0 + 0 = 0
        (-1, 1, 0),   # Test case 3: -1 + 1 = 0
        (10, -5, 5)   # Test case 4: 10 + (-5) = 5
    ]
)
def test_add_parameterized(a, b, expected):
    \"\"\"Test addition with multiple input combinations.\"\"\"
    result = add(a, b)
    assert result == expected, f"{a} + {b} should equal {expected}, got {result}"
"""
            ),
            TestingPattern(
                name="Exception Testing",
                description="Verify that exceptions are raised correctly",
                example="""
def test_divide_by_zero():
    \"\"\"Test that division by zero raises ValueError.\"\"\"
    calculator = Calculator()
    
    with pytest.raises(ValueError) as exc_info:
        calculator.divide(5, 0)
    
    # Optionally verify the exception message
    assert "division by zero" in str(exc_info.value)
"""
            ),
            TestingPattern(
                name="Setup and Teardown",
                description="Prepare environment before tests and clean up after",
                example="""
def test_with_temp_file():
    \"\"\"Test with a temporary file that gets cleaned up.\"\"\"
    # Setup
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"Test data")
    temp_file.close()
    
    try:
        # Test
        with open(temp_file.name, "r") as f:
            content = f.read()
        assert content == "Test data"
    finally:
        # Teardown
        os.unlink(temp_file.name)
"""
            ),
            TestingPattern(
                name="Integration Test",
                description="Test multiple components working together",
                example="""
def test_user_registration_flow():
    \"\"\"
    Integration test for the complete user registration flow.
    
    This tests the UserService, EmailService, and DatabaseService working together.
    \"\"\"
    # Setup test database
    db_service = DatabaseService(":memory:")
    db_service.create_tables()
    
    # Mock email service to avoid sending real emails
    mock_email_service = MockEmailService()
    
    # Initialize user service with dependencies
    user_service = UserService(db_service, mock_email_service)
    
    # Execute the registration flow
    result = user_service.register(
        username="newuser",
        email="newuser@example.com",
        password="securepass123"
    )
    
    # Verify user was created in database
    user = db_service.find_user_by_username("newuser")
    assert user is not None
    assert user["email"] == "newuser@example.com"
    
    # Verify welcome email was "sent"
    assert len(mock_email_service.sent_emails) == 1
    email = mock_email_service.sent_emails[0]
    assert email["to"] == "newuser@example.com"
    assert "Welcome" in email["subject"]
    
    # Verify overall result
    assert result["success"] is True
"""
            )
        ]
    
    def demonstrate_test_organization(self):
        """
        Demonstrate how to organize tests in a project.
        
        This method shows the recommended directory structure and naming
        conventions for tests.
        """
        print("\n" + "=" * 80)
        print("📁 TEST ORGANIZATION")
        print("=" * 80)
        print("✨ Following §5: 'Write Tests using pytest'")
        
        # Create a sample project structure
        print("\n📋 Recommended Test Directory Structure:")
        
        folder_structure = """
project_root/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       ├── services.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   └── test_api.py
│   └── e2e/                     # End-to-end tests
│       ├── __init__.py
│       └── test_workflows.py
├── pyproject.toml               # Project config with pytest settings
└── .coveragerc                  # Coverage configuration
"""
        print(folder_structure)
        
        # Explain test file naming conventions
        print("\n📝 Test File Naming Conventions:")
        print("  • All test files should be prefixed with 'test_'")
        print("  • Test files should have the same name as the module they're testing")
        print("  • Test functions should be prefixed with 'test_'")
        print("  • Test classes should be prefixed with 'Test'")
        
        # Show pytest configuration
        print("\n📄 Pytest Configuration in pyproject.toml:")
        pytest_config = """
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
python_classes = "Test*"
addopts = "--strict-markers --cov=src --cov-report=term-missing"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Tests that take a long time to run",
]
"""
        print(pytest_config)
        
        # Coverage configuration
        print("\n📄 Coverage Configuration in .coveragerc:")
        coverage_config = """
[run]
source = src
omit = tests/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    raise ImportError
"""
        print(coverage_config)
        
        print("\n📝 Best Practices for Test Organization:")
        print("  • Separate tests by type (unit, integration, e2e)")
        print("  • Use fixtures to share setup code")
        print("  • Define test markers for categorization")
        print("  • Configure coverage reporting")
        print("  • Include test directories in Python package")
    
    def demonstrate_pytest_features(self):
        """
        Demonstrate key pytest features for effective testing.
        
        This method shows how to use pytest fixtures, parameterization,
        and other features.
        """
        print("\n" + "=" * 80)
        print("🧪 PYTEST FEATURES")
        print("=" * 80)
        print("✨ Following §5: 'Write Tests using pytest'")
        
        # Show fixtures example in conftest.py
        print("\n📄 Shared Fixtures in conftest.py:")
        conftest_example = """
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from myapp.models import Base
from myapp.services import UserService, EmailService

@pytest.fixture
def temp_file():
    """Create a temporary file that is cleaned up after the test."""
    fd, path = tempfile.mkstemp()
    try:
        yield path
    finally:
        os.close(fd)
        os.unlink(path)

@pytest.fixture
def db_session():
    """Create an in-memory SQLite database session."""
    # Create an in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:")
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create a session factory
    SessionLocal = sessionmaker(bind=engine)
    
    # Create a session
    session = SessionLocal()
    
    try:
        # Return the session to the test
        yield session
    finally:
        # Close and rollback the session after the test
        session.rollback()
        session.close()

@pytest.fixture
def mock_email_service(mocker):
    """Create a mock email service."""
    service = mocker.Mock(spec=EmailService)
    service.send_email.return_value = True
    return service

@pytest.fixture
def user_service(db_session, mock_email_service):
    """Create a user service with mocked dependencies."""
    return UserService(db_session, mock_email_service)
"""
        print(conftest_example)
        
        # Show parameterization example
        print("\n📄 Test Parameterization Example:")
        parameterization_example = """
import pytest
from myapp.utils import validate_email

@pytest.mark.parametrize(
    "email,is_valid",
    [
        ("user@example.com", True),      # Valid email
        ("user.name@example.co.uk", True),  # Valid with subdomain
        ("user+tag@example.com", True),  # Valid with + tag
        ("user@.com", False),            # Invalid: missing domain
        ("user@example", False),         # Invalid: missing TLD
        ("user.example.com", False),     # Invalid: missing @
        ("@example.com", False),         # Invalid: missing username
        ("user@@example.com", False),    # Invalid: double @
    ],
    ids=[
        "simple_valid",
        "subdomain_valid",
        "plus_tag_valid",
        "missing_domain",
        "missing_tld",
        "missing_at",
        "missing_username",
        "double_at"
    ]
)
def test_validate_email(email, is_valid):
    """Test email validation with various inputs."""
    assert validate_email(email) == is_valid
"""
        print(parameterization_example)
        
        # Show integration test with fixture composition
        print("\n📄 Integration Test with Fixture Composition:")
        integration_example = """
import pytest
from myapp.models import User
from myapp.services import AuthService

@pytest.fixture
def user_in_db(db_session):
    """Create a test user in the database."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password="$2b$12$JMbCkKI/6yZDn9GUmh.a7.e1OFVBq.e7FuqK7CdZl6A/EEHiqdNi2"  # "password"
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_user_authentication(db_session, user_in_db):
    """Test that a user can authenticate with correct credentials."""
    # Arrange
    auth_service = AuthService(db_session)
    
    # Act
    result = auth_service.authenticate("testuser@example.com", "password")
    
    # Assert
    assert result is not None
    assert result.username == "testuser"
    assert result.email == "testuser@example.com"

def test_failed_authentication(db_session, user_in_db):
    """Test that authentication fails with incorrect password."""
    # Arrange
    auth_service = AuthService(db_session)
    
    # Act
    result = auth_service.authenticate("testuser@example.com", "wrong_password")
    
    # Assert
    assert result is None
"""
        print(integration_example)
        
        # Show test markers
        print("\n📄 Using Test Markers:")
        markers_example = """
import pytest

@pytest.mark.unit
def test_simple_calculation():
    """A simple unit test."""
    assert 1 + 1 == 2

@pytest.mark.integration
def test_database_integration(db_session):
    """Test database integration."""
    # Test database operations
    pass

@pytest.mark.slow
@pytest.mark.e2e
def test_complete_workflow():
    """A slow end-to-end test."""
    # Test a complete workflow
    pass
"""
        print(markers_example)
        
        # Show running tests with markers
        print("\n📝 Running Tests with Markers:")
        print("  • Run unit tests only: pytest -m unit")
        print("  • Run integration tests only: pytest -m integration")
        print("  • Run e2e tests only: pytest -m e2e")
        print("  • Run non-slow tests: pytest -m 'not slow'")
        print("  • Run unit or integration tests: pytest -m 'unit or integration'")
        
        print("\n📝 Key pytest Features:")
        print("  • Fixtures for reusable test setup and dependencies")
        print("  • Parameterization for testing multiple inputs")
        print("  • Markers for categorizing tests")
        print("  • Fixture composition for complex test scenarios")
        print("  • Automatic test discovery")
    
    def demonstrate_tdd(self):
        """
        Demonstrate the Test-Driven Development (TDD) process.
        
        This method shows the RED-GREEN-REFACTOR cycle with examples.
        """
        print("\n" + "=" * 80)
        print("🔄 TEST-DRIVEN DEVELOPMENT (TDD)")
        print("=" * 80)
        print("✨ Following §5.1: 'Test-Driven Development (TDD) — RED → GREEN → REFACTOR'")
        
        print("\n📋 TDD Cycle:")
        print("  1. RED: Write a failing test")
        print("  2. GREEN: Implement the minimal code to make the test pass")
        print("  3. REFACTOR: Improve the code while keeping tests passing")
        
        # TDD Example: Implementing a password validation function
        print("\n📄 TDD Example: Password Validation")
        
        # Step 1: RED - Write a failing test
        print("\n1️⃣ RED - Write a failing test:")
        red_test = """
# test_password_validator.py
import pytest
from myapp.validators import validate_password

def test_password_length_validation():
    """Test that passwords must be at least 8 characters."""
    # Too short password
    assert validate_password("short") is False
    
    # Minimum length password
    assert validate_password("password") is True
"""
        print(red_test)
        print("\n⚠️ Running this test would fail because the function doesn't exist yet.")
        
        # Step 2: GREEN - Implement minimal code to pass
        print("\n2️⃣ GREEN - Implement minimal code to pass:")
        green_code = """
# myapp/validators.py
def validate_password(password):
    """Validate a password meets security requirements."""
    # Minimum password length validation
    return len(password) >= 8
"""
        print(green_code)
        print("\n✅ Now the test passes because the function meets the minimal requirements.")
        
        # Step 3: Add more tests for additional requirements
        print("\n3️⃣ Add more requirements (back to RED):")
        more_tests = """
def test_password_complexity():
    """Test that passwords must contain mixed case letters and numbers."""
    # Missing uppercase
    assert validate_password("password123") is False
    
    # Missing lowercase
    assert validate_password("PASSWORD123") is False
    
    # Missing number
    assert validate_password("PasswordABC") is False
    
    # Valid complex password
    assert validate_password("Password123") is True
"""
        print(more_tests)
        print("\n⚠️ These tests would fail because the implementation doesn't check complexity.")
        
        # Step 4: Update implementation to pass all tests
        print("\n4️⃣ Update implementation (back to GREEN):")
        updated_code = """
def validate_password(password):
    """Validate a password meets security requirements."""
    # Check minimum length
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase letter
    if not any(char.isupper() for char in password):
        return False
    
    # Check for at least one lowercase letter
    if not any(char.islower() for char in password):
        return False
    
    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return False
    
    # All checks passed
    return True
"""
        print(updated_code)
        print("\n✅ Now all tests pass with the updated implementation.")
        
        # Step 5: Refactor the code
        print("\n5️⃣ REFACTOR - Improve the code while keeping tests passing:")
        refactored_code = """
import re

def validate_password(password):
    """Validate a password meets security requirements."""
    # Use a single regular expression for all checks
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    return bool(re.match(pattern, password))
"""
        print(refactored_code)
        print("\n✅ The code is now more concise but still passes all tests.")
        
        # Final step: Add even more requirements
        print("\n6️⃣ Continue the cycle with more requirements:")
        special_char_test = """
def test_password_special_char():
    """Test that passwords must contain at least one special character."""
    # Missing special character
    assert validate_password("Password123") is False
    
    # Valid password with special character
    assert validate_password("Password123!") is True
"""
        print(special_char_test)
        
        # Updated implementation
        final_code = """
import re

def validate_password(password):
    """Validate a password meets security requirements."""
    # Updated pattern to require special character
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
    return bool(re.match(pattern, password))
"""
        print("\nFinal implementation:")
        print(final_code)
        
        print("\n📝 TDD Benefits:")
        print("  • Forces clear requirements and test cases")
        print("  • Ensures code is testable by design")
        print("  • Builds a comprehensive test suite")
        print("  • Encourages minimal, focused implementations")
        print("  • Provides confidence during refactoring")
    
    def demonstrate_mocking(self):
        """
        Demonstrate mocking techniques for isolating units in tests.
        
        This method shows how to use mocks to replace dependencies.
        """
        print("\n" + "=" * 80)
        print("🎭 MOCKING")
        print("=" * 80)
        print("✨ Following §5: 'Keep tests isolated with mocks'")
        
        # Show mocking an HTTP client
        print("\n📄 Mocking HTTP Requests:")
        http_mock = """
import pytest
from myapp.services import UserService

def test_get_user_details(mocker):
    """Test that the user service correctly processes user details from the API."""
    # Create a mock HTTP response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 123,
        "name": "Test User",
        "email": "test@example.com",
        "role": "admin"
    }
    
    # Mock the requests.get method to return our mock response
    mock_requests = mocker.patch("myapp.services.requests")
    mock_requests.get.return_value = mock_response
    
    # Create the service and call the method under test
    service = UserService(api_url="https://api.example.com")
    user = service.get_user_details(user_id=123)
    
    # Verify the service correctly processed the API response
    assert user.id == 123
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.role == "admin"
    
    # Verify the service called the API with the correct URL
    mock_requests.get.assert_called_once_with(
        "https://api.example.com/users/123",
        headers={"Authorization": "Bearer fake-token"}
    )
"""
        print(http_mock)
        
        # Show mocking a database
        print("\n📄 Mocking Database Interactions:")
        db_mock = """
def test_create_user(mocker):
    """Test user creation without hitting a real database."""
    # Create a mock database session
    mock_session = mocker.Mock()
    
    # Mock the User model and its behavior
    mock_user = mocker.Mock()
    mock_user.id = 1
    mock_user.username = "newuser"
    mock_user.email = "newuser@example.com"
    
    # Configure the mock session's behavior
    # When session.add() is called with any User object, store it for later
    mock_session.add.side_effect = lambda user: setattr(mock_user, "username", user.username)
    
    # When session.query(User).filter_by().first() is called, return None to simulate user not found
    query_mock = mocker.Mock()
    filter_mock = mocker.Mock()
    filter_mock.first.return_value = None
    query_mock.filter_by.return_value = filter_mock
    mock_session.query.return_value = query_mock
    
    # Create the service with the mock session
    user_service = UserService(db_session=mock_session)
    
    # Call the method under test
    result = user_service.create_user(
        username="newuser",
        email="newuser@example.com",
        password="password123"
    )
    
    # Verify the result
    assert result["success"] is True
    assert result["user_id"] == 1
    
    # Verify the correct database calls were made
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
"""
        print(db_mock)
        
        # Show mocking filesystem operations
        print("\n📄 Mocking Filesystem Operations:")
        fs_mock = """
def test_save_config(mocker, tmp_path):
    """Test config file saving without writing to the real filesystem."""
    # Create a temporary directory using pytest's tmp_path fixture
    config_path = tmp_path / "config.json"
    
    # Mock the open() function to track calls and return a file-like object
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    
    # Create the config service
    config_service = ConfigService(config_path=str(config_path))
    
    # Call the method under test
    config_service.save_config({"setting1": "value1", "setting2": 123})
    
    # Verify open() was called correctly
    mock_open.assert_called_once_with(str(config_path), "w")
    
    # Verify the correct data was written
    file_handle = mock_open()
    file_handle.write.assert_called_once_with('{"setting1": "value1", "setting2": 123}')
"""
        print(fs_mock)
        
        # Show mocking time
        print("\n📄 Mocking Time and Dates:")
        time_mock = """
from datetime import datetime, timedelta

def test_is_token_expired(mocker):
    """Test token expiration checking with a mocked current time."""
    # Mock the datetime.now() method
    mock_now = datetime(2025, 5, 12, 12, 0, 0)  # May 12, 2025, 12:00:00
    mocker.patch("myapp.auth.datetime", autospec=True)
    myapp.auth.datetime.now.return_value = mock_now
    
    # Create a token with an expiration 30 minutes in the future
    token_expiration = mock_now + timedelta(minutes=30)
    token = {"exp": token_expiration.timestamp()}
    
    # Check that the token is not expired
    auth_service = AuthService()
    assert auth_service.is_token_expired(token) is False
    
    # Now set the current time to 1 hour in the future
    myapp.auth.datetime.now.return_value = mock_now + timedelta(hours=1)
    
    # Check that the token is now expired
    assert auth_service.is_token_expired(token) is True
"""
        print(time_mock)
        
        print("\n📝 Mocking Best Practices:")
        print("  • Only mock at the boundaries of your system")
        print("  • Mock dependencies, not the system under test")
        print("  • Use the 'mocker' fixture from pytest-mock")
        print("  • Verify both return values and interactions")
        print("  • Don't mock everything - use real objects where possible")
        print("  • Set up mocks with the minimum required behavior")
    
    def demonstrate_test_coverage(self):
        """
        Demonstrate measuring and enforcing test coverage.
        
        This method shows how to use pytest-cov to measure coverage.
        """
        print("\n" + "=" * 80)
        print("📊 TEST COVERAGE")
        print("=" * 80)
        print("✨ Following §5.2: 'Running Pytest & Enforcing Coverage'")
        
        # Command examples
        print("\n📋 Coverage Commands:")
        print("  • Basic testing with coverage: pytest --cov=myapp")
        print("  • Testing with coverage report: pytest --cov=myapp --cov-report=term")
        print("  • Testing with missing lines report: pytest --cov=myapp --cov-report=term-missing")
        print("  • Testing with HTML report: pytest --cov=myapp --cov-report=html")
        print("  • Fail if coverage below threshold: pytest --cov=myapp --cov-fail-under=80")
        
        # GitHub Actions workflow for coverage
        print("\n📄 GitHub Actions Workflow with Coverage:")
        gh_actions = """
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
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
          pip install pytest pytest-cov
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term --cov-fail-under=70
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
"""
        print(gh_actions)
        
        # Coverage badge in README
        print("\n📄 Coverage Badge in README.md:")
        badge = """
# My Project

[![Tests](https://github.com/username/project/actions/workflows/tests.yml/badge.svg)](https://github.com/username/project/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/username/project/branch/main/graph/badge.svg)](https://codecov.io/gh/username/project)

Project description here...
"""
        print(badge)
        
        # HTML coverage report example (text representation)
        print("\n📄 HTML Coverage Report (example):")
        html_coverage = """
COVERAGE REPORT
==============================================================================
Name                        Stmts   Miss  Cover   Missing
--------------------------------------------------------------
src/myapp/__init__.py           2      0   100%
src/myapp/models.py            45      2    96%   72, 89
src/myapp/services.py          78     12    85%   55-61, 102-110
src/myapp/utils.py             32      8    75%   82-89
--------------------------------------------------------------
TOTAL                         157     22    86%
"""
        print(html_coverage)
        
        print("\n📝 Coverage Policy from §5.2:")
        print("  • Minimum acceptable coverage: 70%")
        print("  • Desired target coverage: ≥ 80%")
        print("  • CI should fail if coverage < 70%")
        print("  • Teams can raise the threshold after reaching 80%")
    
    def create_demo_project(self):
        """
        Create a demo project with tests to show testing practices in action.
        
        This method generates a sample project with tests.
        """
        print("\n" + "=" * 80)
        print("💻 DEMO PROJECT WITH TESTS")
        print("=" * 80)
        print("✨ Creating a sample project with tests to demonstrate practices")
        
        # Create a directory structure
        demo_dir = Path("./testing_demo")
        demo_dir.mkdir(exist_ok=True)
        
        # Create a source directory
        src_dir = demo_dir / "src" / "calculator"
        src_dir.mkdir(exist_ok=True, parents=True)
        
        # Create a tests directory
        tests_dir = demo_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Create source files
        init_file = src_dir / "__init__.py"
        with open(init_file, "w") as f:
            f.write('"""Calculator package."""\n\n')
            f.write('__version__ = "0.1.0"\n')
        
        calculator_file = src_dir / "calculator.py"
        with open(calculator_file, "w") as f:
            f.write("""
\"\"\"
Calculator module that provides basic arithmetic operations.

This module demonstrates testing best practices by providing a simple
calculator implementation that can be easily tested.
\"\"\"

class Calculator:
    \"\"\"A simple calculator that performs basic arithmetic operations.\"\"\"
    
    def add(self, a, b):
        \"\"\"Add two numbers and return the result.\"\"\"
        return a + b
    
    def subtract(self, a, b):
        \"\"\"Subtract b from a and return the result.\"\"\"
        return a - b
    
    def multiply(self, a, b):
        \"\"\"Multiply two numbers and return the result.\"\"\"
        return a * b
    
    def divide(self, a, b):
        \"\"\"Divide a by b and return the result.
        
        Args:
            a: The dividend
            b: The divisor
            
        Returns:
            The quotient
            
        Raises:
            ValueError: If b is zero
        \"\"\"
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
""")
        
        # Create test files
        test_init = tests_dir / "__init__.py"
        with open(test_init, "w") as f:
            f.write('"""Calculator test package."""\n')
        
        conftest_file = tests_dir / "conftest.py"
        with open(conftest_file, "w") as f:
            f.write("""
\"\"\"Shared test fixtures for calculator tests.\"\"\"

import pytest
from src.calculator.calculator import Calculator

@pytest.fixture
def calculator():
    \"\"\"Return a Calculator instance.\"\"\"
    return Calculator()
""")
        
        test_calculator_file = tests_dir / "test_calculator.py"
        with open(test_calculator_file, "w") as f:
            f.write("""
\"\"\"Tests for the calculator module.\"\"\"

import pytest
from src.calculator.calculator import Calculator

def test_calculator_creation():
    \"\"\"Test that a Calculator instance can be created.\"\"\"
    calc = Calculator()
    assert isinstance(calc, Calculator)

class TestCalculator:
    \"\"\"Tests for the Calculator class.\"\"\"
    
    def test_add(self, calculator):
        \"\"\"Test addition.\"\"\"
        assert calculator.add(1, 2) == 3
        
    def test_subtract(self, calculator):
        \"\"\"Test subtraction.\"\"\"
        assert calculator.subtract(5, 3) == 2
        
    def test_multiply(self, calculator):
        \"\"\"Test multiplication.\"\"\"
        assert calculator.multiply(2, 3) == 6
        
    def test_divide(self, calculator):
        \"\"\"Test division.\"\"\"
        assert calculator.divide(6, 2) == 3
        
    def test_divide_by_zero(self, calculator):
        \"\"\"Test that division by zero raises a ValueError.\"\"\"
        with pytest.raises(ValueError) as exc_info:
            calculator.divide(1, 0)
        assert "Cannot divide by zero" in str(exc_info.value)

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
        (100, 200, 300)
    ]
)
def test_add_parameterized(calculator, a, b, expected):
    \"\"\"Test addition with multiple input combinations.\"\"\"
    assert calculator.add(a, b) == expected
""")
        
        # Create pyproject.toml
        pyproject_file = demo_dir / "pyproject.toml"
        with open(pyproject_file, "w") as f:
            f.write("""
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "calculator"
version = "0.1.0"
description = "A simple calculator package"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    { name = "Example User", email = "user@example.com" }
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
python_classes = "Test*"
addopts = "--strict-markers --cov=src"
markers = [
    "unit: Unit tests",
]
""")
        
        # Create README.md
        readme_file = demo_dir / "README.md"
        with open(readme_file, "w") as f:
            f.write("""# Calculator

A simple calculator package that demonstrates testing best practices.

## Installation

```bash
pip install -e .
```

## Usage

```python
from calculator.calculator import Calculator

calc = Calculator()
result = calc.add(1, 2)
print(result)  # Output: 3
```

## Testing

Run the tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src
```
""")
        
        print(f"\n📁 Created demo project at {demo_dir}")
        print("\n📝 Project Structure:")
        print(f"  • Source code: {src_dir}")
        print(f"  • Tests: {tests_dir}")
        print(f"  • Configuration: {pyproject_file}")
        print(f"  • Documentation: {readme_file}")
        
        # Create instructions for running the tests
        print("\n📋 To Run the Tests:")
        print(f"  1. cd {demo_dir}")
        print("  2. Install pytest: pip install pytest pytest-cov")
        print("  3. Run the tests: pytest")
        print("  4. Run with coverage: pytest --cov=src")
        
        return demo_dir
    
    def run_demo(self):
        """Run a comprehensive demonstration of testing best practices."""
        print("\n" + "=" * 80)
        print("🚀 TESTING PRACTICES DEMONSTRATION")
        print(f"✨ Demonstrating §5 of the Python Development Best Practices")
        print("=" * 80)
        
        print("\n📋 This demonstration will show you:")
        print("  1. Test Organization")
        print("  2. pytest Features")
        print("  3. Test-Driven Development")
        print("  4. Mocking")
        print("  5. Test Coverage")
        print("  6. Demo Project with Tests")
        
        # Demonstrate each component
        self.demonstrate_test_organization()
        self.demonstrate_pytest_features()
        self.demonstrate_tdd()
        self.demonstrate_mocking()
        self.demonstrate_test_coverage()
        
        # Ask if the user wants to create the demo project
        print("\n📁 Would you like to create a demo project with tests?")
        print("  1. Yes - Create the demo project")
        print("  2. No - Skip this step")
        
        try:
            choice = input("Enter your choice (1-2): ").strip()
            if choice == "1":
                self.create_demo_project()
            else:
                print("Skipping demo project creation.")
        except Exception as e:
            print(f"Error: {e}")
            print("Skipping demo project creation.")
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nRecommended next steps:")
        print("  1. Start writing tests first (TDD)")
        print("  2. Organize tests by type and module")
        print("  3. Use fixtures for reusable test setup")
        print("  4. Mock dependencies to isolate units")
        print("  5. Measure and enforce test coverage")
        print("  6. Run tests automatically in CI/CD")
    
    def generate_markdown(self) -> str:
        """
        Generate markdown documentation for the Testing section
        of our best practices guide.
        """
        return """
## Testing

* **Write Tests** using **`pytest`** as the default framework (rich fixtures, parametrization, and plug-ins).
* Include unit, integration, and end-to-end tests.
* Keep tests isolated with mocks (`unittest.mock`, `pytest-mock`) and factories.
* Automate tests in CI/CD; tools like `tox` or `nox` run across Python versions.

**Mocking HTTP**

```python
import responses, httpx

@responses.activate
def test_create_invoice():
    responses.add(responses.POST, "https://api.stripe.com/v1/invoices", json={"id": "inv_1"}, status=200)
    resp = httpx.post("https://api.stripe.com/v1/invoices", data={…})
    assert resp.json()["id"] == "inv_1"
```

### Test-Driven Development (TDD) — RED → GREEN → REFACTOR

Follow this loop for every new feature or bug-fix unless explicitly instructed otherwise.

| Phase                             | Command Example                   | Expectation                                          |
| --------------------------------- | --------------------------------- | ---------------------------------------------------- |
| **1. Write a failing test (RED)** | `pytest -k new_feature -q`        | The new test fails (assertions trigger).             |
| **2. Implement the minimal code** | edit source files                 | Only add what's necessary for the test to pass.      |
| **3. Run the suite (GREEN)**      | `pytest -q`                       | All tests pass.                                      |
| **4. Refactor safely**            | improve names, remove duplication | No behavior change; run `pytest -q` after each step. |

> **Rule — Tests are authoritative:** Code must satisfy tests; do **not** alter tests merely to make them pass unless the specification itself has legitimately changed **and you explicitly instruct otherwise**.

Embed this cycle into your daily workflow (IDE test runner, `uv pip sync && pytest -q` watch scripts, etc.) to keep the codebase robust and regression-free.

### Running Pytest & Enforcing Coverage

| Goal                             | Command                                                                          | Notes                                           |
| -------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------- |
| Run the full suite, quiet output | `pytest -q`                                                                      | Fast feedback loop while coding.                |
| Run tests matching a keyword     | `pytest -k "billing and not slow" -q`                                            | Combine expressions for fine-grained selection. |
| Run a single file or directory   | `pytest tests/api/test_users.py -q`                                              | Paths are relative to repo root.                |
| Collect-only (no execution)      | `pytest --collect-only`                                                          | Inspect discovered tests.                       |
| **Run with coverage**            | `pytest --cov=<package_or_srcdir> --cov-report=term`                             | Shows annotated summary in terminal.            |
| **Fail when coverage < 70%**     | `pytest --cov=<package_or_srcdir> --cov-fail-under=70 --cov-report=term-missing` | The CI pipeline must include this gate.         |

**Coverage Policy**

* **Minimum acceptable:** 70% statement coverage (`--cov-fail-under=70`).
* **Desired target:** ≥ 80% on mainline / release branches.

CI should treat < 70% coverage as a failure. Teams are encouraged to raise the threshold incrementally once 80% has been met sustainably.

Add this step to your CI workflow (GitHub Actions example):

```yaml
- name: Run pytest with coverage
  run: |
    uv pip sync
    pytest --cov=src --cov-fail-under=70 --cov-report=xml
```

> Tip: For local pre-push checks, add a **pre-commit** stage using the [`pytest-pre-commit` hook](https://github.com/kevin1024/pytest-pre-commit) or simply invoke the same coverage command in a `pre-push` script.
"""
    
    def __str__(self):
        """String representation"""
        return f"{self.name}: Strategies for effective testing in Python applications"


# Run the demo if this file is executed directly
if __name__ == "__main__":
    testing = TestingPractices()
    testing.run_demo()