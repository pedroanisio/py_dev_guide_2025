#!/usr/bin/env python3
"""
Environment Management & Setup - Living Documentation

This module demonstrates best practices for Python project environment setup,
repository management, and dependency handling while narrating the principles
behind them (§1 in our best practices guide).

Key concepts demonstrated:
- Virtual environment management with uv
- Project configuration with pyproject.toml
- Multi-environment patterns (.env files)
- Git repository initialization
- Dependency handling

Run this file directly to see a narrated demonstration of these concepts.
"""

import logging
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union

# Try to import other modules
try:
    from observability import LoggingObservabilityStandards
except ImportError:
    # Create a minimal logger if the observability module isn't available
    class LoggingObservabilityStandards:
        def __init__(self):
            pass
        def create_basic_jsonl_logger(self):
            import logging
            logger = logging.getLogger("environment")
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            return logger


@dataclass
class BranchingStrategy:
    """Represents a Git branching strategy as defined in §1"""
    main_branch: str
    development_branch: str
    feature_prefix: str
    bugfix_prefix: str
    hotfix_prefix: str


@dataclass
class EnvFile:
    """
    Represents an environment file according to our multi-environment pattern
    from §1 of the best practices guide.
    """
    name: str
    purpose: str
    example_content: str


class EnvironmentManagement:
    """
    Environment Management & Setup
    
    This class demonstrates best practices for Python project environment setup,
    repository management, and dependency handling as described in §1 of our guide.
    """
    
    def __init__(self):
        """Initialize with best practices from §1 of our guide."""
        self.name = "Environment Management & Setup"
        self.recommended_python_version = "3.13 (as of 2025)"
        
        # Setup structured logging (§7 integration)
        self.logging_module = LoggingObservabilityStandards()
        self.logger = self.logging_module.create_basic_jsonl_logger()
        
        # Git branching strategy - following §1
        self.branching_strategy = BranchingStrategy(
            main_branch="main",
            development_branch="dev",
            feature_prefix="feature/",
            bugfix_prefix="bugfix/",
            hotfix_prefix="hotfix/"
        )
        
        # Environment file patterns - following §1 Multi-environment pattern
        self.env_files = [
            EnvFile(
                ".env", 
                "Local development environment", 
                "DEBUG=True\nLOG_LEVEL=DEBUG\nDATABASE_URL=sqlite:///./dev.db"
            ),
            EnvFile(
                ".env.staging", 
                "Staging environment", 
                "DEBUG=False\nLOG_LEVEL=INFO\nDATABASE_URL=postgresql://user:pass@localhost/staging"
            ),
            EnvFile(
                ".env.prod", 
                "Production environment (loaded in CI/CD → Secrets Manager at runtime)", 
                "DEBUG=False\nLOG_LEVEL=WARNING\nDATABASE_URL=postgresql://user:pass@prod-db/app"
            )
        ]
        
        # Dependency management tool - following §1 Dependency Management
        self.dependency_tool = "uv"
        self.dependency_file = "pyproject.toml"
        self.lock_file = "uv.lock"
        
        # Essential commands for uv - as specified in §1
        self.uv_commands = {
            "create_venv": "uv venv",
            "install_deps": "uv pip install -r uv.lock",
            "sync_deps": "uv pip sync",
            "compile_deps": "uv pip compile",
            "check_outdated": "uv pip list --outdated",
            "upgrade_deps": "uv pip upgrade",
            "security_audit": "uv pip audit"
        }
        
        self.logger.info("Environment management initialized", 
                        python_version=self.recommended_python_version,
                        dependency_tool=self.dependency_tool)
        
    def demonstrate_env_file_creation(self, output_dir: Path = None):
        """
        Actively demonstrate the multi-environment pattern from §1 by creating
        example environment files.
        """
        print("\n" + "=" * 80)
        print("🌍 MULTI-ENVIRONMENT PATTERN DEMONSTRATION")
        print("=" * 80)
        print("✨ From §1: 'Use multiple environment files for different contexts'")
        
        if not output_dir:
            output_dir = Path("./demo_env")
            output_dir.mkdir(exist_ok=True)
            
        print(f"\n📂 Creating environment files in {output_dir}:")
        
        # GOOD PATTERN: Create multiple environment files with appropriate settings
        print("\n✅ RECOMMENDED PATTERN: Multiple env files with context-specific values")
        for env_file in self.env_files:
            env_path = output_dir / env_file.name
            with open(env_path, 'w') as f:
                f.write(f"# {env_file.purpose}\n")
                f.write(env_file.example_content)
            print(f"  • Created {env_file.name}: {env_file.purpose}")
        
        # Add .env to .gitignore
        gitignore_path = output_dir / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write("# Generated by environment.py demo\n")
            f.write("\n# Environment variables - NEVER commit these to Git\n")
            f.write(".env\n")
        print(f"  • Added .env to .gitignore")
        
        # ANTI-PATTERN: Show what not to do
        print("\n❌ ANTI-PATTERN: Hard-coded secrets directly in code")
        anti_pattern = """
# DON'T DO THIS!
DATABASE_URL = "postgresql://admin:SuperSecret123!@prod-db.example.com/app"
API_KEY = "sk_live_a1b2c3d4e5f6g7h8i9j0"

def connect_db():
    # Using hard-coded credentials 😱
    return create_connection(DATABASE_URL)
"""
        anti_pattern_path = output_dir / "anti_pattern_config.py"
        with open(anti_pattern_path, 'w') as f:
            f.write(anti_pattern)
        print(f"  • Created example of what NOT to do: {anti_pattern_path}")
        
        print("\n📝 Key principles shown:")
        print("  1. Separate environment files for different deployment contexts")
        print("  2. Exclusion of .env from version control (via .gitignore)")
        print("  3. Clear documentation of each environment file's purpose")
        print("  4. Appropriate debug levels for different environments")
        
        return output_dir
    
    def demonstrate_pyproject_toml(self, project_name: str = "example_project"):
        """
        Demonstrate the creation of a pyproject.toml file following best practices
        from §1, §2, and §5.
        """
        print("\n" + "=" * 80)
        print("📦 PYPROJECT.TOML CONFIGURATION DEMONSTRATION")
        print("=" * 80)
        print("✨ From §1: 'Declare dependencies in pyproject.toml'")
        
        pyproject_content = self.setup_pyproject_toml(project_name)
        
        # Create a demo directory
        demo_dir = Path(f"./demo_{project_name}")
        demo_dir.mkdir(exist_ok=True)
        
        # Write the pyproject.toml file
        pyproject_path = demo_dir / "pyproject.toml"
        with open(pyproject_path, 'w') as f:
            f.write(pyproject_content)
        
        print(f"\n📄 Created {pyproject_path}")
        print("\n📝 Key sections explained:")
        print("  • [build-system]: Specifies the build system (hatchling)")
        print("  • [project]: Project metadata and dependencies")
        print("  • [project.optional-dependencies]: Development dependencies")
        print("  • [tool.ruff]: Linting and formatting (§2)")
        print("  • [tool.mypy]: Type checking configuration")
        print("  • [tool.pytest]: Test configuration (§5)")
        
        return demo_dir
    
    def setup_pyproject_toml(self, project_name: str, version: str = "0.1.0") -> str:
        """
        Create a template pyproject.toml file following the recommendations
        in §1, §2, and §5 of our best practices guide.
        
        Returns the content of the file.
        """
        return f"""
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "{version}"
description = "Add your project description here"
readme = "README.md"
requires-python = ">={self.recommended_python_version.split()[0]}"
license = {{ file = "LICENSE" }}
authors = [
    {{ name = "Your Name", email = "your.email@example.com" }}
]
dependencies = [
    # Core dependencies
    "fastapi>=0.110.0",
    "uvicorn>=0.27.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "structlog>=24.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.5",
    "mypy>=1.6.1",
]

[tool.ruff]
# §2 Code Style configuration
line-length = 100
target-version = "{self.recommended_python_version.split()[0]}"
select = ["E", "F", "B", "I"]  # Error, Flake8, Bug, Import sorting

[tool.mypy]
# §3 Type Checking configuration
python_version = "{self.recommended_python_version.split()[0]}"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
# §5 Testing configuration  
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
"""
    
    def demonstrate_venv_creation(self):
        """
        Demonstrate virtual environment creation with uv, following 
        the §1 recommendation to use uv for virtual environments.
        """
        print("\n" + "=" * 80)
        print("🔧 VIRTUAL ENVIRONMENT CREATION DEMONSTRATION")
        print("=" * 80)
        print("✨ From §1: 'Use uv—a fast, drop-in Python installer and virtual-environment manager'")
        
        # Check if uv is installed
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
            has_uv = True
        except (subprocess.SubprocessError, FileNotFoundError):
            has_uv = False
        
        venv_path = Path("./demo_venv")
        
        print("\n📋 Virtual Environment Commands:")
        
        # Show the command to create a virtual environment
        create_cmd = self.setup_venv_command(str(venv_path))
        print(f"  • Create venv: {create_cmd}")
        
        # Show the command to install dependencies
        print(f"  • Install dependencies: {self.uv_commands['sync_deps']}")
        
        # Show the command to compile dependencies
        print(f"  • Compile dependencies to lock file: {self.uv_commands['compile_deps']}")
        
        # Actually create the venv if uv is installed
        if has_uv:
            print("\n🔄 Creating virtual environment...")
            result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Virtual environment created at {venv_path}")
            else:
                print(f"  ❌ Failed to create virtual environment: {result.stderr}")
        else:
            print("\n⚠️ uv not found in path. To install:")
            print("  curl -sSf https://install.python-poetry.org | python3 -")
            print("  # Or")
            print("  pip install uv")
        
        print("\n📝 Key principles shown:")
        print("  1. Isolated environments prevent dependency conflicts")
        print("  2. uv provides fast, deterministic dependency resolution")
        print("  3. Lock files ensure reproducible builds")
        
        return venv_path
    
    def demonstrate_repository_initialization(self):
        """
        Demonstrate Git repository initialization following the lightweight
        branching flow from §1.
        """
        print("\n" + "=" * 80)
        print("🌿 GIT REPOSITORY INITIALIZATION DEMONSTRATION")
        print("=" * 80)
        print("✨ From §1: 'Follow a lightweight branching flow'")
        
        repo_name = "demo_repo"
        repo_path = Path(f"./{repo_name}")
        
        # Check if git is installed
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            has_git = True
        except (subprocess.SubprocessError, FileNotFoundError):
            has_git = False
        
        print(f"\n📋 Repository structure for {repo_name}:")
        
        # Generate and display the commands
        commands = self._get_git_init_commands(repo_name)
        for cmd in commands:
            if cmd.strip():
                print(f"  {cmd}")
        
        # Actually create the repo if git is installed
        if has_git and not repo_path.exists():
            print(f"\n🔄 Creating git repository at {repo_path}...")
            
            # Create directory
            repo_path.mkdir()
            
            # Initialize git repo
            subprocess.run("git init", shell=True, cwd=repo_path, capture_output=True)
            
            # Create README
            with open(repo_path / "README.md", "w") as f:
                f.write(f"# {repo_name}\n\nA demonstration repository.\n")
            
            # Initial commit
            subprocess.run("git add README.md", shell=True, cwd=repo_path, capture_output=True)
            subprocess.run('git commit -m "Initial commit"', shell=True, cwd=repo_path, capture_output=True)
            
            # Create development branch
            subprocess.run(f"git checkout -b {self.branching_strategy.development_branch}", 
                          shell=True, cwd=repo_path, capture_output=True)
            
            print(f"  ✅ Repository created with {self.branching_strategy.main_branch} and {self.branching_strategy.development_branch} branches")
        elif repo_path.exists():
            print(f"\n⚠️ Directory {repo_path} already exists. Skipping creation.")
        else:
            print("\n⚠️ Git not found in path. Install git to create repositories.")
        
        print("\n📝 Key principles shown:")
        print(f"  1. Main branch ({self.branching_strategy.main_branch}) for production-ready code")
        print(f"  2. Development branch ({self.branching_strategy.development_branch}) for integration")
        print(f"  3. Feature branches ({self.branching_strategy.feature_prefix}*) for new work")
        print(f"  4. Bugfix branches ({self.branching_strategy.bugfix_prefix}*) for fixes")
        
        return repo_path
    
    def _get_git_init_commands(self, repo_name: str) -> List[str]:
        """Generate Git commands for repository initialization."""
        return [
            f"# Create repository directory",
            f"mkdir {repo_name}",
            f"cd {repo_name}",
            f"",
            f"# Initialize Git repository",
            f"git init",
            f"",
            f"# Create minimal README.md",
            f"echo '# {repo_name}' > README.md",
            f"echo '' >> README.md",
            f"echo 'A demonstration repository.' >> README.md",
            f"",
            f"# Initial commit",
            f"git add README.md",
            f"git commit -m 'Initial commit'",
            f"",
            f"# Create development branch",
            f"git checkout -b {self.branching_strategy.development_branch}",
            f"",
            f"# Set up remote (if needed)",
            f"# git remote add origin git@github.com:yourusername/{repo_name}.git",
            f"# git push -u origin main",
            f"# git push -u origin {self.branching_strategy.development_branch}"
        ]
    
    def setup_venv_command(self, venv_name: Optional[str] = None) -> str:
        """
        Generate the command to create a virtual environment with uv.
        If venv_name is not provided, uses '.venv' as the default.
        """
        venv_path = venv_name or ".venv"
        return f"{self.uv_commands['create_venv']} {venv_path}"
    
    def generate_settings_loader(self) -> str:
        """
        Generate a Python code snippet for a settings loader that handles 
        different environments, following our best practices.
        """
        return '''
from pathlib import Path
import os
from typing import Dict, Any
import tomli
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Settings loader that handles multiple environments.
    
    Following §1 and §6 best practices for configuration management.
    """
    # Basic settings with validation
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Log level")
    database_url: str = Field(..., description="Database connection string")
    
    # Configuration for .env file loading
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        # Load environment-specific .env file based on ENVIRONMENT
        env = os.getenv("ENVIRONMENT", "local").lower()
        if env != "local":
            env_file = f".env.{env}"
            if Path(env_file).exists():
                load_dotenv(env_file)
        
        # Load default .env if it exists
        if Path(".env").exists():
            load_dotenv()
        
        # Initialize with loaded environment variables
        super().__init__(**kwargs)
    
    @property
    def is_production(self) -> bool:
        """Determine if this is a production environment."""
        return os.getenv("ENVIRONMENT", "").lower() == "prod"

# Singleton instance creation using function caching
import functools

@functools.lru_cache()
def get_settings() -> Settings:
    """Returns the settings instance (cached for efficiency)."""
    return Settings()

# Usage:
# settings = get_settings()
# print(f"Debug mode: {settings.debug}")
# print(f"Database URL: {settings.database_url}")
'''
    
    def run_demo(self):
        """Run a comprehensive demonstration of all environment management concepts."""
        print("\n" + "=" * 80)
        print("🚀 ENVIRONMENT MANAGEMENT & SETUP DEMONSTRATION")
        print(f"✨ Demonstrating §1 of the Python Development Best Practices")
        print("=" * 80)
        
        print("\n📋 This demonstration will show you:")
        print("  1. Multi-environment pattern with .env files")
        print("  2. Project configuration with pyproject.toml")
        print("  3. Virtual environment management with uv")
        print("  4. Git repository initialization")
        print("  5. Settings management with Pydantic")
        
        # Demonstrate each component
        self.demonstrate_env_file_creation()
        self.demonstrate_pyproject_toml()
        self.demonstrate_venv_creation()
        self.demonstrate_repository_initialization()
        
        # Show settings loader
        print("\n" + "=" * 80)
        print("⚙️ SETTINGS MANAGEMENT WITH PYDANTIC")
        print("=" * 80)
        print("✨ From §1: 'Settings() picks env file via ENVIRONMENT=prod var'")
        print("✨ Also implementing §6: 'Centralize runtime configuration in Settings class'")
        
        print("\n📄 Example Settings implementation:")
        print(self.generate_settings_loader())
        
        print("\n📝 Key principles shown:")
        print("  1. Environment-specific configuration loading")
        print("  2. Validation of configuration values")
        print("  3. Singleton pattern with lru_cache")
        print("  4. Type safety through Pydantic")
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nRecommended next steps:")
        print("  • Explore other best practice modules")
        print("  • Apply these practices to your own projects")
        print("  • Use uv for dependency management")
        print("  • Set up multi-environment configurations")
    
    def generate_markdown(self) -> str:
        """
        Generate markdown documentation for the Environment Management section
        of our best practices guide.
        """
        return f"""
## Environment Management & Setup

* **Initialize the Repository:** Create a new Git repository (e.g., on GitHub), add and commit a minimal `README.md`, push to `main`, then clone the repository onto your development machine *before* any environment work. Follow a lightweight branching flow: keep `main` production-ready, use `dev` (or `develop`) for ongoing integration, and create short-lived `feature/*`, `bugfix/*`, or `hotfix/*` branches that merge back via pull requests.

* **Multi-environment pattern:**

```text
.env        # local dev
.env.staging
.env.prod   # loaded in CI/CD → Secrets Manager at runtime
```

`Settings()` picks env file via `ENVIRONMENT=prod` var.

* **Use Virtual Environments:** Prefer `uv`—a fast, drop-in Python installer and virtual-environment manager—to create isolated environments and prevent dependency conflicts.

* **Use the Latest Stable Python:** Aim to use the most recent stable version of Python (e.g., **{self.recommended_python_version.split()[0]}** as of {self.recommended_python_version.split('(')[1].split(')')[0]}) that is compatible with your project's dependencies to leverage new features and performance improvements. Check project requirements for minimum versions.

* **Dependency Management (`uv`-centric):**

  * Declare dependencies in `pyproject.toml` under `[project] dependencies` (or an equivalent tool-specific section).

  * Resolve and pin exact versions with `uv pip compile`, committing the generated **`uv.lock`** file for fully reproducible builds (hashes included by default).

  * Recreate environments deterministically using `uv pip sync` (or `uv pip install -r uv.lock`).

  * Use `uv pip list --outdated` (or `uv pip upgrade`) to identify and apply updates; always run the full test suite after upgrades.

  * Integrate `uv pip audit` (or tools like `safety`) into CI/CD to catch known vulnerabilities early.

### Example Settings Implementation

```python
{self.generate_settings_loader()}
```

This implementation demonstrates:
1. Loading different environment files based on the `ENVIRONMENT` variable
2. Type validation with Pydantic
3. Centralized configuration that can be accessed throughout the application
4. Caching for efficient access
"""
    
    def __str__(self):
        """Return a string representation of the environment manager"""
        return f"{self.name} (Python {self.recommended_python_version}, {self.dependency_tool})"


# Run the demo if this file is executed directly
if __name__ == "__main__":
    env_management = EnvironmentManagement()
    env_management.run_demo()