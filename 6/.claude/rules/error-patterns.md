# Error Patterns Reference

Common student errors and how to address them.

## Detecting Student's Errors

```bash
python -c "from core.education_tools import tool_get_student_state; s=tool_get_student_state(); print(s['global_error_patterns'])"
```

## Error Types & Solutions

### off_by_one
**What it looks like:**
- `range(n)` when they need `range(n+1)`
- Loop stops one iteration early/late
- "Sum 1 to 5" gives 10 instead of 15

**How to address:**
- Visual: Trace through showing exactly which values are processed
- Question: "What values does range(5) give? Does it include 5?"
- Problem design: Use "INCLUSIVE" explicitly in problem statement

**Target with problems like:**
"Sum all numbers from 1 to n INCLUSIVE"

---

### forgotten_return
**What it looks like:**
- Function computes correct value but returns None
- Student prints instead of returns

**How to address:**
- Explain: "print() shows output, return gives it back to the caller"
- Question: "What happens when another function tries to use this result?"

**Target with problems like:**
"Write a function that RETURNS the result" (emphasize return)

---

### index_error
**What it looks like:**
- Accessing list[-1] when empty
- Accessing list[len(list)] instead of list[len(list)-1]
- Off-by-one in index access

**How to address:**
- Visual: Show indices vs values
  ```
  Values:  [10, 20, 30]
  Indices:  0   1   2
  ```
- Question: "If a list has 3 items, what's the last valid index?"

**Target with problems like:**
"Return the last element of the list" (test with single-element and empty)

---

### infinite_loop
**What it looks like:**
- While loop never terminates
- Forgetting to update loop variable
- Wrong termination condition

**How to address:**
- Visual: Trace showing why condition never becomes False
- Question: "What needs to change for the loop to eventually stop?"

**Target with problems like:**
"Keep dividing by 2 until you reach 1 or less"

---

### logic_error
**What it looks like:**
- Wrong operator (+ instead of *)
- Wrong condition (< instead of <=)
- Incorrect algorithm

**How to address:**
- Trace through with specific input showing where logic diverges
- Compare expected vs actual step by step

---

### type_error
**What it looks like:**
- Adding string to int
- Calling method on wrong type
- None + something

**How to address:**
- Explain: "Python has different types. '5' (string) ≠ 5 (number)"
- Show: `type(value)` to inspect

---

### syntax_error
**What it looks like:**
- Missing colon
- Wrong indentation
- Mismatched brackets

**How to address:**
- Point to exact line and character
- Show correct syntax pattern

## Problem Design by Error

| Error Pattern | Problem That Tests It |
|--------------|----------------------|
| off_by_one | "Sum 1 to n INCLUSIVE" |
| forgotten_return | "Return the computed value" |
| index_error | "Get first AND last element" |
| infinite_loop | "Loop until condition met" |
| logic_error | Multi-step calculations |
| type_error | Mix strings and numbers |
