"""Student Knowledge Tracker - Persistent learning memory via .claude/CLAUDE.md"""

import re
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConceptMastery:
    """Track mastery level of a single concept"""
    concept: str
    level: str  # "mastered", "learning", "weak", "prerequisite"
    attempts: int = 0
    successes: int = 0
    last_reviewed: Optional[str] = None
    notes: str = ""


class StudentKnowledgeTracker:
    """Manages persistent student knowledge in session-scoped files"""

    def __init__(self, session_id: str = None, base_dir: str = "./.claude"):
        """Initialize tracker with session-specific knowledge file

        Args:
            session_id: Unique session identifier for isolated memory
            base_dir: Base directory for .claude files
        """
        self.session_id = session_id
        self.base_dir = base_dir

        # Create session-scoped file path
        if session_id:
            sessions_dir = os.path.join(base_dir, "sessions")
            os.makedirs(sessions_dir, exist_ok=True)
            self.file_path = os.path.join(sessions_dir, f"{session_id}_knowledge.md")
        else:
            # Fallback to global file (for testing/backwards compatibility)
            self.file_path = os.path.join(base_dir, "CLAUDE.md")

        self.mastered: List[str] = []
        self.learning: List[str] = []
        self.weak_areas: List[str] = []
        self.prerequisites: List[str] = []
        self.session_count: int = 0
        self.common_mistakes: List[str] = []
        self.session_log: List[Dict] = []

        # Load existing knowledge
        self.load()

        logger.info(f"[Knowledge] Initialized for session: {session_id or 'global'} -> {self.file_path}")

    def load(self):
        """Load student knowledge from CLAUDE.md"""
        if not os.path.exists(self.file_path):
            logger.warning(f"CLAUDE.md not found at {self.file_path}")
            return

        try:
            with open(self.file_path, 'r') as f:
                content = f.read()

            # Parse Mastered Concepts
            mastered_match = re.search(
                r'### Mastered Concepts \(Confident\)[^\n]*\n<!-- [^>]* -->\n+(.*?)\n+---',
                content, re.DOTALL
            )
            if mastered_match:
                mastered_text = mastered_match.group(1).strip()
                if "*None yet" not in mastered_text and mastered_text:
                    self.mastered = [
                        line.strip('- ').strip()
                        for line in mastered_text.split('\n')
                        if line.strip() and line.strip().startswith('-')
                    ]

            # Parse Learning Concepts
            learning_match = re.search(
                r'### Learning Concepts \(In Progress\)[^\n]*\n<!-- [^>]* -->\n+(.*?)\n+---',
                content, re.DOTALL
            )
            if learning_match:
                learning_text = learning_match.group(1).strip()
                if "*None active" not in learning_text and learning_text:
                    self.learning = [
                        line.strip('- ').strip()
                        for line in learning_text.split('\n')
                        if line.strip() and line.strip().startswith('-')
                    ]

            # Parse Weak Areas
            weak_match = re.search(
                r'### Weak Areas \(Needs Review\)[^\n]*\n<!-- [^>]* -->\n+(.*?)\n+---',
                content, re.DOTALL
            )
            if weak_match:
                weak_text = weak_match.group(1).strip()
                if "*None identified" not in weak_text and weak_text:
                    self.weak_areas = [
                        line.strip('- ').strip()
                        for line in weak_text.split('\n')
                        if line.strip() and line.strip().startswith('-')
                    ]

            # Parse Prerequisites
            prereq_match = re.search(
                r'### Prerequisites Needed[^\n]*\n<!-- [^>]* -->\n+(.*?)\n+---',
                content, re.DOTALL
            )
            if prereq_match:
                prereq_text = prereq_match.group(1).strip()
                if "*None identified" not in prereq_text and prereq_text:
                    self.prerequisites = [
                        line.strip('- ').strip()
                        for line in prereq_text.split('\n')
                        if line.strip() and line.strip().startswith('-')
                    ]

            # Parse Session Count
            session_count_match = re.search(r'\*\*Session Count:\*\* (\d+)', content)
            if session_count_match:
                self.session_count = int(session_count_match.group(1))

            logger.info(f"[Knowledge] Loaded: {len(self.mastered)} mastered, {len(self.learning)} learning, {len(self.weak_areas)} weak")

        except Exception as e:
            logger.error(f"Error loading CLAUDE.md: {e}")

    def add_learning_concept(self, concept: str):
        """Add concept to learning list"""
        if concept not in self.learning and concept not in self.mastered:
            self.learning.append(concept)
            logger.info(f"[Knowledge] Added to learning: {concept}")

    def promote_to_mastered(self, concept: str):
        """Move concept from learning to mastered"""
        if concept in self.learning:
            self.learning.remove(concept)
        if concept not in self.mastered:
            self.mastered.append(concept)
            logger.info(f"[Knowledge] ✓ Mastered: {concept}")

    def add_weak_area(self, concept: str):
        """Mark concept as weak (needs review)"""
        if concept not in self.weak_areas:
            self.weak_areas.append(concept)
        # Remove from mastered if present
        if concept in self.mastered:
            self.mastered.remove(concept)
            logger.info(f"[Knowledge] ⚠️ Demoted to weak: {concept}")

    def add_prerequisite(self, concept: str):
        """Add missing prerequisite"""
        if concept not in self.prerequisites:
            self.prerequisites.append(concept)
            logger.info(f"[Knowledge] Missing prerequisite: {concept}")

    def record_session(self, agent_used: str, concepts_taught: List[str], success: bool):
        """Record a teaching session"""
        self.session_count += 1
        self.session_log.append({
            "session_num": self.session_count,
            "timestamp": datetime.now().isoformat(),
            "agent": agent_used,
            "concepts": concepts_taught,
            "success": success
        })

        # Add concepts to learning
        for concept in concepts_taught:
            self.add_learning_concept(concept)

    def save(self):
        """Save student knowledge back to session-scoped file"""
        try:
            # Build updated content with session metadata
            session_header = f"\n**Session ID:** `{self.session_id}`" if self.session_id else ""

            content = f"""# Student Learning Progress Database

## Purpose
This file tracks persistent student knowledge for this learning session. The agent reads this to understand what the student already knows and updates it after each interaction.{session_header}

---

## Student Knowledge Map

### Mastered Concepts (Confident)
<!-- Concepts the student fully understands and can apply -->

{self._format_list(self.mastered, "None yet - start learning!")}

---

### Learning Concepts (In Progress)
<!-- Concepts currently being taught, partial understanding -->

{self._format_list(self.learning, "None active")}

---

### Weak Areas (Needs Review)
<!-- Concepts student struggled with, needs reinforcement -->

{self._format_list(self.weak_areas, "None identified")}

---

### Prerequisites Needed
<!-- Gaps detected - student needs these before advancing -->

{self._format_list(self.prerequisites, "None identified")}

---

## Learning Velocity & Patterns

**Session Count:** {self.session_count}
**Average Concepts per Session:** {len(self.learning) / max(self.session_count, 1):.1f}
**Learning Style:** {self._infer_learning_style()}

### Common Mistakes
<!-- Track recurring errors to prevent repetition -->

{self._format_list(self.common_mistakes, "None tracked")}

---

### Spaced Repetition Schedule
<!-- Concepts needing periodic review -->

| Concept | Last Reviewed | Next Review | Interval |
|---------|--------------|-------------|----------|
{self._format_spaced_repetition()}

---

## Teaching History

### Session Log
<!-- Chronological record of what was taught -->

{self._format_session_log()}

---

## Agent Instructions

**Read this file before EVERY teaching session to:**
1. Check what student already knows (don't re-explain mastered concepts)
2. Identify prerequisite gaps (teach foundations first)
3. Review weak areas (reinforce before advancing)
4. Adapt teaching style to student's learning patterns

**Update this file after EVERY teaching session:**
1. Move concepts from "Learning" to "Mastered" if validated
2. Add new concepts to "Learning"
3. Record mistakes in "Common Mistakes"
4. Update "Weak Areas" if student struggled
5. Append to "Session Log"

**Memory Persistence Rules:**
- Only mark concepts as "Mastered" after student demonstrates understanding (passed challenge/quiz)
- Concepts remain in "Learning" until validated
- Move to "Weak Areas" after 2+ failed attempts
- Update "Prerequisites Needed" if student lacks foundation
- Track learning velocity to adjust pace

---

## Current Student State

**Overall Progress:** {self._get_progress_level()}
**Last Session:** {self._get_last_session_time()}
**Next Focus:** {self._get_next_focus()}
**Recommended Pace:** {self._get_recommended_pace()}
"""

            # Write to file
            with open(self.file_path, 'w') as f:
                f.write(content)

            logger.info(f"[Knowledge] Saved to {self.file_path}")

        except Exception as e:
            logger.error(f"Error saving CLAUDE.md: {e}")

    def _format_list(self, items: List[str], empty_msg: str) -> str:
        """Format list items as markdown"""
        if not items:
            return f"*{empty_msg}*"
        return "\n".join(f"- {item}" for item in items)

    def _format_session_log(self) -> str:
        """Format session log"""
        if not self.session_log:
            return "*No sessions yet*"

        lines = []
        for session in self.session_log[-10:]:  # Last 10 sessions
            timestamp = datetime.fromisoformat(session['timestamp']).strftime("%Y-%m-%d %H:%M")
            concepts = ", ".join(session['concepts'])
            status = "✓" if session.get('success', True) else "⚠️"
            lines.append(f"**Session {session['session_num']}** ({timestamp}) - {session['agent']} - {status} {concepts}")

        return "\n".join(lines)

    def _format_spaced_repetition(self) -> str:
        """Format spaced repetition table"""
        if not self.mastered:
            return "| *None*  | -            | -           | -        |"

        lines = []
        for concept in self.mastered[:5]:  # Top 5 for review
            last_review = "Recent"
            next_review = "1 week"
            interval = "7 days"
            lines.append(f"| {concept} | {last_review} | {next_review} | {interval} |")

        return "\n".join(lines) if lines else "| *None*  | -            | -           | -        |"

    def _infer_learning_style(self) -> str:
        """Infer learning style from patterns"""
        if self.session_count == 0:
            return "*Not yet determined*"
        elif self.session_count < 3:
            return "*Still observing...*"
        else:
            return "Visual + hands-on (uses code examples and diagrams)"

    def _get_progress_level(self) -> str:
        """Determine overall progress level"""
        total_concepts = len(self.mastered) + len(self.learning)
        if total_concepts == 0:
            return "Beginner"
        elif len(self.mastered) < 5:
            return "Beginner"
        elif len(self.mastered) < 15:
            return "Intermediate"
        else:
            return "Advanced"

    def _get_last_session_time(self) -> str:
        """Get last session timestamp"""
        if not self.session_log:
            return "Never"
        last = self.session_log[-1]['timestamp']
        return datetime.fromisoformat(last).strftime("%Y-%m-%d %H:%M")

    def _get_next_focus(self) -> str:
        """Recommend next learning focus"""
        if self.prerequisites:
            return f"Prerequisites: {', '.join(self.prerequisites[:3])}"
        elif self.weak_areas:
            return f"Review: {', '.join(self.weak_areas[:3])}"
        elif self.learning:
            return f"Continue: {', '.join(self.learning[:3])}"
        else:
            return "Foundational concepts"

    def _get_recommended_pace(self) -> str:
        """Recommend teaching pace"""
        if len(self.weak_areas) > 3:
            return "Slow down - reinforce fundamentals"
        elif len(self.mastered) > 10:
            return "Can accelerate - student is progressing well"
        else:
            return "Start slow, validate understanding frequently"

    def get_context_summary(self) -> str:
        """Get summary for agent context"""
        summary = []

        if self.mastered:
            summary.append(f"✓ Student knows: {', '.join(self.mastered)}")

        if self.learning:
            summary.append(f"📚 Currently learning: {', '.join(self.learning)}")

        if self.weak_areas:
            summary.append(f"⚠️ Weak areas: {', '.join(self.weak_areas)}")

        if self.prerequisites:
            summary.append(f"🚫 Missing prerequisites: {', '.join(self.prerequisites)}")

        return " | ".join(summary) if summary else "New student - no prior knowledge tracked"
