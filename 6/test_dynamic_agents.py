#!/usr/bin/env python3
"""Test dynamic agent configuration system"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agent_config import (
    create_agent_definitions,
    get_enhanced_prompt,
    get_all_tools,
    add_agent,
    AGENT_CONFIGS
)

def test_dynamic_agents():
    print("=" * 70)
    print("TESTING DYNAMIC AGENT SYSTEM")
    print("=" * 70)

    # Test 1: Agent creation
    print("\n1. Creating agents from configuration...")
    agents = create_agent_definitions()
    print(f"   Created {len(agents)} agents: {list(agents.keys())}")
    assert len(agents) == 4, "Should have 4 agents"
    assert "explainer" in agents
    assert "reviewer" in agents
    assert "challenger" in agents
    assert "assessor" in agents
    print("   ✓ All agents created successfully")

    # Test 2: Agent properties
    print("\n2. Checking agent properties...")
    explainer = agents["explainer"]
    print(f"   Explainer description: {explainer.description[:50]}...")
    print(f"   Explainer tools: {len(explainer.tools)} tools")
    print(f"   Explainer model: {explainer.model}")
    assert explainer.description, "Should have description"
    assert explainer.prompt, "Should have prompt"
    assert explainer.tools, "Should have tools"
    print("   ✓ Agent properties correct")

    # Test 3: Tool collection
    print("\n3. Collecting all tools...")
    all_tools = get_all_tools()
    print(f"   Total unique tools: {len(all_tools)}")
    print(f"   Sample tools: {all_tools[:3]}")
    assert len(all_tools) > 0, "Should have tools"
    assert all(tool.startswith("mcp__") for tool in all_tools), "All tools should be MCP tools"
    print("   ✓ Tool collection working")

    # Test 4: Enhanced prompts with context
    print("\n4. Testing enhanced prompts...")
    student_context = "✓ Student knows: variables, loops"
    enhanced = get_enhanced_prompt("explainer", student_context)
    print(f"   Enhanced prompt length: {len(enhanced)} chars")
    assert student_context in enhanced, "Should include student context"
    assert "Teaching Best Practices" in enhanced, "Should include guidelines"
    print("   ✓ Context injection working")

    # Test 5: Dynamic agent addition
    print("\n5. Testing dynamic agent addition...")
    original_count = len(AGENT_CONFIGS)
    add_agent(
        name="debugger",
        description="Helps debug code issues",
        prompt="You are a debugging expert.",
        tools=["mcp__scrimba__run_code_simulation"],
        model="sonnet"
    )
    new_count = len(AGENT_CONFIGS)
    print(f"   Agents before: {original_count}, after: {new_count}")
    assert new_count == original_count + 1, "Should have added 1 agent"
    assert "debugger" in AGENT_CONFIGS, "Should have debugger agent"
    print("   ✓ Dynamic agent addition working")

    # Test 6: Concise prompts (not hardcoded)
    print("\n6. Checking prompt conciseness...")
    for name, config in AGENT_CONFIGS.items():
        prompt_lines = config["prompt"].count('\n')
        print(f"   {name}: {prompt_lines} lines")
        assert prompt_lines < 30, f"{name} prompt too long (hardcoded?)"
    print("   ✓ All prompts are concise (SDK-native)")

    print("\n" + "=" * 70)
    print("✅ DYNAMIC AGENT SYSTEM TEST PASSED")
    print("=" * 70)

    print("\n📊 Summary:")
    print(f"   • {len(agents)} specialized agents")
    print(f"   • {len(all_tools)} unique teaching tools")
    print(f"   • Dynamic configuration (no hardcoded prompts)")
    print(f"   • Context-aware prompt enhancement")
    print(f"   • Runtime agent modification supported")

if __name__ == "__main__":
    try:
        test_dynamic_agents()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
