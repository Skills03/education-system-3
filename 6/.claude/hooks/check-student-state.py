#!/usr/bin/env python3
"""
Hook: Checks if student is onboarded and provides context.
Used with UserPromptSubmit to enhance prompts with student state.
"""

import sys
import json
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from core.education_tools import tool_get_student_state

    state = tool_get_student_state()

    # Build context message
    context_parts = []

    if not state['profile']['onboarded']:
        context_parts.append("STUDENT NOT ONBOARDED - Ask about their interests first!")
    else:
        interest = state['profile']['primary_interest']
        context_parts.append(f"Student interest: {interest}")

        if state['learning_style']['best_style'] != 'example_first':
            context_parts.append(f"Best learning style: {state['learning_style']['best_style']}")

        if state['practicing']:
            current = state['practicing'][0]
            context_parts.append(f"Currently practicing: {current['concept']} ({current['successes']}/3)")
            if current.get('most_common_error'):
                context_parts.append(f"Common error: {current['most_common_error']}")

        if state['due_for_review']:
            context_parts.append(f"Due for review: {', '.join(state['due_for_review'])}")

    if context_parts:
        # Output context as JSON for Claude to see
        result = {
            "student_context": " | ".join(context_parts)
        }
        print(json.dumps(result))

except Exception as e:
    # Don't block on errors
    print(json.dumps({"error": str(e)}), file=sys.stderr)

sys.exit(0)
