# 🎓 Scrimba-Style Teacher Agent - Web Version

Interactive coding teacher with live code execution and real-time explanations!

## Quick Start

### 1. Install Dependencies

```bash
pip install flask flask-cors claude-agent-sdk
```

### 2. Start the Backend Server

```bash
python3 teacher_server.py
```

You should see:
```
🎓 Teacher API Server starting on http://localhost:5000
```

### 3. Open the Frontend

Open `teacher.html` in your browser:
```bash
# Option 1: Direct file open
open teacher.html  # macOS
xdg-open teacher.html  # Linux
start teacher.html  # Windows

# Option 2: Or just double-click teacher.html
```

## How to Use

1. **Click "Start Session"** - Initializes the teacher agent
2. **Choose a lesson template** from the sidebar, or type your own question
3. **Watch the teacher**:
   - 📝 Creates code files
   - ▶️ Runs the code
   - 🎓 Explains concepts step-by-step
4. **Ask follow-up questions** anytime
5. **Click "End Session"** when done

## Features

✨ **Live Code Execution** - Teacher writes and runs actual code
💬 **Interactive Q&A** - Ask questions, get instant answers
📚 **Lesson Templates** - Pre-built lessons for common topics
🎨 **Beautiful UI** - Scrimba-inspired modern interface
💰 **Cost Tracking** - See API costs per interaction

## Example Prompts

- "Teach me Python list comprehensions with examples"
- "How do decorators work? Show me live code"
- "Build a simple REST API with Flask"
- "Explain async/await with running examples"

## Architecture

```
teacher.html (Frontend)
    ↕ REST API + Server-Sent Events
teacher_server.py (Backend)
    ↕ ClaudeSDKClient
Claude Agent (Teacher)
    ↕ Tools: Read, Write, Edit, Bash
Your Filesystem
```

## API Endpoints

- `POST /api/session/start` - Start teaching session
- `POST /api/teach` - Send learning request
- `GET /api/stream/<session_id>` - SSE stream for responses
- `GET /api/lessons` - Get lesson templates

## Troubleshooting

**CORS errors?**
- Make sure `flask-cors` is installed
- Backend must run on http://localhost:5000

**Permission errors?**
- Teacher has pre-approved tools (already fixed!)

**Streaming not working?**
- Check browser console for errors
- Ensure backend is running

## Files

- `teacher.html` - Standalone HTML frontend
- `teacher_server.py` - Flask backend API
- `scrimba_teacher.py` - CLI version (updated with permissions)
