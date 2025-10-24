#!/usr/bin/env python3
"""Test dual-mode builder: Velocity vs Tutorial"""

import asyncio
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, AgentDefinition, create_sdk_mcp_server
from tools.app_building_tools import (
    list_app_templates,
    customize_app_template,
    generate_client_proposal,
    add_code_step
)

# Create MCP server with new tool
app_builder = create_sdk_mcp_server(
    name="app_builder",
    version="1.0.0",
    tools=[list_app_templates, customize_app_template, generate_client_proposal, add_code_step],
)

# Builder agent with dual-mode prompt
builder_dual_mode_prompt = """You help students build apps using TWO modes:

## MODE DETECTION (CRITICAL)

**TUTORIAL MODE** - If request contains:
- "teach me", "show me step by step", "how to build", "explain while building", "learn to build"
→ Use `add_code_step` tool (15 incremental steps)

**VELOCITY MODE** - All other requests:
- "Build me", "create", "make me", "I need"
→ Use `customize_app_template` + `generate_client_proposal` (fast)

## 🎓 TUTORIAL MODE (Scrimba-style)

Use add_code_step tool 12-15 times sequentially. Start with empty string for current_code.

**Pattern for portfolio:**
Step 1: HTML skeleton (<!DOCTYPE html>...)
Step 2: Add title in head
Step 3: Add CSS reset in style
Step 4: Add hero div in body
Step 5: Style hero with gradient
Step 6: Add hero h1
Step 7: Style h1 text
[...continue to 15 steps]

Pass previous step's updated_code to next step's current_code parameter.

## ⚡ VELOCITY MODE

Call customize_app_template, then generate_client_proposal. Done.

DETECT mode and execute."""

builder_agent = AgentDefinition(
    description="Dual-mode app builder: Tutorial or Velocity",
    tools=[
        "mcp__app_builder__list_app_templates",
        "mcp__app_builder__customize_app_template",
        "mcp__app_builder__generate_client_proposal",
        "mcp__app_builder__add_code_step"
    ],
    prompt=builder_dual_mode_prompt,
    model="sonnet"
)

# Orchestrator
orchestrator_prompt = """Route app building requests to 'builder' subagent using Task tool."""

options = ClaudeAgentOptions(
    agents={"builder": builder_agent},
    mcp_servers={"app_builder": app_builder},
    allowed_tools=[
        "Task",
        "mcp__app_builder__list_app_templates",
        "mcp__app_builder__customize_app_template",
        "mcp__app_builder__generate_client_proposal",
        "mcp__app_builder__add_code_step"
    ],
    system_prompt=orchestrator_prompt,
)


async def test_velocity_mode():
    """Test fast velocity mode"""
    print("=" * 80)
    print("TEST 1: VELOCITY MODE")
    print("=" * 80)
    print("\nRequest: 'Build me a portfolio for Sarah the designer'\n")

    client = ClaudeSDKClient(options=options)
    await client.connect()

    await client.query("Build me a portfolio for Sarah the designer")

    step_count = 0
    async for msg in client.receive_response():
        if hasattr(msg, 'content'):
            for block in msg.content:
                if hasattr(block, 'name'):
                    step_count += 1
                    print(f"✓ Tool called: {block.name}")

    await client.disconnect()
    print(f"\n✓ Velocity mode complete: {step_count} tool calls\n")


async def test_tutorial_mode():
    """Test step-by-step tutorial mode"""
    print("=" * 80)
    print("TEST 2: TUTORIAL MODE")
    print("=" * 80)
    print("\nRequest: 'Teach me to build a portfolio step by step for Mike'\n")

    client = ClaudeSDKClient(options=options)
    await client.connect()

    await client.query("Teach me to build a portfolio step by step for Mike")

    step_count = 0
    add_code_step_count = 0
    async for msg in client.receive_response():
        if hasattr(msg, 'content'):
            for block in msg.content:
                if hasattr(block, 'name'):
                    step_count += 1
                    if block.name == 'add_code_step':
                        add_code_step_count += 1
                        print(f"🏗️  Step {add_code_step_count}: Building incrementally...")

    await client.disconnect()
    print(f"\n✓ Tutorial mode complete: {add_code_step_count} incremental steps\n")


async def main():
    print("\n🧪 TESTING DUAL-MODE BUILDER\n")

    print("Expected behavior:")
    print("- Velocity: 2 tool calls (customize + proposal)")
    print("- Tutorial: 12-15 tool calls (add_code_step)\n")

    await test_velocity_mode()
    await test_tutorial_mode()

    print("=" * 80)
    print("✅ TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
