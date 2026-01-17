"""
Education MCP Tools - 10x Version

Minimal tools that EMPOWER Claude to generate everything dynamically.
Claude generates problems, Claude analyzes errors, Claude adapts.
"""

import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

from .sandbox import execute_code, classify_error, ExecutionResult
from .database import (
    get_mastery, get_all_mastery, update_mastery,
    record_error, get_error_patterns, get_concept_errors,
    save_current_problem, get_current_problem,
    increment_attempts, update_hint_level,
    get_due_reviews, log_session, get_progress_summary,
    # New 10x functions
    get_profile, save_profile,
    record_explanation, update_explanation_outcome, get_effective_styles, get_best_style,
    save_reflection, get_reflections,
    save_identity_insight, get_identity_insights, generate_identity_insights
)


# Prerequisites graph
PREREQUISITES = {
    "variables": [],
    "data_types": ["variables"],
    "operators": ["variables"],
    "conditionals": ["variables", "operators"],
    "loops": ["variables", "conditionals"],
    "functions": ["variables", "loops"],
    "lists": ["variables", "loops"],
    "strings": ["variables", "loops"],
    "dictionaries": ["lists"],
    "file_io": ["strings", "functions"],
    "recursion": ["functions", "conditionals"],
    "list_comprehension": ["lists", "loops", "functions"],
    "classes": ["functions", "dictionaries"],
    "exceptions": ["functions", "conditionals"],
    "decorators": ["functions"],
    "generators": ["functions", "loops"],
}

# Concept metadata for Claude
CONCEPT_INFO = {
    "variables": {
        "description": "Storing and naming data",
        "key_skills": ["assignment", "naming conventions", "types"],
        "common_errors": ["using undefined variables", "overwriting values"],
        "difficulty": 1
    },
    "operators": {
        "description": "Math, comparison, and logical operators",
        "key_skills": ["+, -, *, /, //, %, **", "==, !=, <, >, <=, >=", "and, or, not"],
        "common_errors": ["= vs ==", "integer division", "operator precedence"],
        "difficulty": 1
    },
    "conditionals": {
        "description": "if, elif, else statements",
        "key_skills": ["boolean expressions", "branching logic", "nested conditions"],
        "common_errors": ["missing colon", "wrong indentation", "elif vs else"],
        "difficulty": 2
    },
    "loops": {
        "description": "for and while loops",
        "key_skills": ["range()", "iterating sequences", "break/continue", "loop variables"],
        "common_errors": ["off-by-one", "infinite loops", "wrong range bounds"],
        "difficulty": 3
    },
    "functions": {
        "description": "Defining and calling functions",
        "key_skills": ["def", "parameters", "return values", "scope"],
        "common_errors": ["forgotten return", "wrong argument count", "modifying global"],
        "difficulty": 3
    },
    "lists": {
        "description": "Ordered collections",
        "key_skills": ["indexing", "slicing", "append/extend", "list methods"],
        "common_errors": ["index out of range", "mutating while iterating"],
        "difficulty": 3
    },
    "strings": {
        "description": "Text manipulation",
        "key_skills": ["indexing", "slicing", "methods", "formatting"],
        "common_errors": ["immutability", "index errors"],
        "difficulty": 3
    },
    "dictionaries": {
        "description": "Key-value storage",
        "key_skills": ["keys/values", "get()", "iteration", "nesting"],
        "common_errors": ["KeyError", "unhashable keys"],
        "difficulty": 4
    },
    "recursion": {
        "description": "Functions calling themselves",
        "key_skills": ["base case", "recursive case", "call stack"],
        "common_errors": ["no base case", "wrong recursive call", "stack overflow"],
        "difficulty": 5
    },
    "list_comprehension": {
        "description": "Concise list creation",
        "key_skills": ["[expr for x in iter]", "conditions", "nested"],
        "common_errors": ["syntax", "readability"],
        "difficulty": 4
    },
    "classes": {
        "description": "Object-oriented programming",
        "key_skills": ["__init__", "self", "methods", "attributes"],
        "common_errors": ["forgetting self", "wrong __init__"],
        "difficulty": 5
    },
}

# Cross-domain analogies for each concept
ANALOGIES = {
    "variables": {
        "games": {
            "analogy": "Like the score display - a labeled box that holds your points and updates",
            "problem_frame": "game score tracking",
            "example": "score = 0; score = score + 100"
        },
        "music": {
            "analogy": "Like the tempo marking - a name that holds a number (BPM)",
            "problem_frame": "tempo and beat tracking",
            "example": "tempo = 120; beats = 4"
        },
        "cooking": {
            "analogy": "Like labeled containers in your kitchen - flour jar, sugar jar",
            "problem_frame": "ingredient measurements",
            "example": "flour_cups = 2; sugar_cups = 1"
        },
        "sports": {
            "analogy": "Like a scoreboard - player names with their scores",
            "problem_frame": "player statistics",
            "example": "player_score = 0; player_name = 'Alex'"
        },
        "default": {
            "analogy": "Like a labeled box that stores a value",
            "problem_frame": "basic calculations",
            "example": "x = 5; y = x + 3"
        }
    },
    "loops": {
        "games": {
            "analogy": "Like the game loop - update, render, repeat 60 times per second",
            "problem_frame": "processing game events or enemy lists",
            "example": "for enemy in enemies: total_damage += enemy.attack"
        },
        "music": {
            "analogy": "Like repeating a 4-bar phrase until the chorus ends",
            "problem_frame": "counting beats or processing notes",
            "example": "for bar in song: total_beats += bar.beats"
        },
        "cooking": {
            "analogy": "Like stirring continuously - repeat until done",
            "problem_frame": "processing recipe steps or ingredients",
            "example": "for ingredient in recipe: add_to_bowl(ingredient)"
        },
        "sports": {
            "analogy": "Like running laps - repeat until you've done 10",
            "problem_frame": "calculating totals from player stats",
            "example": "for player in team: total_score += player.points"
        },
        "data": {
            "analogy": "Like processing each row in a spreadsheet",
            "problem_frame": "data aggregation and analysis",
            "example": "for row in dataset: total += row.value"
        },
        "default": {
            "analogy": "Like following a recipe step multiple times",
            "problem_frame": "repetitive calculations",
            "example": "for i in range(5): print(i)"
        }
    },
    "functions": {
        "games": {
            "analogy": "Like a power-up - put in a player, get back a boosted player",
            "problem_frame": "game mechanics (damage calculation, level up)",
            "example": "def apply_powerup(player, boost): return player.strength + boost"
        },
        "music": {
            "analogy": "Like a transpose function - put in a note, get back a shifted note",
            "problem_frame": "music transformations",
            "example": "def transpose(note, steps): return note + steps"
        },
        "cooking": {
            "analogy": "Like a recipe - put in ingredients, get out a dish",
            "problem_frame": "recipe calculations",
            "example": "def make_dough(flour, water): return flour + water"
        },
        "default": {
            "analogy": "Like a vending machine - put in input, get output",
            "problem_frame": "reusable calculations",
            "example": "def double(x): return x * 2"
        }
    },
    "conditionals": {
        "games": {
            "analogy": "Like checking if player has enough coins to buy an item",
            "problem_frame": "game state checks",
            "example": "if coins >= price: buy_item()"
        },
        "music": {
            "analogy": "Like a conductor deciding tempo based on the movement",
            "problem_frame": "dynamic music behavior",
            "example": "if section == 'chorus': tempo = 140"
        },
        "sports": {
            "analogy": "Like a referee checking if a goal is valid",
            "problem_frame": "rule validation",
            "example": "if ball_crossed_line: award_goal()"
        },
        "default": {
            "analogy": "Like a fork in the road - go left or right based on a sign",
            "problem_frame": "decision making",
            "example": "if age >= 18: print('adult')"
        }
    },
    "lists": {
        "games": {
            "analogy": "Like your inventory - a collection of items in slots",
            "problem_frame": "inventory management",
            "example": "inventory = ['sword', 'shield', 'potion']"
        },
        "music": {
            "analogy": "Like a playlist - songs in order",
            "problem_frame": "playlist operations",
            "example": "playlist = ['song1', 'song2', 'song3']"
        },
        "sports": {
            "analogy": "Like a team roster - players in order",
            "problem_frame": "team management",
            "example": "team = ['Alice', 'Bob', 'Charlie']"
        },
        "default": {
            "analogy": "Like numbered lockers in a row",
            "problem_frame": "ordered collections",
            "example": "numbers = [1, 2, 3, 4, 5]"
        }
    },
    "dictionaries": {
        "games": {
            "analogy": "Like a character stats screen - name → value pairs",
            "problem_frame": "game stats and attributes",
            "example": "player = {'health': 100, 'attack': 25, 'defense': 10}"
        },
        "music": {
            "analogy": "Like a chord chart - chord name → notes",
            "problem_frame": "music data lookup",
            "example": "chords = {'C': ['C', 'E', 'G'], 'G': ['G', 'B', 'D']}"
        },
        "default": {
            "analogy": "Like a phone book - name → number",
            "problem_frame": "lookup tables",
            "example": "contacts = {'Alice': '555-1234', 'Bob': '555-5678'}"
        }
    },
    "recursion": {
        "games": {
            "analogy": "Like a fractal level that contains smaller versions of itself",
            "problem_frame": "tree traversal, nested structures",
            "example": "def explore(room): for door in room.doors: explore(door.leads_to)"
        },
        "default": {
            "analogy": "Like Russian nesting dolls - each contains a smaller version",
            "problem_frame": "self-similar problems",
            "example": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
        }
    },
    "classes": {
        "games": {
            "analogy": "Like a character template - defines what every Player can do",
            "problem_frame": "game entities (Player, Enemy, Item)",
            "example": "class Player: def __init__(self, name): self.name = name"
        },
        "default": {
            "analogy": "Like a cookie cutter - a template for making similar things",
            "problem_frame": "object blueprints",
            "example": "class Dog: def __init__(self, name): self.name = name"
        }
    }
}


def tool_get_student_state() -> Dict[str, Any]:
    """
    Get comprehensive student state for Claude to make decisions.

    Returns everything Claude needs to generate appropriate problems:
    - Profile (interests, goals, onboarded status)
    - What's mastered
    - What's being practiced (with success rates)
    - Specific error patterns
    - What's available to learn
    - Learning style effectiveness
    - Recent performance
    """
    all_mastery = get_all_mastery()
    due_reviews = get_due_reviews()
    progress = get_progress_summary()
    profile = get_profile()
    styles = get_effective_styles()
    best_style = get_best_style()

    # Categorize concepts with detail
    mastered = []
    practicing = []

    for concept, m in all_mastery.items():
        if m.status == "mastered":
            mastered.append(concept)
        elif m.status in ["practicing", "review_needed"]:
            # Get error breakdown for this concept
            concept_errors = get_concept_errors(concept)
            success_rate = m.successes / max(m.attempts, 1)

            practicing.append({
                "concept": concept,
                "successes": m.successes,
                "attempts": m.attempts,
                "success_rate": round(success_rate, 2),
                "sessions": len(m.sessions_practiced),
                "needs_for_mastery": {
                    "successes": max(0, 3 - m.successes),
                    "sessions": max(0, 2 - len(m.sessions_practiced))
                },
                "error_patterns": concept_errors,
                "most_common_error": max(concept_errors.items(), key=lambda x: x[1])[0] if concept_errors else None
            })

    # Find available concepts
    available = []
    for concept, prereqs in PREREQUISITES.items():
        if concept not in mastered and concept not in [p["concept"] for p in practicing]:
            missing = [p for p in prereqs if p not in mastered]
            if not missing:
                info = CONCEPT_INFO.get(concept, {})
                available.append({
                    "concept": concept,
                    "description": info.get("description", ""),
                    "difficulty": info.get("difficulty", 3),
                    "key_skills": info.get("key_skills", [])
                })

    # Get current problem if any
    current = get_current_problem()

    return {
        "profile": {
            "onboarded": profile.get("onboarded", False),
            "interests": profile.get("interests", []),
            "goals": profile.get("goals", ""),
            "primary_interest": profile.get("interests", ["default"])[0] if profile.get("interests") else "default"
        },
        "learning_style": {
            "best_style": best_style,
            "effectiveness": styles
        },
        "mastered": mastered,
        "practicing": practicing,
        "available_to_learn": sorted(available, key=lambda x: x["difficulty"]),
        "due_for_review": due_reviews,
        "current_problem": current,
        "overall": {
            "total_attempts": progress["total_attempts"],
            "total_successes": progress["total_successes"],
            "success_rate": round(progress["success_rate"], 2),
            "concepts_mastered": len(mastered),
            "concepts_in_progress": len(practicing)
        },
        "global_error_patterns": get_error_patterns(limit=5),
        "concept_info": CONCEPT_INFO
    }


def tool_save_problem(
    concept: str,
    prompt: str,
    function_name: str,
    test_cases: List[Dict]
) -> Dict[str, Any]:
    """
    Save a generated problem. Claude generates the problem, this stores it.

    Args:
        concept: The concept being tested
        prompt: The problem description Claude generated
        function_name: Name of function student should write
        test_cases: List of {"call": "func(1)", "expected": 2}

    Returns:
        Confirmation with problem ID
    """
    # Validate concept
    if concept not in CONCEPT_INFO and concept not in PREREQUISITES:
        return {"error": f"Unknown concept: {concept}"}

    # Validate test cases
    if not test_cases or len(test_cases) < 2:
        return {"error": "Need at least 2 test cases"}

    for tc in test_cases:
        if "call" not in tc or "expected" not in tc:
            return {"error": "Each test case needs 'call' and 'expected'"}

    # Save
    save_current_problem(concept, prompt, test_cases)
    log_session("problem_generated", concept, f"{function_name}: {prompt[:50]}")

    return {
        "success": True,
        "concept": concept,
        "function_name": function_name,
        "test_count": len(test_cases),
        "message": "Problem saved. Ready for student code."
    }


def tool_run_code(code: str) -> Dict[str, Any]:
    """
    Execute student code against current problem's test cases.

    Returns raw execution results for Claude to analyze and explain.
    Claude should provide intelligent, contextual feedback - not canned hints.

    Args:
        code: Student's Python code

    Returns:
        Detailed execution results
    """
    current = get_current_problem()
    if not current:
        return {"error": "No active problem. Generate one first."}

    concept = current["concept"]
    test_cases = current["test_cases"]
    attempts = increment_attempts()

    # Execute in sandbox
    result = execute_code(code, test_cases)

    # Prepare detailed results for Claude
    if result.security_error:
        return {
            "status": "security_blocked",
            "message": result.security_error,
            "attempts": attempts,
            "code": code
        }

    if result.syntax_error:
        record_error(concept, "syntax_error", code)
        return {
            "status": "syntax_error",
            "error": result.syntax_error,
            "attempts": attempts,
            "code": code
        }

    # Detailed test results
    test_results = []
    for r in result.results:
        test_results.append({
            "call": r.call,
            "expected": r.expected,
            "actual": r.actual,
            "passed": r.passed,
            "error": r.error,
            "stdout": r.stdout if r.stdout else None
        })

    if result.all_passed:
        # Success - update mastery
        mastery = update_mastery(concept, True)
        log_session("problem_solved", concept, f"attempts: {attempts}")

        return {
            "status": "all_passed",
            "test_results": test_results,
            "attempts": attempts,
            "mastery_update": {
                "concept": concept,
                "successes": mastery.successes,
                "sessions": len(mastery.sessions_practiced),
                "status": mastery.status,
                "just_mastered": mastery.status == "mastered" and mastery.successes == 3
            }
        }
    else:
        # Failure - let Claude analyze
        # Do basic classification but let Claude provide real insight
        failed = [r for r in result.results if not r.passed]
        first_fail = failed[0] if failed else None

        error_type, _ = classify_error(
            code,
            first_fail.error if first_fail else "",
            first_fail.expected if first_fail else None,
            first_fail.actual if first_fail else None
        )

        record_error(concept, error_type, code)
        update_mastery(concept, False)

        return {
            "status": "failed",
            "passed_count": result.passed_count,
            "total_count": result.total_count,
            "test_results": test_results,
            "detected_error_type": error_type,
            "attempts": attempts,
            "code": code,
            "concept": concept,
            "student_error_history": get_concept_errors(concept)
        }


def tool_record_mastery_event(
    concept: str,
    event_type: str,
    details: str = ""
) -> Dict[str, Any]:
    """
    Record a learning event. Used for tracking beyond just code submission.

    Args:
        concept: The concept
        event_type: "explained", "practiced", "reviewed", "struggled"
        details: Additional context
    """
    log_session(event_type, concept, details)

    return {
        "recorded": True,
        "concept": concept,
        "event": event_type
    }


def tool_get_concept_guide(concept: str) -> Dict[str, Any]:
    """
    Get teaching guide for a concept. Helps Claude teach effectively.

    Args:
        concept: The concept to teach

    Returns:
        Teaching information
    """
    if concept not in CONCEPT_INFO:
        return {"error": f"Unknown concept: {concept}"}

    info = CONCEPT_INFO[concept]
    prereqs = PREREQUISITES.get(concept, [])

    # Check what's next after this
    unlocks = [c for c, ps in PREREQUISITES.items() if concept in ps]

    return {
        "concept": concept,
        "description": info.get("description"),
        "difficulty": info.get("difficulty"),
        "prerequisites": prereqs,
        "key_skills": info.get("key_skills", []),
        "common_errors": info.get("common_errors", []),
        "unlocks": unlocks,
        "teaching_tips": [
            "Start with real-world analogy",
            "Show ONE simple example first",
            "Let student try before explaining more",
            "Address common errors proactively"
        ]
    }


def tool_get_progress() -> Dict[str, Any]:
    """
    Get detailed progress for display.
    """
    state = tool_get_student_state()

    # Build visual progress
    all_concepts = list(CONCEPT_INFO.keys())

    progress_map = {}
    for c in all_concepts:
        if c in state["mastered"]:
            progress_map[c] = {"status": "mastered", "display": "✓"}
        elif c in [p["concept"] for p in state["practicing"]]:
            prac = next(p for p in state["practicing"] if p["concept"] == c)
            progress_map[c] = {
                "status": "practicing",
                "display": f"{prac['successes']}/3",
                "success_rate": prac["success_rate"]
            }
        else:
            # Check if available
            avail = [a["concept"] for a in state["available_to_learn"]]
            if c in avail:
                progress_map[c] = {"status": "available", "display": "○"}
            else:
                progress_map[c] = {"status": "locked", "display": "🔒"}

    return {
        "progress_map": progress_map,
        "summary": state["overall"],
        "weak_areas": [
            {"concept": p["concept"], "error": p["most_common_error"]}
            for p in state["practicing"]
            if p.get("most_common_error")
        ],
        "recommendations": _get_recommendations(state),
        "due_reviews": state["due_for_review"]
    }


def _get_recommendations(state: Dict) -> List[str]:
    """Generate personalized recommendations."""
    recs = []

    # Due reviews
    if state["due_for_review"]:
        recs.append(f"Review due: {', '.join(state['due_for_review'])}")

    # Struggling concepts
    for p in state["practicing"]:
        if p["success_rate"] < 0.5 and p["attempts"] >= 3:
            recs.append(f"Consider reviewing {p['concept']} fundamentals - {int(p['success_rate']*100)}% success rate")

    # Ready for new
    if not state["practicing"] and state["available_to_learn"]:
        next_concept = state["available_to_learn"][0]["concept"]
        recs.append(f"Ready to learn: {next_concept}")

    # Close to mastery
    for p in state["practicing"]:
        if p["successes"] == 2 and p["needs_for_mastery"]["sessions"] == 0:
            recs.append(f"One more success to master {p['concept']}!")

    return recs


# ============ NEW 10X TOOLS ============

def tool_setup_profile(
    interests: List[str],
    goals: str,
    background: str = ""
) -> Dict[str, Any]:
    """
    Set up student profile with interests and goals.
    Call this on first interaction to personalize the experience.

    Args:
        interests: List like ["games", "music", "data", "web"]
        goals: What they want to achieve ("build games", "get job", etc.)
        background: Optional background info

    Returns:
        Confirmation with profile data
    """
    valid_interests = ["games", "music", "data", "web", "cooking", "sports", "art", "science"]
    filtered = [i for i in interests if i in valid_interests] or ["default"]

    result = save_profile(filtered, goals, background)
    log_session("profile_created", details=f"interests: {filtered}, goals: {goals}")

    return {
        "success": True,
        "profile": {
            "interests": filtered,
            "goals": goals,
            "background": background
        },
        "message": f"Profile set! I'll frame problems around {filtered[0]} to make learning relevant."
    }


def tool_get_profile() -> Dict[str, Any]:
    """
    Get current student profile.

    Returns:
        Profile with interests, goals, learning style effectiveness
    """
    profile = get_profile()
    styles = get_effective_styles()
    best_style = get_best_style()

    return {
        "profile": profile,
        "learning_styles": {
            "effectiveness": styles,
            "best_style": best_style
        },
        "onboarded": profile.get("onboarded", False)
    }


def tool_record_explanation(
    concept: str,
    style: str
) -> Dict[str, Any]:
    """
    Record what explanation style was used.
    Call this after explaining something to track effectiveness.

    Args:
        concept: The concept being explained
        style: One of "example_first", "theory_first", "analogy", "visual", "socratic"

    Returns:
        Event ID for tracking outcome
    """
    valid_styles = ["example_first", "theory_first", "analogy", "visual", "socratic"]
    if style not in valid_styles:
        return {"error": f"Invalid style. Use one of: {valid_styles}"}

    event_id = record_explanation(concept, style)
    log_session("explanation_given", concept, f"style: {style}")

    return {
        "success": True,
        "event_id": event_id,
        "style": style,
        "message": "Tracked. Will measure if this leads to success."
    }


def tool_record_reflection(
    concept: str,
    strategy_used: str = "",
    confusion_points: str = "",
    confidence_after: int = 5,
    teach_back: str = ""
) -> Dict[str, Any]:
    """
    Record student reflection after a problem attempt.
    Builds metacognition and tracks learning strategies.

    Args:
        concept: The concept practiced
        strategy_used: What approach they used ("drew diagram", "traced code", etc.)
        confusion_points: What was confusing
        confidence_after: Self-rated confidence 1-10
        teach_back: How they'd explain the concept to someone else

    Returns:
        Confirmation
    """
    result = save_reflection(
        concept=concept,
        strategy_used=strategy_used,
        confusion_points=confusion_points,
        confidence_after=confidence_after,
        teach_back=teach_back
    )

    log_session("reflection_recorded", concept, f"strategy: {strategy_used}")

    # Generate insight if we have enough data
    reflections = get_reflections(limit=5)
    insight = None
    if len(reflections) >= 3:
        # Look for patterns in strategies
        strategies = [r["strategy_used"] for r in reflections if r["strategy_used"]]
        if strategies:
            from collections import Counter
            common = Counter(strategies).most_common(1)[0]
            if common[1] >= 2:
                insight = f"You often use '{common[0]}' - this is becoming your go-to strategy!"
                save_identity_insight("strategy_pattern", insight, {"strategy": common[0], "count": common[1]})

    return {
        "success": True,
        "concept": concept,
        "insight": insight,
        "message": "Reflection saved. This builds self-awareness about your learning."
    }


def tool_get_identity_insights() -> Dict[str, Any]:
    """
    Get identity insights and progress narrative.
    Shows who the student is becoming as a learner.

    Returns:
        Learning patterns, growth areas, strengths, and narrative
    """
    insights = generate_identity_insights()
    saved_insights = get_identity_insights()

    # Get learning style info
    styles = get_effective_styles()
    best_style = get_best_style()

    # Get recent reflections for context
    reflections = get_reflections(limit=5)
    strategies = [r["strategy_used"] for r in reflections if r["strategy_used"]]

    return {
        "insights": insights,
        "saved_insights": saved_insights[-5:] if saved_insights else [],
        "learning_style": {
            "best": best_style,
            "all": styles
        },
        "recent_strategies": strategies,
        "narrative": insights.get("identity_narrative", "")
    }


def tool_get_analogy(concept: str, domain: str = None) -> Dict[str, Any]:
    """
    Get a cross-domain analogy for a concept.
    Helps connect new concepts to familiar domains.

    Args:
        concept: The concept to explain
        domain: Preferred domain (games, music, cooking, etc.) or None for auto-detect

    Returns:
        Analogy, problem frame, and example for that domain
    """
    if concept not in ANALOGIES:
        return {"error": f"No analogies for concept: {concept}"}

    concept_analogies = ANALOGIES[concept]

    # If no domain specified, try to get from profile
    if not domain:
        profile = get_profile()
        interests = profile.get("interests", [])
        domain = interests[0] if interests else "default"

    # Get analogy for domain, fall back to default
    if domain in concept_analogies:
        analogy_data = concept_analogies[domain]
    else:
        analogy_data = concept_analogies.get("default", {
            "analogy": f"A fundamental programming concept",
            "problem_frame": "general programming",
            "example": ""
        })

    return {
        "concept": concept,
        "domain": domain,
        "analogy": analogy_data.get("analogy", ""),
        "problem_frame": analogy_data.get("problem_frame", ""),
        "example": analogy_data.get("example", ""),
        "message": f"Frame problems around {analogy_data.get('problem_frame', 'this context')} for this student."
    }


# Simplified tool list
TOOLS = {
    "get_student_state": {
        "function": tool_get_student_state,
        "description": "Get comprehensive student state: mastery, errors, what to practice. CALL THIS FIRST.",
    },
    "save_problem": {
        "function": tool_save_problem,
        "description": "Save a problem YOU generated. Include concept, prompt, function_name, and test_cases.",
    },
    "run_code": {
        "function": tool_run_code,
        "description": "Execute student code against current problem. Returns detailed results for you to analyze.",
    },
    "get_concept_guide": {
        "function": tool_get_concept_guide,
        "description": "Get teaching guide for a concept before teaching it.",
    },
    "get_progress": {
        "function": tool_get_progress,
        "description": "Get visual progress report with recommendations.",
    },
    "record_mastery_event": {
        "function": tool_record_mastery_event,
        "description": "Log learning events like explanations or struggles.",
    },
    # New 10x tools
    "setup_profile": {
        "function": tool_setup_profile,
        "description": "Set up student profile with interests and goals. Call on first interaction.",
    },
    "get_profile": {
        "function": tool_get_profile,
        "description": "Get student profile with interests, goals, and learning style effectiveness.",
    },
    "record_explanation": {
        "function": tool_record_explanation,
        "description": "Record what explanation style was used (example_first, theory_first, analogy, visual, socratic).",
    },
    "record_reflection": {
        "function": tool_record_reflection,
        "description": "Record student reflection: strategy used, confusion points, confidence, teach-back.",
    },
    "get_identity_insights": {
        "function": tool_get_identity_insights,
        "description": "Get identity insights: learning patterns, growth areas, strengths, narrative.",
    },
    "get_analogy": {
        "function": tool_get_analogy,
        "description": "Get cross-domain analogy for a concept based on student's interests.",
    },
}
