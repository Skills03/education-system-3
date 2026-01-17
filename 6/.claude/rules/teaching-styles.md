# Teaching Styles Reference

Use this when explaining concepts or giving feedback.

## How to Detect Best Style

```bash
python -c "from core.education_tools import tool_get_profile; p=tool_get_profile(); print(p['learning_styles']['best_style'])"
```

## Style Definitions

### example_first
**When:** Student has high success rate with examples
**How:** Show working code FIRST, then explain the pattern

```python
# Example first:
result = []
for x in [1, 2, 3]:
    result.append(x * 2)
# result is [2, 4, 6]

# Now the explanation:
# This loop takes each item, doubles it, and collects results
```

### theory_first
**When:** Student asks "why" questions, prefers understanding before doing
**How:** Explain the concept, then show code

```
# Theory first:
"A loop iterates through a collection, executing code for each element.
This avoids repetitive code when you need to do the same thing many times."

# Then the code:
for x in [1, 2, 3]:
    print(x)
```

### analogy
**When:** Teaching new concepts, student is visual/creative
**How:** Real-world comparison first, then bridge to code

```
# Analogy:
"A loop is like a playlist on repeat - each song (item) gets played (processed) one after another until the list ends."

# Bridge:
"In code, 'playing each song' looks like this:"
for song in playlist:
    play(song)
```

### visual
**When:** Student makes index/order errors, needs to see execution
**How:** Draw diagrams, trace through step-by-step

```
Input: [10, 20, 30]
       ↓
Step 1: x = 10 → sum = 0 + 10 = 10
       ↓
Step 2: x = 20 → sum = 10 + 20 = 30
       ↓
Step 3: x = 30 → sum = 30 + 30 = 60
       ↓
Output: 60
```

### socratic
**When:** Student is close to understanding, needs to discover
**How:** Ask guiding questions instead of telling

```
"What values does range(3) produce?"
"If you want to include 3, what would you change?"
"Why do you think range excludes the end value?"
```

## Recording Style Used

After explaining, always record:
```bash
python -c "from core.education_tools import tool_record_explanation; print(tool_record_explanation('CONCEPT', 'STYLE'))"
```

This tracks what works for the student over time.
