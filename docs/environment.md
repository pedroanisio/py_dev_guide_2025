## 1. Environment Management & Setup  
* **Initialize the Repository:** Create a new Git repository (e.g., on GitHub), add and commit a minimal `README.md`, push to `main`, then clone the repository onto your development machine *before* any environment work. Follow a lightweight branching flow: keep `main` production-ready, use `dev` (or `develop`) for ongoing integration, and create short-lived `feature/*`, `bugfix/*`, or `hotfix/*` branches that merge back via pull requests.  
* **Multi-environment pattern:**  
```text
.env        # local dev
.env.staging
.env.prod   # loaded in CI/CD → Secrets Manager at runtime
```  
`Settings()` picks env file via `ENVIRONMENT=prod` var.  
* **Use Virtual Environments:** Prefer `uv`—a fast, drop-in Python installer and virtual-environment manager—to create isolated environments and prevent dependency conflicts.  
* **Use the Latest Stable Python:** Aim to use the most recent stable version of Python (e.g., **3.13** as of mid-2025) that is compatible with your project's dependencies to leverage new features and performance improvements. Check project requirements for minimum versions.  
* **Dependency Management (`uv`-centric):**  
* Declare dependencies in `pyproject.toml` under `[project] dependencies` (or an equivalent tool-specific section).  
* Resolve and pin exact versions with `uv pip compile`, committing the generated **`uv.lock`** file for fully reproducible builds (hashes included by default).  
* Recreate environments deterministically using `uv pip sync` (or `uv pip install -r uv.lock`).  
* Use `uv pip list --outdated` (or `uv pip upgrade`) to identify and apply updates; always run the full test suite after upgrades.  
* Integrate `uv pip audit` (or tools like `safety`) into CI/CD to catch known vulnerabilities early.  
---