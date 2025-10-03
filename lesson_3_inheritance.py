"""
LESSON 3: INHERITANCE
======================

CONCEPT: Inheritance allows a class to inherit attributes and methods from another
class. It creates a parent-child relationship.

Real-world analogy:
- Vehicles: All vehicles have wheels and can move, but a Car, Motorcycle, and Truck
  each have their own specific features while sharing common vehicle traits.
- Animals: All animals eat and sleep, but a Dog, Cat, and Bird each have unique
  behaviors while sharing animal characteristics.
"""

# PARENT CLASS (also called Base Class or Superclass)
class Employee:
    """Base class representing a general employee"""

    def __init__(self, name, employee_id, salary):
        self.name = name
        self.employee_id = employee_id
        self.salary = salary

    def get_details(self):
        return f"Employee: {self.name} (ID: {self.employee_id})"

    def work(self):
        return f"{self.name} is working..."

    def get_annual_bonus(self):
        return self.salary * 0.05  # Base 5% bonus


# CHILD CLASS 1: Developer inherits from Employee
class Developer(Employee):
    """Specialized employee class for developers"""

    def __init__(self, name, employee_id, salary, programming_languages):
        # Call parent class constructor
        super().__init__(name, employee_id, salary)
        # Add developer-specific attribute
        self.programming_languages = programming_languages

    # Override parent method with specialized behavior
    def work(self):
        return f"{self.name} is coding in {', '.join(self.programming_languages)}..."

    # Add new method specific to developers
    def code_review(self):
        return f"{self.name} is reviewing code..."

    # Override bonus calculation
    def get_annual_bonus(self):
        return self.salary * 0.10  # Developers get 10% bonus


# CHILD CLASS 2: Manager inherits from Employee
class Manager(Employee):
    """Specialized employee class for managers"""

    def __init__(self, name, employee_id, salary, team_size):
        super().__init__(name, employee_id, salary)
        self.team_size = team_size

    def work(self):
        return f"{self.name} is managing a team of {self.team_size} people..."

    def conduct_meeting(self):
        return f"{self.name} is conducting a team meeting..."

    def get_annual_bonus(self):
        # Managers get base 8% + 1% per team member
        return self.salary * (0.08 + 0.01 * self.team_size)


# CHILD CLASS 3: Intern inherits from Employee
class Intern(Employee):
    """Specialized employee class for interns"""

    def __init__(self, name, employee_id, salary, university):
        super().__init__(name, employee_id, salary)
        self.university = university

    def work(self):
        return f"{self.name} (student at {self.university}) is learning and working..."

    def attend_training(self):
        return f"{self.name} is attending a training session..."

    # Interns get smaller bonus
    def get_annual_bonus(self):
        return self.salary * 0.02  # 2% bonus


# Let's see inheritance in action!
print("=" * 70)
print("INHERITANCE IN ACTION")
print("=" * 70)

# Create different types of employees
dev = Developer("Sarah Chen", "D001", 90000, ["Python", "JavaScript", "Go"])
manager = Manager("John Smith", "M001", 110000, 8)
intern = Intern("Alex Johnson", "I001", 40000, "MIT")

# All inherit the get_details method from Employee
print("\nAll employees share inherited methods:")
print(f"  {dev.get_details()}")
print(f"  {manager.get_details()}")
print(f"  {intern.get_details()}")

# But each has specialized work behavior (method overriding)
print("\nEach employee type has specialized behavior:")
print(f"  {dev.work()}")
print(f"  {manager.work()}")
print(f"  {intern.work()}")

# Each class can have its own unique methods
print("\nSpecialized methods unique to each type:")
print(f"  {dev.code_review()}")
print(f"  {manager.conduct_meeting()}")
print(f"  {intern.attend_training()}")

# Method overriding: same method name, different implementation
print("\nMethod overriding - different bonus calculations:")
print(f"  Developer {dev.name}: ${dev.get_annual_bonus():,.2f} bonus")
print(f"  Manager {manager.name}: ${manager.get_annual_bonus():,.2f} bonus")
print(f"  Intern {intern.name}: ${intern.get_annual_bonus():,.2f} bonus")

# Demonstrate isinstance() - checking class relationships
print("\n" + "=" * 70)
print("CHECKING CLASS RELATIONSHIPS")
print("=" * 70)

employees = [dev, manager, intern]

for emp in employees:
    print(f"\n{emp.name}:")
    print(f"  Is an Employee? {isinstance(emp, Employee)}")
    print(f"  Is a Developer? {isinstance(emp, Developer)}")
    print(f"  Is a Manager? {isinstance(emp, Manager)}")

print("\n" + "=" * 70)
print("KEY BENEFITS OF INHERITANCE")
print("=" * 70)
print("""
1. CODE REUSE: Don't repeat common attributes/methods
   (All employees have name, id, salary - defined once in Employee)

2. LOGICAL HIERARCHY: Models real-world relationships
   (Developer IS-A Employee, Manager IS-A Employee)

3. EASY MAINTENANCE: Change parent class, all children benefit
   (Add a method to Employee, all subclasses get it)

4. SPECIALIZATION: Child classes can override parent behavior
   (Each employee type has specialized work() and bonus calculations)

5. POLYMORPHISM: Treat different types uniformly
   (We can treat Developer, Manager, Intern all as Employees)

WHEN TO USE INHERITANCE:
- There's a clear "IS-A" relationship (Developer IS-A Employee)
- Subclasses share common functionality
- You want to specialize or extend base behavior
""")
