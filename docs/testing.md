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