---
description: Run student code against test cases and provide feedback
---

# Run Code Flow

When student submits code, execute this flow.

## Step 1: Run the Code

```bash
python -c "
from core.education_tools import tool_run_code
import json
code = '''
STUDENT_CODE_HERE
'''
result = tool_run_code(code)
print(json.dumps(result, indent=2, default=str))
"
```

## Step 2: Handle Results

### If SUCCESS (status == "all_passed"):

1. Celebrate: "Nice! All tests passed!"

2. Check mastery update:
   - If `just_mastered == true`: "🎉 You've MASTERED [concept]!"
   - Otherwise: "Progress: [successes]/3 successes on [concept]"

3. Trigger reflection flow:
   - Ask: "What strategy helped you solve this?"
   - Record with tool_record_reflection

4. Show cross-domain connection

5. Offer next step: "Want another problem or ready for something new?"

### If FAILURE (status == "failed"):

1. Analyze the failure:
   - Which test failed first?
   - What was expected vs actual?
   - What error_type was detected?

2. Get their learning style and give feedback accordingly:

   **example_first:** Show what the correct output looks like for that input

   **theory_first:** Explain why their logic is wrong conceptually

   **visual:** Draw/trace through their code step by step

   **socratic:** Ask "What do you think happens when input is X?"

3. Record explanation style:
   ```bash
   python -c "from core.education_tools import tool_record_explanation; print(tool_record_explanation('CONCEPT', 'STYLE'))"
   ```

4. If attempts >= 3, ask: "What's confusing about this?" to understand their mental model

5. Give progressive hints:
   - Attempt 1-2: Point to the area of the bug
   - Attempt 3-4: Explain the concept they're missing
   - Attempt 5+: Show a similar working example

## Feedback Guidelines

**DON'T say:** "Check your loop boundaries"

**DO say:** "Your code returned 10 but should return 15. You're summing 1 to 4 instead of 1 to 5. `range(5)` gives `[0,1,2,3,4]` - try `range(1, n+1)` to include n."

Be SPECIFIC:
- Point to the exact issue
- Show what their code produces
- Explain WHY that's wrong
- Hint at the fix without giving the answer
