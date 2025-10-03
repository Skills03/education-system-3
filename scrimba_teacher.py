#!/usr/bin/env python3
"""Scrimba-Style Interactive Teaching Agent.

A teacher agent that provides interactive coding lessons with:
- Live code demonstrations
- Real-time code execution and output
- Step-by-step explanations
- Interactive Q&A
- Practice exercises with feedback
- Multi-turn conversations

Usage:
    python scrimba_teacher.py                    # Interactive lesson
    python scrimba_teacher.py --quick-demo       # Quick demo
"""

import asyncio
import sys
from typing import Optional

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
)


# Define the teacher agent
TEACHER_AGENT = AgentDefinition(
    description="Interactive coding teacher that explains concepts with live code",
    prompt="""You are an expert programming instructor inspired by Scrimba's interactive teaching style.

TEACHING PHILOSOPHY:
1. **Show, Don't Just Tell**: Write actual code and run it to demonstrate concepts
2. **Build Incrementally**: Start simple, add complexity step-by-step
3. **Explain the Why**: Connect code to real-world use cases
4. **Encourage Exploration**: Invite questions and deeper investigation

TEACHING PROCESS:
1. Introduce the concept with a clear, relatable explanation
2. Write clean, well-commented code to demonstrate
3. Execute the code and show the output
4. Explain what happened and why it works
5. Point out common gotchas or best practices
6. Connect to previous concepts when relevant

CODE STYLE:
- Write clean, readable code with meaningful variable names
- Add comments to explain non-obvious parts
- Show output after running code
- Use real-world examples when possible

INTERACTION STYLE:
- Be encouraging and patient
- Celebrate "aha!" moments
- Break down complex topics into digestible pieces
- Use analogies to explain abstract concepts
- Ask thought-provoking questions to deepen understanding

When teaching:
- Create files to demonstrate concepts
- Run code to show actual results
- Edit code to show iterations and improvements
- Be enthusiastic about the learning journey""",
    tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    model="sonnet",
)


class ScrimbaSession:
    """Manages an interactive teaching session."""

    def __init__(self, topic: str):
        self.topic = topic
        self.client: Optional[ClaudeSDKClient] = None
        self.tools_used = []

    async def start(self):
        """Initialize the teaching session."""
        options = ClaudeAgentOptions(
            agents={"teacher": TEACHER_AGENT},
            # Grant permissions to all tools the teacher needs
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        )
        self.client = ClaudeSDKClient(options=options)
        await self.client.connect()

    async def stop(self):
        """Clean up the session."""
        if self.client:
            await self.client.disconnect()

    def display_message(self, msg) -> Optional[str]:
        """Display messages with appropriate formatting."""
        response = ""

        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    text = block.text
                    print(f"\n🎓 Teacher: {text}\n")
                    response += text
                elif isinstance(block, ToolUseBlock):
                    # Show what the teacher is doing
                    tool = block.name
                    self.tools_used.append(tool)

                    if tool == "Write":
                        path = block.input.get("file_path", "?")
                        print(f"📝 Creating file: {path}")
                    elif tool == "Edit":
                        path = block.input.get("file_path", "?")
                        print(f"✏️  Editing file: {path}")
                    elif tool == "Bash":
                        cmd = block.input.get("command", "?")
                        print(f"▶️  Running: {cmd}")
                    elif tool == "Read":
                        path = block.input.get("file_path", "?")
                        print(f"📖 Reading: {path}")

        elif isinstance(msg, UserMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"\n👤 You: {block.text}\n")
                elif isinstance(block, ToolResultBlock):
                    # Show command output if it's bash
                    if block.content and len(block.content) < 500:
                        print(f"💻 Output:\n{block.content}\n")

        elif isinstance(msg, ResultMessage):
            if msg.total_cost_usd and msg.total_cost_usd > 0:
                print(f"💰 Cost: ${msg.total_cost_usd:.4f}")

        return response if response else None

    async def teach(self, instruction: str):
        """Send teaching instruction and stream response."""
        await self.client.query(f"Use the teacher agent: {instruction}")

        async for msg in self.client.receive_response():
            self.display_message(msg)

    async def ask(self, question: str):
        """Ask the teacher a question."""
        await self.client.query(f"Use the teacher agent: {question}")

        async for msg in self.client.receive_response():
            self.display_message(msg)


async def quick_demo():
    """Run a quick demonstration of the teacher agent."""
    print("=" * 70)
    print("🎓 SCRIMBA-STYLE TEACHING AGENT - QUICK DEMO")
    print("=" * 70)

    session = ScrimbaSession("Python List Comprehensions")
    await session.start()

    try:
        print("\n📚 Starting lesson on Python List Comprehensions...\n")

        # Initial teaching
        await session.teach(
            "Teach me Python list comprehensions. Create a file called 'comprehensions.py' "
            "with 3 progressive examples:\n"
            "1. Basic list comprehension (squares of numbers)\n"
            "2. List comprehension with a filter (even numbers only)\n"
            "3. Nested list comprehension (2D matrix)\n"
            "Run the code after writing it and explain each example clearly."
        )

        print("\n" + "-" * 70)
        print("💬 Student asks a follow-up question...")
        print("-" * 70)

        # Follow-up question
        await session.ask(
            "When should I use list comprehensions versus regular for loops? "
            "Show me a comparison."
        )

        print("\n" + "=" * 70)
        print(f"✅ Demo complete! Tools used: {', '.join(set(session.tools_used))}")
        print("=" * 70)

    finally:
        await session.stop()


async def interactive_lesson():
    """Run an interactive lesson with user input."""
    print("=" * 70)
    print("🎓 SCRIMBA-STYLE INTERACTIVE TEACHING SESSION")
    print("=" * 70)
    print("\nWelcome to your interactive coding lesson!")
    print("\nAvailable commands:")
    print("  - Type your question or request")
    print("  - 'next' - Move to next topic")
    print("  - 'exercise' - Get a practice exercise")
    print("  - 'quit' - Exit the session")
    print("=" * 70)

    # Get topic from user
    topic = input("\n📚 What would you like to learn about? ").strip()
    if not topic:
        print("No topic provided. Exiting.")
        return

    session = ScrimbaSession(topic)
    await session.start()

    try:
        # Start with initial teaching
        print(f"\n{'=' * 70}")
        print(f"Starting lesson: {topic}")
        print(f"{'=' * 70}\n")

        await session.teach(
            f"Teach me about {topic}. Start with the fundamentals, "
            f"write example code, run it, and explain the results. "
            f"Make it practical and engaging."
        )

        # Interactive loop
        step = 1
        while True:
            print(f"\n{'─' * 70}")
            user_input = input("💬 Your turn (or 'next'/'exercise'/'quit'): ").strip()

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd == 'quit':
                print("\n👋 Great job learning! Keep coding!")
                break

            elif cmd == 'next':
                step += 1
                print(f"\n📖 Moving to advanced concept #{step}...\n")
                await session.teach(
                    f"Now teach me the next level concept related to {topic}. "
                    f"Show practical code examples and explain best practices."
                )

            elif cmd == 'exercise':
                print("\n📝 Generating practice exercise...\n")
                await session.teach(
                    f"Create a coding exercise for {topic} that reinforces what we've learned. "
                    f"Provide clear requirements and explain what the solution should demonstrate."
                )

                print("\n" + "─" * 70)
                solution = input("📋 Paste your solution (or 'skip' to see answer): ").strip()

                if solution.lower() != 'skip' and solution:
                    await session.ask(
                        f"Review this student solution and provide constructive feedback:\n\n"
                        f"{solution}\n\n"
                        f"Then show an optimal solution with explanation."
                    )
                elif solution.lower() == 'skip':
                    await session.ask("Show me the optimal solution with detailed explanation.")

            else:
                # Student question
                await session.ask(user_input)

    finally:
        await session.stop()


async def structured_lesson():
    """Run a pre-defined structured lesson."""
    print("=" * 70)
    print("🎓 STRUCTURED LESSON: Python Decorators")
    print("=" * 70)

    session = ScrimbaSession("Python Decorators")
    await session.start()

    lessons = [
        {
            "title": "Step 1: Understanding Functions as First-Class Objects",
            "instruction": (
                "Teach the foundation for decorators: functions as first-class objects. "
                "Create 'decorators_lesson.py' and show:\n"
                "1. Assigning functions to variables\n"
                "2. Passing functions as arguments\n"
                "3. Returning functions from functions\n"
                "Run examples and explain why this matters for decorators."
            ),
        },
        {
            "title": "Step 2: Your First Decorator",
            "instruction": (
                "Now create a simple decorator. In the same file, add:\n"
                "1. A timing decorator that measures execution time\n"
                "2. Show both the manual wrapping way and the @ syntax\n"
                "3. Apply it to a slow function\n"
                "Run it and explain what's happening under the hood."
            ),
        },
        {
            "title": "Step 3: Decorators with Arguments",
            "instruction": (
                "Level up with decorator factories. Add to the file:\n"
                "1. A @repeat(n) decorator that runs a function n times\n"
                "2. Show the three levels of nesting\n"
                "3. Demonstrate with different values\n"
                "Run examples and explain the pattern."
            ),
        },
    ]

    try:
        for i, lesson in enumerate(lessons, 1):
            print(f"\n{'=' * 70}")
            print(f"📖 {lesson['title']}")
            print(f"{'=' * 70}\n")

            await session.teach(lesson['instruction'])

            if i < len(lessons):
                input("\n⏎  Press Enter to continue to next step...")

        print(f"\n{'=' * 70}")
        print("🎉 Lesson Complete!")
        print(f"{'=' * 70}")
        print("\n💡 Try experimenting with the code you learned!")
        print(f"Tools used: {', '.join(set(session.tools_used))}")

    finally:
        await session.stop()


async def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode in ["--quick-demo", "-q"]:
            await quick_demo()
        elif mode in ["--structured", "-s"]:
            await structured_lesson()
        elif mode in ["--help", "-h"]:
            print(__doc__)
        else:
            print(f"Unknown option: {mode}")
            print("Use --help for usage information")
    else:
        # Default to interactive mode
        await interactive_lesson()


if __name__ == "__main__":
    asyncio.run(main())
