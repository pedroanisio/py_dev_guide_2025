## 6. Testing

*   **Write Tests:** Use **[`pytest`](https://docs.pytest.org/)** as the primary framework due to its rich fixtures, parametrization, and extensive plugin ecosystem.
*   **Test Types:** Include unit, integration, and end-to-end (E2E) tests as appropriate for comprehensive validation.
*   **Isolation:** Keep tests independent using mocks (e.g., [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html), [`pytest-mock`](https://pytest-mock.readthedocs.io/)) and factories/fixtures.
*   **Automation:** Integrate tests into CI/CD pipelines. Tools like [`tox`](https://tox.wiki/) or [`nox`](https://nox.thea.codes/) help run tests across different Python versions and environments.

**Mocking HTTP Requests**

Use libraries like [`responses`](https://github.com/getsentry/responses) to simulate HTTP interactions:

```python
import responses
import httpx

@responses.activate
def test_external_api_call():
    # Define the expected request and its mock response
    responses.add(
        method=responses.POST,
        url="https://api.example.com/v1/items",
        json={"id": "item_123", "status": "created"},
        status=200,
        match=[responses.matchers.json_params_matcher({"name": "Test Item"})]
    )

    # Code under test that makes the HTTP call
    client = httpx.Client()
    api_response = client.post(
        "https://api.example.com/v1/items",
        json={"name": "Test Item"}
    )

    # Assertions
    assert api_response.status_code == 200
    assert api_response.json()["id"] == "item_123"
    assert len(responses.calls) == 1 # Verify the call was made
```

### 6.1 Test-Driven Development (TDD) — 🔴 RED → 🟢 GREEN → ♻️ REFACTOR

Follow this iterative cycle for every new feature or bug fix unless explicitly instructed otherwise. This ensures tests drive implementation and prevents regressions.

| Phase                             | Command Example                   | Expectation                                            |
| :-------------------------------- | :-------------------------------- | :----------------------------------------------------- |
| **1. Write a failing test (RED)** | `pytest -k new_feature_test -q`   | The new test fails predictably (e.g., `AssertionError`). |
| **2. Implement minimal code**     | *Edit source file(s)*             | Add only the code required for the test to pass.         |
| **3. Run the test suite (GREEN)** | `pytest -q`                       | All tests, including the new one, should now pass.       |
| **4. Refactor safely**            | *Improve names, remove duplication* | Code quality improves without changing behavior. Run `pytest -q` frequently to confirm. |

> **Authoritative Tests Rule:** Code *must* satisfy the tests. Do **not** modify tests merely to make them pass. Only change tests if the requirements or specification have legitimately changed **and you explicitly state this reason**. This maintains the integrity of the test suite as a living specification.

Embed this TDD cycle into your daily workflow (e.g., using IDE test runners, file watchers triggering `pytest`, or pre-commit hooks) to build robust and maintainable code.

### 6.2 Running Pytest & Enforcing Coverage

Use [`pytest-cov`](https://pytest-cov.readthedocs.io/) to measure test coverage.

| Goal                             | Command                                                                          | Notes                                                            |
| :------------------------------- | :------------------------------------------------------------------------------- | :--------------------------------------------------------------- |
| Run the full suite (quiet)       | `pytest -q`                                                                      | Provides a fast feedback loop during development.                |
| Run tests matching a keyword     | `pytest -k "billing and not slow" -q`                                            | Use expressions (`and`, `or`, `not`) for fine-grained selection. |
| Run a specific file/directory    | `pytest tests/api/test_users.py -q`                                              | Paths are relative to the repository root.                       |
| Collect tests (no execution)     | `pytest --collect-only`                                                          | Useful for inspecting which tests `pytest` discovers.            |
| **Run with coverage**            | `pytest --cov=<package_or_srcdir> --cov-report=term-missing`                     | Shows a summary and missing line numbers in the terminal.        |
| **Enforce minimum coverage**     | `pytest --cov=<package_or_srcdir> --cov-fail-under=70 --cov-report=term-missing` | **Essential for CI.** Fails the run if coverage is below 70%.    |

**Coverage Policy**

*   **Minimum Acceptable:** 70% statement coverage (`--cov-fail-under=70`). Builds **must** fail if coverage drops below this threshold in CI.
*   **Desired Target:** ≥ 80% coverage on mainline/release branches.

Teams are encouraged to incrementally raise the threshold once the current target is met sustainably.

Add a coverage check step to your CI workflow (e.g., GitHub Actions):

```yaml
- name: Run tests and check coverage
  run: |
    # Ensure dependencies are installed (using uv)
    uv pip sync --quiet
    # Run pytest, generate coverage report, and fail if below threshold
    pytest --cov=src --cov-fail-under=70 --cov-report=xml --cov-report=term-missing
```
*(Adjust `--cov=src` to match your source directory, e.g., `--cov=<app_name>` if not using `src/` layout)*

> **Tip:** For local checks before pushing, consider adding a **pre-commit** stage using a tool like the [`pytest-pre-commit` hook](https://github.com/kevin1024/pytest-pre-commit) or by adding the coverage command to a custom `pre-push` Git hook script.

---