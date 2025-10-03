"""
LIST COMPREHENSIONS vs FOR LOOPS: A Practical Guide
====================================================

This guide shows you WHEN to use each approach with real-world examples.
"""

import time


# =============================================================================
# SECTION 1: When List Comprehensions are BETTER
# =============================================================================

print("=" * 80)
print("SECTION 1: When List Comprehensions SHINE")
print("=" * 80)

# Example 1A: Simple Transformation
print("\n1A. SIMPLE TRANSFORMATION: Converting temperatures")
print("-" * 60)

celsius_temps = [0, 10, 20, 30, 40]

# Using list comprehension (BETTER for this case)
fahrenheit_lc = [(temp * 9/5) + 32 for temp in celsius_temps]

# Using for loop
fahrenheit_loop = []
for temp in celsius_temps:
    fahrenheit_loop.append((temp * 9/5) + 32)

print(f"Celsius: {celsius_temps}")
print(f"Fahrenheit (list comp): {fahrenheit_lc}")
print(f"Fahrenheit (for loop):  {fahrenheit_loop}")
print("\nWINNER: List comprehension - cleaner, more Pythonic for simple transformations")


# Example 1B: Filtering Data
print("\n\n1B. FILTERING: Finding valid user ages")
print("-" * 60)

user_ages = [15, 22, 17, 35, 12, 48, 19, 8, 25]

# Using list comprehension (BETTER for this case)
adult_ages_lc = [age for age in user_ages if age >= 18]

# Using for loop
adult_ages_loop = []
for age in user_ages:
    if age >= 18:
        adult_ages_loop.append(age)

print(f"All ages: {user_ages}")
print(f"Adults (list comp): {adult_ages_lc}")
print(f"Adults (for loop):  {adult_ages_loop}")
print("\nWINNER: List comprehension - more concise for simple filtering")


# Example 1C: Transform + Filter Combined
print("\n\n1C. TRANSFORM + FILTER: Processing product prices")
print("-" * 60)

prices = [10.50, 25.00, 5.99, 45.00, 15.75, 3.50]

# Using list comprehension (BETTER for this case)
discounted_expensive_lc = [price * 0.9 for price in prices if price > 10]

# Using for loop
discounted_expensive_loop = []
for price in prices:
    if price > 10:
        discounted_expensive_loop.append(price * 0.9)

print(f"Original prices: {prices}")
print(f"10% off items over $10 (list comp): {discounted_expensive_lc}")
print(f"10% off items over $10 (for loop):  {discounted_expensive_loop}")
print("\nWINNER: List comprehension - combines filter + transform elegantly")


# Example 1D: Performance for Simple Operations
print("\n\n1D. PERFORMANCE: Processing large datasets")
print("-" * 60)

numbers = list(range(100000))

# List comprehension timing
start = time.perf_counter()
squares_lc = [n ** 2 for n in numbers]
lc_time = time.perf_counter() - start

# For loop timing
start = time.perf_counter()
squares_loop = []
for n in numbers:
    squares_loop.append(n ** 2)
loop_time = time.perf_counter() - start

print(f"List comprehension: {lc_time:.4f} seconds")
print(f"For loop:          {loop_time:.4f} seconds")
print(f"Speed difference:  {((loop_time - lc_time) / loop_time * 100):.1f}% faster with list comp")
print("\nWINNER: List comprehension - slightly faster due to optimization")


# =============================================================================
# SECTION 2: When For Loops are BETTER
# =============================================================================

print("\n\n" + "=" * 80)
print("SECTION 2: When For Loops are BETTER")
print("=" * 80)

# Example 2A: Complex Logic with Multiple Steps
print("\n2A. COMPLEX LOGIC: Processing user registrations")
print("-" * 60)

users = [
    {"name": "Alice", "email": "alice@test.com", "age": 25},
    {"name": "Bob", "email": "invalid-email", "age": 17},
    {"name": "Charlie", "email": "charlie@test.com", "age": 30},
    {"name": "Diana", "email": "diana@test.com", "age": 16},
]

# Using for loop (BETTER for this case)
print("Processing with FOR LOOP:")
validated_users_loop = []
for user in users:
    # Multiple validation steps
    if user["age"] < 18:
        print(f"  Rejected {user['name']}: Too young")
        continue
    if "@" not in user["email"]:
        print(f"  Rejected {user['name']}: Invalid email")
        continue
    # Transform the data
    validated_user = {
        "username": user["name"].lower(),
        "email": user["email"],
        "status": "active"
    }
    validated_users_loop.append(validated_user)
    print(f"  Accepted {user['name']}")

# List comprehension version (harder to read!)
print("\nSame logic with LIST COMPREHENSION (messy!):")
validated_users_lc = [
    {"username": u["name"].lower(), "email": u["email"], "status": "active"}
    for u in users
    if u["age"] >= 18 and "@" in u["email"]
]

print(f"\nResults: {validated_users_loop}")
print("\nWINNER: For loop - better for complex logic with multiple conditions and debugging")


# Example 2B: Side Effects (printing, writing files, API calls)
print("\n\n2B. SIDE EFFECTS: Sending notification emails")
print("-" * 60)

orders = [
    {"id": 101, "customer": "alice@test.com", "total": 50.00},
    {"id": 102, "customer": "bob@test.com", "total": 125.00},
    {"id": 103, "customer": "charlie@test.com", "total": 75.00},
]

# Using for loop (BETTER for this case)
print("Sending emails with FOR LOOP:")
for order in orders:
    # Side effect: simulating email send
    print(f"  Sending email to {order['customer']}: Order #{order['id']} - ${order['total']}")
    # In real code, you'd call: send_email(order['customer'], order)

# List comprehension (WRONG approach - don't do this!)
print("\nDON'T DO THIS with list comprehension:")
emails_sent = [print(f"  Email to {o['customer']}") for o in orders]
print(f"Created useless list: {emails_sent}")

print("\nWINNER: For loop - use for side effects, not for building lists")


# Example 2C: Early Exit / Break Conditions
print("\n\n2C. EARLY EXIT: Finding first match in large dataset")
print("-" * 60)

products = [
    {"id": 1, "name": "Laptop", "price": 999},
    {"id": 2, "name": "Mouse", "price": 25},
    {"id": 3, "name": "Keyboard", "price": 75},
    {"id": 4, "name": "Monitor", "price": 350},
    {"id": 5, "name": "Desk", "price": 450},
]

# Using for loop with break (BETTER)
print("Finding first expensive item with FOR LOOP:")
target_product = None
for product in products:
    print(f"  Checking: {product['name']}")
    if product['price'] > 500:
        target_product = product
        print(f"  Found it! Stopping early.")
        break

print(f"Result: {target_product}")

# List comprehension (processes ALL items even though we only need one)
print("\nWith list comprehension (processes everything):")
expensive_products = [p for p in products if p['price'] > 500]
first_expensive = expensive_products[0] if expensive_products else None
print(f"Result: {first_expensive} (but checked all items unnecessarily)")

print("\nWINNER: For loop - can exit early, saving processing time")


# Example 2D: Accumulating State / Running Calculations
print("\n\n2D. STATEFUL OPERATIONS: Calculating running balance")
print("-" * 60)

transactions = [
    {"type": "deposit", "amount": 100},
    {"type": "withdrawal", "amount": 30},
    {"type": "deposit", "amount": 50},
    {"type": "withdrawal", "amount": 20},
    {"type": "deposit", "amount": 75},
]

# Using for loop (BETTER for this case)
print("Calculating running balance with FOR LOOP:")
balance = 0
balance_history = []
for trans in transactions:
    if trans["type"] == "deposit":
        balance += trans["amount"]
    else:
        balance -= trans["amount"]
    balance_history.append(balance)
    print(f"  {trans['type'].capitalize():12} ${trans['amount']:>3} -> Balance: ${balance}")

print(f"\nBalance history: {balance_history}")
print("\nWINNER: For loop - maintains state across iterations")


# =============================================================================
# SECTION 3: Side-by-Side Comparisons
# =============================================================================

print("\n\n" + "=" * 80)
print("SECTION 3: Side-by-Side Comparisons - Same Task, Both Styles")
print("=" * 80)

# Example 3A: When Both Work, But One is Clearer
print("\n3A. EXTRACTING DATA: Getting all email addresses")
print("-" * 60)

contacts = [
    {"name": "Alice", "email": "alice@company.com"},
    {"name": "Bob", "email": "bob@company.com"},
    {"name": "Charlie", "email": "charlie@company.com"},
]

# List comprehension (BETTER)
emails_lc = [contact["email"] for contact in contacts]

# For loop
emails_loop = []
for contact in contacts:
    emails_loop.append(contact["email"])

print(f"Contacts: {contacts}")
print(f"\nEmails (list comp): {emails_lc}")
print(f"Emails (for loop):  {emails_loop}")
print("\nRECOMMENDATION: Use list comprehension - simpler extraction")


# Example 3B: Nested Loops - When Complexity Matters
print("\n\n3B. NESTED OPERATIONS: Creating coordinate pairs")
print("-" * 60)

x_coords = [1, 2, 3]
y_coords = [10, 20]

# List comprehension (acceptable but getting complex)
pairs_lc = [(x, y) for x in x_coords for y in y_coords]

# For loop (more explicit)
pairs_loop = []
for x in x_coords:
    for y in y_coords:
        pairs_loop.append((x, y))

print(f"X coordinates: {x_coords}")
print(f"Y coordinates: {y_coords}")
print(f"\nPairs (list comp): {pairs_lc}")
print(f"Pairs (for loop):  {pairs_loop}")
print("\nRECOMMENDATION: List comp OK here, but for loop is clearer for beginners")


# Example 3C: When List Comprehension Becomes Too Complex
print("\n\n3C. TOO COMPLEX: Flattening nested data with conditions")
print("-" * 60)

departments = [
    {"name": "Engineering", "employees": [
        {"name": "Alice", "salary": 90000, "active": True},
        {"name": "Bob", "salary": 85000, "active": False},
    ]},
    {"name": "Sales", "employees": [
        {"name": "Charlie", "salary": 70000, "active": True},
        {"name": "Diana", "salary": 75000, "active": True},
    ]},
]

# List comprehension (possible but hard to read)
active_names_lc = [
    emp["name"]
    for dept in departments
    for emp in dept["employees"]
    if emp["active"] and emp["salary"] > 70000
]

# For loop (BETTER - easier to understand)
active_names_loop = []
for dept in departments:
    for emp in dept["employees"]:
        if emp["active"] and emp["salary"] > 70000:
            active_names_loop.append(emp["name"])

print(f"Active high earners (list comp): {active_names_lc}")
print(f"Active high earners (for loop):  {active_names_loop}")
print("\nRECOMMENDATION: Use for loop - nested list comp is hard to read")


# =============================================================================
# SECTION 4: Decision Guide
# =============================================================================

print("\n\n" + "=" * 80)
print("DECISION GUIDE: When to Use Each Approach")
print("=" * 80)

decision_guide = """
USE LIST COMPREHENSION when:
  ✓ Simple transformation: [x * 2 for x in numbers]
  ✓ Simple filtering: [x for x in items if x > 0]
  ✓ Extracting one field: [user['email'] for user in users]
  ✓ Transform + filter: [x.upper() for x in words if len(x) > 3]
  ✓ Creating new list is the PRIMARY goal
  ✓ Logic fits on ONE readable line (maybe two)

USE FOR LOOP when:
  ✓ Complex logic with multiple conditions
  ✓ Need to perform side effects (print, write files, API calls)
  ✓ Need to break/continue based on conditions
  ✓ Accumulating state across iterations
  ✓ Multiple operations per item
  ✓ Debugging complex logic (easier to add print statements)
  ✓ Nested loops that become hard to read
  ✓ You're modifying an existing list/dict instead of creating new one

READABILITY TEST:
  If your list comprehension spans multiple lines or needs a comment
  to explain what it does, use a for loop instead!
"""

print(decision_guide)


# =============================================================================
# SECTION 5: Real-World Scenarios
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 5: Real-World Scenarios")
print("=" * 80)

# Scenario 1: Data cleaning for API response
print("\n5A. REAL-WORLD: Cleaning API response data")
print("-" * 60)

api_response = [
    {"id": 1, "name": "  Alice  ", "score": "95"},
    {"id": 2, "name": "Bob", "score": "invalid"},
    {"id": 3, "name": "  Charlie  ", "score": "88"},
    {"id": 4, "name": None, "score": "72"},
]

# For loop (BETTER - handles errors, logs issues)
cleaned_data = []
for item in api_response:
    # Skip invalid entries
    if not item.get("name"):
        print(f"  Warning: Skipping item {item['id']} - missing name")
        continue

    # Try to parse score
    try:
        score = int(item["score"])
    except ValueError:
        print(f"  Warning: Skipping {item['name']} - invalid score")
        continue

    # Clean and store
    cleaned_data.append({
        "id": item["id"],
        "name": item["name"].strip(),
        "score": score
    })

print(f"\nCleaned data: {cleaned_data}")
print("CHOICE: For loop - better error handling and logging")


# Scenario 2: Simple data transformation for display
print("\n\n5B. REAL-WORLD: Formatting prices for display")
print("-" * 60)

raw_prices = [29.99, 15.5, 100, 7.95, 45.0]

# List comprehension (BETTER - simple transformation)
formatted_prices = [f"${price:.2f}" for price in raw_prices]

print(f"Raw: {raw_prices}")
print(f"Formatted: {formatted_prices}")
print("CHOICE: List comprehension - simple, clean transformation")


print("\n" + "=" * 80)
print("END OF GUIDE")
print("=" * 80)
