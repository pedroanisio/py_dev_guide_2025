# Python Best Practices as Living Documentation

This repository is a self-documenting guide to Python development best practices. Rather than just describing best practices, each module **actively demonstrates** them through executable code that also explains the underlying principles.

## Core Philosophy

- **Learn by doing**: Run any module directly to see best practices in action
- **Self-narrating code**: Each file explains what it does while it does it
- **Compare and contrast**: See both recommended practices and anti-patterns
- **Holistic coverage**: Every section of our development guide is represented

## Modules Overview

The repository is organized to match our development guide sections:

| Module | Development Guide Section | Description |
|--------|--------------------------|-------------|
| [`security.py`](./security.py) | §0: Security Practices | Secret management, auth patterns, vulnerability prevention |
| [`environment.py`](./environment.py) | §1: Environment Management & Setup | Project setup, dependency management, config isolation |
| [`code_style.py`](./code_style.py) | §2: Code Style & Formatting | PEP 8, linting, formatting tools, naming conventions |
| [`modern.py`](./modern.py) | §3: Modern Python Syntax & Idioms | Type hints, f-strings, pathlib, contextlib, etc. |
| [`application_design.py`](./application_design.py) | §4: Application Design & Structure | Project organization, SOLID, DRY principles |
| [`testing.py`](./testing.py) | §5: Testing | Pytest, mocking, TDD, coverage enforcement |
| [`validation.py`](./validation.py) | §6: Data Validation & Configuration | Pydantic models, settings management, schemas |
| [`observability.py`](./observability.py) | §7: Logging & Observability | Structured logging, tracing, monitoring |
| [`containerization.py`](./containerization.py) | §8: Containerization & Docker | Dockerfile best practices, compose patterns |
| [`fast_api_best_practice.py`](./fast_api_best_practice.py) | §9: API Development | FastAPI routes, validation, dependencies |
| [`tasks.py`](./tasks.py) | §10: Background Tasks & Concurrency | Celery, async/await, pub/sub, execution models |
| [`data_persistence.py`](./data_persistence.py) | §11: Data Persistence & Storage | Database selection, connection patterns, migrations |
| [`ai_ml_practices.py`](./ai_ml_practices.py) | §12: AI & Data-Science Practices | Model serving, pipelines, experiment tracking |
| [`edge_cases.py`](./edge_cases.py) | §13: Edge-Case Pitfalls | Common gotchas and their solutions |
| [`git_branching.py`](./git_branching.py) | §1: Environment Management (Git) | Git workflow and branching strategies |
| [`dry.py`](./dry.py) | §4: Application Design (DRY) | Don't Repeat Yourself principle |
| [`solid.py`](./solid.py) | §4: Application Design (SOLID) | SOLID principles of object-oriented design |

## Getting Started

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run any module to see it in action:
   ```bash
   python validation.py
   ```
4. Explore the integrated demo:
   ```bash
   python main.py
   ```
5. Try the sample application for a complete example:
   ```bash
   python sample_app.py
   ```

## Features

- **Interactive Learning**: Each module can be run standalone to demonstrate concepts
- **Markdown Generation**: Each module can generate its own documentation section
- **Cross-Referenced**: Files reference each other to show integration patterns
- **Anti-Patterns**: See what not to do alongside best practices
- **Real-World Examples**: Practical code samples that solve common problems

## Documentation Generation

Generate the full development guide by running:

```bash
python generate_docs.py
```

This will produce a comprehensive markdown document that pulls from all modules.

## Contributing

To contribute to this project:

1. Each file should follow the "living documentation" pattern - demonstrating what it teaches
2. Add a `generate_markdown()` method to any new module to contribute to the guide
3. Include both positive examples and anti-patterns where appropriate
4. Ensure cross-references to related modules
5. Make files both educational and executable

## License

MIT License - Use, modify, and share freely, with attribution.