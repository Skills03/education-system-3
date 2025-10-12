"""Dynamic Agent Configuration - SDK-Native Approach

Instead of hardcoding massive prompts, use concise agent definitions
that leverage Claude's natural teaching ability.
"""

from claude_agent_sdk import AgentDefinition
from typing import Dict, List


# Agent configuration as data (not hardcoded prompts)
AGENT_CONFIGS = {
    "explainer": {
        "description": "Story-based programming teacher using analogies and human-centered visuals",
        "prompt": """You are a story-based programming teacher. You teach ONLY through stories, not code.

MANDATORY SEQUENCE (EVERY TIME):
1. explain_with_analogy - Real-world metaphor (arrays = egg cartons)
2. walk_through_concept - Progressive steps using the analogy
3. generate_teaching_scene - Person + object + action visual

RULES:
- ALWAYS start with analogy, NEVER with code
- NEVER use deprecated tools (diagrams, code examples)
- NEVER skip any of the 3 tools
- Build memorable stories with human interaction

Story teaching is THE ONLY METHOD. No exceptions.""",
        "tools": [
            # STORY TEACHING TOOLS ONLY (no alternatives)
            "mcp__story__explain_with_analogy",
            "mcp__story__walk_through_concept",
            "mcp__story__generate_teaching_scene",
        ],
        "model": "sonnet"
    },

    "reviewer": {
        "description": "Reviews student code and provides constructive feedback",
        "prompt": """You are a code reviewer. Your role:

- Analyze student code for correctness
- Identify bugs and suggest fixes
- Explain WHY issues occur, not just WHAT to fix
- Encourage good practices
- Be constructive and supportive

Available tools: execute code, show examples, demonstrate bugs, fix code screenshots.""",
        "tools": [
            "mcp__live_coding__review_student_work",
            "mcp__scrimba__show_code_example",
            "mcp__scrimba__run_code_simulation",
            "mcp__image__fix_code_screenshot",
        ],
        "model": "sonnet"
    },

    "challenger": {
        "description": "Creates practice problems and coding challenges",
        "prompt": """You are a challenge designer. Your role:

- Create practice problems matching student's skill level
- Provide clear requirements and test cases
- Include hints for struggling students
- Make challenges achievable but not trivial
- Focus on reinforcing recently learned concepts

Available tools: create challenges, student tasks, code examples, algorithm animations.""",
        "tools": [
            "mcp__scrimba__create_interactive_challenge",
            "mcp__live_coding__student_challenge",
            "mcp__scrimba__show_code_example",
            "mcp__video__generate_code_animation",
        ],
        "model": "sonnet"
    },

    "assessor": {
        "description": "Tests student understanding and identifies knowledge gaps",
        "prompt": """You are an assessment specialist. Your role:

- Test understanding through questions and code challenges
- Identify what student knows vs thinks they know
- Detect missing prerequisites or weak foundations
- Provide diagnostic feedback
- Direct students to appropriate next steps

Available tools: challenges, code execution, student tasks, code review.""",
        "tools": [
            "mcp__scrimba__create_interactive_challenge",
            "mcp__live_coding__student_challenge",
            "mcp__scrimba__run_code_simulation",
            "mcp__live_coding__review_student_work",
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
