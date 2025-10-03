#!/usr/bin/env python3
"""Live Coding Teacher - Scrimba-Style Project Building"""

import asyncio
import json
from datetime import datetime
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import uuid
import traceback
import logging
from pathlib import Path

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
    ToolResultBlock,
    tool,
    create_sdk_mcp_server,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# ===== LIVE CODING TOOLS =====

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
    "Add code incrementally with live explanation - like typing in real-time",
    {"feature": str, "code_to_add": str, "explanation": str, "language": str}
)
async def code_live_increment(args):
    """Show code being added with explanation."""
    feature = args["feature"]
    code_to_add = args["code_to_add"]
    explanation = args["explanation"]
    language = args.get("language", "python")

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


# Create MCP server
live_coding_tools = create_sdk_mcp_server(
    name="live_coding",
    version="1.0.0",
    tools=[
        project_kickoff,
        code_live_increment,
        demonstrate_code,
        student_challenge,
        review_student_work,
    ],
)


# Live Coding Agent
LIVE_CODING_AGENT = AgentDefinition(
    description="Live coding teacher - builds projects WITH students Scrimba-style",
    prompt="""You are a LIVE CODING instructor like Scrimba. You BUILD projects WITH students in real-time.

🎯 YOUR STYLE:
You're the teacher who codes WHILE explaining. Students learn by WATCHING you build, then TRYING themselves.

🔧 YOUR TOOLS:

1. **mcp__live_coding__project_kickoff** - Start any project
   Parameters: project_description
   Use when: Student says "let's build X" or "teach me Y by building"

2. **mcp__live_coding__code_live_increment** - Add code piece by piece
   Parameters: feature, code_to_add, explanation, language
   Use when: Adding ANY new code (functions, classes, features)
   IMPORTANT: Show code INCREMENTALLY, not all at once!

3. **mcp__live_coding__demonstrate_code** - Run and show results
   Parameters: code, example_usage, expected_output, language
   Use when: You want to show code working
   Show the execution and output!

4. **mcp__live_coding__student_challenge** - Challenge student to code
   Parameters: task, hints, function_signature
   Use when: Student should try coding themselves
   Give them a clear task!

5. **mcp__live_coding__review_student_work** - Review their code
   Parameters: student_code, task_description
   Use when: Student submits code for review
   Be constructive and encouraging!

📚 TEACHING FLOW:

**Starting a Project:**
Student: "Let's build a todo app"
You:
  → Call project_kickoff("todo app with add/delete/complete")
  → "Alright! Let's start with the basic Todo class..."
  → Call code_live_increment to add __init__ method
  → Call demonstrate_code to show it working
  → "Now let's add the add_todo method..."
  → Call code_live_increment again
  → Continue building together!

**Teaching Pattern:**
1. Explain WHAT you'll build
2. USE code_live_increment to ADD code (show, don't tell!)
3. USE demonstrate_code to RUN it
4. Build up complexity gradually
5. USE student_challenge when they should try
6. USE review_student_work on their submissions
7. Continue building together!

**Key Principles:**
✅ BUILD projects, don't just explain concepts
✅ Show code incrementally (like typing live)
✅ Demonstrate execution after each addition
✅ Let students try - then review
✅ Make it feel interactive and hands-on
✅ Connect to real-world use cases
✅ Celebrate their progress!

**Example Session:**
Student: "Teach me Python classes by building a calculator"

You: [Call project_kickoff]
"Perfect! Let's build a calculator together. We'll start with basic operations..."

You: [Call code_live_increment with Calculator class __init__]
"First, let's create our Calculator class..."

You: [Call demonstrate_code showing Calculator()]
"See? We can now create a calculator object!"

You: [Call code_live_increment with add method]
"Now let's add the addition method..."

You: [Call demonstrate_code showing 5 + 3 = 8]
"Beautiful! It works!"

You: "Now YOUR turn - add a subtract method!"
You: [Call student_challenge]

Student: [submits code]

You: [Call review_student_work]
"Excellent! You got it!"

You: [Continue building...]

Remember: You're BUILDING together, like Scrimba! Code live, explain as you go, let them participate!""",
    tools=[
        "mcp__live_coding__project_kickoff",
        "mcp__live_coding__code_live_increment",
        "mcp__live_coding__demonstrate_code",
        "mcp__live_coding__student_challenge",
        "mcp__live_coding__review_student_work",
    ],
    model="sonnet",
)


app = Flask(__name__)
CORS(app)

sessions = {}
message_queues = {}


class LiveCodingSession:
    """Live coding session"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.options = ClaudeAgentOptions(
            agents={"live_coder": LIVE_CODING_AGENT},
            mcp_servers={"live_coding": live_coding_tools},
            allowed_tools=[
                "mcp__live_coding__project_kickoff",
                "mcp__live_coding__code_live_increment",
                "mcp__live_coding__demonstrate_code",
                "mcp__live_coding__student_challenge",
                "mcp__live_coding__review_student_work",
            ],
        )
        self.messages = []

    async def teach(self, instruction):
        """Live coding session"""
        logger.info(f"[{self.session_id[:8]}] Live coding: {instruction}")

        try:
            async with ClaudeSDKClient(options=self.options) as client:
                await client.query(f"Use the live_coder agent: {instruction}")

                message_count = 0
                async for msg in client.receive_response():
                    message_count += 1
                    formatted_list = self._format_message(msg)
                    if formatted_list:
                        for formatted in formatted_list:
                            self.messages.append(formatted)
                            if self.session_id in message_queues:
                                message_queues[self.session_id].append(formatted)

                logger.info(f"[{self.session_id[:8]}] ✓ Complete! {message_count} messages")

            complete_msg = {"type": "complete", "timestamp": datetime.now().isoformat()}
            self.messages.append(complete_msg)
            if self.session_id in message_queues:
                message_queues[self.session_id].append(complete_msg)

        except Exception as e:
            logger.error(f"[{self.session_id[:8]}] ❌ Error: {e}")
            logger.error(traceback.format_exc())
            error_msg = {
                "type": "error",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            if self.session_id in message_queues:
                message_queues[self.session_id].append(error_msg)

    def _format_message(self, msg):
        """Format message"""
        result = []

        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    if block.text and block.text.strip():
                        result.append({
                            "type": "teacher",
                            "content": block.text,
                            "timestamp": datetime.now().isoformat()
                        })
                elif isinstance(block, ToolUseBlock):
                    result.append({
                        "type": "action",
                        "content": f"🔧 {block.name}",
                        "timestamp": datetime.now().isoformat()
                    })

        elif isinstance(msg, UserMessage):
            for block in msg.content:
                if isinstance(block, ToolResultBlock):
                    if block.content:
                        result.append({
                            "type": "output",
                            "content": block.content,
                            "timestamp": datetime.now().isoformat()
                        })

        elif isinstance(msg, ResultMessage):
            if msg.total_cost_usd:
                result.append({
                    "type": "cost",
                    "content": f"${msg.total_cost_usd:.4f}",
                    "timestamp": datetime.now().isoformat()
                })

        return result if result else None


@app.route('/')
def index():
    html_path = Path(__file__).parent / 'project.html'
    return send_file(html_path)


@app.route('/api/session/start', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    session = LiveCodingSession(session_id)
    sessions[session_id] = session
    message_queues[session_id] = []
    return jsonify({"session_id": session_id, "status": "ready"})


@app.route('/api/teach', methods=['POST'])
def teach():
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message')

    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    session = sessions[session_id]

    import threading
    def run():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(session.teach(message))
            loop.close()
        except Exception as e:
            logger.error(f"Error: {e}")

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "processing"})


@app.route('/api/stream/<session_id>')
def stream(session_id):
    if session_id not in message_queues:
        return jsonify({"error": "Session not found"}), 404

    def generate():
        queue = message_queues[session_id]
        sent_count = 0
        heartbeat_count = 0

        while heartbeat_count < 60:
            if len(queue) > sent_count:
                for msg in queue[sent_count:]:
                    yield f"data: {json.dumps(msg)}\n\n"
                    sent_count += 1
                    if msg.get('type') in ['complete', 'error']:
                        return
                heartbeat_count = 0
            else:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                heartbeat_count += 1
            import time
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    print("=" * 70)
    print("🎓 LIVE CODING TEACHER - Scrimba Style")
    print("=" * 70)
    print("\n📱 Browser: http://localhost:5001")
    print("💡 Say: 'Let's build a todo app' or 'Teach me classes by building X'")
    print("\n✅ I'll code WITH you - just like Scrimba!")
    print("💡 Ctrl+C to stop\n")
    app.run(debug=True, port=5001, threaded=True)
