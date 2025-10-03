# 🎓 Unified Learning Server

## Overview

**Single server, ONE port (5000), THREE teaching modes, 13 tools, 3 agents.**

Complete multi-modal learning platform combining concept teaching, project building, and visual learning on a unified server architecture.

## Architecture

```
/6/
├── server.py              # Unified server on port 5000
├── tools/
│   ├── concept_tools.py   # 4 concept teaching tools
│   ├── project_tools.py   # 5 live coding tools
│   └── visual_tools.py    # 4 AI image generation tools
└── agents/
    ├── concept_agent.py   # Scrimba-style concept teacher
    ├── project_agent.py   # Live coding project builder
    └── visual_agent.py    # Visual diagram teacher
```

## Three Teaching Modes

### 1. Concept Mode
**Tools:** 4 concept teaching tools
- `show_code_example` - Display formatted code with explanations
- `run_code_simulation` - Show code execution and output
- `show_concept_progression` - Basic → Advanced evolution
- `create_interactive_challenge` - Practice problems

**Usage:**
```bash
POST /api/session/start {"mode": "concept"}
POST /api/teach {"session_id": "...", "message": "Teach me list comprehensions"}
```

### 2. Project Mode
**Tools:** 5 live coding tools
- `project_kickoff` - Initialize project
- `code_live_increment` - Add code piece-by-piece
- `demonstrate_code` - Run and show results
- `student_challenge` - Challenge student to code
- `review_student_work` - Review code submissions

**Usage:**
```bash
POST /api/session/start {"mode": "project"}
POST /api/teach {"session_id": "...", "message": "Build a calculator with me"}
```

### 3. Visual Mode
**Tools:** 4 AI image generation tools
- `generate_concept_diagram` - Visualize programming concepts
- `generate_data_structure_viz` - Data structure diagrams
- `generate_algorithm_flowchart` - Algorithm flowcharts
- `generate_architecture_diagram` - System architecture diagrams

**Usage:**
```bash
POST /api/session/start {"mode": "visual"}
POST /api/teach {"session_id": "...", "message": "Show me a binary search tree"}
```

## API Endpoints

### `POST /api/session/start`
Create new session with specified mode.

**Request:**
```json
{"mode": "concept"}  // or "project" or "visual"
```

**Response:**
```json
{
  "session_id": "uuid",
  "mode": "concept",
  "status": "ready"
}
```

### `POST /api/teach`
Send teaching request.

**Request:**
```json
{
  "session_id": "uuid",
  "message": "Your question or request"
}
```

**Response:**
```json
{"status": "processing"}
```

### `GET /api/stream/{session_id}`
Server-Sent Events stream for real-time messages.

**Event types:**
- `teacher` - Teacher response
- `action` - Tool being called
- `output` - Tool output
- `cost` - Session cost
- `complete` - Session finished
- `error` - Error occurred
- `heartbeat` - Keep-alive

## How It Works

### Single ClaudeAgentOptions

```python
ClaudeAgentOptions(
    agents={
        "concept": CONCEPT_AGENT,
        "project": PROJECT_AGENT,
        "visual": VISUAL_AGENT,
    },
    mcp_servers={
        "scrimba": scrimba_tools,
        "live_coding": live_coding_tools,
        "visual": visual_tools,
    },
    allowed_tools=[
        # All 13 tools listed
    ],
)
```

### Mode Selection

Session class uses agent based on mode:
```python
await client.query(f"Use the {self.mode} agent: {instruction}")
```

## Test Results

### ✅ Concept Mode
- **Request:** "Teach me Python list comprehensions"
- **Tools called:** 4+ concept tools
- **Messages:** 22
- **Status:** ✅ Complete

### ✅ Project Mode
- **Request:** "Build a simple calculator with me"
- **Tools called:** 5 project tools
- **Messages:** 18
- **Status:** ✅ Complete

### ✅ Visual Mode
- **Request:** "Show me a binary search tree visualization"
- **Tools called:** `generate_data_structure_viz`
- **Image:** Generated via FAL AI
- **Messages:** 6
- **Status:** ✅ Complete

## Running the Server

```bash
cd /home/mahadev/Desktop/dev/education/6
python3 server.py
```

**Server starts on:** `http://localhost:5000`

**Output:**
```
🎓 UNIFIED LEARNING SERVER
======================================================================

📱 Server: http://localhost:5000

🎯 Three Teaching Modes:
  1. Concept Teaching  - Interactive code examples & simulations
  2. Project Building  - Live coding Scrimba-style
  3. Visual Learning   - AI-generated diagrams

📊 Total: 13 tools, 3 agents, 1 server
```

## Benefits

### ✅ Unified Architecture
- **One port** - Easy to manage and deploy
- **One server** - Single point of entry
- **One codebase** - Modular and maintainable

### ✅ Modular Design
- Tools separated by functionality
- Agents defined independently
- Easy to add new modes/tools

### ✅ Complete Learning Platform
- **Text-based:** Code examples and simulations
- **Interactive:** Live coding and project building
- **Visual:** AI-generated diagrams

### ✅ Scalable
- Add new teaching modes easily
- Extend existing agents with more tools
- Modify tool behavior independently

## Comparison to Previous Architecture

### Before (Folders 3, 4, 5):
- **3 separate servers** on different ports
- **3 separate sessions** to manage
- **Code duplication** across servers
- **Complex deployment**

### Now (Folder 6):
- **1 unified server** on port 5000
- **1 session** with mode selection
- **Shared infrastructure** (SSE, session management)
- **Simple deployment**

## Environment Requirements

- **FAL_KEY** - Required for visual mode image generation
- **Python 3.12+**
- **Dependencies:** flask, flask-cors, claude-agent-sdk, fal-client

## Future Enhancements

1. **Mode switching** - Change mode within same session
2. **Multi-modal** - Use tools from different modes together
3. **Persistence** - Save sessions to database
4. **Authentication** - User accounts and history
5. **Frontend** - Unified UI for all three modes
6. **More modes** - Interview prep, algorithm practice, etc.

## Summary

**Unified Learning Server = Complete Scrimba-style education platform on ONE server.**

- 🎯 3 teaching modes
- 🔧 13 tools total
- 🤖 3 specialized agents
- 🌐 1 unified API
- 🚀 1 port (5000)

**All learning modalities accessible through a single, elegant API.**
