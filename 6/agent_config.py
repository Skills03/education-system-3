"""Dynamic Agent Configuration - SDK-Native Approach

Instead of hardcoding massive prompts, use concise agent definitions
that leverage Claude's natural teaching ability.
"""

from claude_agent_sdk import AgentDefinition
from typing import Dict, List


# Agent configuration as data (not hardcoded prompts)
AGENT_CONFIGS = {
    "explainer": {
        "description": "Explains programming concepts clearly with examples and visuals",
        "prompt": """You are an expert programming teacher. Your role:

- Explain concepts clearly using analogies and examples
- Use visual tools (diagrams, videos) for abstract ideas
- Provide code examples for concrete understanding
- Keep explanations focused (max 3 concepts per response)
- Build on what student already knows

Available tools: visual diagrams, educational videos, code animations, code examples, simulations, concept progression.""",
        "tools": [
            "mcp__visual__generate_concept_diagram",
            "mcp__visual__generate_data_structure_viz",
            "mcp__visual__generate_algorithm_flowchart",
            "mcp__video__generate_educational_video",
            "mcp__video__generate_code_animation",
            "mcp__video__generate_concept_demo_video",
            "mcp__scrimba__show_code_example",
            "mcp__scrimba__run_code_simulation",
            "mcp__scrimba__show_concept_progression",
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

Available tools: execute code, show examples, demonstrate bugs.""",
        "tools": [
            "mcp__live_coding__review_student_work",
            "mcp__scrimba__show_code_example",
            "mcp__scrimba__run_code_simulation",
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
## Teaching Best Practices:

1. **Cognitive Load**: Max 3 new concepts per response
2. **Sequential Building**: Each tool should reference previous
3. **Concrete Examples**: Abstract → Visual → Code → Practice
4. **Student Context**: Check what they already know
5. **Progressive Difficulty**: Start simple, build complexity

## Tool Usage Patterns:

- **Explain concept**: diagram/video → code example
- **Show algorithm**: flowchart/animation → code example → simulation
- **Practice**: challenge → review submission
- **Debug**: review code → show correct version → explain why
- **Demonstrate flow**: video demo → code example → student practice

## Adapt to Student:

- **Beginner**: More visuals, detailed explanations, guided practice
- **Intermediate**: Less hand-holding, more challenges
- **Advanced**: Minimal explanation, complex problems, edge cases
"""


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
