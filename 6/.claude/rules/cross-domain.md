# Cross-Domain Connections

Use analogies to connect programming concepts to student's interests.

## Getting Student's Domain

```bash
python -c "from core.education_tools import tool_get_profile; p=tool_get_profile(); print(p['profile']['interests'])"
```

## Domain Analogies

### Variables

| Domain | Analogy |
|--------|---------|
| Games | Score display - labeled box holding points that updates |
| Music | Tempo marking - a name holding BPM value |
| Data | Spreadsheet cell - labeled location with a value |
| Cooking | Labeled containers - flour jar, sugar jar |

### Loops

| Domain | Analogy |
|--------|---------|
| Games | Game loop - update, render, repeat 60x/second |
| Music | Playlist on repeat - same action for each song |
| Data | Processing each row in a spreadsheet |
| Cooking | Stirring continuously until done |

### Functions

| Domain | Analogy |
|--------|---------|
| Games | Power-up - input player, output boosted player |
| Music | Transpose - input note, output shifted note |
| Data | Formula - input values, output calculation |
| Cooking | Recipe - input ingredients, output dish |

### Lists

| Domain | Analogy |
|--------|---------|
| Games | Inventory - collection of items in slots |
| Music | Playlist - songs in order |
| Data | Column of values in a spreadsheet |
| Cooking | Shopping list - ingredients in order |

### Conditionals

| Domain | Analogy |
|--------|---------|
| Games | "If enough coins, buy item" |
| Music | "If verse, play soft; if chorus, play loud" |
| Data | "If value > threshold, flag it" |
| Cooking | "If sauce thick enough, stop stirring" |

### Dictionaries

| Domain | Analogy |
|--------|---------|
| Games | Character stats screen - name → value pairs |
| Music | Chord chart - chord name → notes |
| Data | Lookup table - key → value |
| Cooking | Recipe book - dish name → instructions |

## How to Use

1. Get student's interest
2. Get analogy: `tool_get_analogy(concept, interest)`
3. Start explanation with analogy
4. Bridge to code
5. After mastery, show connections to OTHER domains:

"This loop pattern also appears in:
- Music: repeating bars in a song
- Games: processing each enemy in a list
- Data: iterating through dataset rows

You just learned **iteration** - a universal programming pattern!"

## Universal Patterns to Highlight

| Concept | Universal Pattern |
|---------|-------------------|
| Variables | Storage and state |
| Loops | Iteration and repetition |
| Functions | Abstraction and reuse |
| Conditionals | Decision making |
| Lists | Ordered collections |
| Dictionaries | Key-value mapping |

These patterns appear EVERYWHERE in computing and beyond.
