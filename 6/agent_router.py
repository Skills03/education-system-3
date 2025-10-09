"""Intelligent Agent Router - Routes queries to specialized teaching agents"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class AgentRouter:
    """Routes student queries to the most appropriate specialist agent"""

    # Keyword patterns for each agent type
    EXPLAINER_PATTERNS = [
        r'\b(what is|what are|explain|how does|how do|teach me|learn|understand)\b',
        r'\b(concept|theory|definition|meaning|purpose)\b',
        r'\b(show me|demonstrate|example of)\b',
        r'\b(why does|why do|reason|because)\b',
    ]

    REVIEWER_PATTERNS = [
        r'\b(check|review|look at|analyze|fix|debug)\b.*\b(my code|this code|my solution)\b',
        r'\b(is this correct|am i right|did i do|does this work)\b',
        r'\b(wrong|error|bug|broken|not working)\b',
        r'\b(improve|better|optimize|refactor)\b.*\b(code|solution)\b',
        r'here is my code|here\'s my code|my code is',
    ]

    CHALLENGER_PATTERNS = [
        r'\b(challenge me|give me|create|practice|exercise|problem|quiz)\b',
        r'\b(try|attempt|solve|work on)\b.*\b(problem|challenge|exercise)\b',
        r'\b(test myself|practice|train|drill)\b',
        r'\b(homework|assignment|task)\b',
    ]

    ASSESSOR_PATTERNS = [
        r'\b(test me|quiz me|assess|evaluate|check if i)\b',
        r'\b(do i understand|am i ready|have i learned)\b',
        r'\b(verify|validate|confirm)\b.*\b(understanding|knowledge)\b',
        r'\b(know|mastered|learned)\b.*\b(enough|correctly|well)\b',
    ]

    # Code submission patterns
    CODE_SUBMISSION_INDICATORS = [
        r'```[\w]*\n',  # Code blocks
        r'\bdef\s+\w+\s*\(',  # Function definitions
        r'\bclass\s+\w+',  # Class definitions
        r'\bfunction\s+\w+\s*\(',  # JS functions
        r'{\s*\n.*:\s*.*\n\s*}',  # Code-like structure
    ]

    def __init__(self):
        self.last_agent = None
        self.conversation_context = []

    def route(self, query: str, conversation_history: list = None) -> Tuple[str, float]:
        """Route query to appropriate agent

        Returns:
            (agent_name, confidence_score)
        """
        query_lower = query.lower()

        # Track conversation for context
        if conversation_history:
            self.conversation_context = conversation_history[-5:]  # Last 5 exchanges

        # 1. Check for code submission (highest priority)
        if self._contains_code(query):
            logger.info(f"[Router] Code detected → CODE_REVIEWER")
            return "reviewer", 0.95

        # 2. Check for explicit routing keywords
        explicit_route = self._check_explicit_routing(query_lower)
        if explicit_route:
            return explicit_route

        # 3. Pattern matching with scoring
        scores = {
            "explainer": self._score_patterns(query_lower, self.EXPLAINER_PATTERNS),
            "reviewer": self._score_patterns(query_lower, self.REVIEWER_PATTERNS),
            "challenger": self._score_patterns(query_lower, self.CHALLENGER_PATTERNS),
            "assessor": self._score_patterns(query_lower, self.ASSESSOR_PATTERNS),
        }

        # 4. Context-based boosting
        if self.last_agent == "explainer":
            # After explanation, likely wants practice
            scores["challenger"] *= 1.3
            scores["assessor"] *= 1.2
        elif self.last_agent == "challenger":
            # After challenge, likely submitting code or asking for help
            scores["reviewer"] *= 1.4
            scores["explainer"] *= 1.2
        elif self.last_agent == "assessor":
            # After assessment, likely wants to learn gaps
            scores["explainer"] *= 1.5

        # 5. Select highest scoring agent
        best_agent = max(scores.items(), key=lambda x: x[1])
        agent_name, confidence = best_agent

        # 6. Default to explainer if no clear winner
        if confidence < 0.3:
            logger.info(f"[Router] Low confidence ({confidence:.2f}) → Default to EXPLAINER")
            agent_name = "explainer"
            confidence = 0.5

        # Track for context
        self.last_agent = agent_name

        logger.info(f"[Router] Selected: {agent_name.upper()} (confidence: {confidence:.2f})")
        logger.debug(f"[Router] All scores: {scores}")

        return agent_name, confidence

    def _contains_code(self, text: str) -> bool:
        """Detect if query contains code"""
        for pattern in self.CODE_SUBMISSION_INDICATORS:
            if re.search(pattern, text):
                return True
        return False

    def _check_explicit_routing(self, query: str) -> Tuple[str, float] | None:
        """Check for explicit agent requests"""

        # Explicit explainer requests
        if any(phrase in query for phrase in ["explain to me", "teach me", "what is", "how does"]):
            if "then quiz me" in query or "then test me" in query:
                return "assessor", 0.9  # Wants assessment after
            return "explainer", 0.9

        # Explicit review requests
        if any(phrase in query for phrase in ["review my code", "check my code", "is my code"]):
            return "reviewer", 0.95

        # Explicit challenge requests
        if any(phrase in query for phrase in ["challenge me", "give me a problem", "practice problem"]):
            return "challenger", 0.95

        # Explicit assessment requests
        if any(phrase in query for phrase in ["test me", "quiz me", "am i ready"]):
            return "assessor", 0.95

        return None

    def _score_patterns(self, text: str, patterns: list) -> float:
        """Score text against pattern list"""
        score = 0.0
        matches = 0

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
                score += 1.0

        # Normalize by number of patterns
        if patterns:
            score = score / len(patterns)

        # Boost if multiple patterns match
        if matches > 1:
            score *= (1 + matches * 0.2)

        return min(score, 1.0)  # Cap at 1.0

    def get_routing_explanation(self, query: str) -> str:
        """Get human-readable routing explanation"""
        agent, confidence = self.route(query)

        explanations = {
            "explainer": "🎓 Routing to EXPLAINER - You're asking to learn a concept",
            "reviewer": "🔍 Routing to CODE REVIEWER - You submitted code for review",
            "challenger": "🎯 Routing to CHALLENGER - You want a practice problem",
            "assessor": "📊 Routing to ASSESSOR - You want to test your understanding",
        }

        base_msg = explanations.get(agent, f"Routing to {agent}")
        return f"{base_msg} (confidence: {confidence:.0%})"


# ============================================================================
# CONTEXTUAL ROUTING STRATEGIES
# ============================================================================

class ContextualRouter(AgentRouter):
    """Extended router with learning path awareness"""

    def __init__(self):
        super().__init__()
        self.student_state = "exploring"  # exploring, practicing, mastering

    def route_with_learning_state(self, query: str, student_level: str = "beginner") -> Tuple[str, float]:
        """Route based on learning state and student level"""

        base_agent, confidence = self.route(query)

        # Beginner students - favor explainer and heavy scaffolding
        if student_level == "beginner":
            if base_agent == "challenger":
                # First explain, then challenge
                logger.info("[Router] Beginner detected - explaining before challenging")
                return "explainer", 0.8
            elif base_agent == "assessor":
                # Too early to assess, build confidence first
                logger.info("[Router] Beginner detected - building foundation before assessment")
                return "explainer", 0.7

        # Advanced students - favor challenges and less explanation
        elif student_level == "advanced":
            if base_agent == "explainer" and confidence < 0.7:
                # Skip explanation, go straight to challenge
                logger.info("[Router] Advanced student - challenging instead of explaining")
                return "challenger", 0.8

        return base_agent, confidence

    def suggest_next_agent(self, current_agent: str, success: bool) -> str:
        """Suggest next agent based on current interaction outcome"""

        flow_map = {
            "explainer": {
                True: "challenger",  # Understood → Practice
                False: "explainer",  # Confused → Re-explain
            },
            "challenger": {
                True: "assessor",    # Solved → Test understanding
                False: "reviewer",   # Stuck → Review and help
            },
            "reviewer": {
                True: "challenger",  # Fixed → Try again
                False: "explainer",  # Still confused → Back to basics
            },
            "assessor": {
                True: "challenger",  # Passed → Harder challenges
                False: "explainer",  # Failed → Fill gaps
            }
        }

        next_agent = flow_map.get(current_agent, {}).get(success, "explainer")
        logger.info(f"[Router] Suggested flow: {current_agent} ({'✓' if success else '✗'}) → {next_agent}")

        return next_agent
