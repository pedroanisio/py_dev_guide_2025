## 4. Application Design & Structure  
*   Organize code into logical packages; include `__init__.py`.
*   Use `logging`, not `print()`, for diagnostics and errors.
*   Manage configuration via TOML (`pyproject.toml`) or environment variables. See `pyproject.toml` for tool-specific settings (linters, formatters, etc.).
*   Write robust error handling with specific exceptions; avoid bare `except Exception`.
*   Follow [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) and "[Explicit is better than implicit](https://peps.python.org/pep-0020/)" (PEP 20) principles.
*   For CLI apps, use libraries like [`argparse`](https://docs.python.org/3/library/argparse.html), [`typer`](https://typer.tiangolo.com/), or [`click`](https://click.palletsprojects.com/).
*   Use [`asyncio`](https://docs.python.org/3/library/asyncio.html) (`async`/`await`) and libraries like [`httpx`](https://www.python-httpx.org/) for efficient I/O‑bound concurrency.

### 4.1 Mandatory Design Principles: DRY & SOLID

#### DRY (Don't Repeat Yourself)

*   **Core Idea:** Every piece of knowledge must have a single, unambiguous representation within the codebase.
*   **Practical Enforcement:**
    *   Centralize shared logic in functions or classes.
    *   Extract common constants/config values.
    *   Use parametrized tests to avoid duplicate test logic.
    *   Document conventions in `docs/` to prevent ad‑hoc re‑implementation.

#### SOLID

*   **Core Idea:** Five principles that promote maintainable, extensible OOP designs.
*   **Practical Enforcement:**
    *   **S** Single‑Responsibility: Each module/class handles one concern.
    *   **O** Open‑Closed: Classes are open for extension, closed for modification—use inheritance or composition instead of editing core logic directly.
    *   **L** Liskov Substitution: Subclasses should be drop‑in replacements for their base types; respect type contracts and Pydantic model invariants.
    *   **I** Interface Segregation: Prefer small, focused Abstract Base Classes (ABCs) or Protocols over monolithic ones.
    *   **D** Dependency Inversion: Depend on abstractions (e.g., type‑hinted protocols) not concrete implementations; inject collaborators via constructor or function parameters.

Embed DRY/SOLID checks in **code reviews** and **CI lint rules** configured in `pyproject.toml`—e.g., flag duplicate code with Ruff ([`RUF013`](https://docs.astral.sh/ruff/rules/#flake8-implicit-str-concat-isc) series - Note: specific rule code might vary) and enforce complexity thresholds ([`flake8-cyclomatic-complexity`](https://pypi.org/project/flake8-cyclomatic-complexity/)).  
### 4.2 CLI Skeleton (typer)  
```python
# cli.py
# ★★★ Add standard project file header here if required by conventions ★★★
import typer

app = typer.Typer()

@app.command()
def hello(name: str):
    """Say hello."""
    typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
    app()
```  
Run: `python -m <your_package_name>.cli hello --name Pedro`. (Adjust `<your_package_name>` accordingly)
### 4.3 Recommended Project Structures  
A well-defined project structure is crucial for maintainability, collaboration, and scalability. The following layouts provide standardized starting points. While the specific structure can vary, **consistency within a project is paramount**. `<root>` refers to the directory created after cloning the git repository.

The `src/` layout, used in several examples, helps clearly separate the installable Python package code from other project files like tests, scripts, and documentation. This prevents accidental imports and packaging issues.

**Common Requirements Across All Projects:**

*   **`docs/`**: Houses all human-readable documentation (e.g., using Sphinx, MkDocs). Should include architectural diagrams, usage guides, and potentially `README.md` files for complex sub-components.
*   **`m2m/`**: Contains Machine-to-Machine instructions and resources. This is the designated place for documentation, prompts, schemas, or configurations specifically intended for **AI/LLM agents** involved in development, analysis, or maintenance. An `m2m/README.md` should define goals, expected inputs/outputs, or relevant schemas for these agents.
*   **`pyproject.toml`**: Serves as the central configuration file ([PEP 518](https://peps.python.org/pep-0518/), [PEP 621](https://peps.python.org/pep-0621/)) for the build system, dependencies (managed by `uv`), linters (`ruff`), type checkers (`mypy`), formatters, and other development tools. Tool configurations typically reside under the `[tool.<tool_name>]` section.
*   **`.gitignore`**: Lists intentionally untracked files and patterns that Git should ignore (e.g., virtual environment directories, cache files, secret keys, compiled artifacts).
*   **`README.md`** (Root): Provides the top-level project description, primary goals, setup instructions, and a quick start guide. Acts as the main entry point for new contributors and users.
*   **`LICENSE`**: Specifies the project's open-source or commercial license terms.

**Structure Examples:**  

**1. Web Applications (FastAPI / Flask / Django)**  
*Ideal for web services, emphasizing separation of concerns (API, core logic, data access).*  
This structure utilizes the `src/` layout to isolate the main application package.  
```text
<root>/
├── .git/
├── .github/            # CI/CD workflows (e.g., GitHub Actions)
├── .vscode/            # Editor settings (optional, for consistency)
├── docs/               # Human documentation
├── m2m/                # AI/LLM instructions & resources
├── scripts/            # Utility/automation scripts (deployment, data migration, etc.)
│   └── README.md       # Explain script usage
├── src/
│   └── <app_name>/     # Main application Python package
│       ├── __init__.py
│       ├── api/          # API endpoints/routers (FastAPI/Flask Blueprints)
│       ├── core/         # Core logic, config loading (config.py), reusable components
│       ├── crud/         # Create, Read, Update, Delete operations (data access layer)
│       ├── models/       # Data models (e.g., Pydantic models, ORM models)
│       ├── schemas/      # API data validation schemas (e.g., Pydantic schemas)
│       ├── services/     # Business logic layer orchestrating operations
│       ├── README.md     # Overview of the application structure
│       └── main.py       # Application entry point (e.g., FastAPI app instance)
├── tests/              # All tests (unit, integration, end-to-end)
│   ├── __init__.py
│   ├── conftest.py     # Shared Pytest fixtures
│   ├── integration/    # Tests requiring external services (DB, APIs)
│   ├── unit/           # Tests for isolated components
│   └── README.md       # Guide on running tests
├── .env.example        # Template for environment variables
├── .gitignore
├── .pre-commit-config.yaml # Pre-commit hook configurations
├── compose.yml         # Base Docker Compose configuration
├── compose-dev.yml     # Docker Compose overrides for development
├── Dockerfile          # Container build definition
├── LICENSE
├── pyproject.toml      # Project metadata and tool configuration
├── README.md           # Top-level project overview
└── uv.lock             # Pinned dependencies (generated by `uv pip compile`)
```  

**2. CLI Tools (Typer / Click / Argparse)**  
*Suitable for command-line applications, structuring code around commands.*  
Also typically uses a `src/` layout.  
```text
<root>/
├── .git/
├── docs/
├── m2m/
├── src/
│   └── <cli_tool_name>/ # Main CLI package
│       ├── __init__.py
│       ├── cli.py        # Main Typer/Click app definition and entry point
│       ├── commands/     # Directory for subcommand modules
│       │   ├── __init__.py
│       │   └── subcommand1.py
│       ├── core/         # Core logic shared across commands
│       └── README.md     # Overview of the CLI structure
├── tests/
│   └── README.md       # Guide on running tests
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```  

**3. Modular Libraries / Packages**  
*Designed to be installed and imported by other projects (`pip install .`).*  
The core logic resides directly within the package directory under `src/`.  
```text
<root>/
├── .git/
├── docs/
├── examples/           # Practical usage examples (optional but recommended)
│   └── README.md       # How to run examples
├── m2m/
├── src/
│   └── <library_name>/ # The actual Python package to be installed
│       ├── __init__.py
│       ├── module1.py
│       └── subpackage/
│           ├── __init__.py
│           └── feature.py
├── tests/
│   └── README.md       # Guide on running tests
├── .gitignore
├── LICENSE
├── pyproject.toml      # Includes build backend (e.g., hatchling, setuptools)
├── README.md
└── uv.lock
```  

**4. Standalone Scripts**  
*For simpler projects focused on one or a few automation or processing scripts.*  
A flat structure might suffice initially, but consider migrating to a `src/` layout (like Example 2 or 3) if complexity grows or if parts become reusable.  
```text
<root>/
├── .git/
├── docs/
├── m2m/
├── scripts/            # The main script(s)
│   └── process_data.py
│   └── README.md       # Explanation of scripts and usage
├── tests/              # Tests for the script(s)
│   └── README.md       # Guide on running tests
├── .gitignore
├── LICENSE
├── pyproject.toml      # Dependencies required by the scripts
├── README.md
└── uv.lock
```  
Choose the structure that best fits the project's current needs and anticipated future complexity. Adapting these patterns consistently promotes clarity and maintainability across projects.
---