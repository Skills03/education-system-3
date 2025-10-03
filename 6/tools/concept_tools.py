"""Concept Teaching Tools - Show examples and simulations"""

from claude_agent_sdk import tool


@tool(
    "show_code_example",
    "Display code example - MAX 3 LINES (Use code_live_increment for teaching instead!)",
    {"language": str, "code": str, "explanation": str, "title": str}
)
async def show_code_example(args):
    """Show formatted code example. ENFORCES MAX 3 LINES. Use code_live_increment for Scrimba-style teaching!"""
    language = args.get("language", "python")
    code = args["code"]
    explanation = args.get("explanation", "")
    title = args.get("title", "Code Example")

    # ENFORCE MAX 3 LINES
    lines = code.strip().split('\n')
    if len(lines) > 3:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ ERROR: show_code_example allows MAX 3 LINES.\nYou tried: {len(lines)} lines.\n\n⚠️ For teaching, use code_live_increment instead (call it multiple times, one increment at a time)!\n\nThis tool is for quick reference only, not teaching."
            }]
        }

    formatted = f"""### {title}

{explanation}

```{language}
{code}
```
"""
    return {"content": [{"type": "text", "text": formatted}]}


@tool(
    "run_code_simulation",
    "Simulate running code - MAX 3 LINES (for quick demos, use demonstrate_code for full programs)",
    {"code": str, "output": str, "language": str}
)
async def run_code_simulation(args):
    """Simulate code execution. ENFORCES MAX 3 LINES."""
    code = args["code"]
    output = args["output"]
    language = args.get("language", "python")

    # ENFORCE MAX 3 LINES
    lines = code.strip().split('\n')
    if len(lines) > 3:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ ERROR: run_code_simulation allows MAX 3 LINES.\nYou tried: {len(lines)} lines.\n\n💡 For full programs, use demonstrate_code instead!"
            }]
        }

    formatted = f"""#### 💻 Running Code:

```{language}
{code}
```

#### 📤 Output:
```
{output}
```
"""
    return {"content": [{"type": "text", "text": formatted}]}


@tool(
    "show_concept_progression",
    "Show code evolution - MAX 3 LINES for basic AND advanced versions (Scrimba-style)",
    {"concept": str, "basic_code": str, "advanced_code": str, "explanation": str}
)
async def show_concept_progression(args):
    """Show code progression. ENFORCES MAX 3 LINES each."""
    concept = args["concept"]
    basic_code = args["basic_code"]
    advanced_code = args["advanced_code"]
    explanation = args["explanation"]

    # ENFORCE MAX 3 LINES for both
    basic_lines = basic_code.strip().split('\n')
    advanced_lines = advanced_code.strip().split('\n')

    if len(basic_lines) > 3 or len(advanced_lines) > 3:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ ERROR: show_concept_progression allows MAX 3 LINES for EACH version.\nBasic: {len(basic_lines)} lines, Advanced: {len(advanced_lines)} lines.\n\n💡 Keep examples small! Use code_live_increment for longer code."
            }]
        }

    formatted = f"""### 📈 {concept} - Progressive Learning

#### Level 1: Basic Version
```python
{basic_code}
```

#### Level 2: Advanced Version
```python
{advanced_code}
```

**What changed?** {explanation}
"""
    return {"content": [{"type": "text", "text": formatted}]}


@tool(
    "create_interactive_challenge",
    "Create coding challenge - MAX 3 LINES for solution (keep challenges simple!)",
    {"challenge": str, "hint": str, "solution": str}
)
async def create_interactive_challenge(args):
    """Create challenge. ENFORCES MAX 3 LINES for solution."""
    challenge = args["challenge"]
    hint = args.get("hint", "Think about the problem step by step!")
    solution = args["solution"]

    # ENFORCE MAX 3 LINES for solution
    solution_lines = solution.strip().split('\n')
    if len(solution_lines) > 3:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ ERROR: create_interactive_challenge allows MAX 3 LINES for solution.\nYou tried: {len(solution_lines)} lines.\n\n💡 Keep challenges SIMPLE! Scrimba-style = small, focused challenges."
            }]
        }

    formatted = f"""### 🎯 Challenge Time!

**Task:** {challenge}

**Hint:** 💡 {hint}

<details>
<summary>Click to see solution</summary>

```python
{solution}
```

</details>
"""
    return {"content": [{"type": "text", "text": formatted}]}
