"""Intelligent Agent Router - Uses SDK client and heuristics

Routes student queries to specialized teaching agents using:
1. Code detection (reviewer)
2. Intent keywords (assessor, challenger)
3. Context awareness (conversation flow)
4. Smart defaults (explainer)
"""

import logging
import re
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)


class AgentRouter:
    """Intelligent agent routing using heuristics + context"""

    def __init__(self):
        self.last_agent = None
        self.query_history = []
        self.agent_history = []

    def route(self, query: str, conversation_history: Optional[List] = None) -> Tuple[str, float]:
        """Route query to appropriate agent

        Returns:
            (agent_name, confidence_score)
        """
        # Handle None or empty query
        if not query:
            logger.warning("[Router] Empty query → defaulting to EXPLAINER")
            return "explainer", 0.50

        query_lower = query.lower()

        # 1. CODE DETECTION (highest priority) - student submitting code
        if self._contains_code(query):
            logger.info(f"[Router] Code detected → REVIEWER")
            return "reviewer", 0.95

        # 2. ASSESSMENT REQUEST - explicit testing
        if self._is_assessment_request(query_lower):
            logger.info(f"[Router] Assessment request → ASSESSOR")
            return "assessor", 0.90

        # 3. CHALLENGE REQUEST - wants practice
        if self._is_challenge_request(query_lower):
            logger.info(f"[Router] Challenge request → CHALLENGER")
            return "challenger", 0.90

        # 4. EXPLANATION REQUEST - learning new concept
        if self._is_explanation_request(query_lower):
            logger.info(f"[Router] Explanation request → EXPLAINER")
            return "explainer", 0.85

        # 5. CONTEXT-BASED ROUTING - consider conversation flow
        if self.last_agent:
            contextual_agent = self._route_by_context(query_lower)
            if contextual_agent:
                logger.info(f"[Router] Context-based → {contextual_agent.upper()}")
                return contextual_agent, 0.75

        # 6. DEFAULT - when in doubt, explain
        logger.info(f"[Router] Default → EXPLAINER")
        return "explainer", 0.70

    def _contains_code(self, text: str) -> bool:
        """Detect if query contains code submission"""
        code_indicators = [
            r'```',  # Code blocks
            r'\bdef\s+\w+\s*\(',  # Python function
            r'\bclass\s+\w+',  # Python class
            r'\bfunction\s+\w+\s*\(',  # JS function
            r'=>\s*{',  # Arrow function
            r';\s*$',  # Ends with semicolon (code)
            r'^\s*#include',  # C/C++ include
            r'^\s*import\s+\w+',  # Python/Java import
        ]

        for pattern in code_indicators:
            if re.search(pattern, text, re.MULTILINE):
                return True

        # Long text with multiple lines and special chars (likely code)
        lines = text.split('\n')
        if len(lines) > 3 and re.search(r'[{}()\[\];]', text):
            return True

        return False

    def _is_assessment_request(self, text: str) -> bool:
        """Detect assessment/testing intent"""
        patterns = [
            r'\b(test me|quiz me|assess|evaluate)\b',
            r'\bam i ready\b',
            r'\bdo i (understand|know|get)\b',
            r'\bhave i (learned|mastered)\b',
            r'\bcheck (my|if i) (understanding|knowledge)\b',
        ]
        return any(re.search(p, text) for p in patterns)

    def _is_challenge_request(self, text: str) -> bool:
        """Detect practice/challenge intent"""
        patterns = [
            r'\b(challenge me|give me.*problem)\b',
            r'\b(practice|exercise|drill)\b',
            r'\b(can i|let me|want to) (try|practice|attempt)\b',
            r'\bneed.*practice\b',
        ]
        return any(re.search(p, text) for p in patterns)

    def _is_explanation_request(self, text: str) -> bool:
        """Detect learning/explanation intent"""
        patterns = [
            r'^(what|how|why|explain|teach|show|tell)',
            r'\b(explain|teach me|show me|learn)\b',
            r'\b(what is|what are|how does|how do)\b',
            r'\bdon\'t understand\b',
            r'\bconfused about\b',
        ]
        return any(re.search(p, text) for p in patterns)

    def _route_by_context(self, query: str) -> Optional[str]:
        """Use conversation context to inform routing"""

        # After explainer, student often wants to practice
        if self.last_agent == "explainer":
            # Generic response after explanation → probably wants practice
            if len(query.split()) < 10 and any(word in query for word in ["ok", "got it", "understand", "thanks"]):
                return "challenger"

        # After challenger, student likely submitting code or asking for help
        elif self.last_agent == "challenger":
            # Confused/stuck → need explanation
            if any(word in query for word in ["help", "stuck", "don't get", "confused", "hint"]):
                return "explainer"
            # Otherwise likely code submission (caught by code detection)

        # After assessor, student wants to learn gaps
        elif self.last_agent == "assessor":
            return "explainer"

        # After reviewer, student trying again
        elif self.last_agent == "reviewer":
            if any(word in query for word in ["fixed", "better", "tried"]):
                return "challenger"

        return None

    def get_routing_explanation(self, query: str) -> str:
        """Get human-readable routing explanation"""
        agent, confidence = self.route(query)

        explanations = {
            "explainer": "🎓 Routing to EXPLAINER - Learning new concept",
            "reviewer": "🔍 Routing to REVIEWER - Analyzing code submission",
            "challenger": "🎯 Routing to CHALLENGER - Creating practice problem",
            "assessor": "📊 Routing to ASSESSOR - Testing understanding",
        }

        base_msg = explanations.get(agent, f"Routing to {agent}")
        return f"{base_msg} (confidence: {confidence:.0%})"

    def suggest_next_agent(self, current_agent: str, success: bool) -> str:
        """Suggest next agent based on learning flow"""

        flow_map = {
            "explainer": {
                True: "challenger",   # Understood → Practice
                False: "explainer",   # Confused → Re-explain
            },
            "challenger": {
                True: "assessor",     # Solved → Test deeper
                False: "reviewer",    # Stuck → Get help
            },
            "reviewer": {
                True: "challenger",   # Fixed → Try more
                False: "explainer",   # Still lost → Fundamentals
            },
            "assessor": {
                True: "challenger",   # Passed → Harder problems
                False: "explainer",   # Failed → Fill gaps
            }
        }

        next_agent = flow_map.get(current_agent, {}).get(success, "explainer")
        logger.info(f"[Router] Suggested path: {current_agent} ({'✓' if success else '✗'}) → {next_agent}")

        self.last_agent = next_agent
        return next_agent

    def update_context(self, agent: str, query: str):
        """Track conversation for context-aware routing"""
        self.last_agent = agent
        self.query_history.append(query)
        self.agent_history.append(agent)

        # Keep last 10 for memory efficiency
        if len(self.query_history) > 10:
            self.query_history = self.query_history[-10:]
            self.agent_history = self.agent_history[-10:]

    def detect_learning_loop(self) -> Optional[str]:
        """Detect if student is stuck in unproductive pattern"""

        if len(self.agent_history) < 3:
            return None

        recent = self.agent_history[-3:]

        # Stuck in explanation loop (not progressing)
        if recent == ["explainer", "explainer", "explainer"]:
            logger.warning("[Router] Stuck in explanation loop - forcing practice")
            return "challenger"

        # Bouncing between challenger and explainer (struggling)
        if set(recent) == {"challenger", "explainer"} and len(set(recent)) == 2:
            logger.warning("[Router] Struggling pattern detected - routing to reviewer")
            return "reviewer"

        return None


class ContextualRouter(AgentRouter):
    """Extended router with student profile awareness"""

    def __init__(self):
        super().__init__()
        self.student_level = "beginner"  # Can be updated based on performance

    def route_with_level(self, query: str, student_level: str = None) -> Tuple[str, float]:
        """Route considering student skill level"""

        if student_level:
            self.student_level = student_level

        agent, confidence = self.route(query)

        # Beginners need more support
        if self.student_level == "beginner":
            if agent == "assessor" and confidence < 0.9:
                logger.info("[Router] Beginner - building confidence first")
                return "explainer", 0.75
            elif agent == "challenger" and confidence < 0.85:
                logger.info("[Router] Beginner - explaining before challenging")
                return "explainer", 0.75

        # Advanced students skip redundant explanations
        elif self.student_level == "advanced":
            if agent == "explainer" and confidence < 0.85:
                logger.info("[Router] Advanced - moving to practice")
                return "challenger", 0.75

        return agent, confidence
