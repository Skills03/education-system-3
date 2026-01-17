"""Core education system modules - 10x Version."""

from .sandbox import execute_code, classify_error, ExecutionResult
from .database import (
    init_db,
    get_mastery, get_all_mastery, update_mastery,
    record_error, get_error_patterns, get_concept_errors,
    save_current_problem, get_current_problem,
    increment_attempts, get_due_reviews, get_progress_summary, log_session,
    # New 10x functions
    get_profile, save_profile,
    record_explanation, update_explanation_outcome, get_effective_styles, get_best_style,
    save_reflection, get_reflections,
    save_identity_insight, get_identity_insights, generate_identity_insights
)
from .education_tools import (
    tool_get_student_state,
    tool_save_problem,
    tool_run_code,
    tool_get_concept_guide,
    tool_get_progress,
    tool_record_mastery_event,
    # New 10x tools
    tool_setup_profile,
    tool_get_profile,
    tool_record_explanation,
    tool_record_reflection,
    tool_get_identity_insights,
    tool_get_analogy,
    TOOLS, PREREQUISITES, CONCEPT_INFO, ANALOGIES
)
