---
description: Show your learning progress, strengths, and identity insights
---

# Progress Flow

## Step 1: Get Progress Data
```bash
python -c "from core.education_tools import tool_get_progress; import json; print(json.dumps(tool_get_progress(), indent=2, default=str))"
```

## Step 2: Get Identity Insights
```bash
python -c "from core.education_tools import tool_get_identity_insights; import json; print(json.dumps(tool_get_identity_insights(), indent=2, default=str))"
```

## Step 3: Format and Display

Show this format:

```
📊 YOUR LEARNING JOURNEY
========================

✅ Mastered: [list mastered concepts]
◐ Practicing: [concept] ([successes]/3 successes)
○ Available: [list available concepts]
🔒 Locked: [concepts needing prerequisites]

🎯 YOUR STRENGTHS
- [Learning style that works: e.g., "Examples work best for you (85% success)"]
- [Strategy patterns: e.g., "You debug systematically"]

📈 YOUR GROWTH
- [Error improvements: e.g., "Off-by-one errors: down 60%"]
- [Speed improvements: e.g., "Average attempts: 5 → 3"]

🧠 YOUR LEARNING IDENTITY
"[Identity narrative from insights]"

🎮 NEXT UNLOCK
[Next concept] → [What it enables]
```

## Key Points
- Celebrate progress, no matter how small
- Highlight their unique learning style
- Show concrete improvements with numbers
- Build their identity as a learner
