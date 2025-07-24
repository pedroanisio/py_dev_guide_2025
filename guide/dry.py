class DRY:
    """
    Don't Repeat Yourself (DRY) Principle
    
    A simple class representing the DRY software development principle.
    """
    
    def __init__(self):
        self.name = "DRY"
        self.full_name = "Don't Repeat Yourself"
        self.core_idea = "Every piece of knowledge must have a single, unambiguous representation within the codebase."
        
        # Guidelines for implementing DRY
        self.practical_enforcement = [
            "Centralize shared logic in functions or classes",
            "Extract common constants/config values",
            "Use parametrized tests to avoid duplicate test logic",
            "Document conventions in docs/ to prevent ad-hoc re-implementation"
        ]
        
        # Benefits of following DRY
        self.benefits = [
            "Reduced code maintenance overhead",
            "Fewer bugs due to inconsistent updates",
            "Easier refactoring and code evolution",
            "Better reusability of components"
        ]
    
    def get_examples(self):
        """Return examples of non-DRY and DRY code"""
        examples = {
            "non_dry": """
# Non-DRY code with duplication
def process_users():
    # Database connection repeated in multiple functions
    conn = connect_to_database("localhost", "mydb", "user", "pass")
    # Process users...
    conn.close()

def process_orders():
    # Same database connection logic repeated
    conn = connect_to_database("localhost", "mydb", "user", "pass")
    # Process orders...
    conn.close()
""",
            "dry": """
# DRY code with centralized logic
def get_database_connection():
    return connect_to_database("localhost", "mydb", "user", "pass")

def process_users():
    conn = get_database_connection()
    # Process users...
    conn.close()

def process_orders():
    conn = get_database_connection()
    # Process orders...
    conn.close()
"""
        }
        return examples
    
    def __str__(self):
        """String representation of the DRY principle"""
        return f"{self.full_name} ({self.name}): {self.core_idea}"


# Example usage
if __name__ == "__main__":
    dry = DRY()
    
    print(f"💡 Principle: {dry}")
    print("\n👉 Practical Enforcement:")
    for guideline in dry.practical_enforcement:
        print(f"- {guideline}")
    
    print("\n✨ Benefits:")
    for benefit in dry.benefits:
        print(f"- {benefit}")
    
    print("\n💻 Code Examples:")
    examples = dry.get_examples()
    print("❌ Non-DRY Code:")
    print(examples["non_dry"])
    print("✅ DRY Code:")
    print(examples["dry"])