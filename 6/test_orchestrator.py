#!/usr/bin/env python3
"""Test orchestrator pattern - delegating to builder agent"""

import asyncio
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, AgentDefinition, create_sdk_mcp_server
from tools.app_building_tools import list_app_templates, customize_app_template, generate_client_proposal

# Create MCP server
app_builder = create_sdk_mcp_server(
    name="app_builder",
    version="1.0.0",
    tools=[list_app_templates, customize_app_template, generate_client_proposal],
)

# Builder agent with velocity prompt
builder_velocity_prompt = """You help students build apps with maximum velocity using byte-sized building.

## CRITICAL: EXECUTE TOOLS IMMEDIATELY

**DO NOT explain. DO NOT ask questions. DO NOT wait. EXECUTE TOOLS NOW.**

When you receive a build request:
1. IMMEDIATELY call customize_app_template (skip list if portfolio/menu mentioned)
2. IMMEDIATELY call generate_client_proposal after customize completes
3. ONLY THEN explain what you built

## VELOCITY PRINCIPLE: Default Fast, Skip Slow

**If request mentions "portfolio" or "website":**
→ Skip list_app_templates (saves 30 seconds)
→ Go straight to customize_app_template with template_name="portfolio"

## TOOL EXECUTION (NOT OPTIONAL)

**STEP 1: Call customize_app_template FIRST**
template_name: "portfolio" (default) OR "restaurant_menu" OR "booking" OR "invoice"
client_name: Extract from request
customizations: Extract 3-5 words max

**STEP 2: Call generate_client_proposal IMMEDIATELY after**

**NO text responses before tools execute. Tools FIRST, explanation AFTER.**"""

builder_agent = AgentDefinition(
    description="App builder agent that creates income-generating apps for students using templates",
    tools=[
        "mcp__app_builder__list_app_templates",
        "mcp__app_builder__customize_app_template",
        "mcp__app_builder__generate_client_proposal"
    ],
    prompt=builder_velocity_prompt,
    model="sonnet"
)

# Orchestrator prompt
orchestrator_prompt = """You are an orchestrator agent that routes requests to specialized agents.

**Routing Rules:**
- App building requests (portfolio, website, app, menu, booking, invoice, build) → delegate to 'builder' subagent

**How to delegate:**
Use the Task tool with:
- prompt: The user's EXACT request
- subagent_type: 'builder'
- description: Short 3-5 word description like "Build portfolio app"

CRITICAL: Do NOT try to build yourself. ONLY delegate using Task tool."""

# Options with orchestrator - allow all MCP tools
options = ClaudeAgentOptions(
    agents={"builder": builder_agent},
    mcp_servers={"app_builder": app_builder},
    allowed_tools=[
        "Task",
        "mcp__app_builder__list_app_templates",
        "mcp__app_builder__customize_app_template",
        "mcp__app_builder__generate_client_proposal"
    ],
    system_prompt=orchestrator_prompt,
)

async def test():
    print("=" * 80)
    print("Testing Orchestrator Pattern with AgentDefinition")
    print("=" * 80)
    print("\nRequest: 'Build me a portfolio for James the photographer'\n")

    client = ClaudeSDKClient(options=options)
    await client.connect()

    await client.query("Build me a portfolio for James the photographer")

    print("\n--- Response Stream ---\n")
    async for msg in client.receive_response():
        print(f"{msg.__class__.__name__}:")
        if hasattr(msg, 'content'):
            for block in msg.content:
                print(f"  {block}")
        print()

    await client.disconnect()
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test())
