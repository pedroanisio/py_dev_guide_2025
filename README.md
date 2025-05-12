# py_dev_guide_2025

Welcome to **py_dev_guide_2025**, the definitive guide to Python development best practices for 2025. This comprehensive resource provides actionable recommendations for building high-quality, modern Python applications, covering everything from environment setup to AI and data science workflows.

Built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme, this guide is designed for Python developers aiming to follow industry-standard practices in 2025.

---

## 🎯 Purpose

**py_dev_guide_2025** is your go-to reference for:

- Setting up reproducible Python environments with [`uv`](https://github.com/astral-sh/uv) and Python 3.13.
- Writing clean, maintainable code with `PEP 8`, [`black`](https://github.com/psf/black), and type hinting.
- Designing robust applications using SOLID principles and [`Pydantic v2`](https://docs.pydantic.dev/latest/).
- Testing effectively with [`pytest`](https://docs.pytest.org/) and Test-Driven Development (TDD).
- Containerizing applications with Docker and deploying with confidence.
- Building APIs with [`FastAPI`](https://fastapi.tiangolo.com/), managing tasks with [`Celery`](https://docs.celeryq.dev/), and persisting data with modern databases.
- Implementing AI and data science pipelines using tools like [`Ollama`](https://ollama.ai/) and [`MLflow`](https://mlflow.org/).

Whether you're a solo developer or part of a team, this guide helps you craft elegant, scalable Python software.

---

## 📖 Documentation

The full guide is available as an interactive MkDocs site, either locally or hosted.

### Key Sections:
- **Ethos**: Our philosophy for coding excellence.
- **Environment Management**: Git, virtual environments, dependencies.
- **Code Style**: Formatting with `black`, PEP 8 compliance.
- **Testing**: Using `pytest` and enforcing coverage.
- **Containerization**: Using Docker in dev and prod.
- **API Development**: FastAPI usage patterns.
- **AI & Data Science**: Serving models, data pipelines.

📍 [View Local Setup Guide](#-getting-started)  
📍 Hosted version (add your deployed URL here): `https://your-hosted-site-url`

---

## 🚀 Getting Started

### Prerequisites

- Python **3.13+**  
- [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- Git

### Installation

Clone the repository:

```bash
git clone https://github.com/pedroanisio/py_dev_guide_2025.git
cd py_dev_guide_2025
````

(Optional) Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

Install MkDocs and dependencies:

```bash
pip install mkdocs mkdocs-material
```

### Serve Locally

```bash
mkdocs serve
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

### Build for Deployment

```bash
mkdocs build
```

This generates the static site in the `site/` directory, ready to deploy to GitHub Pages, Netlify, or another platform.

---

## 🛠️ Contributing

We welcome contributions to improve **py\_dev\_guide\_2025**!

1. Fork the repository.
2. Create a branch:

   ```bash
   git checkout -b feature/my-improvement
   ```
3. Make your changes in the `docs/` folder.
4. Test locally:

   ```bash
   mkdocs serve
   ```
5. Open a Pull Request with a clear description.

Please follow the guide’s [Code Style](docs/style.md) and [Ethos](docs/ethos.md) when contributing.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

For questions, suggestions, or feedback, open an [issue on GitHub](https://github.com/pedroanisio/py_dev_guide_2025/issues) or contact the maintainer:

📧 [pedroanisio@arc4d3.com](mailto:pedroanisio@arc4d3.com)

---

Happy coding, and let’s build excellent Python software together in 2025!
