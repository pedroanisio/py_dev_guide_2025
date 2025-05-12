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