"""
Python List Comprehensions - Interactive Tutorial
A powerful and elegant way to create lists in Python!
"""

print("=" * 60)
print("EXAMPLE 1: Basic List Comprehension - Squares of Numbers")
print("=" * 60)

# Traditional approach with a for loop
squares_traditional = []
for num in range(1, 6):
    squares_traditional.append(num ** 2)

print("\nTraditional way (using for loop):")
print(f"squares_traditional = {squares_traditional}")

# List comprehension approach - same result, cleaner code!
squares_comprehension = [num ** 2 for num in range(1, 6)]

print("\nList comprehension way:")
print(f"squares_comprehension = {squares_comprehension}")
print("\nSyntax: [expression for item in iterable]")

print("\n" + "=" * 60)
print("EXAMPLE 2: List Comprehension with Filter - Even Numbers Only")
print("=" * 60)

# Traditional approach with if condition
evens_traditional = []
for num in range(1, 11):
    if num % 2 == 0:
        evens_traditional.append(num)

print("\nTraditional way (using for loop with if):")
print(f"evens_traditional = {evens_traditional}")

# List comprehension with condition
evens_comprehension = [num for num in range(1, 11) if num % 2 == 0]

print("\nList comprehension way:")
print(f"evens_comprehension = {evens_comprehension}")
print("\nSyntax: [expression for item in iterable if condition]")

# Bonus: We can also transform while filtering!
squared_evens = [num ** 2 for num in range(1, 11) if num % 2 == 0]
print(f"\nBonus - Squared even numbers: {squared_evens}")

print("\n" + "=" * 60)
print("EXAMPLE 3: Nested List Comprehension - 2D Matrix")
print("=" * 60)

# Traditional approach for creating a 3x3 matrix
matrix_traditional = []
for row in range(3):
    row_list = []
    for col in range(3):
        row_list.append(row * 3 + col)
    matrix_traditional.append(row_list)

print("\nTraditional way (nested for loops):")
for row in matrix_traditional:
    print(row)

# Nested list comprehension - creates the same matrix!
matrix_comprehension = [[row * 3 + col for col in range(3)] for row in range(3)]

print("\nNested list comprehension way:")
for row in matrix_comprehension:
    print(row)

print("\nSyntax: [[inner_expression for inner_item in inner_iterable] for outer_item in outer_iterable]")

# Let's create a more visual example - a multiplication table!
print("\n" + "-" * 40)
print("Bonus: 5x5 Multiplication Table")
print("-" * 40)

mult_table = [[row * col for col in range(1, 6)] for row in range(1, 6)]

for i, row in enumerate(mult_table, 1):
    print(f"{i}: {row}")

print("\n" + "=" * 60)
print("KEY TAKEAWAY")
print("=" * 60)
print("List comprehensions are:")
print("  ✓ More concise and readable")
print("  ✓ Generally faster than loops")
print("  ✓ Pythonic and elegant")
print("  ✓ Perfect for transforming and filtering data")
print("=" * 60)
