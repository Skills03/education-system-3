"""Concept-based Learning Rate Limiter

Limits information density and novelty instead of tool count.
Enforces working memory constraints (3-4 concepts max per response).
"""

import re
import logging
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class ConceptTracker:
    """Tracks concepts being taught in a single request/response cycle"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.declared_concepts: List[str] = []
        self.tools_used: List[Dict] = []
        self.concept_limit = 3  # Working memory constraint
        self.has_declaration = False

    def parse_concept_declaration(self, text: str) -> Optional[List[str]]:
        """Extract concept declaration from agent's text (flexible patterns)

        Accepts multiple formats:
        - "This response teaches 3 concepts: variables, assignment, data types"
        - "I'll teach 2 concepts: functions and return values"
        - "Teaching: variables and loops"
        - "Covering 2 topics: arrays, indexing"
        - "Focus on: async/await"
        """
        # Multiple flexible patterns
        patterns = [
            # Standard: "teaches N concepts: X, Y"
            r"teach(?:es|ing)?\s+(\d+)\s+concepts?:\s*([^.\n]+)",
            # Alternative: "teach/cover/explain: X, Y"
            r"(?:teach|cover|explain)(?:ing)?:\s*([^.\n]+)",
            # Topics: "N topics: X, Y"
            r"(\d+)\s+topics?:\s*([^.\n]+)",
            # Focus: "focus on: X"
            r"focus(?:ing)?\s+on:\s*([^.\n]+)",
            # Will cover: "will cover X and Y"
            r"will\s+(?:teach|cover|explain)\s+([^.\n]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                # Extract concepts from matched text
                if len(match.groups()) == 2:
                    # Has count (e.g., "2 concepts: X, Y")
                    concepts_text = match.group(2)
                else:
                    # No count (e.g., "Teaching: X, Y")
                    concepts_text = match.group(1)

                # Split by commas or "and"
                concepts_text = concepts_text.replace(' and ', ', ')
                concepts = [c.strip() for c in concepts_text.split(',') if c.strip()]

                if concepts:
                    logger.info(f"[{self.session_id[:8]}] Declared {len(concepts)} concepts: {concepts}")
                    return concepts

        return None

    def set_concepts(self, concepts: List[str]) -> bool:
        """Set declared concepts and validate count"""
        self.declared_concepts = concepts
        self.has_declaration = True

        if len(concepts) > self.concept_limit:
            logger.warning(
                f"[{self.session_id[:8]}] Too many concepts: {len(concepts)} > {self.concept_limit}"
            )
            return False

        return True

    def add_tool_usage(self, tool_name: str, input_data: dict):
        """Record tool usage for sequencing validation"""
        self.tools_used.append({
            "name": tool_name,
            "input": input_data,
            "timestamp": datetime.now().isoformat()
        })

    def validate_sequencing(self, tool_name: str, input_data: dict) -> tuple[bool, str]:
        """Check if tool builds on previous tools (sequential learning)

        STORY TEACHING SEQUENCE (MANDATORY):
        1. explain_with_analogy (real-world metaphor)
        2. walk_through_concept (progressive exploration)
        3. generate_teaching_scene (person + object + action visual)

        Non-teaching patterns (for review/assessment):
        - student_challenge → review_student_work
        - create_interactive_challenge → review_student_work
        """
        if len(self.tools_used) == 0:
            return True, "First tool - no sequencing to validate"

        last_tool = self.tools_used[-1]

        # STORY TEACHING SEQUENCE (strict enforcement)
        story_teaching_chain = {
            "explain_with_analogy": ["walk_through_concept"],
            "walk_through_concept": ["generate_teaching_scene"],
            "generate_teaching_scene": [],  # End of sequence
        }

        # Non-teaching chains (assessment/review)
        assessment_chains = {
            "student_challenge": ["review_student_work"],
            "create_interactive_challenge": ["review_student_work"],
            "review_student_work": ["student_challenge", "create_interactive_challenge"],
        }

        # Combine all valid chains
        valid_chains = {**story_teaching_chain, **assessment_chains}

        # Extract base tool name (remove mcp__ prefix)
        last_base = last_tool["name"].split("__")[-1]
        current_base = tool_name.split("__")[-1]

        # STRICT ENFORCEMENT for story teaching tools
        if last_base in story_teaching_chain:
            allowed_next = story_teaching_chain[last_base]
            if not allowed_next:
                # End of sequence reached
                return False, f"Story teaching sequence complete. No more tools allowed after {last_base}."
            if current_base not in allowed_next:
                return False, f"STORY TEACHING VIOLATION: {last_base} → {current_base}. MUST be: {last_base} → {allowed_next[0]}"
            return True, f"✓ Story teaching sequence: {last_base} → {current_base}"

        # Soft check for non-teaching tools
        if last_base in assessment_chains:
            allowed_next = assessment_chains[last_base]
            if current_base in allowed_next:
                return True, f"Valid assessment sequence: {last_base} → {current_base}"
            else:
                # Warn but allow
                return True, f"Non-standard sequence: {last_base} → {current_base} (allowing)"

        # Unknown tool - check if it's a story teaching tool starting sequence
        if current_base == "explain_with_analogy":
            return True, "✓ Starting story teaching sequence with analogy"

        # Default: allow but warn
        return True, f"Unknown pattern: {last_base} → {current_base} (allowing)"

    def get_status(self) -> Dict:
        """Get current tracking status"""
        return {
            "concepts": self.declared_concepts,
            "concept_count": len(self.declared_concepts),
            "concept_limit": self.concept_limit,
            "tools_used": len(self.tools_used),
            "has_declaration": self.has_declaration
        }


class ConceptBasedPermissionSystem:
    """Permission system that enforces concept limits and sequencing"""

    def __init__(self, session_id: str):
        self.tracker = ConceptTracker(session_id)
        self.session_id = session_id
        self.concept_declaration_checked = False

    def check_concept_declaration(self, text: str) -> tuple[bool, str]:
        """Validate concept declaration (optional - graceful fallback)"""
        concepts = self.tracker.parse_concept_declaration(text)

        if concepts:
            if self.tracker.set_concepts(concepts):
                self.concept_declaration_checked = True
                return True, f"Declared {len(concepts)} concepts (within limit)"
            else:
                # Too many concepts - WARN but allow (don't break teaching)
                logger.warning(f"[{self.session_id[:8]}] Too many concepts: {len(concepts)} > {self.tracker.concept_limit} (allowing anyway)")
                self.tracker.set_concepts(concepts[:self.tracker.concept_limit])  # Truncate
                self.concept_declaration_checked = True
                return True, f"Too many concepts declared, using first {self.tracker.concept_limit}"

        # No declaration found - ALLOW with warning (don't block tools)
        if not self.concept_declaration_checked:
            logger.info(f"[{self.session_id[:8]}] No concept declaration found - proceeding anyway (will infer from tools)")
            self.concept_declaration_checked = True
            return True, "No declaration (will infer concepts from teaching)"

        return True, "Declaration already checked"

    def can_use_tool(self, tool_name: str, input_data: dict, agent_message: str) -> tuple[bool, str]:
        """Main permission check - soft concept/sequencing validation (hard limit enforced in server.py)"""

        # NOTE: Hard tool limit (3) is enforced in server.py limit_tools function
        # This function only does soft validation (concepts, sequencing)

        # First tool call triggers concept declaration check (soft)
        if len(self.tracker.tools_used) == 0:
            can_use, reason = self.check_concept_declaration(agent_message)
            # Concept declaration is optional, so can_use should always be True

        # Check sequencing (does this tool build on previous?) - SOFT CHECK
        sequencing_valid, sequencing_msg = self.tracker.validate_sequencing(tool_name, input_data)
        if not sequencing_valid:
            # WARN but ALLOW (sequencing is a guideline, not a hard rule)
            logger.warning(f"[{self.session_id[:8]}] Sequencing warning: {sequencing_msg} (allowing anyway)")

        # Record tool usage
        self.tracker.add_tool_usage(tool_name, input_data)

        logger.info(f"[{self.session_id[:8]}] ✓ Tool allowed (soft check passed): {tool_name}")
        return True, sequencing_msg if sequencing_valid else "Non-sequential but allowed"

    def reset(self):
        """Reset for new request"""
        self.tracker = ConceptTracker(self.session_id)
        self.concept_declaration_checked = False
