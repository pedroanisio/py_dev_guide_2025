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