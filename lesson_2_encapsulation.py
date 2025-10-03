"""
LESSON 2: ENCAPSULATION
========================

CONCEPT: Encapsulation means bundling data and methods together, and controlling
access to them. It's like putting things in a capsule with a controlled interface.

Real-world analogy:
- A car: You don't need to know how the engine works internally. You just use the
  steering wheel, pedals, and gear shift (the public interface).
- An ATM: You can't directly access the cash inside. You interact through the
  interface (keypad, card reader).
"""

class BankAccount:
    """Demonstrates encapsulation with private attributes and controlled access"""

    def __init__(self, account_holder, initial_balance=0):
        self.account_holder = account_holder  # Public attribute
        self.__balance = initial_balance      # Private attribute (note the __)
        self.__transaction_history = []       # Private attribute

    # Public method - anyone can use this
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            self.__transaction_history.append(f"Deposited: ${amount}")
            return f"Successfully deposited ${amount}. New balance: ${self.__balance}"
        else:
            return "Invalid deposit amount. Must be positive."

    # Public method with validation
    def withdraw(self, amount):
        if amount <= 0:
            return "Invalid withdrawal amount. Must be positive."
        elif amount > self.__balance:
            return f"Insufficient funds. Current balance: ${self.__balance}"
        else:
            self.__balance -= amount
            self.__transaction_history.append(f"Withdrew: ${amount}")
            return f"Successfully withdrew ${amount}. New balance: ${self.__balance}"

    # Controlled read access to private data
    def get_balance(self):
        """Getter method - controlled way to read private data"""
        return self.__balance

    # Controlled access to transaction history
    def get_transaction_history(self):
        """Returns a copy of transaction history"""
        return self.__transaction_history.copy()

    def get_account_info(self):
        return f"Account holder: {self.account_holder}, Balance: ${self.__balance}"


# Let's see encapsulation in action!
print("=" * 60)
print("ENCAPSULATION IN ACTION")
print("=" * 60)

# Create a bank account
my_account = BankAccount("Alice Smith", 1000)

print(f"\n{my_account.get_account_info()}")

# Using public methods (the controlled interface)
print(f"\n{my_account.deposit(500)}")
print(f"{my_account.withdraw(200)}")
print(f"{my_account.withdraw(2000)}")  # This should fail - not enough money!

# We can access balance through the getter method
print(f"\nCurrent balance (via getter): ${my_account.get_balance()}")

# Show transaction history
print("\nTransaction History:")
for transaction in my_account.get_transaction_history():
    print(f"  - {transaction}")

# Demonstrate why encapsulation matters
print("\n" + "=" * 60)
print("WHY ENCAPSULATION MATTERS")
print("=" * 60)

# We can access public attributes directly
print(f"\nPublic attribute (OK): {my_account.account_holder}")

# Private attributes are protected (Python uses name mangling)
print("\nTrying to access private attribute directly:")
try:
    # This won't work as expected - it's "protected"
    print(f"  my_account.__balance = {my_account.__balance}")
except AttributeError as e:
    print(f"  Error: {e}")
    print("  Private attributes can't be accessed directly!")

# Python's name mangling (for demonstration)
print("\nPython technically allows access via name mangling, but it's discouraged:")
print(f"  my_account._BankAccount__balance = {my_account._BankAccount__balance}")
print("  (But you should NEVER do this! Use the getter instead.)")

print("\n" + "=" * 60)
print("KEY BENEFITS OF ENCAPSULATION")
print("=" * 60)
print("""
1. DATA PROTECTION: Can't accidentally set balance to negative
2. VALIDATION: All changes go through methods that check validity
3. CONTROLLED ACCESS: Only allowed operations are exposed
4. FLEXIBILITY: Can change internal implementation without breaking code
5. SECURITY: Sensitive data is protected from direct manipulation

Example: The BankAccount class ensures you can't:
  - Set a negative balance directly
  - Withdraw more than you have
  - Corrupt the transaction history
  - Skip validation rules
""")
