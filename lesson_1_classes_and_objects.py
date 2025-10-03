"""
LESSON 1: CLASSES AND OBJECTS
==============================

CONCEPT: Think of a class as a blueprint, and objects as actual things built from that blueprint.

Real-world analogy:
- A blueprint for a house (CLASS) vs. actual houses built from it (OBJECTS)
- A cookie cutter (CLASS) vs. actual cookies (OBJECTS)
- A car design (CLASS) vs. actual cars on the road (OBJECTS)
"""

# Let's create our first class - a Dog class
class Dog:
    """A simple class representing a dog"""

    # The __init__ method is called when we create a new dog
    # It's like the birth certificate - it defines what information every dog needs
    def __init__(self, name, age, breed):
        self.name = name      # Attribute: the dog's name
        self.age = age        # Attribute: the dog's age
        self.breed = breed    # Attribute: the dog's breed

    # Methods are actions/behaviors that our dog can perform
    def bark(self):
        return f"{self.name} says: Woof! Woof!"

    def birthday(self):
        self.age += 1
        return f"Happy birthday {self.name}! You are now {self.age} years old!"

    def describe(self):
        return f"{self.name} is a {self.age}-year-old {self.breed}"


# Now let's CREATE OBJECTS (actual dogs) from our Dog class
print("=" * 60)
print("CREATING OBJECTS FROM THE DOG CLASS")
print("=" * 60)

# Create three different dog objects
buddy = Dog("Buddy", 3, "Golden Retriever")
max_dog = Dog("Max", 5, "German Shepherd")
bella = Dog("Bella", 2, "Poodle")

# Each object has its own unique data
print(f"\n1. {buddy.describe()}")
print(f"   {buddy.bark()}")

print(f"\n2. {max_dog.describe()}")
print(f"   {max_dog.bark()}")

print(f"\n3. {bella.describe()}")
print(f"   {bella.bark()}")

# Objects can change state (their data can be modified)
print("\n" + "=" * 60)
print("OBJECTS CAN CHANGE STATE")
print("=" * 60)
print(f"\nBefore birthday: {buddy.describe()}")
print(buddy.birthday())
print(f"After birthday: {buddy.describe()}")

# Key takeaway demonstration
print("\n" + "=" * 60)
print("KEY TAKEAWAY")
print("=" * 60)
print("""
CLASS = Blueprint/Template (Dog class defines what all dogs have)
OBJECT = Specific instance (buddy, max_dog, bella are actual dogs)

Each object:
  - Has its own data (buddy's name is different from max's name)
  - Shares the same behaviors (all dogs can bark)
  - Can change its state independently (buddy's birthday doesn't affect max)
""")
