"""
SQLite Persistence Layer

Stores student progress with proper schema and constraints.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


DB_PATH = Path(__file__).parent.parent / "student_data.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Student state
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            id TEXT PRIMARY KEY DEFAULT 'default',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_sessions INTEGER DEFAULT 0,
            last_session_at TIMESTAMP
        )
    """)

    # Concept mastery
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mastery (
            student_id TEXT DEFAULT 'default',
            concept TEXT NOT NULL,
            status TEXT DEFAULT 'not_started',
            successes INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            sessions_practiced TEXT DEFAULT '[]',
            last_success_at TIMESTAMP,
            next_review_at TIMESTAMP,
            interval_days REAL DEFAULT 1.0,
            ease_factor REAL DEFAULT 2.5,
            PRIMARY KEY (student_id, concept)
        )
    """)

    # Error history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT DEFAULT 'default',
            concept TEXT NOT NULL,
            error_type TEXT NOT NULL,
            code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Problem history (to avoid repeats)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problem_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT DEFAULT 'default',
            concept TEXT NOT NULL,
            problem_hash TEXT NOT NULL,
            passed BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Current problem context
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS current_problem (
            student_id TEXT PRIMARY KEY DEFAULT 'default',
            concept TEXT,
            prompt TEXT,
            test_cases TEXT,
            attempts INTEGER DEFAULT 0,
            last_hint_level INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Session log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT DEFAULT 'default',
            action TEXT NOT NULL,
            concept TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Student profile (interests, goals, learning preferences)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profile (
            student_id TEXT PRIMARY KEY DEFAULT 'default',
            interests TEXT DEFAULT '[]',
            goals TEXT DEFAULT '',
            background TEXT DEFAULT '',
            preferred_style TEXT DEFAULT 'example_first',
            onboarded BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Learning style tracking (what explanations work)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS explanation_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT DEFAULT 'default',
            concept TEXT NOT NULL,
            style TEXT NOT NULL,
            followed_by_success BOOLEAN,
            attempts_until_success INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Reflections (metacognition)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT DEFAULT 'default',
            concept TEXT NOT NULL,
            problem_id INTEGER,
            strategy_used TEXT,
            confusion_points TEXT,
            confidence_before INTEGER,
            confidence_after INTEGER,
            teach_back TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Identity insights (generated patterns)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS identity_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT DEFAULT 'default',
            insight_type TEXT NOT NULL,
            content TEXT NOT NULL,
            evidence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ensure default student exists
    cursor.execute("""
        INSERT OR IGNORE INTO student (id) VALUES ('default')
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO student_profile (student_id) VALUES ('default')
    """)

    conn.commit()
    conn.close()


# Initialize on import
init_db()


@dataclass
class MasteryState:
    concept: str
    status: str
    successes: int
    attempts: int
    sessions_practiced: List[str]
    next_review_at: Optional[datetime]
    interval_days: float
    ease_factor: float


def get_mastery(concept: str, student_id: str = "default") -> Optional[MasteryState]:
    """Get mastery state for a concept."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM mastery WHERE student_id = ? AND concept = ?
    """, (student_id, concept))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return MasteryState(
        concept=row["concept"],
        status=row["status"],
        successes=row["successes"],
        attempts=row["attempts"],
        sessions_practiced=json.loads(row["sessions_practiced"]),
        next_review_at=datetime.fromisoformat(row["next_review_at"]) if row["next_review_at"] else None,
        interval_days=row["interval_days"],
        ease_factor=row["ease_factor"]
    )


def get_all_mastery(student_id: str = "default") -> Dict[str, MasteryState]:
    """Get all mastery states."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM mastery WHERE student_id = ?
    """, (student_id,))

    results = {}
    for row in cursor.fetchall():
        results[row["concept"]] = MasteryState(
            concept=row["concept"],
            status=row["status"],
            successes=row["successes"],
            attempts=row["attempts"],
            sessions_practiced=json.loads(row["sessions_practiced"]),
            next_review_at=datetime.fromisoformat(row["next_review_at"]) if row["next_review_at"] else None,
            interval_days=row["interval_days"],
            ease_factor=row["ease_factor"]
        )

    conn.close()
    return results


def update_mastery(
    concept: str,
    success: bool,
    student_id: str = "default"
) -> MasteryState:
    """Update mastery after an attempt."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get or create mastery record
    cursor.execute("""
        INSERT OR IGNORE INTO mastery (student_id, concept, status)
        VALUES (?, ?, 'practicing')
    """, (student_id, concept))

    cursor.execute("""
        SELECT * FROM mastery WHERE student_id = ? AND concept = ?
    """, (student_id, concept))
    row = cursor.fetchone()

    # Parse sessions
    sessions = json.loads(row["sessions_practiced"])
    today = datetime.now().strftime("%Y-%m-%d")

    # Add today if not already present
    if today not in sessions:
        sessions.append(today)

    # Update counts
    new_successes = row["successes"] + (1 if success else 0)
    new_attempts = row["attempts"] + 1

    # Determine status
    status = row["status"]
    interval_days = row["interval_days"]
    ease_factor = row["ease_factor"]
    next_review = None

    if success:
        # Check for mastery: 3+ successes, 2+ sessions
        if new_successes >= 3 and len(sessions) >= 2:
            status = "mastered"
            # Set up spaced repetition
            next_review = datetime.now() + timedelta(days=interval_days)
        else:
            status = "practicing"

        # Update spaced repetition (SM-2 algorithm)
        if status == "mastered":
            if interval_days < 1:
                interval_days = 1
            elif interval_days == 1:
                interval_days = 6
            else:
                interval_days *= ease_factor
            ease_factor = max(1.3, ease_factor + 0.1)
    else:
        status = "practicing"
        # Reset on failure if mastered
        if row["status"] == "mastered":
            status = "review_needed"
            interval_days = 1
            ease_factor = max(1.3, ease_factor - 0.2)

    # Update record
    cursor.execute("""
        UPDATE mastery SET
            status = ?,
            successes = ?,
            attempts = ?,
            sessions_practiced = ?,
            last_success_at = ?,
            next_review_at = ?,
            interval_days = ?,
            ease_factor = ?
        WHERE student_id = ? AND concept = ?
    """, (
        status,
        new_successes,
        new_attempts,
        json.dumps(sessions),
        datetime.now().isoformat() if success else row["last_success_at"],
        next_review.isoformat() if next_review else None,
        interval_days,
        ease_factor,
        student_id,
        concept
    ))

    conn.commit()
    conn.close()

    return MasteryState(
        concept=concept,
        status=status,
        successes=new_successes,
        attempts=new_attempts,
        sessions_practiced=sessions,
        next_review_at=next_review,
        interval_days=interval_days,
        ease_factor=ease_factor
    )


def record_error(
    concept: str,
    error_type: str,
    code: str = "",
    student_id: str = "default"
):
    """Record an error for analysis."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO errors (student_id, concept, error_type, code)
        VALUES (?, ?, ?, ?)
    """, (student_id, concept, error_type, code))

    conn.commit()
    conn.close()


def get_error_patterns(student_id: str = "default", limit: int = 10) -> Dict[str, int]:
    """Get most common error types."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT error_type, COUNT(*) as count
        FROM errors
        WHERE student_id = ?
        GROUP BY error_type
        ORDER BY count DESC
        LIMIT ?
    """, (student_id, limit))

    results = {row["error_type"]: row["count"] for row in cursor.fetchall()}
    conn.close()
    return results


def get_concept_errors(concept: str, student_id: str = "default") -> Dict[str, int]:
    """Get errors for a specific concept."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT error_type, COUNT(*) as count
        FROM errors
        WHERE student_id = ? AND concept = ?
        GROUP BY error_type
        ORDER BY count DESC
    """, (student_id, concept))

    results = {row["error_type"]: row["count"] for row in cursor.fetchall()}
    conn.close()
    return results


def save_current_problem(
    concept: str,
    prompt: str,
    test_cases: List[Dict],
    student_id: str = "default"
):
    """Save current problem context."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO current_problem
        (student_id, concept, prompt, test_cases, attempts, last_hint_level, created_at)
        VALUES (?, ?, ?, ?, 0, 0, CURRENT_TIMESTAMP)
    """, (student_id, concept, prompt, json.dumps(test_cases)))

    conn.commit()
    conn.close()


def get_current_problem(student_id: str = "default") -> Optional[Dict]:
    """Get current problem context."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM current_problem WHERE student_id = ?
    """, (student_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "concept": row["concept"],
        "prompt": row["prompt"],
        "test_cases": json.loads(row["test_cases"]),
        "attempts": row["attempts"],
        "last_hint_level": row["last_hint_level"]
    }


def increment_attempts(student_id: str = "default") -> int:
    """Increment attempt counter and return new value."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE current_problem SET attempts = attempts + 1
        WHERE student_id = ?
    """, (student_id,))

    cursor.execute("""
        SELECT attempts FROM current_problem WHERE student_id = ?
    """, (student_id,))

    row = cursor.fetchone()
    conn.commit()
    conn.close()

    return row["attempts"] if row else 0


def update_hint_level(level: int, student_id: str = "default"):
    """Update hint level given."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE current_problem SET last_hint_level = ?
        WHERE student_id = ?
    """, (level, student_id))

    conn.commit()
    conn.close()


def get_due_reviews(student_id: str = "default") -> List[str]:
    """Get concepts due for review."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT concept FROM mastery
        WHERE student_id = ? AND status = 'mastered'
        AND next_review_at <= ?
    """, (student_id, datetime.now().isoformat()))

    results = [row["concept"] for row in cursor.fetchall()]
    conn.close()
    return results


def log_session(
    action: str,
    concept: str = None,
    details: str = None,
    student_id: str = "default"
):
    """Log a session action."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO session_log (student_id, action, concept, details)
        VALUES (?, ?, ?, ?)
    """, (student_id, action, concept, details))

    conn.commit()
    conn.close()


def get_progress_summary(student_id: str = "default") -> Dict[str, Any]:
    """Get overall progress summary."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get mastery counts
    cursor.execute("""
        SELECT status, COUNT(*) as count FROM mastery
        WHERE student_id = ?
        GROUP BY status
    """, (student_id,))

    status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

    # Get total attempts
    cursor.execute("""
        SELECT SUM(attempts) as total FROM mastery WHERE student_id = ?
    """, (student_id,))
    total_attempts = cursor.fetchone()["total"] or 0

    # Get total successes
    cursor.execute("""
        SELECT SUM(successes) as total FROM mastery WHERE student_id = ?
    """, (student_id,))
    total_successes = cursor.fetchone()["total"] or 0

    # Get recent errors
    cursor.execute("""
        SELECT error_type, COUNT(*) as count FROM errors
        WHERE student_id = ?
        GROUP BY error_type
        ORDER BY count DESC
        LIMIT 3
    """, (student_id,))
    top_errors = {row["error_type"]: row["count"] for row in cursor.fetchall()}

    conn.close()

    return {
        "mastered": status_counts.get("mastered", 0),
        "practicing": status_counts.get("practicing", 0),
        "not_started": status_counts.get("not_started", 0),
        "total_attempts": total_attempts,
        "total_successes": total_successes,
        "success_rate": total_successes / total_attempts if total_attempts > 0 else 0,
        "top_errors": top_errors
    }


# ============ PROFILE FUNCTIONS ============

def get_profile(student_id: str = "default") -> Dict[str, Any]:
    """Get student profile."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM student_profile WHERE student_id = ?
    """, (student_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"onboarded": False, "interests": [], "goals": "", "background": "", "preferred_style": "example_first"}

    return {
        "onboarded": bool(row["onboarded"]),
        "interests": json.loads(row["interests"]),
        "goals": row["goals"],
        "background": row["background"],
        "preferred_style": row["preferred_style"]
    }


def save_profile(
    interests: List[str],
    goals: str,
    background: str = "",
    preferred_style: str = "example_first",
    student_id: str = "default"
) -> Dict[str, Any]:
    """Save student profile."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO student_profile
        (student_id, interests, goals, background, preferred_style, onboarded, updated_at)
        VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
    """, (student_id, json.dumps(interests), goals, background, preferred_style))

    conn.commit()
    conn.close()

    return {"success": True, "interests": interests, "goals": goals}


# ============ LEARNING STYLE FUNCTIONS ============

def record_explanation(
    concept: str,
    style: str,
    student_id: str = "default"
) -> int:
    """Record an explanation event. Returns event ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO explanation_events (student_id, concept, style)
        VALUES (?, ?, ?)
    """, (student_id, concept, style))

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return event_id


def update_explanation_outcome(
    event_id: int,
    success: bool,
    attempts: int
):
    """Update explanation event with outcome."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE explanation_events
        SET followed_by_success = ?, attempts_until_success = ?
        WHERE id = ?
    """, (success, attempts, event_id))

    conn.commit()
    conn.close()


def get_effective_styles(student_id: str = "default") -> Dict[str, Dict]:
    """Get learning style effectiveness stats."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT style,
               COUNT(*) as total,
               SUM(CASE WHEN followed_by_success = 1 THEN 1 ELSE 0 END) as successes,
               AVG(attempts_until_success) as avg_attempts
        FROM explanation_events
        WHERE student_id = ? AND followed_by_success IS NOT NULL
        GROUP BY style
    """, (student_id,))

    results = {}
    for row in cursor.fetchall():
        results[row["style"]] = {
            "total": row["total"],
            "successes": row["successes"],
            "success_rate": row["successes"] / row["total"] if row["total"] > 0 else 0,
            "avg_attempts": row["avg_attempts"] or 0
        }

    conn.close()
    return results


def get_best_style(student_id: str = "default") -> str:
    """Get the most effective learning style for this student."""
    styles = get_effective_styles(student_id)

    if not styles:
        return "example_first"  # default

    # Find style with highest success rate (min 3 attempts)
    best_style = "example_first"
    best_rate = 0

    for style, data in styles.items():
        if data["total"] >= 3 and data["success_rate"] > best_rate:
            best_rate = data["success_rate"]
            best_style = style

    return best_style


# ============ REFLECTION FUNCTIONS ============

def save_reflection(
    concept: str,
    strategy_used: str = "",
    confusion_points: str = "",
    confidence_before: int = 5,
    confidence_after: int = 5,
    teach_back: str = "",
    student_id: str = "default"
) -> Dict[str, Any]:
    """Save a reflection after problem attempt."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get current problem id
    cursor.execute("""
        SELECT rowid FROM current_problem WHERE student_id = ?
    """, (student_id,))
    row = cursor.fetchone()
    problem_id = row[0] if row else None

    cursor.execute("""
        INSERT INTO reflections
        (student_id, concept, problem_id, strategy_used, confusion_points,
         confidence_before, confidence_after, teach_back)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, concept, problem_id, strategy_used, confusion_points,
          confidence_before, confidence_after, teach_back))

    conn.commit()
    conn.close()

    return {"success": True, "concept": concept}


def get_reflections(concept: str = None, student_id: str = "default", limit: int = 10) -> List[Dict]:
    """Get recent reflections."""
    conn = get_connection()
    cursor = conn.cursor()

    if concept:
        cursor.execute("""
            SELECT * FROM reflections
            WHERE student_id = ? AND concept = ?
            ORDER BY created_at DESC LIMIT ?
        """, (student_id, concept, limit))
    else:
        cursor.execute("""
            SELECT * FROM reflections
            WHERE student_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (student_id, limit))

    results = []
    for row in cursor.fetchall():
        results.append({
            "concept": row["concept"],
            "strategy_used": row["strategy_used"],
            "confusion_points": row["confusion_points"],
            "confidence_before": row["confidence_before"],
            "confidence_after": row["confidence_after"],
            "teach_back": row["teach_back"],
            "created_at": row["created_at"]
        })

    conn.close()
    return results


# ============ IDENTITY INSIGHT FUNCTIONS ============

def save_identity_insight(
    insight_type: str,
    content: str,
    evidence: Dict = None,
    student_id: str = "default"
):
    """Save an identity insight."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO identity_insights (student_id, insight_type, content, evidence)
        VALUES (?, ?, ?, ?)
    """, (student_id, insight_type, content, json.dumps(evidence or {})))

    conn.commit()
    conn.close()


def get_identity_insights(student_id: str = "default") -> List[Dict]:
    """Get all identity insights."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM identity_insights
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (student_id,))

    results = []
    for row in cursor.fetchall():
        results.append({
            "type": row["insight_type"],
            "content": row["content"],
            "evidence": json.loads(row["evidence"]) if row["evidence"] else {},
            "created_at": row["created_at"]
        })

    conn.close()
    return results


def generate_identity_insights(student_id: str = "default") -> Dict[str, Any]:
    """Analyze learning history and generate identity insights."""
    conn = get_connection()
    cursor = conn.cursor()

    insights = {
        "learning_patterns": [],
        "growth_areas": [],
        "strengths": [],
        "identity_narrative": ""
    }

    # 1. Analyze error evolution
    cursor.execute("""
        SELECT concept, error_type,
               COUNT(*) as count,
               MIN(created_at) as first_error,
               MAX(created_at) as last_error
        FROM errors
        WHERE student_id = ?
        GROUP BY concept, error_type
        ORDER BY count DESC
    """, (student_id,))

    error_data = cursor.fetchall()

    # 2. Analyze mastery progression
    cursor.execute("""
        SELECT concept, successes, attempts, status,
               sessions_practiced
        FROM mastery
        WHERE student_id = ?
    """, (student_id,))

    mastery_data = cursor.fetchall()

    # 3. Analyze reflections for strategies
    cursor.execute("""
        SELECT strategy_used, COUNT(*) as count
        FROM reflections
        WHERE student_id = ? AND strategy_used != ''
        GROUP BY strategy_used
        ORDER BY count DESC
        LIMIT 3
    """, (student_id,))

    strategy_data = cursor.fetchall()

    # 4. Get learning style effectiveness
    styles = get_effective_styles(student_id)

    conn.close()

    # Generate insights

    # Error improvement insight
    total_errors = sum(row["count"] for row in error_data) if error_data else 0
    if total_errors > 0:
        top_error = error_data[0] if error_data else None
        if top_error:
            insights["growth_areas"].append({
                "area": top_error["error_type"],
                "count": top_error["count"],
                "insight": f"Working on {top_error['error_type']} errors in {top_error['concept']}"
            })

    # Mastery insight
    mastered = [row for row in mastery_data if row["status"] == "mastered"]
    if mastered:
        insights["strengths"].append(f"Mastered {len(mastered)} concept(s)")

    # Strategy insight
    if strategy_data:
        top_strategy = strategy_data[0]["strategy_used"]
        insights["learning_patterns"].append(f"Frequently uses: {top_strategy}")

    # Learning style insight
    if styles:
        best = max(styles.items(), key=lambda x: x[1]["success_rate"]) if styles else None
        if best and best[1]["success_rate"] > 0.6:
            insights["learning_patterns"].append(f"Learns best from: {best[0]} ({int(best[1]['success_rate']*100)}% success)")

    # Build narrative
    narrative_parts = []

    if mastered:
        narrative_parts.append(f"You've mastered {len(mastered)} concept(s).")

    if insights["learning_patterns"]:
        narrative_parts.append(" ".join(insights["learning_patterns"]) + ".")

    if insights["growth_areas"]:
        area = insights["growth_areas"][0]
        narrative_parts.append(f"Focus area: {area['area']} - keep practicing!")

    if not narrative_parts:
        narrative_parts.append("Just getting started - every expert was once a beginner!")

    insights["identity_narrative"] = " ".join(narrative_parts)

    return insights


if __name__ == "__main__":
    # Test database
    print("Testing database...")

    # Update mastery
    state = update_mastery("loops", True)
    print(f"After success: {state.successes} successes, status={state.status}")

    state = update_mastery("loops", True)
    print(f"After success: {state.successes} successes, status={state.status}")

    state = update_mastery("loops", True)
    print(f"After success: {state.successes} successes, status={state.status}")

    # Record error
    record_error("loops", "off_by_one", "for i in range(n):")
    errors = get_error_patterns()
    print(f"Errors: {errors}")

    # Progress
    progress = get_progress_summary()
    print(f"Progress: {progress}")

    print("\nDatabase tests complete!")
