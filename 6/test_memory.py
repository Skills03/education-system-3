#!/usr/bin/env python3
"""Test script to verify memory persistence across teaching sessions"""

import asyncio
import json
from concept_tracker import ConceptBasedPermissionSystem
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
)
from claude_agent_sdk.types import PermissionResultAllow, PermissionResultDeny, ToolPermissionContext
from agents.master_agent import MASTER_TEACHER_AGENT
from tools.concept_tools import show_code_example, run_code_simulation, show_concept_progression, create_interactive_challenge
from tools.project_tools import project_kickoff, code_live_increment, demonstrate_code, student_challenge, review_student_work
from tools.visual_tools import generate_concept_diagram, generate_data_structure_viz, generate_algorithm_flowchart, generate_architecture_diagram
from claude_agent_sdk import create_sdk_mcp_server

# Create MCP servers
scrimba_tools = create_sdk_mcp_server(
    name="scrimba_tools",
    version="1.0.0",
    tools=[show_code_example, run_code_simulation, show_concept_progression, create_interactive_challenge],
)

live_coding_tools = create_sdk_mcp_server(
    name="live_coding",
    version="1.0.0",
    tools=[project_kickoff, code_live_increment, demonstrate_code, student_challenge, review_student_work],
)

visual_tools = create_sdk_mcp_server(
    name="visual_tools",
    version="1.0.0",
    tools=[generate_concept_diagram, generate_data_structure_viz, generate_algorithm_flowchart, generate_architecture_diagram],
)

class TestSession:
    def __init__(self, session_id="test-session"):
        self.session_id = session_id
        self.concept_permission = ConceptBasedPermissionSystem(session_id)
        self.current_agent_message = ""

        async def limit_tools(tool_name: str, input_data: dict, context: ToolPermissionContext):
            can_use, reason = self.concept_permission.can_use_tool(tool_name, input_data, self.current_agent_message)
            if can_use:
                print(f"  ✓ Tool allowed: {tool_name}")
                return PermissionResultAllow(behavior="allow")
            else:
                print(f"  ✗ Tool denied: {tool_name} - {reason}")
                return PermissionResultDeny(behavior="deny", message=reason, interrupt=False)

        self.options = ClaudeAgentOptions(
            agents={"master": MASTER_TEACHER_AGENT},
            mcp_servers={"scrimba": scrimba_tools, "live_coding": live_coding_tools, "visual": visual_tools},
            allowed_tools=[
                "mcp__scrimba__show_code_example", "mcp__scrimba__run_code_simulation",
                "mcp__scrimba__show_concept_progression", "mcp__scrimba__create_interactive_challenge",
                "mcp__live_coding__project_kickoff", "mcp__live_coding__code_live_increment",
                "mcp__live_coding__demonstrate_code", "mcp__live_coding__student_challenge",
                "mcp__live_coding__review_student_work", "mcp__visual__generate_concept_diagram",
                "mcp__visual__generate_data_structure_viz", "mcp__visual__generate_algorithm_flowchart",
                "mcp__visual__generate_architecture_diagram",
            ],
            can_use_tool=limit_tools,
            setting_sources=["project"]  # Enable memory persistence
        )

    async def teach(self, instruction):
        print(f"\n{'='*80}")
        print(f"🎓 Teaching: {instruction}")
        print(f"{'='*80}")

        self.concept_permission.reset()
        self.current_agent_message = ""

        client = ClaudeSDKClient(options=self.options)
        await client.connect()

        prompt = f"""Use the master agent: {instruction}

CRITICAL: Follow concept-based teaching protocol:
1. DECLARE concepts first: "This response teaches N concepts: ..."
2. Maximum 3 concepts per response (working memory limit)
3. Use sequential tool chaining (each tool builds on previous)

Remember our previous conversation context from .claude/CLAUDE.md"""

        await client.query(prompt)

        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock) and block.text:
                        self.current_agent_message += block.text + " "
                        print(f"\n💬 Agent: {block.text[:200]}...")

        await client.disconnect()

        status = self.concept_permission.tracker.get_status()
        print(f"\n📊 Session Summary:")
        print(f"  • Concepts taught: {status['concept_count']}")
        print(f"  • Tools used: {status['tools_used']}")
        print(f"  • Concepts: {', '.join(status['concepts'])}")

async def main():
    print("\n" + "="*80)
    print("🧪 TESTING MEMORY PERSISTENCE")
    print("="*80)

    # Check initial CLAUDE.md state
    print("\n📖 Reading initial .claude/CLAUDE.md...")
    with open('.claude/CLAUDE.md', 'r') as f:
        initial_content = f.read()
        if 'Session Count: 0' in initial_content:
            print("  ✓ Starting with clean state (0 sessions)")
        else:
            print("  ⚠ CLAUDE.md has existing data")

    session = TestSession()

    # Session 1: Teach variables
    print("\n" + "="*80)
    print("SESSION 1: Teaching fundamental concept")
    print("="*80)
    await session.teach("Teach me about variables in Python")

    # Check CLAUDE.md after session 1
    print("\n📖 Reading .claude/CLAUDE.md after Session 1...")
    with open('.claude/CLAUDE.md', 'r') as f:
        session1_content = f.read()
        if 'variables' in session1_content.lower():
            print("  ✓ CLAUDE.md mentions 'variables'")
        if 'Session Count: 1' in session1_content or 'Session 1' in session1_content:
            print("  ✓ Session count incremented")
        else:
            print("  ✗ Session count not updated")

    # Session 2: Teach loops (should reference variables)
    print("\n" + "="*80)
    print("SESSION 2: Teaching related concept (should build on Session 1)")
    print("="*80)
    await session.teach("Now teach me about loops in Python")

    # Check CLAUDE.md after session 2
    print("\n📖 Reading .claude/CLAUDE.md after Session 2...")
    with open('.claude/CLAUDE.md', 'r') as f:
        session2_content = f.read()
        if 'loops' in session2_content.lower():
            print("  ✓ CLAUDE.md mentions 'loops'")
        if 'variables' in session2_content.lower():
            print("  ✓ CLAUDE.md still has 'variables' from Session 1")
        if session2_content != session1_content:
            print("  ✓ CLAUDE.md was updated (content changed)")
        else:
            print("  ✗ CLAUDE.md was NOT updated")

    print("\n" + "="*80)
    print("🎉 MEMORY PERSISTENCE TEST COMPLETE")
    print("="*80)
    print("\nExpected behavior:")
    print("  1. Session 1 teaches variables → CLAUDE.md updated")
    print("  2. Session 2 teaches loops → Agent reads CLAUDE.md, sees variables")
    print("  3. Agent builds on existing knowledge (uses variables in loop examples)")
    print("  4. CLAUDE.md now contains both variables AND loops")

    print("\n📄 Final CLAUDE.md content preview:")
    print("-" * 80)
    print(session2_content[:800])
    print("-" * 80)

if __name__ == "__main__":
    asyncio.run(main())
