## 4. Application Design & Structure  
* Organize code into logical packages; include `__init__.py`.
* **Use `logging`**, not `print()`, for diagnostics and errors.
* Manage configuration via **TOML** (`pyproject.toml`) or environment variables.
* Write robust **error handling** with specific exceptions; avoid bare `except Exception`.
* Follow **DRY** and **Explicit is better than implicit (PEP 20)** principles.
* For CLI apps, use **`argparse`**, **`typer`**, or **`click`**.
* Leverage **`asyncio`** (`async`/`await`) and libraries like `httpx` for I/O‑bound concurrency.  
### 4.1 Mandatory Design Principles: DRY & SOLID  
| Acronym                        | Core Idea                                                                                    | Practical Enforcement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------ | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DRY**(Don't Repeat Yourself) | Every piece of knowledge must have a single, unambiguous representation within the codebase. | • Centralize shared logic in functions or classes.• Extract common constants/config values.• Use parametrized tests to avoid duplicate cases.• Document conventions in `docs/` to prevent ad‑hoc re‑implementation.                                                                                                                                                                                                                                                                                                                                                                                            |
| **SOLID**                      | Five principles that promote maintainable, extensible OOP designs.                           | **S** Single‑Responsibility: Each module/class handles one concern.**O** Open‑Closed: Classes are open for extension, closed for modification—use inheritance or composition instead of editing core.**L** Liskov Substitution: Subclasses should be drop‑in replacements for their base types; respect type contracts and Pydantic model invariants.**I** Interface Segregation: Prefer small, focused ABCs or Protocols over monolithic ones.**D** Dependency Inversion: Depend on abstractions (e.g., type‑hinted protocols) not concrete details; inject collaborators via constructor or function params. |  
Embed DRY/SOLID checks in **code reviews** and **CI lint rules**—e.g., flag duplicate code with Ruff (`RUF013`‑series) and enforce complexity thresholds (`flake8‑cyclomatic‑complexity`).  
### 4.2 CLI Skeleton (typer)  
```python
# cli.py  ★ HDR required in actual project files
import typer

app = typer.Typer()

@app.command()
def hello(name: str):
"""Say hello."""
typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
app()
```  
Run: `python -m cli hello --name Pedro`.  
### 4.3 Recommended Project Structures  
A well-defined project structure is crucial for maintainability, collaboration, and scalability. While the specific layout can vary depending on the project type, consistency within a project is key. `<root>` refers to the directory created after cloning the git repository.  
**Common Requirements Across All Projects:**  
* **`docs/`**: Contains human-readable documentation (e.g., using Sphinx, MkDocs). This includes architectural diagrams, usage guides, and `README.md` files for sub-components if needed.
* **`m2m/`**: Machine-to-Machine instructions. This folder houses documentation, prompts, schemas, or configuration specifically intended for AI/LLM agents involved in development or maintenance. For example, `m2m/README.md` might define high-level goals, API schemas for code generation, or data format specifications.
* **`pyproject.toml`**: Central configuration file for build system, dependencies (`uv`), linters (`ruff`), type checkers (`mypy`), etc.
* **`.gitignore`**: Specifies intentionally untracked files that Git should ignore.
* **`README.md`**: Top-level project description, setup instructions, and quick start guide.
* **`LICENSE`**: Project's license file.  
**Structure Examples:**  
**1. Web Applications (FastAPI / Flask / Django)**  
This structure emphasizes separation of application code (`src/`) from tests, scripts, and configuration.  
```text
<root>/
├── .git/
├── .github/            # CI/CD workflows
├── .vscode/            # Editor settings (optional)
├── docs/               # Human documentation
├── m2m/                # AI/LLM instructions
├── scripts/            # Helper/utility scripts (deployment, data migration)
├── src/
│   └── <app_name>/     # Main application package
│       ├── __init__.py
│       ├── api/          # API endpoints/routers (FastAPI/Flask Blueprints)
│       ├── core/         # Core logic, configuration loading (config.py)
│       ├── crud/         # Data access logic (optional, depends on complexity)
│       ├── models/       # Pydantic models / ORM models
│       ├── schemas/      # Pydantic schemas for API validation
│       ├── services/     # Business logic layer
│       └── main.py       # Application entry point (FastAPI app creation)
├── tests/              # All tests (unit, integration, e2e)
│   ├── __init__.py
│   ├── conftest.py     # Pytest fixtures
│   ├── integration/
│   └── unit/
├── .env.example        # Example environment variables
├── .gitignore
├── .pre-commit-config.yaml
├── compose.yml         # Docker Compose base config
├── compose-dev.yml     # Docker Compose dev overrides
├── Dockerfile
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock             # Pinned dependencies
```  
**2. CLI Tools (Typer / Click / Argparse)**  
Similar to web apps, often using a `src/` layout, but the internal structure reflects CLI commands and logic.  
```text
<root>/
├── .git/
├── docs/
├── m2m/
├── src/
│   └── <cli_tool_name>/
│       ├── __init__.py
│       ├── cli.py        # Main Typer/Click app definition
│       ├── commands/     # Subcommands module
│       │   ├── __init__.py
│       │   └── subcommand1.py
│       └── core/         # Core logic accessed by commands
├── tests/
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```  
**3. Modular Libraries / Packages**  
Designed to be installable (`pip install .`). The core logic resides within the package directory.  
```text
<root>/
├── .git/
├── docs/
├── examples/           # Usage examples (optional)
├── m2m/
├── src/
│   └── <library_name>/ # The actual Python package
│       ├── __init__.py
│       ├── module1.py
│       └── subpackage/
│           ├── __init__.py
│           └── feature.py
├── tests/
├── .gitignore
├── LICENSE
├── pyproject.toml      # Includes build backend (e.g., hatchling, setuptools)
├── README.md
└── uv.lock
```  
**4. Standalone Scripts**  
For simpler projects consisting of one or a few scripts, a flat structure might suffice initially, but consider migrating to a `src/` layout if complexity grows.  
```text
<root>/
├── .git/
├── docs/
├── m2m/
├── scripts/            # The main script(s)
│   └── process_data.py
├── tests/              # Tests for the script(s)
├── .gitignore
├── LICENSE
├── pyproject.toml      # Dependencies for the scripts
├── README.md
└── uv.lock
```  
Choose the structure that best fits the project's current needs and anticipated future complexity. Adhering to these patterns promotes consistency across projects.  
---