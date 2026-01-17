---
description: Record reflection after solving a problem - builds metacognition
---

# Reflection Flow

Use this AFTER a student successfully solves a problem.

## Step 1: Ask Reflection Questions

Ask these questions one at a time:

1. "What strategy helped you solve this?"
   - Examples: "traced through with print", "drew it out", "thought about real-world analogy"

2. "How confident do you feel now? (1-10)"

3. "How would you explain this concept to a friend?"
   - This is "teach-back" - reveals true understanding

## Step 2: Record Reflection

```bash
python -c "
from core.education_tools import tool_record_reflection
import json
result = tool_record_reflection(
    concept='CONCEPT',
    strategy_used='THEIR_STRATEGY',
    confusion_points='WHAT_WAS_CONFUSING',
    confidence_after=THEIR_CONFIDENCE,
    teach_back='THEIR_EXPLANATION'
)
print(json.dumps(result, indent=2))
"
```

## Step 3: Provide Cross-Domain Connection

Show how this concept appears in other domains:

"This [concept] pattern also appears in:
- [Domain 1]: [Example]
- [Domain 2]: [Example]

You just learned [underlying principle] - a universal pattern!"

## Step 4: Identity Insight

Give them an insight about their learning:

Examples:
- "You connected code to real-world scenarios - that's expert thinking!"
- "Your strategy of tracing through step-by-step is exactly how pros debug."
- "You're building pattern recognition - the core skill of programming."

## Step 5: Show Next Step

"Progress: [X]/3 successes on [concept]. [Y] more to master!
Want another problem, or ready to try [next concept]?"
