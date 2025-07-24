## 3. Modern Python Syntax & Idioms
*   **Use f-strings** for string formatting (e.g., `f"Hello, {name}!"`).
*   **Type Hinting ([PEP 484](https://peps.python.org/pep-0484/)+)** improves clarity; run tools like `mypy` for static checks.
*   **Data Classes ([PEP 557](https://peps.python.org/pep-0557/))** via `@dataclass` reduce boilerplate for data containers.
*   **`pathlib`** for filesystem paths; prefer `os.scandir()` over `os.listdir()` when metadata is needed.
*   **Context Managers** with `with` for resource management.
*   **`breakpoint()`** (Python 3.7+) as a modern debugger hook.
*   **`enumerate()`**, dictionary/set comprehensions, and the **walrus operator (`:=`)** where they aid readability.
*   **Walrus operator demo**:
    ```python
    if (chunk := stream.read(1024)):
        process(chunk)  # more concise than two-line read+check.
    ```
*   **New Type Parameter Syntax ([PEP 695](https://peps.python.org/pep-0695/))**: For Python 3.12+, use the new syntax for defining generic functions and classes (e.g., `def func[T](...)`, `class MyClass[T]: ...`), and type aliases (`type AliasName[T] = ...`). This syntax is generally clearer and avoids explicit `TypeVar` definitions in simple cases.
*   **`collections.abc`** when defining custom collections.
*   **Timezone-aware `datetime`** objects for unambiguous timestamps.

### 3.1 Referenced Python Enhancement Proposals (PEPs)

This guide references or incorporates principles from the following PEPs:

*   **[PEP 8](https://peps.python.org/pep-0008/):** Style Guide for Python Code (See §2 Code Style & Formatting)
*   **[PEP 20](https://peps.python.org/pep-0020/):** The Zen of Python ("Explicit is better than implicit", See §4 Application Design & Structure)
*   **[PEP 257](https://peps.python.org/pep-0257/):** Docstring Conventions (See Language-Specific Rules)
*   **[PEP 484](https://peps.python.org/pep-0484/):** Type Hints (See §3 Modern Python Syntax & Idioms, Language-Specific Rules)
*   **[PEP 557](https://peps.python.org/pep-0557/):** Data Classes (See §3 Modern Python Syntax & Idioms)
*   **[PEP 695](https://peps.python.org/pep-0695/):** Type Parameter Syntax (Introduces `type` statements and `def func[T]`, `class Class[T]` syntax; See §3 Modern Python Syntax & Idioms)
*   **[PEP 696](https://peps.python.org/pep-0696/):** Type Defaults for Type Parameters (Allows defaults in type parameters, e.g., `type ListOrSet[T = int] = ...`; requires Python 3.13+)
*   **[PEP 719](https://peps.python.org/pep-0719/):** Python 3.13 Release Schedule (See §15 References)
*   **[PEP 3129](https://peps.python.org/pep-3129/):** Class Decorators (Extends decorator syntax to classes)

> **Python Version Note:** This guide assumes Python 3.12+ with a preference for Python 3.13 when available. Features that require Python 3.13 specifically are clearly marked.

---

<!-- The next section's anchor will be generated automatically by MkDocs from its header -->