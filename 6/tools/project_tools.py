"""Live Coding Tools - Build projects step-by-step"""

from claude_agent_sdk import tool


@tool(
    "project_kickoff",
    "Initialize a new project by analyzing what to build and showing the starting point",
    {"project_description": str}
)
async def project_kickoff(args):
    """Start a new project with overview and initial structure."""
    project_desc = args["project_description"]

    formatted = f"""### 🚀 Let's Build Together: {project_desc}

**I'm analyzing what we need to build...**

We'll create this project step-by-step, and I'll code it WITH you - just like Scrimba!

**Here's our starting point:**

```python
# {project_desc}
# Starting fresh - let's build this together!

```

**Ready? Let's write our first line of code!** 👨‍💻
"""
    return {"content": [{"type": "text", "text": formatted}]}


@tool(
    "code_live_increment",
    "Add code incrementally - MAXIMUM 3 LINES per call (Scrimba-style line-by-line teaching)",
    {"feature": str, "code_to_add": str, "explanation": str, "language": str}
)
async def code_live_increment(args):
    """Show code being added with explanation. ENFORCES MAX 3 LINES."""
    feature = args["feature"]
    code_to_add = args["code_to_add"]
    explanation = args["explanation"]
    language = args.get("language", "python")

    # ENFORCE MAX 3 LINES - Scrimba style!
    lines = code_to_add.strip().split('\n')
    if len(lines) > 3:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ ERROR: code_live_increment allows MAX 3 LINES at a time (Scrimba-style teaching).\nYou tried to add {len(lines)} lines.\n\nSplit your code into smaller increments and call this tool multiple times!\n\nExample:\nCall 1: let count = 0\nCall 2: console.log(count)\nCall 3: count = count + 1"
            }]
        }

    formatted = f"""### ✍️ Adding: {feature}

**{explanation}**

**Watch me code this:**

```{language}
{code_to_add}
```

**💡 Why this works:**
{explanation}

---

Let's see it in action... 🚀
"""
    return {"content": [{"type": "text", "text": formatted}]}


@tool(
    "demonstrate_code",
    "Run the code and show what happens - simulate execution",
    {"code": str, "example_usage": str, "expected_output": str, "language": str}
)
async def demonstrate_code(args):
    """Demonstrate code execution."""
    code = args["code"]
    example_usage = args["example_usage"]
    expected_output = args["expected_output"]
    language = args.get("language", "python")

    formatted = f"""### ▶️ Running The Code

**Current code:**
```{language}
{code}
```

**Let's test it:**
```{language}
{example_usage}
```

**📤 Output:**
```
{expected_output}
```

**🎉 It works!** See how that function does exactly what we need?
"""
    return {"content": [{"type": "text", "text": formatted}]}


@tool(
    "student_challenge",
    "Give student a coding challenge to try themselves",
    {"task": str, "hints": str, "function_signature": str}
)
async def student_challenge(args):
    """Challenge the student to code."""
    task = args["task"]
    hints = args.get("hints", "Think about what we just learned!")
    function_signature = args.get("function_signature", "")

    formatted = f"""### 🎯 Your Turn to Code!

**Challenge:** {task}

**Starting point:**
```python
{function_signature}
```

**💡 Hints:**
{hints}

**Try it yourself!** I'll review your code and help if you get stuck. 🚀
"""
    return {"content": [{"type": "text", "text": formatted}]}


@tool(
    "review_student_work",
    "Review student's submitted code with constructive feedback",
    {"student_code": str, "task_description": str}
)
async def review_student_work(args):
    """Review and provide feedback."""
    student_code = args["student_code"]
    task_desc = args.get("task_description", "the task")

    # Simple analysis
    feedback = []

    if len(student_code.strip()) < 10:
        feedback.append("❌ Code seems incomplete - try adding more!")
        next_action = "retry"
    else:
        if "def " in student_code:
            feedback.append("✅ Good function definition!")
        if "return" in student_code:
            feedback.append("✅ Returns a value - excellent!")
        if "#" in student_code:
            feedback.append("✅ Code comments - nice!")

        feedback.append("🎉 Great work! This looks good!")
        next_action = "continue"

    formatted = f"""### 📝 Code Review

**Your code:**
```python
{student_code}
```

**Feedback:**
{chr(10).join(feedback)}

**Next:** {"Let's keep building! 🚀" if next_action == "continue" else "Try again - you're close! 💪"}
"""
    return {"content": [{"type": "text", "text": formatted}]}
