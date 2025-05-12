# Python Development Best Practices (2025 edition)

> **Version:** 2025‑05‑12 · Maintainer Team Core‑Python · **Status:** LIVING‑DOC (update via PR)

---

## Table of Contents

0. [Security Practices (NEW 2025‑05‑12)](#0-security-practices)
1. [Environment Management & Setup](#1-environment-management--setup)
2. [Code Style & Formatting](#2-code-style--formatting)
3. [Modern Python Syntax & Idioms](#3-modern-python-syntax--idioms)
4. [Application Design & Structure](#4-application-design--structure)
5. [Testing](#5-testing)
6. [Data Validation & Configuration — Pydantic v2](#6-data-validation--configuration--pydantic-v2)
7. [Logging & Observability](#7-logging--observability)
8. [Containerization & Docker Usage](#8-containerization--docker-usage)
9. [API Development — FastAPI **(Mandatory)**](#9-api-development--fastapi-mandatory)
10. [Background Tasks & Concurrency](#10-background-tasks--concurrency)
11. [Data Persistence & Storage](#11-data-persistence--storage)
12. [AI & Data‑Science Practices](#12-ai--data-science-practices)
13. [Edge‑Case Pitfalls & Gotchas](#13-edge-case-pitfalls--gotchas)
14. [References](#14-references)

## Our Ethos

### Rules for Coding / Working

* **PHIL-FIXFORWARD**  – We fix forward. No regressions. In doubt, ask or explain.
* **PHIL-ELEGANCE**  – We aim for high‑quality, elegant software‑engineering solutions.
* **PHIL-TESTS-SPEC**  – Tests are the ultimate specification. To know the rules, read the tests.
* **PHIL-NO-CHEAT**  – Do not bend tests to make them pass. Build elegant, correct software. Ask if unsure.
* **PHIL-ASPIRATION**  – We aim for greater things—always elevate the standard.
* **PHIL-FILE-GOVERN**  – Each file must have a well‑defined purpose, human approval, and justification.
* **PHIL-SECURE** *(NEW)* – Security is non‑negotiable: never hard‑code secrets, apply least‑privilege, and threat‑model every feature by default.

### Files Header

* **HDR-DESCRIPTION**  – Provide a clear description of the file in the header.
* **HDR-FILENAME**  – Add the filename in the header.
* **HDR-FILEPATH**  – Add the full file path in the header.
* **HDR-FORMAT**  – Format the header comment block according to the file's language and content constraints.
* **HDR-REQUIRED**  – Include a header at the top of every file.
* **HDR-UML**  – Include a UML diagram of the class or code in the header.
* **HDR-VERSION**  – Include a version number in the header.

### General Software Design

* **GEN-DESIGN-PATTERN**  – Use appropriate design patterns suited to the problem context.
* **GEN-DRY**  – Avoid duplication by following the DRY principle.
* **GEN-MINDSET**  – We FixForward! We are building excellent software here.
* **GEN-SOLID**  – Apply SOLID principles to guide software‑design decisions.
* **GEN-STRUCTURE**  – Place each file in the folder that matches its responsibility.
* **GEN-ONE-CLASS**  – Aim for *one* public class per file, with a **mandatory upper limit of three classes** (including helpers). If you exceed this, move classes into their own files.
* **GEN-VERSIONING**  – Follow software‑engineering best practices for versioning.

### Language‑Specific Rules

#### Python

* **PY-RUFF** – Use the Ruff formatter and linter for consistent code and quality checks.
* **PY-CONFIG**  – Centralize tool configs in `pyproject.toml`.
* **PY-COVERAGE**  – Measure test coverage with `coverage.py`.
* **PY-DOCSTRING**  – Document all functions/classes per PEP 257.
* **PY-ISORT**  – Organize imports with isort.
* **PY-LOCKFILE**  – Pin dependencies with a lock file (`uv.lock`).
* **PY-MYPY**  – Run MyPy for type checks.
* **PY-PACKAGE-LAYOUT**  – Use clear `src/` or package layout.
* **PY-PRECOMMIT**  – Automate checks via pre‑commit hooks.
* **PY-PYDANTIC**  – Use Pydantic 2.11.4+ for models when applicable.
* **PY-PYTEST**  – Write tests with pytest.
* **PY-STYLE-PEP8**  – Follow PEP 8 style.
* **PY-TYPING-PEP484**  – Adopt PEP 484 typing.
* **PY-VENV**  – Use virtual environments (`uv`).

---

<a id="0-security-practices"></a>

## 0. Security Practices (NEW)

| Concern | Mandate |
| ------- | ------- |
| **Secret Management** | *Never* commit secrets. Load via **python‑dotenv** in *dev* and Vault/Doppler/SM in *prod*. |
| **Configuration** | Use `Settings(BaseSettings)`; map secret env vars (`DB_URL`, `JWT_KEY`). |
| **Dependency Scanning** | CI runs **trivy fs . --exit-code 1** and `uv pip audit`. |
| **Auth & AuthZ** | FastAPI routes use **OAuth2 Bearer** with scopes; enforce with `Depends(get_current_user)`. See §9. |
| **Input Sanitization** | Pydantic validates all inbound data; never `eval()` untrusted strings. |
| **HTTPS Everywhere** | Traefik or Cloud LB terminates TLS; internal networks may allow mTLS. |
| **Security Headers** | Add `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` through Traefik middleware. |
| **Transport Encryption** | Databases use TLS (`sslmode=require`), Redis with `--tls`. |
| **Static Analysis** | Enable **Bandit** in pre‑commit (`bandit -ll -r src`). |

**Example: Loading environment variables**

```python
from dotenv import load_dotenv; load_dotenv()
```

> **Golden Rule:** If you touch credentials, crypto, or user data, open a **SECURITY.md** threat‑model PR.

---

<a id="1-environment-management--setup"></a>

## 1. Environment Management & Setup

* **Initialize the Repository:** Create a new Git repository (e.g., on GitHub), add and commit a minimal `README.md`, push to `main`, then clone the repository onto your development machine *before* any environment work. Follow a lightweight branching flow: keep `main` production‑ready, use `dev` (or `develop`) for ongoing integration, and create short‑lived `feature/*`, `bugfix/*`, or `hotfix/*` branches that merge back via pull requests.

* **Multi‑environment pattern:**

```text
.env        # local dev
.env.staging
.env.prod   # loaded in CI/CD → Secrets Manager at runtime
```

`Settings()` picks env file via `ENVIRONMENT=prod` var.

* **Use Virtual Environments:** Prefer `uv`—a fast, drop‑in Python installer and virtual‑environment manager—to create isolated environments and prevent dependency conflicts.

* **Use the Latest Stable Python:** Aim to use the most recent stable version of Python (e.g., **3.13** as of mid‑2025) that is compatible with your project's dependencies to leverage new features and performance improvements. Check project requirements for minimum versions.

* **Dependency Management (********`uv`****\*\*\*\*\*\*\*\*\*\*\*\*‑centric):**

  * Declare dependencies in `pyproject.toml` under `[project] dependencies` (or an equivalent tool‑specific section).

  * Resolve and pin exact versions with `uv pip compile`, committing the generated **`uv.lock`** file for fully reproducible builds (hashes included by default).

  * Recreate environments deterministically using `uv pip sync` (or `uv pip install -r uv.lock`).

  * Use `uv pip list --outdated` (or `uv pip upgrade`) to identify and apply updates; always run the full test suite after upgrades.

  * Integrate `uv pip audit` (or tools like `safety`) into CI/CD to catch known vulnerabilities early.

---

## 2. Code Style & Formatting

* **Follow PEP 8:** Adhering to the official style guide significantly improves readability and consistency. Key aspects include naming conventions, code layout, imports organization, and comments.
* **Use Automatic Formatters:** Tools like `ruff` (which includes formatting capabilities) enforce a consistent code style with minimal configuration. `isort` specifically sorts imports, though Ruff can also handle this. Many developers use them as part of their workflow or CI/CD pipeline.
* **Use Linters: Ruff** (lint + format + fix) as the default; add Flake8/Pylint only if you need a plugin Ruff doesn't yet cover.
* **Exception‑to‑rule:** long dictionary literals that exceed 120 chars may keep single line *if* the formatter keeps them readable; justify in PR.
* **Naming Conventions:**

  * `lower_case_with_underscores` for functions, methods, variables, and modules.
  * `CapWords` (CamelCase) for classes.
  * `_single_leading_underscore` for protected/internal members.
  * `__double_leading_underscore` for name‑mangling (use sparingly).
  * `ALL_CAPS_WITH_UNDERSCORES` for constants.
  * Use descriptive, intention‑revealing, pronounceable names; avoid ambiguous abbreviations.

### 2.1 Automate Style Enforcement with **pre‑commit**

Add a Git hook that runs *Ruff* (lint/format/fix) and *isort* (import sorting) before every commit.

1. **Declare the hook set** in a top‑level `.pre-commit-config.yaml`:

   ```yaml
   repos:
     - repo: https://github.com/charliermarsh/ruff-pre-commit
       rev: v0.5.0           # match your Ruff version
       hooks:
         - id: ruff
           args: [--fix]
         - id: ruff-format  # Added Ruff formatter hook
   ```

2. **Install** the hooks once per clone:

   ```bash
   uv pip install pre-commit  # or add to pyproject dependencies
   pre-commit install         # sets up .git/hooks/pre-commit
   ```

3. **Run on demand or in CI:**

   ```bash
   pre-commit run --all-files  # useful before pushing / in CI step
   ```

This guarantees every commit has imports sorted and Ruff‑clean code, keeping Section 2's style rules consistently enforced.

---

## 3. Modern Python Syntax & Idioms

* **Use f‑strings** for string formatting (`f"Hello, {name}!"`).
* **Type Hinting (PEP 484+)** improves clarity; run tools like `mypy` for static checks.
* **Data Classes (PEP 557)** via `@dataclass` reduce boilerplate for data containers.
* **`pathlib`** for filesystem paths; prefer `os.scandir()` over `os.listdir()` when metadata is needed.
* **Context Managers** with `with` for resource management.
* **`breakpoint()`** (≥3.7) as a modern debugger hook.
* **`enumerate()`**, dictionary/set comprehensions, and the **walrus operator (`:=`)** where they aid readability.
* **Walrus operator demo**:

```python
if (chunk := stream.read(1024)):
    process(chunk)  # more concise than two‑line read+check.
```

* **New Type Parameter Syntax (PEP 695)**: For Python 3.12+, use the new syntax for defining generic functions and classes (e.g., `def func[T](...)`, `class MyClass[T]: ...`), and type aliases (`type AliasName[T] = ...`). This syntax is generally clearer and avoids explicit `TypeVar` definitions in simple cases.
* **`collections.abc`** when defining custom collections.
* **Timezone‑aware `datetime`** objects for unambiguous timestamps.

### 3.1 Referenced Python Enhancement Proposals (PEPs)

This guide references or incorporates principles from the following PEPs:

* **PEP 8:** Style Guide for Python Code (See §2 Code Style & Formatting)
* **PEP 20:** The Zen of Python ("Explicit is better than implicit", See §4 Application Design & Structure)
* **PEP 257:** Docstring Conventions (See Language‑Specific Rules)
* **PEP 3129:** Class Decorators (Extends decorator syntax to classes)
* **PEP 484:** Type Hints (See §3 Modern Python Syntax & Idioms, Language‑Specific Rules)
* **PEP 557:** Data Classes (See §3 Modern Python Syntax & Idioms)
* **PEP 695:** Type Parameter Syntax (Introduces `type` statements and `def func[T]`, `class Class[T]` syntax; See §3 Modern Python Syntax & Idioms)
* **PEP 696:** Type Defaults for Type Parameters (Allows defaults in type parameters, e.g., `type ListOrSet[T = int] = ...`; requires Python 3.13+)
* **PEP 719:** Python 3.13 Release Schedule (See §14 References)

---

<a id="4-application-design--structure"></a>

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

## 5. Testing

* **Write Tests** using **`pytest`** as the default framework (rich fixtures, parametrization, and plug‑ins).
* Include unit, integration, and end‑to‑end tests.
* Keep tests isolated with mocks (`unittest.mock`, `pytest‑mock`) and factories.
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

### 5.1 Test‑Driven Development (TDD) — RED → GREEN → REFACTOR

Follow this loop for every new feature or bug‑fix unless explicitly instructed otherwise.

| Phase                             | Command Example                   | Expectation                                          |
| --------------------------------- | --------------------------------- | ---------------------------------------------------- |
| **1. Write a failing test (RED)** | `pytest -k new_feature -q`        | The new test fails (assertions trigger).             |
| **2. Implement the minimal code** | edit source files                 | Only add what's necessary for the test to pass.      |
| **3. Run the suite (GREEN)**      | `pytest -q`                       | All tests pass.                                      |
| **4. Refactor safely**            | improve names, remove duplication | No behavior change; run `pytest -q` after each step. |

> **Rule — Tests are authoritative:** Code must satisfy tests; do **not** alter tests merely to make them pass unless the specification itself has legitimately changed **and you explicitly instruct otherwise**.

Embed this cycle into your daily workflow (IDE test runner, `uv pip sync && pytest -q` watch scripts, etc.) to keep the codebase robust and regression‑free.

### 5.2 Running Pytest & Enforcing Coverage

| Goal                             | Command                                                                          | Notes                                           |
| -------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------- |
| Run the full suite, quiet output | `pytest -q`                                                                      | Fast feedback loop while coding.                |
| Run tests matching a keyword     | `pytest -k "billing and not slow" -q`                                            | Combine expressions for fine‑grained selection. |
| Run a single file or directory   | `pytest tests/api/test_users.py -q`                                              | Paths are relative to repo root.                |
| Collect-only (no execution)      | `pytest --collect-only`                                                          | Inspect discovered tests.                       |
| **Run with coverage**            | `pytest --cov=<package_or_srcdir> --cov-report=term`                             | Shows annotated summary in terminal.            |
| **Fail when coverage < 70%**     | `pytest --cov=<package_or_srcdir> --cov-fail-under=70 --cov-report=term-missing` | The CI pipeline must include this gate.         |

**Coverage Policy**

* **Minimum acceptable:** 70 % statement coverage (`--cov-fail-under=70`).
* **Desired target:** ≥ 80 % on mainline / release branches.

CI should treat < 70 % coverage as a failure. Teams are encouraged to raise the threshold incrementally once 80 % has been met sustainably.

Add this step to your CI workflow (GitHub Actions example):

```yaml
- name: Run pytest with coverage
  run: |
    uv pip sync
    pytest --cov=src --cov-fail-under=70 --cov-report=xml
```

> Tip: For local pre‑push checks, add a **pre‑commit** stage using the [`pytest‑pre‑commit` hook](https://github.com/kevin1024/pytest-pre-commit) or simply invoke the same coverage command in a `pre-push` script.

---

## 6. Data Validation & Configuration — **Pydantic v2**

Pydantic (≥ 2.11.4) is **mandatory** for all structured data exchanged inside the codebase—domain models, API schemas, event payloads, and runtime configuration.

### 6.1 Core Rules

1. **Model everything**: Replace raw `dict`/`TypedDict` at module boundaries with `BaseModel` subclasses.
2. **Settings pattern**: Centralize runtime/env config in a single `Settings` class that extends `BaseSettings` (reads from env, `.env`, `secrets/`).
3. **No implicit mutation**: Models are immutable by default (`model_config = {"frozen": True}`) unless mutability is essential.
4. **Validation first**: Construct models as the first step when ingesting external data (HTTP, CLI, DB rows) to reject bad input early.
5. **Serialization**: Use `.model_dump()` / `.model_dump_json()` for outbound payloads—never manual `dict()` manipulation.

**Model Versioning Tip**: include `model_version: Literal["v1"]` in schemas to evolve breaking changes (`v2`, `v3`, …) without downtime. Deprecate via **router.include_router(v1_router, prefix="/v1")**.

### 6.2 Recommended Layout

```text
<root>/
├── app/
│   ├── models.py        # domain DTOs (BaseModel)
│   ├── schemas.py       # API request / response models
│   └── config.py        # Settings(BaseSettings) singleton
```

### 6.3 Minimal Example

```python
# app/models.py
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    id: int = Field(gt=0)
    email: str
    is_active: bool = True

    @field_validator("email")
    def email_must_have_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("invalid email")
        return v

# app/config.py
from functools import lru_cache
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    debug: bool = Field(False, env="DEBUG")
    database_url: str = Field(..., env="DATABASE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 6.4 Tooling & CI Enforcement

| Tool                         | Config Snippet | Purpose |
| ---------------------------- | -------------- | ------- |
| **mypy**                     | \\\n```toml\n[tool.mypy]\nplugins = ["pydantic.mypy"]\n```\n\\\n                     | Static-typing correctness, Pydantic plugin for generics & validators. |
| **ruff** | Rule set `B0`, `ARG`, `PTH` enabled by default. | Flags unused fields, wrong exception style, etc. |

### 6.5 FastAPI Integration Quick‑Ref

```python
from fastapi import FastAPI
from app.schemas import User

app = FastAPI()

@app.post("/users", response_model=User)
async def create_user(user: User):
  # user is already validated ✅
  return user
```

> **Remember**: if a structure could be represented by a Pydantic model, it **must** be—unless explicitly instructed otherwise.

---

## 7. Logging & Observability

### 7.1 Mandatory Format — **JSON Lines (jsonl)**

All runtime logs **must be emitted as JSON objects, one per line** (a.k.a. *jsonl*) to guarantee machine‑readability and easy ingestion by ELK, Loki, Stackdriver, Datadog, etc.

| Field        | Example                    | Notes                                                        |
| ------------ | -------------------------- | ------------------------------------------------------------ |
| `timestamp`  | `2025‑05‑12T13:37:49.123Z` | ISO‑8601, always **UTC**.                                    |
| `level`      | `INFO` / `ERROR` / `DEBUG` | Standard levels.                                             |
| `message`    | `"User created"`           | Human‑readable action description.                           |
| `module`     | `"app.api.users"`          | Python module path.                                          |
| `function`   | `"create_user"`            | Function or method.                                          |
| `line`       | `42`                       | Source line.                                                 |
| `request_id` | `"03f4…"`                  | Correlation / trace ID (optional but highly encouraged).     |
| `extra`      | `{…}`                      | Domain‑specific key‑values (e.g., `user_id`, `order_total`). |

> One line ⇢ one JSON object ⇢ no multiline stack traces; Python exceptions are rendered into `exc_info` fields.

### 7.2 Recommended Stack

| Library                | Purpose                                                          | Install                             |
| ---------------------- | ---------------------------------------------------------------- | ----------------------------------- |
| **structlog**          | Thin wrapper around stdlib logging that outputs structured JSON. | `uv pip install structlog`          |
| **python‑json‑logger** | Drop‑in `logging.Formatter` producing jsonl.                     | `uv pip install python‑json‑logger` |
| **loguru** (optional)  | Batteries‑included alternative with JSON sink.                   | `uv pip install loguru`             |

### 7.3 Minimal Example (structlog)

```python
# app/logging_config.py
import logging, sys, structlog

logging.basicConfig(
    format="%(message)s",  # structlog will render JSON
    stream=sys.stdout,
    level=logging.INFO,
)

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info("User created", user_id=123)
```

Output (one line):

```jsonl
{"timestamp":"2025-05-12T13:37:49.123Z","level":"info","message":"User created","user_id":123}
```

### 7.4 Best Practices

1. **Log to stdout** inside containers; let the orchestrator handle aggregation.
2. **Never log secrets** — mask tokens, passwords, PII.
3. **Use correlation IDs**: propagate `request_id`/`trace_id` from ingress to downstream calls.
4. **Set log level via env var** (`LOG_LEVEL=DEBUG`) and default to `INFO`.
5. **Rotation in dev**: use `TimedRotatingFileHandler` or `loguru` sink to keep disk usage sane.
6. **Alerting hooks**: send `ERROR` logs to Sentry or PagerDuty via handler.
7. **Test log output**: add pytest‑style capture assertions to ensure correct fields.

### 7.5 CI Check

Add a lint step that parses a sample log line to verify valid JSON:

```bash
python -c 'import json,sys; json.loads(sys.stdin.readline())' < sample.log
```

Failure means the formatter emitted invalid JSON—block the PR.

> **Rule**: Any new service/component must initialize logging via the shared `logging_config.py` or an equivalent module that produces jsonl.

**Error Tracking**: integrate Sentry.

```python
import sentry_sdk; sentry_sdk.init(dsn=getenv("SENTRY_DSN"), traces_sample_rate=0.1)
```

---

## 8. Containerization & Docker Usage

### 8.1 Dockerfile Guidelines

* Write **multi‑stage builds** to keep images lean and secure.
* Use official, slim base images and **pin explicit tags** inside the Dockerfile (`python:3.13-slim`, `node:20-alpine`, etc.).

**Vulnerability Scan**

```yaml
- name: Trivy scan
  run: trivy fs --exit-code 1 --severity CRITICAL,HIGH .
```

### 8.2 Compose Files

| File              | Purpose                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| `compose.yml`     | Production‑oriented service definitions (minimal, safe defaults).                                     |
| `compose-dev.yml` | Development overrides ‑ mounts source, enables hot‑reload, adds optional helpers (db, mailhog, etc.). |

#### Mandatory Rules

1. **Do *not* declare a `version:` key** in any Compose file—Compose V2 infers the schema automatically.
2. Extension or local tweaks must go into **`compose-dev.yml`** (or another `*-dev.yml`) rather than editing `compose.yml` directly.

#### Minimal Example: `compose-dev.yml`

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    volumes:
      - ./:/app:ro
    environment:
      - PYTHONUNBUFFERED=1
    ports:
      - "8000:8000"
```

Run locally with both files:

```bash
docker compose -f compose.yml -f compose-dev.yml up --build
```

> **Rule:** Add databases, message brokers, or mock services needed for local hacking to **`compose-dev.yml`**, keep **`compose.yml`** production‑ready, and **never add the `version` property**.

### 8.3 Compose Recipe Library (Mix & Match)

Below are **modular compose snippets** you can combine with `docker compose -f ... -f ... up` to assemble the stack you need. All images have explicit tags and omit a top-level `version:` key.

#### 8.3.1 Database + Admin (`compose.db.yml`)

```yaml
services:
  postgres:
    image: postgres:16.2-alpine
    environment:
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: devpass
      POSTGRES_DB: app_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "dev"]
      interval: 10s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:8.6
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

#### 8.3.2 Cache (`compose.cache.yml`)

```yaml
services:
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
```

#### 8.3.3 API Service (`compose.api.yml`)

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://dev:devpass@postgres/app_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    labels:
      - "traefik.http.routers.api.rule=Host(`api.localhost`)"
      - "traefik.http.services.api.loadbalancer.server.port=8000"
```

#### 8.3.4 Front‑End (`compose.front.yml`)

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      VITE_API_URL: http://api.localhost
    depends_on:
      - api
    labels:
      - "traefik.http.routers.front.rule=Host(`app.localhost`)"
      - "traefik.http.services.front.loadbalancer.server.port=3000"
```

#### 8.3.5 Routing (`compose.proxy.yml`)

```yaml
services:
  traefik:
    image: traefik:v2.11
    command:
      - "--providers.docker=true"
      - "--api.insecure=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"  # dashboard
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
```

#### 8.3.6 Static Assets (`compose.nginx.yml`)

```yaml
services:
  nginx:
    image: nginx:1.25-alpine
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - ./static:/usr/share/nginx/html:ro
    ports:
      - "8081:80"
```

#### 8.3.7 Observability (`compose.observability.yml`)

```yaml
services:
  prometheus:
    image: prom/prometheus:v2.52.0
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:11.0.0
    environment:
      - GF_SECURITY_ADMIN_PASSWORD: admin
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
```

#### Using the Recipes

Spin up API + DB + Redis + Traefik for local dev:

```bash
docker compose \
  -f compose.yml \
  -f compose.db.yml \
  -f compose.cache.yml \
  -f compose.api.yml \
  -f compose.proxy.yml \
  up --build
```

Add the React front‑end and observability stack:

```bash
docker compose \
  -f compose.yml \
  -f compose.db.yml \
  -f compose.cache.yml \
  -f compose.api.yml \
  -f compose.front.yml \
  -f compose.proxy.yml \
  -f compose.observability.yml \
  up --build
```

> **Tip:** Keep `compose.yml` minimal (network/volumes + any global defaults) and layer these recipe files as needed. Remember **never to include a `version` key**.

### 8.4 Docker Command Cheat‑Sheet for Dev & Debug

| Situation                         | Command                                       | What it does                                                |
| --------------------------------- | --------------------------------------------- | ----------------------------------------------------------- |
| **Build images**                  | `docker compose build`                        | Rebuilds service images without starting containers.        |
| **Start stack**                   | `docker compose up -d`                        | Launches all services in detached mode.                     |
| **Follow logs (all)**             | `docker compose logs -f --tail=50`            | Streams last 50 lines and follows logs.                     |
| **Follow logs (one svc)**         | `docker compose logs -f api`                  | Tail just the `api` container.                              |
| **Interactive shell**             | `docker compose exec api bash`                | Open bash inside the running `api` container.               |
| **Run one‑off cmd**               | `docker compose run --rm api pytest -k quick` | Execute ad‑hoc command in throwaway container.              |
| **List running containers**       | `docker compose ps`                           | Show status table.                                          |
| **Stop stack**                    | `docker compose stop`                         | Gracefully stop all containers (preserve volumes/networks). |
| **Remove stack**                  | `docker compose down -v`                      | Stop and remove containers **and** named volumes.           |
| **Prune dangling images/volumes** | `docker system prune -f`                      | Free disk space (dangling only).                            |
| **View Docker resource usage**    | `docker stats`                                | Live CPU/mem/IO stats per container.                        |
| **Inspect container**             | `docker inspect <container_id>`               | Full JSON metadata—mounts, env, IPs.                        |
| **Copy file from container**      | `docker cp api:/app/log.txt ./log.txt`        | Extract files without volume mounts.                        |
| **Open a Python REPL**            | `docker compose exec api python`              | Access project venv inside container.                       |
| **Rebuild & restart changed svc** | `docker compose up -d --build api`            | Hot‑rebuild changed Dockerfile + restart service.           |

> **Shortcut:** Add `alias dcd='docker compose down -v'` in your shell for quick full‑reset during heavy iteration.

### 8.5 Deployment Recipes (Public‑Facing & Internal)

> These recipes assume you have built images with explicit tags (e.g., `myapp-api:1.0.0`) and pushed them to a registry (ghcr.io / gcr.io / registry.digitalocean.com). Adjust resource names to match your project.

#### 8.5.1 Stand‑Alone VPS (DigitalOcean Droplet + Cloudflare DNS)

```bash
# On a fresh Ubuntu 24.04 droplet (root)
adduser deploy
usermod -aG sudo,docker deploy
ssh deploy@droplet

# Clone repo & pull env vars
git clone https://github.com/your‑org/myapp.git && cd myapp
cp .env.prod.example .env

# Export Cloudflare credentials for Traefik DNS‑01 challenge
export CF_DNS_API_TOKEN=cf‑token‑here

# Launch API + Traefik + Postgres
sudo docker compose \
  -f compose.yml \
  -f compose.db.yml \
  -f compose.api.yml \
  -f compose.cache.yml \
  -f compose.proxy.yml \
  up -d
```

Traefik `dynamic/cloudflare.yaml` (inside repo):

```yaml
tls:
  certificatesResolvers:
    letsencrypt:
      acme:
        email: dev@example.com
        storage: /etc/traefik/acme.json
        dnsChallenge:
          provider: cloudflare
          delayBeforeCheck: 0
```

*DNS setup*: create an **`A`** record `api.example.com` → droplet IP in Cloudflare. Traefik will issue/renew TLS via Let's Encrypt automatically.

---

#### 8.5.2 Google Cloud Run (Public HTTPS, No Server Ops)

1. **Build & push**

   ```bash
   gcloud builds submit --tag gcr.io/$GOOGLE_PROJECT/myapp-api:1.0.0
   ```

2. **Deploy**

   ```bash
   gcloud run deploy myapp-api \
      --image gcr.io/$GOOGLE_PROJECT/myapp-api:1.0.0 \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars "DATABASE_URL=$(cat prod_secrets.txt)"
   ```

3. **Map domain** – In Cloud Run console, map `api.example.com` and add the suggested CNAME in Cloudflare → full TLS chain handled by Google.

To keep **internal‑only**, omit `--allow-unauthenticated` and place Cloud Armor or IAP in front.

---

#### 8.5.3 Google Kubernetes Engine (Multi‑Service, Internal & External)

*Simplified YAML snippets*

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: myapp
spec:
  replicas: 3
  selector:
    matchLabels: {app: api}
  template:
    metadata: {labels: {app: api}}
    spec:
      containers:
        - name: api
          image: gcr.io/$PROJECT/myapp-api:1.0.0
          env:
            - name: DATABASE_URL
              valueFrom: {secretKeyRef: {name: db-url, key: url}}
---
apiVersion: v1
kind: Service
metadata:
  name: api-int
  namespace: myapp
spec:
  type: ClusterIP        # internal only
  selector: {app: api}
  ports: [{port: 8000, targetPort: 8000}]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-public
  namespace: myapp
  annotations:
    kubernetes.io/ingress.global-static-ip-name: myapp-ip
    networking.gke.io/managed-certificates: api-cert
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-int
                port: {number: 8000}
```

GKE Ingress controller provisions Cloud Load Balancer + certs automatically.

For a *private TLD* (e.g., `api.internal`), use an **Internal Load Balancer** (`cloud.google.com/neg: "true"`, `networking.gke.io/internal-load-balancer-allow-global-access: "true"`) and route via Cloud DNS‑private zones.

---

#### 8.5.4 Private‑Only Stack in Corp VPC (No Internet)

Combine internal DNS (`*.corp.local`) with Traefik + self‑signed or internal CA certs.

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout tls.key -out tls.crt -subj "/CN=*.corp.local"

kubectl create secret tls internal-tls \
  --cert=tls.crt --key=tls.key -n myapp
```

Traefik `ingressRoute` references `internal-tls`; only corp network can resolve DNS.

---

> **Note:** Stick to the same environment variables and `uv.lock` across deploy targets to guarantee reproducibility.

## 9. API Development — FastAPI **(Mandatory)**  🚀

### Why FastAPI?

* First‑class **async** support (built on Starlette).
* **OpenAPI** docs auto‑generated → contract‑driven dev.
* Pydantic integration = zero‑boilerplate validation.

### Quick‑start Skeleton

```python
# app/main.py ★ HDR required in actual project files
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

class Health(BaseModel):
    status: str = "ok"

app = FastAPI(title="My API", version="1.0.0")

@app.get("/health", response_model=Health, tags=["meta"])
async def health() -> Health:
    return Health()

# Auth dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

@app.get("/secure")
async def secure_endpoint(user = Depends(get_current_user)):
    return {"user": user}
```

### Production Guidelines

| Concern       | Mandate                                                                  |
| ------------- | ------------------------------------------------------------------------ |
| Workers       | **uvicorn\[standard]** via Gunicorn (`-k uvicorn.workers.UvicornWorker`) |
| Timeouts      | 60 s hard, 30 s read.                                                    |
| CORS          | Restrict origins in `CORSMiddleware`.                                    |
| Rate Limiting | Deploy Traefik plugin or Redis‑based SlowAPI.                            |

---

## 10. Background Tasks, Messaging & Concurrency

### 10.1 Choosing the Right Execution Model

| Scenario                                                         | Recommendation                                                                   | Rationale                                           |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------- |
| Quick, non‑blocking work (<20 ms) inside an HTTP request         | Keep synchronous — no added complexity.                                          | Latency negligible; avoids context‑switch overhead. |
| I/O‑bound but may take up to 200 ms (e.g., outbound HTTP call) | Use **`async def`** + `await` inside FastAPI route.                              | Non‑blocking concurrency, simpler than queue.       |
| Anything that can block for >200 ms or involves heavy CPU        | Off‑load to **Celery task** (or equivalent) and return `202 Accepted`.           | Keeps request threads free, scales separately.      |
| High‑throughput event ingestion / multiple consumers             | Publish to **Pub/Sub / Kafka / NATS**; consumers process async.                  | Durable, decoupled fan‑out.                         |
| CPU‑bound batch computation                                      | Celery worker pool with `prefork` (multiprocessing) or dedicated Kubernetes Job. | Bypasses GIL, can autoscale.                        |

### 10.2 **Celery** — Mandatory for Long‑Running Jobs

1. **Broker:** Redis 7 for local/dev; RabbitMQ 3.13 or Google Pub/Sub in production.
2. **Result Backend:** Use Redis, PostgreSQL, or disable (fire‑and‑forget) if not needed.
3. **Idempotency:** Tasks **must** be idempotent — include unique replay keys.
4. **Retries:** Set `autoretry_for=(Exception,)`, `retry_backoff=True`, `max_retries=5` by default.
5. **Ack‑late:** Enable `acks_late=True` so tasks re‑queue on worker crash.
6. **Timeouts:** Guard CPU‑heavy tasks with `soft_time_limit` + `time_limit`.
7. **Instrumentation:** Emit task events to Prometheus via Celery‑Exporter or push to Grafana Tempo/Jaeger.

> **Docker tip:** Add `compose.celery.yml` with `worker` + `beat` services; mount your `uv.lock` to keep env parity.

### 10.3 Pub/Sub & Streaming

| Tech               | When to Use                                         | Notes                                                     |
| ------------------ | --------------------------------------------------- | --------------------------------------------------------- |
| **Google Pub/Sub** | Cloud‑native fan‑out, 10k+ msg/s; auto‑scales.      | Use push subscriptions for near‑real‑time HTTP callbacks. |
| **Kafka**          | High‑volume ordered streams, log‑based audits.      | Run via Confluent Cloud or MSK to avoid ops.              |
| **NATS**           | Ultra‑light, <1 ms latency, request‑reply patterns. | Good for internal microservices in Kubernetes.            |

Rules:

* Use schematized payloads (Avro/Protobuf or JSON validated by Pydantic).
* Include trace headers (`traceparent`) for correlation.
* Consumer code belongs in `/app/subscribers/`.

### 10.4 Async vs Thread vs Process

| Workload                                               | Prefer                                                  | Because                            |
| ------------------------------------------------------ | ------------------------------------------------------- | ---------------------------------- |
| Many small I/O ops                                     | **`asyncio`** (FastAPI, httpx)                          | Minimal threads, high concurrency. |
| CPU‑bound (image resize, crypto)                       | **multiprocessing / Celery**                            | GIL‑free parallelism.              |
| Blocking library with no async port (e.g., legacy SDK) | **`ThreadPoolExecutor`** via `anyio.to_thread.run_sync` | Avoids blocking event loop.        |

Guidelines:

* Never call blocking code directly inside `async def`; wrap in `to_thread`.
* Keep thread pool size ≤ CPU cores ×2.
* Use `asyncpg`, `aioredis`, `aiohttp` for common async clients.

### 10.5 Testing & CI

* Use [`pytest-celery`](https://pypi.org/project/pytest-celery/) to spin up an ephemeral worker for integration tests.
* Mock Pub/Sub topics with \[`pubsub-emulator`], Kafka with `testcontainers`.
* Validate that every task returns within its declared time limit using `py‑test‑timeout`.

> **Rule:** If you add a task queue or message topic, document it in `m2m/README.md` (purpose, schema, idempotency key) so agents and humans stay in sync.

### 10.6 Celery Minimal Example

```python
# tasks.py
from celery import Celery
app = Celery("worker", broker="redis://redis:6379/0", backend="redis://redis:6379/1")

@app.task(acks_late=True, autoretry_for=(Exception,), retry_backoff=True)
def add(a: int, b: int) -> int:
    return a + b
```

Run `celery -A tasks worker -l info`.

---

## 11. Data Persistence & Storage Choices

### 11.1 Core Principles

1. **Own your data**: Each micro‑service controls its own datastore; cross‑service queries flow through APIs or async events—never through shared DB tables.
2. **Right tool for the job**: Pick the engine that matches access patterns (OLTP, graph traversals, vector similarity, full‑text search).
3. **Schema‑first**: Maintain schema definitions in Git (SQL migrations, OpenAPI‑backed event payloads, GraphQL SDL, etc.). Apply via automated CI/CD.
4. **Observability & backups**: Metrics, slow‑query logs, and nightly off‑site backups are non‑negotiable—even in dev/staging.

### 11.2 Database Matrix

| Engine              | Use‑Case Sweet Spot                                                 | Async Driver                    | Migration Tool                    | Recommended Image Tag                       |
| ------------------- | ------------------------------------------------------------------- | ------------------------------- | --------------------------------- | ------------------------------------------- |
| **PostgreSQL 16**   | OLTP, JSONB, analytical queries, extensions (PostGIS, TimescaleDB). | `asyncpg`, `psycopg[pool]`      | Alembic                           | `postgres:16.2-alpine`                      |
| **SQLite 3.45**     | Simple CLI apps, embedded tests, edge devices.                      | `aiosqlite`                     | `sqlite-utils`, Alembic (offline) | Bundled                                     |
| **MongoDB 7**       | High‑write schemaless docs, rapid prototyping.                      | `motor`                         | Mongo‑Migrate / Mongock           | `mongodb/mongodb-community-server:7.0-ubi8` |
| **Neo4j 5**         | Deep graph traversals, recommendation, fraud detection.             | `neo4j-driver` (`asyncio` mode) | Liquibase‑Neo4j                   | `neo4j:5.20`                                |
| **Elasticsearch 8** | Full‑text search, log analytics, observability.                     | `elasticsearch[async]`          | Index template JSONs + ILM        | `elastic/elasticsearch:8.13.0`              |
| **Chroma 0.4**      | Lightweight local vector DB (in‑proc / server) for semantic RAG.    | `chromadb`                      | n/a (implicit collections)        | `ghcr.io/chroma-core/chroma:0.4.24`         |
| **Qdrant 1.9**      | Production vector search, HNSW, filtering.                          | `qdrant-client[async]`          | Collection schema JSON            | `qdrant/qdrant:v1.9.0`                      |

> **Tip:** Pair Postgres with the [pgvector](https://github.com/pgvector/pgvector) extension when you need both relational and vector similarity in the same dataset.

### 11.3 Operational Best Practices

* **Connection Pooling**: Use `asyncpg.create_pool()` (FastAPI startup) or PgBouncer for Postgres; configure pool size = (min(32, CPU×2)).
* **Migrations**: Auto‑generate with Alembic—review SQL diff before merge; CI runs `alembic upgrade head --sql` to lint.
* **Backups**: Nightly `pg_dump` or WAL‑archiving to S3; MongoDB Atlas continuous backup; Neo4j `neo4j-admin dump`.
* **Monitoring**: Export metrics (`pg_exporter`, `mongodb_exporter`, `qdrant_exporter`) to Prometheus; set SLOs on p95 latency and error‑rate.
* **Security**: Least‑privileged DB accounts; rotate secrets via Doppler/Vault; enable TLS in transit.

### 11.4 Patterns in Microservices

| Pattern                       | When to Pick                            | Notes                                                                      |
| ----------------------------- | --------------------------------------- | -------------------------------------------------------------------------- |
| **Database‑per‑Service**      | Default                                 | Avoids tight coupling; join data in app layer or via async saga / CQRS.    |
| **Event‑Sourcing + Snapshot** | Auditability, temporal queries          | Store immutable events (Kafka) + projections in Postgres/Elastic.          |
| **Polyglot Persistence**      | One service needs graph + search + OLTP | Keep write canonical in Postgres, index into Neo4j/Elastic asynchronously. |
| **Shared Read Replica**       | Complex cross‑domain reporting          | Expose read‑only replica to analytics service—never write.                 |

### 11.5 Example Compose Snippets

*Postgres + pgvector + adminer (`compose.db.vector.yml`)*

```yaml
services:
  postgres:
    image: ankane/pgvector:0.8.1-pg16   # pgvector baked in
    environment:
      POSTGRES_PASSWORD: devpass
    volumes: [pgdata:/var/lib/postgresql/data]

  adminer:
    image: adminer:4.8
    ports: ["8082:8080"]
    depends_on: [postgres]

volumes:
  pgdata:
```

*Qdrant + Grafana dashboard (`compose.vector.yml`)*

```yaml
services:
  qdrant:
    image: qdrant/qdrant:v1.9.0
    ports: ["6333:6333", "6334:6334"]

  grafana:
    image: grafana/grafana:11.0.0
    ports: ["3002:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
```

> **Rule:** Declare every database/collection/graph index in `m2m/README.md`—include purpose, schema/version table, backup plan, and retention policy.

### 11.6 CI Migration Stage

```yaml
- name: Alembic dry‑run migration
  run: |
    alembic upgrade head --sql | tee migration.sql
    test -s migration.sql  # fail if empty
```

---

## 12. AI & Data‑Science Practices

### 12.1 Model Serving & Local LLMs

| Tool                                        | Use Case                                                                                          | Notes                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Ollama**                                  | Quickly spin up local LLMs (Mistral, Llama 3) for prototypes, private inference, or edge devices. | Mount `~/.ollama` as a volume in Docker; bind GPU with `--gpus all` if available. |
| **vLLM**                                    | High‑throughput, GPU‑optimized serving for production.                                            | Pair with Triton or FastAPI adapter; use CUDA 12 base image.                      |
| **HuggingFace `text-generation-inference`** | Multi‑GPU distributed serving of bigger models.                                                   | Requires Nvidia A100/H100; run behind Traefik.                                    |

Guidelines:

* **Tag images by model + version** (`ollama/llama3:70b‑q4_1`).
* Store model configs (`model‑config.yaml`) in `m2m/` and load via entrypoint.
* For CPU‑only nodes, pick quantized variants (`q4_K_M`) or distilled models (TinyLlama).

### 12.2 NLP Stack (Python)

| Layer        | Preferred Lib                                      | Alternatives                              |
| ------------ | -------------------------------------------------- | ----------------------------------------- |
| Tokenization | `tokenizers` (HF)                                  | `spaCy` tokenizers                        |
| Core NLP     | **spaCy v3** for POS/NER; `en_core_web_trf` model. | NLTK for teaching / quick regex grammars. |
| Embeddings   | `sentence-transformers`                            | `transformers` + manual mean‑pooling      |
| Vector DB    | **Qdrant** (prod), **Chroma** (dev)                | pgvector extension                        |
| Eval & Bench | `langchain‑bench`, `lm‑eval‑harness`               | custom pytest harness                     |

> **Rule:** New NLP pipelines must expose a **pure‑function endpoint** (`/v1/ner`), accept JSON, and return Pydantic models for entities.

### 12.3 GPU vs CPU Guidelines

| Case                        | Hardware                | Settings                                                           |
| --------------------------- | ----------------------- | ------------------------------------------------------------------ |
| Training small (<1B) models | Consumer GPU (RTX 4090) | `torch.set_float32_matmul_precision("high")`, `bf16` if supported. |
| Serving quantized 7B LLM    | Single GPU (24–48 GB)   | vLLM + Flash‑Attention 2; `--gpu-memory-utilization 0.85`.         |
| Batch inference embeddings  | CPU cluster             | `sentence-transformers` with `torch.set_num_threads($CPU)`.        |
| Vector search >100M vectors | Server with AVX‑512     | Qdrant `hnsw_16` + disk cache.                                     |

### 12.4 Data Pipelines

| Stage          | Tooling                        | Comment                                                         |
| -------------- | ------------------------------ | --------------------------------------------------------------- |
| Orchestration  | **Apache Airflow 2.9**         | DAGs stored in `pipelines/` folder; deploy via Docker Operator. |
| Pythonic flows | **Prefect 2**                  | Great for local dev; run agent in K8s.                          |
| Streaming ETL  | **Apache Beam** on Dataflow    | Use for terabyte‑scale transforms.                              |
| Feature Store  | **Feast** with Postgres/Qdrant | Keep feature definitions versioned.                             |

Guidelines:

* DAG code must pass `ruff` and unit tests (`pytest pipelines/tests`).
* Schedule stored in `pipelines/schedules.yaml`, validated at CI time.

### 12.5 Experiment Tracking & Reproducibility

| Aspect | Tool | Mandatory Config | | ------------------ | --------------------
| ------------------------------------------------------ | | 💾 Artifacts |
**MLflow** | Track params + metrics; log models as `mlflow.pyfunc`. | | 📊
Dashboards | **Weights & Biases** | Link run URL in PR description. | | 🧪 Data
Versioning | **DVC** | Store datasets in S3 bucket; lockfile in Git. |

> **Rule:** All experiments must have a unique run ID, parameter snapshot, and random seed. Without these, results are non‑reviewable.

Integrate MLflow client in FastAPI `/experiments` router for quick lookup.

### 12.6 Ollama Quick‑Serve

```bash
# Pull model & run REST service
ollama pull mistral:7b-instruct
ollama serve -m mistral:7b-instruct -p 11434
```

Query:

```python
import requests, json
resp = requests.post("http://localhost:11434/api/generate", json={"prompt": "Hello"})
print(json.loads(resp.text)["response"])
```

### 12.7 MLflow Tracking Example

```python
import mlflow, sklearn
with mlflow.start_run(run_name="clf_v1"):
    model.fit(X_train, y_train)
    mlflow.sklearn.log_model(model, "model")
    mlflow.log_metric("accuracy", acc)
```

---

## 13. Edge‑Case Pitfalls & Gotchas  🛑

| Category     | Gotcha                                               | Mitigation                                                |
| ------------ | ---------------------------------------------------- | --------------------------------------------------------- |
| **asyncio**  | Blocking lib in `async def` freezes loop.            | Use `asyncio.to_thread` or process pool.                  |
|              | `asyncio.run()` inside running loop (e.g., Jupyter). | Use `await` or `nest_asyncio`.                            |
| **Docker**   | Memory‑overcommit OOM kills containers.              | Set `mem_limit`, monitor `docker stats`.                  |
|              | Mac OS file‑sync slowness.                           | Mount volumes with `cached` or use *colima*.              |
| **Gunicorn** | Worker timeout kills long streaming responses.       | Switch to `uvicorn --reload` in dev or tweak `--timeout`. |
| **Celery**   | Lost tasks when broker restarts.                     | Enable `acks_late` + `worker_prefetch_multiplier=1`.      |

---

## 14. References

### 14.1 Formatting and Linting

[1] "The Ruff Formatter | Ruff", <https://docs.astral.sh/ruff/formatter/>, 2024
[2] "The Ruff Formatter: An extremely fast, Black-compatible Python formatter", <https://astral.sh/blog/the-ruff-formatter>, 2023
[3] "Black vs Ruff - What's the difference?", <https://www.packetcoders.io/whats-the-difference-black-vs-ruff/>, November 2, 2023
[4] "FAQ | Ruff", <https://docs.astral.sh/ruff/faq/>, 2024

### 14.2 Python Versioning

[5] "Python Release Python 3.13.0", <https://www.python.org/downloads/release/python-3130/>, October 7, 2024
[6] "PEP 719 – Python 3.13 Release Schedule", <https://peps.python.org/pep-0719/>, 2024
[7] "What's New In Python 3.13", <https://docs.python.org/3/whatsnew/3.13.html>, October 7, 2024
[8] "Python Documentation by Version", <https://www.python.org/doc/versions/>, 2025

### 14.3 Docker Compose

[9] "docker-compose.yml file naming convention", <https://stackoverflow.com/questions/49718431/docker-compose-yml-file-naming-convention>, 2018
[10] "Why should you call the Docker Compose file 'compose.yaml' instead of 'docker-compose.yaml'?", <https://stackoverflow.com/questions/76751032/why-should-you-call-the-docker-compose-file-compose-yaml-instead-of-docker-co>, 2023
[11] "Does it matter if the docker compose file is named docker-compose.yml or compose.yml?", <https://stackoverflow.com/questions/74317741/does-it-matter-if-the-docker-compose-file-is-named-docker-compose-yml-or-compose>, 2022
[12] "How Compose works | Docker Docs", <https://docs.docker.com/compose/intro/compose-application-model/>, 2024
[13] "Preferred compose file name is now 'compose.yaml' instead of 'docker-compose.yml'", <https://github.com/microsoft/vscode-docker/issues/2618>, 2022

### 14.4 Database Connection and Worker Configuration

[14] "Choosing DB pool_size for a Flask-SQLAlchemy app running on Gunicorn", <https://stackoverflow.com/questions/60233495/choosing-db-pool-size-for-a-flask-sqlalchemy-app-running-on-gunicorn>, 2020
[15] "Design — Gunicorn 23.0.0 documentation", <https://docs.gunicorn.org/en/stable/design.html>, 2024
[16] "Gunicorn Worker Types: How to choose the right one", <https://dev.to/lsena/gunicorn-worker-types-how-to-choose-the-right-one-4n2c>, September 30, 2021

### 14.5 Secrets Management

[17] "Dotenv Vault vs Doppler", <https://www.dotenv.org/blog/2023/05/16/dotenv-vault-vs-doppler.html>, May 16, 2023
[18] "Why syncing .env files doesn't scale for secrets management", <https://dev.to/doppler/why-syncing-env-files-doesnt-scale-for-secrets-management-5325>, October 13, 2022
[19] "How to Handle Secrets in Python", <https://blog.gitguardian.com/how-to-handle-secrets-in-python/>, January 30, 2025
[20] "Secrets Management: Doppler or HashiCorp Vault?", <https://thenewstack.io/secrets-management-doppler-or-hashicorp-vault/>, January 31, 2022

### 14.6 Typing and Language Features (NEW)

[21] "PEP 3129 – Class Decorators", <https://peps.python.org/pep-3129/>, May 1, 2007
[22] "PEP 695 – Type Parameter Syntax", <https://peps.python.org/pep-0695/>, June 15, 2022
[23] "PEP 696 – Type Defaults for Type Parameters", <https://peps.python.org/pep-0696/>, July 14, 2022

---

> End of document. Submit PRs to enhance sections or propose new recipes.
