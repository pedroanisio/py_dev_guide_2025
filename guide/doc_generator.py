#!/usr/bin/env python3
"""
Documentation Generator

This script imports all modules with documentation generators and combines
their output into a single comprehensive guide.
"""

import importlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Mapping of modules to their section numbers and titles
MODULE_MAP = [
    ("security", 0, "Security Practices"),
    ("environment", 1, "Environment Management & Setup"),
    ("code_style", 2, "Code Style & Formatting"),
    ("modern", 3, "Modern Python Syntax & Idioms"),
    ("application_design", 4, "Application Design & Structure"),
    ("testing", 5, "Testing"),
    ("validation", 6, "Data Validation & Configuration — Pydantic v2"),
    ("observability", 7, "Logging & Observability"),
    ("containerization", 8, "Containerization & Docker Usage"),
    ("fast_api_best_practice", 9, "API Development — FastAPI"),
    ("tasks", 10, "Background Tasks & Concurrency"),
    ("data_persistence", 11, "Data Persistence & Storage"),
    ("ai_ml_practices", 12, "AI & Data-Science Practices"),
    ("edge_cases", 13, "Edge-Case Pitfalls & Gotchas"),
]

# Special modules that contribute to specific sections
SPECIAL_MODULES = {
    "git_branching": (1, "Environment Management & Setup (Git Workflow)"),
    "dry": (4, "Application Design & Structure (DRY Principle)"),
    "solid": (4, "Application Design & Structure (SOLID Principles)"),
}


def get_module_markdown(module_name: str) -> Optional[str]:
    """Attempt to import a module and call its generate_markdown method."""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "generate_markdown"):
            print(f"Generating documentation from {module_name}...")
            return module.generate_markdown()
        else:
            print(f"Warning: {module_name} has no generate_markdown method")
            return None
    except ImportError as e:
        print(f"Could not import {module_name}: {e}")
        return None


def generate_header() -> str:
    """Generate the document header."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    return f"""# Python Development Best Practices ({datetime.now().year} edition)

> **Version:** {today} · Maintainer Team Core-Python · **Status:** LIVING-DOC

---

## Table of Contents

"""


def generate_toc(modules: List[Tuple[str, int, str]]) -> str:
    """Generate a table of contents from module information."""
    toc = ""
    for _, section_num, title in sorted(modules, key=lambda x: x[1]):
        toc += f"{section_num}. [{title}](#{section_num}-{title.lower().replace(' ', '-').replace('&', '').replace('—', '').replace('(', '').replace(')', '')})\n"
    return toc


def generate_full_documentation() -> str:
    """Generate the complete documentation by combining all module outputs."""
    documentation = generate_header()
    
    # Prepare all modules (standard + special)
    all_modules = [(name, num, title) for name, num, title in MODULE_MAP]
    for name, (num, title) in SPECIAL_MODULES.items():
        all_modules.append((name, num, title))
    
    # Generate table of contents
    documentation += generate_toc(all_modules)
    documentation += "\n---\n\n"
    
    # Process each standard module in order
    for module_name, section_num, section_title in sorted(MODULE_MAP, key=lambda x: x[1]):
        documentation += f"<a id=\"{section_num}-{section_title.lower().replace(' ', '-').replace('&', '').replace('—', '').replace('(', '').replace(')', '')}\"></a>\n\n"
        documentation += f"## {section_num}. {section_title}\n\n"
        
        # Get content from main module
        content = get_module_markdown(module_name)
        if content:
            documentation += content
        else:
            documentation += f"*Documentation for {section_title} is under development.*\n\n"
        
        # Add content from special modules that belong to this section
        for special_name, (special_num, _) in SPECIAL_MODULES.items():
            if special_num == section_num:
                special_content = get_module_markdown(special_name)
                if special_content:
                    documentation += f"\n### {special_name.replace('_', ' ').title()} Specific Practices\n\n"
                    documentation += special_content
        
        documentation += "\n---\n\n"
    
    return documentation


def main():
    """Generate and save the full documentation."""
    output_path = Path("docs")
    output_path.mkdir(exist_ok=True)
    
    # Generate the full documentation
    documentation = generate_full_documentation()
    
    # Write to file
    output_file = output_path / "python_best_practices.md"
    with open(output_file, "w") as f:
        f.write(documentation)
    
    print(f"Documentation generated successfully: {output_file}")


if __name__ == "__main__":
    main()