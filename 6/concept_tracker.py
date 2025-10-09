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
        """Extract concept declaration from agent's text

        Expected format:
        "This response teaches 3 concepts: variables, assignment, data types"
        or
        "I'll teach 2 concepts: functions and return values"
        """
        # Pattern: "teach(es/ing) N concept(s): concept1, concept2, ..."
        pattern = r"teach(?:es|ing)?\s+(\d+)\s+concepts?:\s*([^.\n]+)"
        match = re.search(pattern, text.lower())

        if match:
            count = int(match.group(1))
            concepts_text = match.group(2)
            concepts = [c.strip() for c in concepts_text.split(',')]

            logger.info(f"[{self.session_id[:8]}] Declared {count} concepts: {concepts}")
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

        Sequential patterns (good):
        - diagram → code_example (code references diagram concept)
        - code_example → challenge (challenge uses same code pattern)
        - challenge → review (review validates challenge)

        Parallel patterns (bad):
        - diagram → unrelated_diagram (no connection)
        - code_example → unrelated_challenge (no shared context)
        """
        if len(self.tools_used) == 0:
            return True, "First tool - no sequencing to validate"

        last_tool = self.tools_used[-1]

        # Valid sequential patterns
        valid_chains = {
            "generate_concept_diagram": ["show_code_example", "create_interactive_challenge"],
            "generate_data_structure_viz": ["show_code_example", "run_code_simulation"],
            "generate_algorithm_flowchart": ["demonstrate_code", "show_code_example"],
            "show_code_example": ["run_code_simulation", "create_interactive_challenge"],
            "run_code_simulation": ["create_interactive_challenge", "student_challenge"],
            "project_kickoff": ["code_live_increment", "demonstrate_code"],
            "code_live_increment": ["demonstrate_code", "student_challenge"],
            "demonstrate_code": ["student_challenge", "create_interactive_challenge"],
            "student_challenge": ["review_student_work"],
            "create_interactive_challenge": ["review_student_work"],
        }

        # Extract base tool name (remove mcp__ prefix)
        last_base = last_tool["name"].split("__")[-1]
        current_base = tool_name.split("__")[-1]

        # Check if current tool is valid follow-up to last tool
        if last_base in valid_chains:
            allowed_next = valid_chains[last_base]
            if current_base in allowed_next:
                return True, f"Valid sequence: {last_base} → {current_base}"
            else:
                return False, f"Invalid sequence: {last_base} → {current_base}. Expected one of: {allowed_next}"

        # If no chain defined, allow it (new pattern)
        return True, f"No chain rule for {last_base} - allowing {current_base}"

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
        """Validate that agent declared concepts before using tools"""
        concepts = self.tracker.parse_concept_declaration(text)

        if concepts:
            if self.tracker.set_concepts(concepts):
                self.concept_declaration_checked = True
                return True, f"Declared {len(concepts)} concepts (within limit)"
            else:
                return False, f"Too many concepts: {len(concepts)} > {self.tracker.concept_limit}"

        # No declaration found
        if not self.concept_declaration_checked:
            return False, "Must declare concepts before using tools (e.g., 'This response teaches 2 concepts: variables, loops')"

        return True, "Declaration already checked"

    def can_use_tool(self, tool_name: str, input_data: dict, agent_message: str) -> tuple[bool, str]:
        """Main permission check - validates concepts and sequencing"""

        # First tool call triggers concept declaration check
        if len(self.tracker.tools_used) == 0:
            can_use, reason = self.check_concept_declaration(agent_message)
            if not can_use:
                return False, reason

        # Check sequencing (does this tool build on previous?)
        sequencing_valid, sequencing_msg = self.tracker.validate_sequencing(tool_name, input_data)
        if not sequencing_valid:
            return False, f"Sequencing violation: {sequencing_msg}"

        # Record tool usage
        self.tracker.add_tool_usage(tool_name, input_data)

        logger.info(f"[{self.session_id[:8]}] ✓ Tool allowed: {tool_name} ({sequencing_msg})")
        return True, sequencing_msg

    def reset(self):
        """Reset for new request"""
        self.tracker = ConceptTracker(self.session_id)
        self.concept_declaration_checked = False
