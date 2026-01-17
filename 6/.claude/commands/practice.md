---
description: Start a practice session - checks state, generates problem in your interest domain
---

# Practice Flow

Execute these steps IN ORDER:

## Step 1: Get Student State
```bash
python -c "from core.education_tools import tool_get_student_state; import json; print(json.dumps(tool_get_student_state(), indent=2))"
```

## Step 2: Check Onboarding
If `profile.onboarded == false`:
- Ask: "What interests you? (games/music/data/web)"
- Ask: "What's your goal? (build projects/get job/school/exploring)"
- Run: `python -c "from core.education_tools import tool_setup_profile; print(tool_setup_profile(['INTEREST'], 'GOAL'))"`

## Step 3: Determine What to Practice
Priority order:
1. `due_for_review` not empty → Review that concept
2. `practicing` with `success_rate < 0.5` → Target weakness
3. `current_problem` exists → Continue current
4. `available_to_learn` → Start new concept

## Step 4: Get Domain Analogy
```bash
python -c "from core.education_tools import tool_get_analogy; import json; print(json.dumps(tool_get_analogy('CONCEPT', 'INTEREST'), indent=2))"
```

## Step 5: Generate Problem
Create a problem that:
- Is framed in student's interest domain (use analogy.problem_frame)
- Targets their weakness (check error_patterns)
- Has 3-5 test cases including edge cases

## Step 6: Save Problem
```bash
python -c "
from core.education_tools import tool_save_problem
import json
result = tool_save_problem(
    concept='CONCEPT',
    prompt='YOUR GENERATED PROMPT',
    function_name='FUNC_NAME',
    test_cases=[
        {'call': 'func(input)', 'expected': output},
        # ... more test cases
    ]
)
print(json.dumps(result, indent=2))
"
```

## Step 7: Present Problem
Show the problem clearly with examples. Wait for student code.
