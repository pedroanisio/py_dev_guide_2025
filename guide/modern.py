class ModernPythonSyntax:
    """
    Modern Python Syntax & Idioms
    
    A class representing modern Python syntax features and idioms
    that should be used in Python 3.12+ codebases.
    """
    
    def __init__(self):
        self.name = "Modern Python Syntax & Idioms"
        self.min_python_version = "3.12+"
        self.preferred_version = "3.13"
        
        # Organize features by category
        self.string_formatting = {
            "name": "F-strings",
            "description": "Use f-strings for string formatting",
            "example": 'name = "World"\ngreeting = f"Hello, {name}!"',
            "pep": None
        }
        
        self.type_system = {
            "type_hints": {
                "name": "Type Hints",
                "description": "Improves clarity; run tools like mypy for static checks",
                "example": "def greet(name: str) -> str:\n    return f'Hello, {name}!'",
                "pep": "484"
            },
            "data_classes": {
                "name": "Data Classes",
                "description": "Reduce boilerplate for data containers via @dataclass",
                "example": """
@dataclass
class User:
    name: str
    email: str
    age: int = 0
""",
                "pep": "557"
            },
            "type_parameter_syntax": {
                "name": "New Type Parameter Syntax",
                "description": "For Python 3.12+, use the new syntax for defining generic functions and classes",
                "example": """
def first[T](items: list[T]) -> T:
    return items[0]
    
class Box[T]:
    def __init__(self, value: T):
        self.value = T
        
type IntOrStr = int | str
""",
                "pep": "695"
            }
        }
        
        self.file_system = {
            "name": "Pathlib",
            "description": "For filesystem paths; prefer os.scandir() over os.listdir() when metadata is needed",
            "example": """
from pathlib import Path

# Create paths
config_path = Path("config/settings.toml")
parent_dir = config_path.parent

# Check properties
if config_path.exists() and config_path.is_file():
    content = config_path.read_text()
""",
            "pep": None
        }
        
        self.resource_management = {
            "name": "Context Managers",
            "description": "Use with for resource management",
            "example": """
with open('file.txt', 'r') as f:
    content = f.read()
    
# File is automatically closed after the block
""",
            "pep": None
        }
        
        self.debugging = {
            "name": "breakpoint()",
            "description": "Python 3.7+ modern debugger hook",
            "example": """
def complex_function(data):
    # When something goes wrong
    if unexpected_condition:
        breakpoint()  # Drops into the debugger
    # Continue processing
""",
            "pep": None
        }
        
        self.syntax_features = {
            "enumerate": {
                "name": "enumerate()",
                "description": "Get index with item in loops",
                "example": """
fruits = ['apple', 'banana', 'cherry']
for i, fruit in enumerate(fruits):
    print(f"{i+1}. {fruit}")
"""
            },
            "comprehensions": {
                "name": "Comprehensions",
                "description": "Concise creation of lists, dicts, and sets",
                "example": """
# List comprehension
squares = [x**2 for x in range(10)]

# Dictionary comprehension
name_to_age = {person.name: person.age for person in people}

# Set comprehension
unique_letters = {char.lower() for char in text}
"""
            },
            "walrus": {
                "name": "Walrus Operator (:=)",
                "description": "Assignment expressions for cleaner code",
                "example": """
# Without walrus operator
chunk = stream.read(1024)
if chunk:
    process(chunk)
    
# With walrus operator
if (chunk := stream.read(1024)):
    process(chunk)
"""
            }
        }
        
        self.collections = {
            "name": "collections.abc",
            "description": "When defining custom collections",
            "example": """
from collections.abc import Sequence

class ReadOnlyList(Sequence):
    def __init__(self, data):
        self._data = list(data)
        
    def __getitem__(self, index):
        return self._data[index]
        
    def __len__(self):
        return len(self._data)
"""
        }
        
        self.datetime = {
            "name": "Timezone-aware datetime",
            "description": "Use for unambiguous timestamps",
            "example": """
from datetime import datetime, timezone

# Create timezone-aware datetime
now = datetime.now(timezone.utc)

# Convert to a specific timezone
import zoneinfo
local_time = now.astimezone(zoneinfo.ZoneInfo('America/New_York'))
"""
        }
        
        # Referenced PEPs
        self.referenced_peps = {
            "8": "Style Guide for Python Code",
            "20": "The Zen of Python",
            "257": "Docstring Conventions",
            "484": "Type Hints",
            "557": "Data Classes",
            "695": "Type Parameter Syntax",
            "696": "Type Defaults for Type Parameters (Python 3.13+)",
            "719": "Python 3.13 Release Schedule",
            "3129": "Class Decorators"
        }
    
    def get_peps(self):
        """Return all referenced PEPs with descriptions"""
        return self.referenced_peps
    
    def get_examples(self):
        """Return examples of all modern syntax features"""
        examples = {}
        
        # String formatting
        examples["f_strings"] = self.string_formatting["example"]
        
        # Type system
        for key, value in self.type_system.items():
            examples[key] = value["example"]
        
        # File system
        examples["pathlib"] = self.file_system["example"]
        
        # Resource management
        examples["context_managers"] = self.resource_management["example"]
        
        # Debugging
        examples["breakpoint"] = self.debugging["example"]
        
        # Syntax features
        for key, value in self.syntax_features.items():
            examples[key] = value["example"]
        
        # Collections
        examples["collections_abc"] = self.collections["example"]
        
        # Datetime
        examples["timezone_datetime"] = self.datetime["example"]
        
        return examples
    
    def __str__(self):
        """String representation of Modern Python Syntax"""
        return f"{self.name} (Python {self.min_python_version}, preferably {self.preferred_version})"


# Example usage
if __name__ == "__main__":
    syntax = ModernPythonSyntax()
    
    print(f"🐍 {syntax}")
    
    print("\n🔤 String Formatting:")
    print(f"- {syntax.string_formatting['name']}: {syntax.string_formatting['description']}")
    print("```python")
    print(syntax.string_formatting['example'])
    print("```")
    
    print("\n📝 Type System:")
    for key, value in syntax.type_system.items():
        print(f"- {value['name']}: {value['description']}")
        if value['pep']:
            print(f"  (PEP {value['pep']})")
        print("```python")
        print(value['example'])
        print("```")
    
    print("\n📂 File System:")
    print(f"- {syntax.file_system['name']}: {syntax.file_system['description']}")
    print("```python")
    print(syntax.file_system['example'])
    print("```")
    
    print("\n🔄 Resource Management:")
    print(f"- {syntax.resource_management['name']}: {syntax.resource_management['description']}")
    print("```python")
    print(syntax.resource_management['example'])
    print("```")
    
    print("\n🐞 Debugging:")
    print(f"- {syntax.debugging['name']}: {syntax.debugging['description']}")
    print("```python")
    print(syntax.debugging['example'])
    print("```")
    
    print("\n⚡ Syntax Features:")
    for key, value in syntax.syntax_features.items():
        print(f"- {value['name']}: {value['description']}")
        print("```python")
        print(value['example'])
        print("```")
    
    print("\n📚 Collections:")
    print(f"- {syntax.collections['name']}: {syntax.collections['description']}")
    print("```python")
    print(syntax.collections['example'])
    print("```")
    
    print("\n🕒 Date and Time:")
    print(f"- {syntax.datetime['name']}: {syntax.datetime['description']}")
    print("```python")
    print(syntax.datetime['example'])
    print("```")
    
    print("\n📑 Referenced PEPs:")
    for pep, description in syntax.get_peps().items():
        print(f"- PEP {pep}: {description}")