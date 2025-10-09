"""Intelligent LLM-Based Agent Router

Uses Claude Haiku to intelligently classify student queries and route to appropriate specialist agent.
"""

import os
import json
import logging
import hashlib
from typing import Tuple, Optional, List, Dict
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class AgentRouter:
    """LLM-powered intelligent agent routing"""

    ROUTING_PROMPT = """You are an intelligent routing system for a teaching platform with 4 specialized agents:

**EXPLAINER Agent** - Use when student wants to:
- Learn a new concept ("explain X", "what is X", "how does X work")
- Understand theory or fundamentals
- Build mental models
- Get examples and demonstrations

**REVIEWER Agent** - Use when student:
- Submits code for review (contains code blocks, functions, classes)
- Asks "is this correct", "check my code", "review this"
- Has errors or bugs to fix
- Wants code improvement suggestions

**CHALLENGER Agent** - Use when student wants:
- Practice problems ("challenge me", "give me a problem")
- Exercises or drills
- Hands-on coding practice
- To test their skills by writing code

**ASSESSOR Agent** - Use when student wants:
- To test understanding ("test me", "quiz me", "am I ready")
- To verify mastery
- To check if they understood correctly
- Gap analysis

Analyze this student query and return ONLY a JSON object:
{
  "agent": "explainer|reviewer|challenger|assessor",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}

Query: """

    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.cache = {}  # Simple in-memory cache
        self.conversation_context = []
        self.last_agent = None

    def route(self, query: str, conversation_history: Optional[List] = None) -> Tuple[str, float]:
        """Route query to appropriate agent using LLM intelligence

        Returns:
            (agent_name, confidence_score)
        """
        # Check cache first (hash the query)
        cache_key = hashlib.md5(query.lower().encode()).hexdigest()
        if cache_key in self.cache:
            logger.info(f"[Router] Cache hit for query")
            return self.cache[cache_key]

        # Build context-aware prompt
        context_info = ""
        if self.last_agent:
            context_info = f"\nContext: Last agent used was {self.last_agent}. "
            if self.last_agent == "explainer":
                context_info += "Student likely wants practice now."
            elif self.last_agent == "challenger":
                context_info += "Student may be submitting solution or asking for help."
            elif self.last_agent == "assessor":
                context_info += "Student may want to learn identified gaps."

        full_prompt = self.ROUTING_PROMPT + f'"{query}"{context_info}'

        try:
            # Use Haiku for fast, cheap routing
            response = self.client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=200,
                temperature=0,  # Deterministic
                messages=[{
                    "role": "user",
                    "content": full_prompt
                }]
            )

            # Parse JSON response
            result_text = response.content[0].text.strip()

            # Extract JSON from response (in case there's extra text)
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result_text = result_text[json_start:json_end]

            result = json.loads(result_text)

            agent = result.get("agent", "explainer")
            confidence = float(result.get("confidence", 0.8))
            reasoning = result.get("reasoning", "")

            logger.info(f"[Router] Selected {agent.upper()} ({confidence:.0%}) - {reasoning}")

            # Update context
            self.last_agent = agent

            # Cache the result
            self.cache[cache_key] = (agent, confidence)

            return agent, confidence

        except Exception as e:
            logger.error(f"[Router] LLM routing failed: {e}, defaulting to explainer")
            # Fallback to explainer on error
            return "explainer", 0.5

    def get_routing_explanation(self, query: str) -> str:
        """Get human-readable routing explanation"""
        agent, confidence = self.route(query)

        explanations = {
            "explainer": "🎓 Routing to EXPLAINER - You're asking to learn a concept",
            "reviewer": "🔍 Routing to CODE REVIEWER - Analyzing your code",
            "challenger": "🎯 Routing to CHALLENGER - Creating practice problem",
            "assessor": "📊 Routing to ASSESSOR - Testing your understanding",
        }

        base_msg = explanations.get(agent, f"Routing to {agent}")
        return f"{base_msg} (confidence: {confidence:.0%})"

    def suggest_next_agent(self, current_agent: str, success: bool) -> str:
        """Suggest next agent based on current interaction outcome"""

        # Optimal learning flow paths
        flow_map = {
            "explainer": {
                True: "challenger",  # Understood → Practice
                False: "explainer",  # Confused → Re-explain differently
            },
            "challenger": {
                True: "assessor",    # Solved → Test deeper understanding
                False: "reviewer",   # Stuck → Get help with code
            },
            "reviewer": {
                True: "challenger",  # Fixed → Try another challenge
                False: "explainer",  # Still confused → Back to fundamentals
            },
            "assessor": {
                True: "challenger",  # Passed → Harder challenges
                False: "explainer",  # Failed → Fill knowledge gaps
            }
        }

        next_agent = flow_map.get(current_agent, {}).get(success, "explainer")
        logger.info(f"[Router] Learning path: {current_agent} ({'✓' if success else '✗'}) → {next_agent}")

        return next_agent

    def route_with_context(
        self,
        query: str,
        student_level: str = "beginner",
        recent_topics: List[str] = None
    ) -> Tuple[str, float]:
        """Advanced routing with student profile context"""

        base_agent, confidence = self.route(query)

        # Beginner students - prioritize explanation and support
        if student_level == "beginner":
            if base_agent == "assessor" and confidence < 0.9:
                logger.info("[Router] Beginner detected - building confidence before assessment")
                return "explainer", 0.7
            elif base_agent == "challenger" and confidence < 0.8:
                logger.info("[Router] Beginner detected - explaining before challenging")
                return "explainer", 0.7

        # Advanced students - skip redundant explanations
        elif student_level == "advanced":
            if base_agent == "explainer" and confidence < 0.8:
                logger.info("[Router] Advanced student - moving to practice")
                return "challenger", 0.7

        return base_agent, confidence


class ContextualRouter(AgentRouter):
    """Extended router with deep conversation awareness"""

    def __init__(self):
        super().__init__()
        self.query_history = []
        self.agent_history = []

    def route_with_history(self, query: str, max_history: int = 5) -> Tuple[str, float]:
        """Route considering conversation flow"""

        # Track query
        self.query_history.append(query)

        # Detect patterns in conversation
        if len(self.agent_history) >= 2:
            last_two = self.agent_history[-2:]

            # Student stuck in explain → explain loop (not learning)
            if last_two == ["explainer", "explainer"]:
                logger.info("[Router] Stuck in explanation loop - pushing to practice")
                agent = "challenger"
                confidence = 0.75
                self.agent_history.append(agent)
                return agent, confidence

            # Student bouncing between challenger and explainer (struggling)
            if set(last_two) == {"challenger", "explainer"}:
                logger.info("[Router] Student struggling - routing to reviewer for help")
                agent = "reviewer"
                confidence = 0.8
                self.agent_history.append(agent)
                return agent, confidence

        # Standard routing
        agent, confidence = self.route(query)
        self.agent_history.append(agent)

        return agent, confidence
