#!/usr/bin/env python3
"""
Code Style & Formatting - Living Documentation

This module demonstrates Python code style and formatting best practices (§2 in our guide)
by both explaining and implementing them. It shows proper Python style through examples
while narrating the reasoning behind each convention.

Key concepts demonstrated:
- PEP 8 style guidelines 
- Naming conventions
- Code layout and organization
- Automatic formatters (Ruff)
- Import organization
- Pre-commit hooks

Run this file directly to see a narrated demonstration of Python code style.
"""

import os
import re
import sys
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from pathlib import Path
import subprocess
from collections import defaultdict


class CodeStyleAndFormatting:
    """
    Code Style & Formatting
    
    A class demonstrating best practices for Python code style as defined in §2.
    This class itself follows the style guidelines it teaches.
    """
    
    def __init__(self):
        """Initialize with style configuration from §2 of our guide."""
        self.name = "Code Style & Formatting"
        self.style_guide = "PEP 8"
        self.formatter = "ruff"
        self.imports_sorter = "isort"
        
        # Line length recommendation
        self.max_line_length = 100  # §2 recommends 100, though PEP 8 uses 79
        
        # Naming conventions (§2)
        self.naming_conventions = {
            "functions": "lower_case_with_underscores",
            "variables": "lower_case_with_underscores",
            "constants": "ALL_CAPS_WITH_UNDERSCORES",
            "classes": "CapWords (CamelCase)",
            "modules": "lower_case_with_underscores",
            "protected_members": "_single_leading_underscore",
            "private_members": "__double_leading_underscore",
        }
        
        # Configuration for ruff
        self.ruff_config = """
[tool.ruff]
# Target Python version
target-version = "py310"

# Line length is 100 characters (§2 recommends 100)
line-length = 100

# Enable flake8 rules and other lints
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "B",   # flake8-bugbear
    "I",   # isort
]

# Never try to automatically fix these violations
unfixable = ["B"]

[tool.ruff.format]
# Use double quotes for strings consistently
quote-style = "double"

# Indent with 4 spaces
indent-style = "space"
indent-size = 4

# Include trailing commas for multiline sequences
skip-magic-trailing-comma = false
"""
        
        # Pre-commit hooks configuration
        self.pre_commit_config = """
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0  # Use the latest version
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
"""
    
    def demonstrate_naming_conventions(self):
        """
        Demonstrate Python naming conventions following §2 guidelines.
        
        This method shows good and bad examples of naming in Python.
        """
        print("\n" + "=" * 80)
        print("📝 NAMING CONVENTIONS")
        print("=" * 80)
        print("✨ Following §2: 'Use descriptive, intention-revealing names'")
        
        # GOOD EXAMPLES - this class demonstrates the conventions it teaches
        
        # Variables (lowercase with underscores)
        user_count = 42
        active_users = ["alice", "bob"]
        
        # Constants (ALL CAPS with underscores)
        MAX_RETRY_COUNT = 5
        DEFAULT_TIMEOUT_SECONDS = 30
        
        # Function (lowercase with underscores)
        def calculate_average_score(scores):
            """Example function with proper naming."""
            if not scores:
                return 0
            return sum(scores) / len(scores)
        
        # Class (CapWords / CamelCase)
        class UserProfile:
            """Example class with proper naming."""
            def __init__(self, username, email):
                # Protected member (single underscore)
                self._user_id = 123  # Hint that this is protected
                
                # Private member (double underscore - will be name mangled)
                self.__password_hash = "secret"  # Will be _UserProfile__password_hash
                
                # Public members
                self.username = username
                self.email = email
            
            def get_display_name(self):
                """Example method with proper naming."""
                return f"{self.username} ({self.email})"
        
        print("\n✅ GOOD NAMING EXAMPLES:")
        code_examples = [
            "# Variables (lowercase with underscores)",
            "user_count = 42",
            "active_users = ['alice', 'bob']",
            "",
            "# Constants (ALL CAPS with underscores)",
            "MAX_RETRY_COUNT = 5",
            "DEFAULT_TIMEOUT_SECONDS = 30",
            "",
            "# Function (lowercase with underscores)",
            "def calculate_average_score(scores):",
            "    if not scores:",
            "        return 0",
            "    return sum(scores) / len(scores)",
            "",
            "# Class (CapWords / CamelCase)",
            "class UserProfile:",
            "    def __init__(self, username, email):",
            "        # Protected member (single underscore)",
            "        self._user_id = 123",
            "",
            "        # Private member (double underscore - will be name mangled)",
            "        self.__password_hash = 'secret'",
            "",
            "        # Public members",
            "        self.username = username",
            "        self.email = email"
        ]
        
        for line in code_examples:
            print(f"  {line}")
        
        # BAD EXAMPLES - common mistakes to avoid
        print("\n❌ BAD NAMING EXAMPLES:")
        bad_examples = [
            "# Too short or unclear variable names",
            "u = 42  # What is 'u'?",
            "a = ['alice', 'bob']  # What is 'a'?",
            "",
            "# Inconsistent capitalization",
            "maxRetryCount = 5  # Mixed case for variable (should be max_retry_count)",
            "default_timeout_SECONDS = 30  # Mixed case and capitalization",
            "",
            "# Class not using CamelCase",
            "class user_profile:  # Should be UserProfile",
            "    pass",
            "",
            "# Function using camelCase instead of snake_case",
            "def calculateAverageScore(scores):  # Should be calculate_average_score",
            "    pass"
        ]
        
        for line in bad_examples:
            print(f"  {line}")
        
        print("\n📝 Key principles:")
        for type_name, convention in self.naming_conventions.items():
            print(f"  • {type_name.replace('_', ' ').title()}: {convention}")
        
        print("\n💡 Remember: Names should be descriptive, intentional, and pronounceable!")
    
    def demonstrate_code_layout(self):
        """
        Demonstrate code layout and organization following §2 guidelines.
        
        This method shows proper indentation, whitespace, and line breaks.
        """
        print("\n" + "=" * 80)
        print("📐 CODE LAYOUT & ORGANIZATION")
        print("=" * 80)
        print("✨ Following §2: 'Code layout significantly improves readability'")
        
        # Good indentation and whitespace
        print("\n✅ PROPER INDENTATION & WHITESPACE:")
        good_layout = [
            "# 4-space indentation (consistent throughout code)",
            "def calculate_total(items):",
            "    total = 0",
            "    for item in items:",
            "        price = item.get('price', 0)",
            "        quantity = item.get('quantity', 1)",
            "        total += price * quantity",
            "    return total",
            "",
            "# Proper whitespace in expressions",
            "x = 5",
            "y = x * 2 + 10",
            "is_valid = x < 10 and y > 0",
            "",
            "# Good line breaks for long lines",
            "def send_notification(",
            "    user_id,",
            "    message,",
            "    priority='normal',",
            "    delivery_method='email',",
            "):",
            "    # Function body here",
            "    pass",
            "",
            "# Dictionary with proper formatting",
            "config = {",
            "    'debug': True,",
            "    'log_level': 'INFO',",
            "    'max_connections': 100,",
            "    'timeout': 30,",
            "}"
        ]
        
        for line in good_layout:
            print(f"  {line}")
        
        # Bad indentation and whitespace
        print("\n❌ POOR INDENTATION & WHITESPACE:")
        bad_layout = [
            "# Inconsistent indentation (mixing tabs and spaces)",
            "def calculate_total(items):",
            "    total = 0",
            "    for item in items:",
            "    \tprice = item.get('price', 0)  # Tab instead of spaces",
            "      quantity = item.get('quantity', 1)  # Wrong indentation level",
            "      total += price * quantity",
            "    return total",
            "",
            "# Missing or excessive whitespace",
            "x=5  # Missing spaces around operator",
            "y = x*2+10  # Missing spaces in expression",
            "is_valid=x<10 and y>0  # Inconsistent spacing",
            "",
            "# Bad line breaks and continuations",
            "def send_notification(user_id, message, priority='normal', delivery_method='email',",
            "    notification_type='system'):  # Inconsistent indentation of wrapped line",
            "    pass",
            "",
            "# Cramming too much on one line",
            "config = {'debug': True, 'log_level': 'INFO', 'max_connections': 100, 'timeout': 30, 'retry_count': 5, 'exponential_backoff': True}"
        ]
        
        for line in bad_layout:
            print(f"  {line}")
        
        print("\n📝 Key layout principles:")
        print("  • Use 4 spaces for indentation (never tabs)")
        print(f"  • Limit line length to {self.max_line_length} characters")
        print("  • Put whitespace around operators (=, +, -, *, /, etc.)")
        print("  • Add blank lines to separate logical sections")
        print("  • Break long lines at logical points")
        print("  • Use consistent formatting for collections (lists, dicts)")
    
    def demonstrate_imports(self):
        """
        Demonstrate proper import organization following §2 guidelines.
        
        This method shows how to organize and sort imports.
        """
        print("\n" + "=" * 80)
        print("📦 IMPORT ORGANIZATION")
        print("=" * 80)
        print("✨ Following §2: 'Sort imports with isort'")
        
        # Good import organization
        print("\n✅ PROPER IMPORT ORGANIZATION:")
        good_imports = [
            "# Standard library imports first",
            "import os",
            "import re",
            "import sys",
            "from datetime import datetime, timedelta",
            "from pathlib import Path",
            "",
            "# Third-party library imports second",
            "import numpy as np",
            "import pandas as pd",
            "import requests",
            "from fastapi import FastAPI, Depends, HTTPException",
            "",
            "# Local application imports last",
            "from myapp.config import Settings",
            "from myapp.models import User, Product",
            "from myapp.utils import format_timestamp",
            "",
            "# Explicit relative imports (if needed)",
            "from . import helper",
            "from .utils import calculate_total"
        ]
        
        for line in good_imports:
            print(f"  {line}")
        
        # Bad import organization
        print("\n❌ POOR IMPORT ORGANIZATION:")
        bad_imports = [
            "# Mixed imports without grouping",
            "import pandas as pd",
            "from datetime import datetime",
            "from myapp.models import User",
            "import os",
            "from .utils import helper",
            "import sys",
            "import numpy as np",
            "",
            "# Using * imports (avoid this!)",
            "from math import *",
            "",
            "# Importing at function level (can be necessary but should be justified)",
            "def some_function():",
            "    import json  # Import buried in function",
            "    return json.dumps({'key': 'value'})"
        ]
        
        for line in bad_imports:
            print(f"  {line}")
        
        # isort configuration
        print("\n📄 ISORT CONFIGURATION (via ruff):")
        isort_config = [
            "[tool.ruff.isort]",
            "# Group imports into sections",
            "sections = [",
            "    'FUTURE',",
            "    'STDLIB',",
            "    'THIRDPARTY',",
            "    'FIRSTPARTY',",
            "    'LOCALFOLDER',",
            "]",
            "",
            "# Group first-party imports",
            "known-first-party = ['myapp']"
        ]
        
        for line in isort_config:
            print(f"  {line}")
        
        print("\n📝 Key import principles:")
        print("  • Group imports: standard library, third-party, local application")
        print("  • Sort alphabetically within each group")
        print("  • Use absolute imports when possible")
        print("  • Avoid wildcard imports (from module import *)")
        print("  • Use isort (via ruff) to automate import sorting")
    
    def demonstrate_auto_formatters(self):
        """
        Demonstrate automatic code formatters following §2 guidelines.
        
        This method explains and shows how to use ruff for formatting.
        """
        print("\n" + "=" * 80)
        print("🔧 AUTOMATIC FORMATTERS")
        print("=" * 80)
        print("✨ Following §2: 'Use Automatic Formatters'")
        
        # Check if ruff is installed
        try:
            result = subprocess.run(["ruff", "--version"], capture_output=True, text=True)
            has_ruff = result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            has_ruff = False
        
        ruff_version = result.stdout.strip() if has_ruff else "not installed"
        
        print(f"\n🔍 Ruff: {ruff_version}")
        
        # Ruff configuration
        print("\n📄 RUFF CONFIGURATION (pyproject.toml):")
        for line in self.ruff_config.strip().split("\n"):
            print(f"  {line}")
        
        # Before and after formatting
        print("\n📝 BEFORE & AFTER FORMATTING:")
        before_code = [
            "# Poorly formatted code",
            "def  calculate_metrics(data,verbose = True,):",
            "    total = sum(data)",
            "    average=total/len(data)if len(data)>0 else 0",
            "    metrics={'total':total,'average':average,'count':len(data), }",
            "    if verbose == True : print(f'Calculated metrics: {metrics}')",
            "    return     metrics"
        ]
        
        after_code = [
            "# After ruff formatting",
            "def calculate_metrics(data, verbose=True):",
            "    total = sum(data)",
            "    average = total / len(data) if len(data) > 0 else 0",
            "    metrics = {",
            "        \"total\": total,",
            "        \"average\": average,",
            "        \"count\": len(data),",
            "    }",
            "    if verbose:",
            "        print(f\"Calculated metrics: {metrics}\")",
            "    return metrics"
        ]
        
        print("\n❌ Before formatting:")
        for line in before_code:
            print(f"  {line}")
        
        print("\n✅ After formatting:")
        for line in after_code:
            print(f"  {line}")
        
        # Show ruff command examples
        print("\n🔨 USING RUFF IN PRACTICE:")
        print("  • Format a single file:")
        print("    $ ruff format file.py")
        print("\n  • Format all Python files in a directory:")
        print("    $ ruff format .")
        print("\n  • Check and lint without changing files:")
        print("    $ ruff check .")
        print("\n  • Automatically fix issues:")
        print("    $ ruff check --fix .")
    
    def demonstrate_pre_commit(self):
        """
        Demonstrate pre-commit hooks following §2 guidelines.
        
        This method explains how to set up pre-commit hooks for code quality.
        """
        print("\n" + "=" * 80)
        print("🔗 PRE-COMMIT HOOKS")
        print("=" * 80)
        print("✨ Following §2: 'Automate Style Enforcement with pre-commit'")
        
        # Pre-commit configuration
        print("\n📄 PRE-COMMIT CONFIGURATION (.pre-commit-config.yaml):")
        for line in self.pre_commit_config.strip().split("\n"):
            print(f"  {line}")
        
        # Installation and usage
        print("\n🔧 INSTALLATION & USAGE:")
        install_steps = [
            "# 1. Install pre-commit",
            "$ pip install pre-commit",
            "",
            "# 2. Add .pre-commit-config.yaml to your project (content shown above)",
            "",
            "# 3. Install the git hooks",
            "$ pre-commit install",
            "",
            "# 4. Run against all files (optional)",
            "$ pre-commit run --all-files",
            "",
            "# 5. Now pre-commit will run automatically on git commit"
        ]
        
        for line in install_steps:
            print(f"  {line}")
        
        # Benefits
        print("\n📝 BENEFITS OF PRE-COMMIT HOOKS:")
        print("  • Prevents committing code that doesn't meet style guidelines")
        print("  • Ensures consistent formatting across the team")
        print("  • Catches issues early, before code review")
        print("  • Reduces bike-shedding discussions about style")
        print("  • Can run multiple tools (ruff, mypy, pytest, etc.)")
    
    def create_demo_files(self, output_dir: Path = None):
        """
        Create example files demonstrating good and bad code style.
        
        This method creates actual Python files showing proper style and common mistakes.
        """
        if not output_dir:
            output_dir = Path("./demo_style")
            output_dir.mkdir(exist_ok=True)
        
        # Good style example
        good_code = """#!/usr/bin/env python3
\"\"\"
Example module demonstrating good code style.

This module follows PEP 8 and our style guidelines from §2.
\"\"\"

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Union

import requests
from fastapi import FastAPI, Depends, HTTPException

from myapp.config import Settings
from myapp.models import User


# Constants at the module level (ALL_CAPS)
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30


def fetch_user_data(user_id: int) -> Optional[Dict[str, Union[str, int, bool]]]:
    \"\"\"
    Fetch user data from the API.
    
    Args:
        user_id: The ID of the user to fetch
        
    Returns:
        User data dictionary or None if not found
    \"\"\"
    url = f"https://api.example.com/users/{user_id}"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            if attempt == MAX_RETRIES - 1:
                return None
    
    return None


class UserManager:
    \"\"\"Class for managing user operations.\"\"\"
    
    def __init__(self, api_key: str):
        \"\"\"Initialize with API key.\"\"\"
        self._api_key = api_key  # Protected member
        self.last_accessed = datetime.utcnow()
    
    def get_user(self, user_id: int) -> Optional[User]:
        \"\"\"Get a user by ID.\"\"\"
        data = fetch_user_data(user_id)
        if not data:
            return None
        
        return User(**data)
    
    def create_user(
        self,
        username: str,
        email: str,
        is_active: bool = True,
    ) -> User:
        \"\"\"Create a new user.\"\"\"
        # Example of a longer dictionary that's still properly formatted
        user_data = {
            "username": username,
            "email": email,
            "is_active": is_active,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Some more code here...
        return User(**user_data)


def main():
    \"\"\"Main function.\"\"\"
    if len(sys.argv) != 2:
        print("Usage: python good_style.py USER_ID")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("Error: USER_ID must be an integer")
        sys.exit(1)
    
    settings = Settings()
    manager = UserManager(api_key=settings.api_key)
    user = manager.get_user(user_id)
    
    if user:
        print(f"Found user: {user.username} ({user.email})")
    else:
        print(f"User with ID {user_id} not found")


if __name__ == "__main__":
    main()
"""
        
        # Bad style example
        bad_code = """#!/usr/bin/env python3
# Bad code style example
import requests
import sys,os
from myapp.models import User
from datetime import datetime
from typing import *
from fastapi import *
from myapp.config import *

# No docstring for the module

maX_RETRIES=3
default_timeout=30 # inconsistent naming

def fetch_user_data(user_id): # No type hints
  """Fetch user data""" # Under-indented docstring
  url= f"https://api.example.com/users/{user_id}" # Missing space
  
  for attempt in range(maX_RETRIES):
    try:
      response=requests.get(url,timeout=default_timeout)
      response.raise_for_status()
      return response.json()
    except:# Bare except clause
      if attempt==maX_RETRIES-1:
          return None # Inconsistent indentation
  
  return None

class userManager: # Class name should be CamelCase
  def __init__(self,api_key):
      self.apiKey=api_key # camelCase instead of snake_case
      self.last_accessed=datetime.utcnow()
  
  def get_user(self,user_id):
      data=fetch_user_data(user_id)
      if not data: return None # Multiple statements on one line
      
      return User(**data)
  
  def create_user(self,username,email,is_active=True):
      user_data={"username":username,"email":email,"is_active":is_active,"created_at":datetime.utcnow().isoformat(),} # Too long, poor spacing
      
      # Some more code here...
      return User(**user_data)

def main():
    if len(sys.argv)!=2:
        print('Usage: python bad_style.py USER_ID')
        sys.exit(1)
    
    try:
        user_id=int(sys.argv[1])
    except ValueError:
        print("Error: USER_ID must be an integer")
        sys.exit(1)
    
    settings=Settings()
    manager=userManager(api_key=settings.api_key)
    user=manager.get_user(user_id)
    
    if user:print(f"Found user: {user.username} ({user.email})") # Multiple statements on one line
    else:
        print(f"User with ID {user_id} not found")

if __name__=="__main__":
    main()
"""
        
        # Write files
        good_path = output_dir / "good_style.py"
        with open(good_path, "w") as f:
            f.write(good_code)
        
        bad_path = output_dir / "bad_style.py"
        with open(bad_path, "w") as f:
            f.write(bad_code)
        
        print("\n" + "=" * 80)
        print("📄 EXAMPLE FILES CREATED")
        print("=" * 80)
        print(f"✨ Created example files demonstrating code style")
        
        print(f"\n✅ Good style example: {good_path}")
        print(f"❌ Bad style example: {bad_path}")
        
        print("\n📝 Compare these files to see the difference between good and bad style.")
        print("  You can also try running ruff on them to see how it would fix the bad style:")
        print(f"  $ ruff format {bad_path}")
        
        return {"good": good_path, "bad": bad_path}
    
    def run_demo(self):
        """Run a comprehensive demonstration of Python code style best practices."""
        print("\n" + "=" * 80)
        print("🚀 CODE STYLE & FORMATTING DEMONSTRATION")
        print(f"✨ Demonstrating §2 of the Python Development Best Practices")
        print("=" * 80)
        
        print("\n📋 This demonstration will show you:")
        print("  1. Naming Conventions")
        print("  2. Code Layout & Organization")
        print("  3. Import Organization")
        print("  4. Automatic Formatters")
        print("  5. Pre-commit Hooks")
        print("  6. Example Files")
        
        # Demonstrate each component
        self.demonstrate_naming_conventions()
        self.demonstrate_code_layout()
        self.demonstrate_imports()
        self.demonstrate_auto_formatters()
        self.demonstrate_pre_commit()
        self.create_demo_files()
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nRecommended next steps:")
        print("  1. Add ruff to your project:")
        print("     $ pip install ruff")
        print("  2. Create a pyproject.toml with the ruff configuration shown above")
        print("  3. Set up pre-commit hooks:")
        print("     $ pip install pre-commit")
        print("     $ pre-commit install")
        print("  4. Run formatters before committing:")
        print("     $ ruff format .")
    
    def generate_markdown(self) -> str:
        """
        Generate markdown documentation for the Code Style section
        of our best practices guide.
        """
        return f"""
## Code Style & Formatting

* **Follow PEP 8:** Adhering to the official style guide significantly improves readability and consistency. Key aspects include naming conventions, code layout, imports organization, and comments.
* **Use Automatic Formatters:** Tools like `ruff` (which includes formatting capabilities) enforce a consistent code style with minimal configuration. `isort` specifically sorts imports, though Ruff can also handle this. Many developers use them as part of their workflow or CI/CD pipeline.
* **Use Linters: Ruff** (lint + format + fix) as the default; add Flake8/Pylint only if you need a plugin Ruff doesn't yet cover.
* **Exception-to-rule:** long dictionary literals that exceed 120 chars may keep single line *if* the formatter keeps them readable; justify in PR.
* **Naming Conventions:**

  * `lower_case_with_underscores` for functions, methods, variables, and modules.
  * `CapWords` (CamelCase) for classes.
  * `_single_leading_underscore` for protected/internal members.
  * `__double_leading_underscore` for name-mangling (use sparingly).
  * `ALL_CAPS_WITH_UNDERSCORES` for constants.
  * Use descriptive, intention-revealing, pronounceable names; avoid ambiguous abbreviations.

### Automate Style Enforcement with **pre-commit**

Add a Git hook that runs *Ruff* (lint/format/fix) and *isort* (import sorting) before every commit.

1. **Declare the hook set** in a top-level `.pre-commit-config.yaml`:

   ```yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       rev: v0.5.0           # match your Ruff version
       hooks:
         - id: ruff
           args: [--fix]
         - id: ruff-format  # Added Ruff formatter hook
   ```

2. **Install** the hooks once per clone:

   ```bash
   pip install pre-commit  # or add to pyproject dependencies
   pre-commit install     # sets up .git/hooks/pre-commit
   ```

3. **Run on demand or in CI:**

   ```bash
   pre-commit run --all-files  # useful before pushing / in CI step
   ```

This guarantees every commit has imports sorted and Ruff-clean code, keeping Section 2's style rules consistently enforced.

### Configuration in pyproject.toml

```toml
[tool.ruff]
# Target Python version
target-version = "py310"

# Line length is 100 characters
line-length = 100

# Enable flake8 rules and other lints
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "B",   # flake8-bugbear
    "I",   # isort
]

# Never try to automatically fix these violations
unfixable = ["B"]

[tool.ruff.format]
# Use double quotes for strings consistently
quote-style = "double"

# Indent with 4 spaces
indent-style = "space"
indent-size = 4
```
"""
    
    def __str__(self):
        """String representation"""
        return f"{self.name}: Following {self.style_guide} with {self.formatter} automation"


# Run the demo if this file is executed directly
if __name__ == "__main__":
    code_style = CodeStyleAndFormatting()
    code_style.run_demo()