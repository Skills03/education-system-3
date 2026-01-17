---
description: Learn a new concept - explains with analogies and gives first problem
allowed-tools: Bash(python:*)
---

# Learn New Concept Flow

Usage: /learn [concept]
Example: /learn loops

## Step 1: Check Prerequisites

```bash
python -c "from core.education_tools import tool_get_concept_guide; import json; print(json.dumps(tool_get_concept_guide('CONCEPT'), indent=2))"
```

If prerequisites not mastered, tell student:
"To learn [concept], you first need to master: [prerequisites]. Want to practice those first?"

## Step 2: Get Student Profile

```bash
python -c "from core.education_tools import tool_get_profile; import json; print(json.dumps(tool_get_profile(), indent=2))"
```

Note their:
- `interests` - Frame explanation in this domain
- `learning_styles.best_style` - Use this explanation approach

## Step 3: Get Domain Analogy

```bash
python -c "from core.education_tools import tool_get_analogy; import json; print(json.dumps(tool_get_analogy('CONCEPT', 'INTEREST'), indent=2))"
```

## Step 4: Explain Using Their Learning Style

**If best_style == "example_first":**
Show code example FIRST, then explain the pattern

**If best_style == "theory_first":**
Explain the concept, then show code

**If best_style == "analogy":**
Start with the analogy from Step 3, then bridge to code

**If best_style == "visual":**
Draw ASCII diagram showing the concept

**If best_style == "socratic":**
Ask guiding questions to help them discover

## Step 5: Record Explanation Style

```bash
python -c "from core.education_tools import tool_record_explanation; print(tool_record_explanation('CONCEPT', 'STYLE_USED'))"
```

## Step 6: Give First Problem

Generate a SIMPLE problem (difficulty 1) in their interest domain.
This should be an easy win to build confidence.

Save with tool_save_problem and present to student.

## Key Teaching Principles
- Start with analogy from their interest domain
- Show ONE simple example first
- Let them try before more explanation
- Celebrate small wins
