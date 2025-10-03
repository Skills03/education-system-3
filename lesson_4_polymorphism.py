"""
LESSON 4: POLYMORPHISM
=======================

CONCEPT: Polymorphism means "many forms." It allows objects of different classes
to be treated as objects of a common parent class, while each maintains its own
specific behavior.

Real-world analogy:
- A "Play" button works on music players, video players, game consoles - same
  interface, different behavior based on what you're playing
- "Start" on a car vs. a computer vs. a blender - same action name, different
  implementations
"""

from abc import ABC, abstractmethod
import math

# Abstract base class defining a common interface
class Shape(ABC):
    """Abstract class - defines what all shapes must do"""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def calculate_area(self):
        """Every shape must implement this method"""
        pass

    @abstractmethod
    def calculate_perimeter(self):
        """Every shape must implement this method"""
        pass

    def describe(self):
        """Shared method all shapes can use"""
        return f"I am a {self.name}"


# Different shapes implement the interface differently
class Circle(Shape):
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius

    def calculate_area(self):
        return math.pi * self.radius ** 2

    def calculate_perimeter(self):
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        super().__init__("Rectangle")
        self.width = width
        self.height = height

    def calculate_area(self):
        return self.width * self.height

    def calculate_perimeter(self):
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, side_a, side_b, side_c):
        super().__init__("Triangle")
        self.side_a = side_a
        self.side_b = side_b
        self.side_c = side_c

    def calculate_area(self):
        # Using Heron's formula
        s = self.calculate_perimeter() / 2
        return math.sqrt(s * (s - self.side_a) * (s - self.side_b) * (s - self.side_c))

    def calculate_perimeter(self):
        return self.side_a + self.side_b + self.side_c


# This is polymorphism in action!
def print_shape_info(shape):
    """
    This function works with ANY shape!
    It doesn't care if it's a Circle, Rectangle, or Triangle.
    This is polymorphism - one interface, many implementations.
    """
    print(f"\n{shape.describe()}")
    print(f"  Area: {shape.calculate_area():.2f}")
    print(f"  Perimeter: {shape.calculate_perimeter():.2f}")


print("=" * 70)
print("POLYMORPHISM IN ACTION")
print("=" * 70)

# Create different shapes
circle = Circle(5)
rectangle = Rectangle(4, 6)
triangle = Triangle(3, 4, 5)

# We can treat all shapes uniformly through the Shape interface
shapes = [circle, rectangle, triangle]

print("\nProcessing different shapes with the SAME function:")
print("-" * 70)
for shape in shapes:
    print_shape_info(shape)  # Same function, different behavior!

# Another polymorphism example: Processing payments
print("\n" + "=" * 70)
print("POLYMORPHISM EXAMPLE 2: PAYMENT PROCESSING")
print("=" * 70)


class PaymentMethod(ABC):
    """Abstract base class for payment methods"""

    @abstractmethod
    def process_payment(self, amount):
        pass

    @abstractmethod
    def validate(self):
        pass


class CreditCard(PaymentMethod):
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv

    def process_payment(self, amount):
        return f"Processing ${amount:.2f} via Credit Card ending in {self.card_number[-4:]}"

    def validate(self):
        return len(self.card_number) == 16 and len(self.cvv) == 3


class PayPal(PaymentMethod):
    def __init__(self, email):
        self.email = email

    def process_payment(self, amount):
        return f"Processing ${amount:.2f} via PayPal account {self.email}"

    def validate(self):
        return "@" in self.email


class Cryptocurrency(PaymentMethod):
    def __init__(self, wallet_address, crypto_type):
        self.wallet_address = wallet_address
        self.crypto_type = crypto_type

    def process_payment(self, amount):
        return f"Processing ${amount:.2f} worth of {self.crypto_type} to {self.wallet_address[:10]}..."

    def validate(self):
        return len(self.wallet_address) > 20


# Polymorphic function that works with ANY payment method
def checkout(payment_method, amount):
    """
    This function doesn't need to know the specific payment type!
    It works with CreditCard, PayPal, Cryptocurrency, or any future payment method.
    """
    if payment_method.validate():
        print(f"  {payment_method.process_payment(amount)}")
        print("  Payment successful!")
    else:
        print("  Payment validation failed!")


print("\nProcessing payments with different methods:")
print("-" * 70)

# Create different payment methods
credit_card = CreditCard("1234567812345678", "123")
paypal = PayPal("user@example.com")
crypto = Cryptocurrency("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin")

payments = [
    (credit_card, 99.99),
    (paypal, 49.99),
    (crypto, 199.99)
]

for payment_method, amount in payments:
    print(f"\nPayment method: {payment_method.__class__.__name__}")
    checkout(payment_method, amount)

print("\n" + "=" * 70)
print("KEY BENEFITS OF POLYMORPHISM")
print("=" * 70)
print("""
1. FLEXIBILITY: Add new shapes/payment methods without changing existing code
   (We can add Square, Pentagon, or BitcoinCash without modifying print_shape_info
    or checkout functions)

2. CODE REUSABILITY: Write functions that work with many types
   (One checkout function handles all payment types)

3. MAINTAINABILITY: Each class manages its own behavior
   (Circle knows how to calculate its area, Rectangle knows its own way)

4. EXTENSIBILITY: Easy to add new implementations
   (Want to add Apple Pay? Just create a new PaymentMethod subclass)

5. CLEAN INTERFACES: Work with abstractions, not concrete implementations
   (Functions depend on Shape or PaymentMethod, not specific types)

TYPES OF POLYMORPHISM:
- Method Overriding: Child class provides specific implementation of parent method
- Duck Typing: "If it walks like a duck and quacks like a duck, it's a duck"
- Interface-based: Objects share common interface (Shape, PaymentMethod)

REAL-WORLD USE CASES:
- Plugin systems (different plugins, same interface)
- Game engines (different game objects, same update/render methods)
- Database drivers (MySQL, PostgreSQL, MongoDB - same query interface)
- UI frameworks (different widgets, same render/event handling)
""")
