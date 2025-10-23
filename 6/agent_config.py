"""Dynamic Agent Configuration - SDK-Native Approach

Instead of hardcoding massive prompts, use concise agent definitions
that leverage Claude's natural teaching ability.
"""

from claude_agent_sdk import AgentDefinition
from typing import Dict, List


# Agent configuration - STORY TEACHING + APP BUILDING
AGENT_CONFIGS = {
    "explainer": {
        "description": "Story teacher: analogies, walkthroughs, visuals",
        "prompt": """Story teaching only. Use 3 tools in order, then stop:
1. explain_with_analogy
2. walk_through_concept
3. generate_teaching_scene""",
        "tools": [
            "mcp__story__explain_with_analogy",
            "mcp__story__walk_through_concept",
            "mcp__story__generate_teaching_scene",
        ],
        "model": "sonnet"
    },
    "builder": {
        "description": "App builder: templates, customization, deployment for income",
        "prompt": """You help students build and sell apps to make money.

WORKFLOW:
1. Ask what client needs
2. Show templates with list_app_templates
3. Customize with customize_app_template
4. Generate proposal with generate_client_proposal

FOCUS: Speed to deployment, not perfection. Client-ready apps in 15-30 minutes.

PRICING GUIDANCE:
- Portfolio: $50-150
- Restaurant Menu: $200-500
- Booking System: $300-800
- Invoice Generator: $100-300

Extra features = higher price.

After customizing, always remind student:
1. Test locally
2. Deploy (Vercel/Netlify)
3. Send proposal to client
4. Get paid!""",
        "tools": [
            "mcp__app_builder__list_app_templates",
            "mcp__app_builder__customize_app_template",
            "mcp__app_builder__generate_client_proposal",
        ],
        "model": "sonnet"
    },
}


def create_agent_definitions() -> Dict[str, AgentDefinition]:
    """Create agent definitions from config (SDK-native)"""
    agents = {}

    for agent_name, config in AGENT_CONFIGS.items():
        agents[agent_name] = AgentDefinition(
            description=config["description"],
            prompt=config["prompt"],
            tools=config.get("tools"),
            model=config.get("model", "sonnet")
        )

    return agents


def get_agent_tools(agent_name: str) -> List[str]:
    """Get tools for specific agent"""
    return AGENT_CONFIGS.get(agent_name, {}).get("tools", [])


def add_agent(name: str, description: str, prompt: str, tools: List[str] = None, model: str = "sonnet"):
    """Dynamically add new agent (runtime configuration)"""
    AGENT_CONFIGS[name] = {
        "description": description,
        "prompt": prompt,
        "tools": tools,
        "model": model
    }


def remove_agent(name: str):
    """Remove agent from configuration"""
    if name in AGENT_CONFIGS:
        del AGENT_CONFIGS[name]


def update_agent_prompt(name: str, new_prompt: str):
    """Update agent's system prompt (hot-reload)"""
    if name in AGENT_CONFIGS:
        AGENT_CONFIGS[name]["prompt"] = new_prompt


def get_all_tools() -> List[str]:
    """Get unique set of all tools used by agents"""
    all_tools = set()
    for config in AGENT_CONFIGS.values():
        if config.get("tools"):
            all_tools.update(config["tools"])
    return list(all_tools)


# Teaching guidelines (shared across agents)
TEACHING_GUIDELINES = """
## Story Teaching Philosophy:

Students learn through STORIES, not abstract code. Every teaching session MUST:
1. Start with real-world analogy (arrays = egg cartons, loops = running laps)
2. Build understanding through progressive steps using the analogy
3. Create memorable human-centered visual (person + object + action)

## MANDATORY 3-TOOL SEQUENCE:

1. **explain_with_analogy**: Real-world metaphor students can relate to
2. **walk_through_concept**: Step-by-step exploration using the analogy
3. **generate_teaching_scene**: Person interacting with object, showing action

## Why This Works:

- **Analogies** create mental hooks for abstract concepts
- **Progressive steps** build understanding without overwhelming
- **Human-centered visuals** trigger emotional memory (more memorable than diagrams)

## DEPRECATED APPROACHES (DO NOT USE):

❌ Starting with code syntax
❌ Abstract diagrams without people
❌ Code-first explanations
❌ Generic images without story context

## Adapt to Student Level:

- **Beginner**: Simple analogies (egg cartons, boxes), slow walkthrough
- **Intermediate**: Nuanced analogies, faster pace
- **Advanced**: Complex analogies with edge cases, brief walkthrough

REMEMBER: Story teaching is THE ONLY METHOD. No alternatives."""


def get_enhanced_prompt(agent_name: str, student_knowledge: str = "") -> str:
    """Get agent prompt enhanced with context"""
    base_config = AGENT_CONFIGS.get(agent_name, {})
    base_prompt = base_config.get("prompt", "")

    enhanced = f"""{base_prompt}

{TEACHING_GUIDELINES}

## Current Student Context:
{student_knowledge if student_knowledge else "New student - no prior knowledge"}

Adapt your teaching to their level and build on what they know."""

    return enhanced
