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