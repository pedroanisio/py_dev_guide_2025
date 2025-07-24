class SOLID:
    """
    SOLID Principles of Object-Oriented Design
    
    A simple class representing the five SOLID design principles.
    """
    
    def __init__(self):
        self.name = "SOLID"
        self.core_idea = "Five principles that promote maintainable, extensible OOP designs."
        
        # The five SOLID principles
        self.principles = {
            "S": {
                "name": "Single-Responsibility",
                "description": "Each module/class handles one concern.",
                "example": """
# Bad: Class with multiple responsibilities
class User:
    def __init__(self, name):
        self.name = name
    
    def save_to_database(self):
        # Database logic here
        print(f"Saving {self.name} to database")
    
    def generate_report(self):
        # Report generation logic here
        print(f"Generating report for {self.name}")
""",
                "improved": """
# Good: Separate classes for different responsibilities
class User:
    def __init__(self, name):
        self.name = name

class UserRepository:
    def save(self, user):
        # Database logic here
        print(f"Saving {user.name} to database")

class ReportGenerator:
    def generate_for_user(self, user):
        # Report generation logic here
        print(f"Generating report for {user.name}")
"""
            },
            "O": {
                "name": "Open-Closed",
                "description": "Classes are open for extension, closed for modification.",
                "example": """
# Bad: Requires modification to add new shapes
class AreaCalculator:
    def calculate_area(self, shape):
        if isinstance(shape, Rectangle):
            return shape.width * shape.height
        elif isinstance(shape, Circle):
            return 3.14 * shape.radius ** 2
        # Need to modify this class for each new shape
""",
                "improved": """
# Good: Open for extension through polymorphism
class Shape:
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class AreaCalculator:
    def calculate_area(self, shape):
        return shape.area()  # Polymorphic call
"""
            },
            "L": {
                "name": "Liskov Substitution",
                "description": "Subclasses should be drop-in replacements for their base types.",
                "example": """
# Bad: Square violates Rectangle's behavior
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def set_width(self, width):
        self.width = width
    
    def set_height(self, height):
        self.height = height

class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)
    
    def set_width(self, width):
        self.width = width
        self.height = width  # Changing behavior!
    
    def set_height(self, height):
        self.height = height
        self.width = height  # Changing behavior!
""",
                "improved": """
# Good: Shape hierarchy respects Liskov principle
class Shape:
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Square(Shape):  # Not a Rectangle subclass
    def __init__(self, side):
        self.side = side
    
    def area(self):
        return self.side * self.side
"""
            },
            "I": {
                "name": "Interface Segregation",
                "description": "Prefer small, focused interfaces over monolithic ones.",
                "example": """
# Bad: Monolithic interface forces implementations of unneeded methods
class Worker:
    def work(self):
        pass
    
    def eat(self):
        pass
    
    def sleep(self):
        pass

class Robot(Worker):
    def work(self):
        print("Robot working")
    
    def eat(self):
        raise NotImplementedError("Robots don't eat")  # Forced to implement
    
    def sleep(self):
        raise NotImplementedError("Robots don't sleep")  # Forced to implement
""",
                "improved": """
# Good: Segregated interfaces
class Workable:
    def work(self):
        pass

class Eatable:
    def eat(self):
        pass

class Sleepable:
    def sleep(self):
        pass

class Human(Workable, Eatable, Sleepable):
    def work(self):
        print("Human working")
    
    def eat(self):
        print("Human eating")
    
    def sleep(self):
        print("Human sleeping")

class Robot(Workable):  # Only implements what it needs
    def work(self):
        print("Robot working")
"""
            },
            "D": {
                "name": "Dependency Inversion",
                "description": "Depend on abstractions, not concrete implementations.",
                "example": """
# Bad: High-level module depends on low-level module
class MySQLDatabase:
    def save(self, data):
        print(f"Saving {data} to MySQL")

class UserService:
    def __init__(self):
        self.database = MySQLDatabase()  # Direct dependency
    
    def save_user(self, user):
        self.database.save(user)
""",
                "improved": """
# Good: Dependency injected through abstraction
class Database:  # Abstract interface
    def save(self, data):
        pass

class MySQLDatabase(Database):
    def save(self, data):
        print(f"Saving {data} to MySQL")

class PostgreSQLDatabase(Database):
    def save(self, data):
        print(f"Saving {data} to PostgreSQL")

class UserService:
    def __init__(self, database):  # Dependency injection
        self.database = database
    
    def save_user(self, user):
        self.database.save(user)

# Usage
db = MySQLDatabase()  # Or PostgreSQLDatabase()
service = UserService(db)
"""
            }
        }
    
    def get_principle(self, letter):
        """Get details for a specific SOLID principle by its letter"""
        if letter.upper() in self.principles:
            return self.principles[letter.upper()]
        return None
    
    def __str__(self):
        """String representation of SOLID principles"""
        return f"SOLID Principles: {self.core_idea}"


# Example usage
if __name__ == "__main__":
    solid = SOLID()
    
    print(f"🏗️ {solid}")
    print("\n🧱 The Five SOLID Principles:")
    
    for letter, principle in solid.principles.items():
        print(f"\n🔹 {letter}: {principle['name']}")
        print(f"   {principle['description']}")
        
        # Print an example for one principle to demonstrate
        if letter == 'S':  # Single Responsibility example
            print("\n📋 Example:")
            print("❌ Violating Single Responsibility:")
            print(principle['example'])
            print("✅ Following Single Responsibility:")
            print(principle['improved'])
    
    # Ask for user input to explore more principles
    print("\n💡 Run this program and enter a letter (S, O, L, I, D) to see examples for that principle.")
    print("   For example, type 'O' to see Open-Closed principle examples.")
    
    """
    # Uncomment this code to make the script interactive
    letter = input("\nEnter a SOLID principle letter to see examples: ").upper()
    principle = solid.get_principle(letter)
    if principle:
        print(f"\n🔹 {letter}: {principle['name']}")
        print(f"   {principle['description']}")
        print("\n📋 Example:")
        print(f"❌ Violating {principle['name']}:")
        print(principle['example'])
        print(f"✅ Following {principle['name']}:")
        print(principle['improved'])
    else:
        print(f"Principle '{letter}' not found. Please enter S, O, L, I, or D.")
    """