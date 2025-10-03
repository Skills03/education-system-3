"""Concept Teaching Tools - Show examples and simulations"""

from claude_agent_sdk import tool


@tool(
    "show_code_example",
    "Display a code example with syntax highlighting and explanation",
    {"language": str, "code": str, "explanation": str, "title": str}
)
async def show_code_example(args):
    """Show formatted code example with explanation."""
    language = args.get("language", "python")
    code = args["code"]
    explanation = args.get("explanation", "")
    title = args.get("title", "Code Example")

    formatted = f"""### {title}

{explanation}

```{language}
{code}
```
"""
    return {"content": [{"type": "text", "text": formatted}]}


@tool(
    "run_code_simulation",
    "Simulate running code and show the output",
    {"code": str, "output": str, "language": str}
)
async def run_code_simulation(args):
    """Simulate code execution with output."""
    code = args["code"]
    output = args["output"]
    language = args.get("language", "python")

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
    "Show how code evolves from basic to advanced",
    {"concept": str, "basic_code": str, "advanced_code": str, "explanation": str}
)
async def show_concept_progression(args):
    """Show code progression from basic to advanced."""
    concept = args["concept"]
    basic_code = args["basic_code"]
    advanced_code = args["advanced_code"]
    explanation = args["explanation"]

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
    "Create a coding challenge for the student",
    {"challenge": str, "hint": str, "solution": str}
)
async def create_interactive_challenge(args):
    """Create an interactive coding challenge."""
    challenge = args["challenge"]
    hint = args.get("hint", "Think about the problem step by step!")
    solution = args["solution"]

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
