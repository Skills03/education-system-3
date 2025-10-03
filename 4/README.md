# 🚀 Live Coding Teacher - Project-Based Learning

## Overview

Scrimba-style interactive teacher that **builds projects WITH students** in real-time. No predefined templates - fully dynamic project creation based on student requests.

## Architecture

### **5 Core Tools**

1. **`project_kickoff`** - Initialize any project dynamically
   - Input: Project description (free text)
   - Output: Project overview + starting structure

2. **`code_live_increment`** - Add code piece by piece with explanations
   - Shows incremental code additions (not full solutions)
   - Inline explanations for each part
   - Simulates "typing live"

3. **`demonstrate_code`** - Run and show code execution
   - Shows current code state
   - Displays example usage
   - Shows expected output

4. **`student_challenge`** - Challenge student to code
   - Assigns specific task
   - Provides function signature/structure
   - Gives contextual hints

5. **`review_student_work`** - Review submitted code
   - Analyzes correctness
   - Provides constructive feedback
   - Decides next action (continue/debug/retry)

### **Agent Behavior**

**Teaching Flow:**
```
Student: "Let's build a todo app"
    ↓
Agent: [calls project_kickoff]
    → Shows project overview
    ↓
Agent: "Let's start with the Todo class..."
Agent: [calls code_live_increment]
    → Shows class definition with explanation
    ↓
Agent: [calls demonstrate_code]
    → Shows code running with output
    ↓
Agent: [calls code_live_increment]
    → Adds next method
    ↓
Agent: "Now YOUR turn - add delete_todo"
Agent: [calls student_challenge]
    ↓
Student: [submits code]
    ↓
Agent: [calls review_student_work]
    → Gives feedback
    ↓
Continues building together...
```

**Key Principles:**
- ✅ Agent BUILDS projects, not just teaches concepts
- ✅ Incremental code additions (like live coding)
- ✅ Demonstrates execution after each part
- ✅ Student participation through challenges
- ✅ Constructive code reviews
- ✅ Fully dynamic - no predefined templates

## Files

- **`project_server.py`** - Flask server with 5 MCP tools + live coding agent (port 5001)
- **`project.html`** - Interactive frontend with quick-start project ideas

## Usage

### Start Server
```bash
python3 /home/mahadev/Desktop/dev/education/4/project_server.py
```

### Open Browser
```
http://localhost:5001
```

### Example Prompts
- "Let's build a todo app together"
- "Teach me Python classes by building a calculator"
- "Build a weather dashboard with me"
- "Create a contact manager"
- "Let's build a quiz game"

## How It Works

1. **Student requests project** → Agent analyzes and creates dynamic plan
2. **Agent codes live** → Shows incremental additions with explanations
3. **Agent demonstrates** → Runs code and shows output
4. **Student participates** → Gets challenges to code themselves
5. **Agent reviews** → Provides constructive feedback
6. **Repeat** → Continue building together until project complete

## Tested

✅ Server starts successfully on port 5001
✅ Session creation works
✅ `project_kickoff` tool called successfully
✅ Markdown rendering in output
✅ SSE streaming functional
✅ Cost tracking working

**Test Example:**
```
Request: "Let's build a simple calculator together"
Response:
  - Called project_kickoff
  - Generated dynamic project plan
  - Showed starting structure
  - Ready to begin coding
  - Cost: $0.0654
```

## Integration with Main System

- **Port 3000**: Concept teaching (show examples, simulations)
- **Port 5001**: Project building (live coding, real projects)

Both systems use same MCP + Agent architecture but different teaching approaches.
