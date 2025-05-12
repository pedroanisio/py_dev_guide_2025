# References and Citations

> This document contains references and citations to support technical decisions and practices outlined in the development guide.

## 📚 Table of Contents
- [14.1 Formatting and Linting](#141-formatting-and-linting)
- [14.2 Python Versioning](#142-python-versioning)
- [14.3 Docker Compose](#143-docker-compose)
- [14.4 Database Connection and Worker Configuration](#144-database-connection-and-worker-configuration)
- [14.5 Secrets Management](#145-secrets-management)
- [14.6 Typing and Language Features](#146-typing-and-language-features)

---

## 14.1 Formatting and Linting

| Reference | Title | Source | Date | Key Points |
|-----------|-------|--------|------|------------|
| [1] | The Ruff Formatter | [Ruff Documentation](https://docs.astral.sh/ruff/formatter/) | 2024 | Official documentation for Ruff formatting capabilities |
| [2] | The Ruff Formatter: An extremely fast, Black-compatible Python formatter | [Astral Blog](https://astral.sh/blog/the-ruff-formatter) | 2023 | Technical deep-dive on Ruff's performance advantages |
| [3] | Black vs Ruff - What's the difference? | [PacketCoders](https://www.packetcoders.io/whats-the-difference-black-vs-ruff/) | November 2, 2023 | Comparative analysis of formatting tools |
| [4] | FAQ \| Ruff | [Ruff Documentation](https://docs.astral.sh/ruff/faq/) | 2024 | Common questions about Ruff integration and usage |

## 14.2 Python Versioning

| Reference | Title | Source | Date | Key Points |
|-----------|-------|--------|------|------------|
| [5] | Python Release Python 3.13.0 | [Python.org](https://www.python.org/downloads/release/python-3130/) | October 7, 2024 | Official release announcement with feature highlights |
| [6] | PEP 719 – Python 3.13 Release Schedule | [Python.org/PEPs](https://peps.python.org/pep-0719/) | 2024 | Timeline for beta, RC, and final release dates |
| [7] | What's New In Python 3.13 | [Python Documentation](https://docs.python.org/3/whatsnew/3.13.html) | October 7, 2024 | Comprehensive list of new features and improvements |
| [8] | Python Documentation by Version | [Python.org](https://www.python.org/doc/versions/) | 2025 | Historical archive of all Python documentation versions |

## 14.3 Docker Compose

| Reference | Title | Source | Date | Key Points |
|-----------|-------|--------|------|------------|
| [9] | docker-compose.yml file naming convention | [Stack Overflow](https://stackoverflow.com/questions/49718431/docker-compose-yml-file-naming-convention) | 2018 | Community consensus on compose file naming |
| [10] | Why should you call the Docker Compose file 'compose.yaml' instead of 'docker-compose.yaml'? | [Stack Overflow](https://stackoverflow.com/questions/76751032/why-should-you-call-the-docker-compose-file-compose-yaml-instead-of-docker-co) | 2023 | Rationale for current naming recommendations |
| [11] | Does it matter if the docker compose file is named docker-compose.yml or compose.yml? | [Stack Overflow](https://stackoverflow.com/questions/74317741/does-it-matter-if-the-docker-compose-file-is-named-docker-compose-yml-or-compose) | 2022 | Practical implications of different naming conventions |
| [12] | How Compose works \| Docker Docs | [Docker Documentation](https://docs.docker.com/compose/intro/compose-application-model/) | 2024 | Official documentation on compose architecture |
| [13] | Preferred compose file name is now 'compose.yaml' instead of 'docker-compose.yml' | [GitHub Issue](https://github.com/microsoft/vscode-docker/issues/2618) | 2022 | VS Code integration changes reflecting Docker's recommendations |

## 14.4 Database Connection and Worker Configuration

| Reference | Title | Source | Date | Key Points |
|-----------|-------|--------|------|------------|
| [14] | Choosing DB pool_size for a Flask-SQLAlchemy app running on Gunicorn | [Stack Overflow](https://stackoverflow.com/questions/60233495/choosing-db-pool-size-for-a-flask-sqlalchemy-app-running-on-gunicorn) | 2020 | Guidelines for connection pool sizing |
| [15] | Design — Gunicorn 23.0.0 documentation | [Gunicorn Documentation](https://docs.gunicorn.org/en/stable/design.html) | 2024 | Architecture details on Gunicorn's worker model |
| [16] | Gunicorn Worker Types: How to choose the right one | [Dev.to](https://dev.to/lsena/gunicorn-worker-types-how-to-choose-the-right-one-4n2c) | September 30, 2021 | Comparison of sync, async, and thread worker types |

## 14.5 Secrets Management

| Reference | Title | Source | Date | Key Points |
|-----------|-------|--------|------|------------|
| [17] | Dotenv Vault vs Doppler | [Dotenv.org Blog](https://www.dotenv.org/blog/2023/05/16/dotenv-vault-vs-doppler.html) | May 16, 2023 | Feature comparison of secrets management tools |
| [18] | Why syncing .env files doesn't scale for secrets management | [Dev.to](https://dev.to/doppler/why-syncing-env-files-doesnt-scale-for-secrets-management-5325) | October 13, 2022 | Challenges with traditional environment file approaches |
| [19] | How to Handle Secrets in Python | [GitGuardian Blog](https://blog.gitguardian.com/how-to-handle-secrets-in-python/) | January 30, 2025 | Best practices for Python-specific secrets handling |
| [20] | Secrets Management: Doppler or HashiCorp Vault? | [The New Stack](https://thenewstack.io/secrets-management-doppler-or-hashicorp-vault/) | January 31, 2022 | Enterprise-focused comparison of solutions |

## 14.6 Typing and Language Features

| Reference | Title | Source | Date | Key Points |
|-----------|-------|--------|------|------------|
| [21] | PEP 3129 – Class Decorators | [Python.org/PEPs](https://peps.python.org/pep-3129/) | May 1, 2007 | Specification for decorator syntax on classes |
| [22] | PEP 695 – Type Parameter Syntax | [Python.org/PEPs](https://peps.python.org/pep-0695/) | June 15, 2022 | Introduction of first-class type parameter declarations |
| [23] | PEP 696 – Type Defaults for Type Parameters | [Python.org/PEPs](https://peps.python.org/pep-0696/) | July 14, 2022 | Specification for default values in generic types |

---

## Contributing

> To add new references, please follow the established table format and include complete citation information. Submit PRs to enhance sections or propose new categories.