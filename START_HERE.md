# 🎓 Scrimba-Style Teacher - Quick Start

## The Problem You Had:
❌ Running HTML from `file://` URL caused CORS issues
❌ EventSource couldn't connect to localhost:5000

## The Fix (Following Progressive Enhancement):
✅ Serve HTML from the SAME Flask server
✅ No CORS issues - same origin
✅ Simple, works immediately

---

## Run It:

```bash
# 1. Start server (serves both API and HTML)
python3 teacher_server.py

# 2. Open browser to:
http://localhost:5000

# 3. Done! No build process, no CORS issues
```

---

## How It Works:

```
Browser → http://localhost:5000
          ↓
          Flask Server
          ├── GET / → Serves teacher.html
          ├── POST /api/session/start → Creates session
          ├── POST /api/teach → Sends to agent
          └── GET /api/stream/<id> → SSE responses
```

**Same origin = No CORS = Works perfectly**

---

## What Teacher Does Now:

✅ Shows code **inline** with markdown blocks
✅ No file creation (cleaner, faster)
✅ Real-time streaming responses
✅ Full debugging (terminal + browser console)

Example response:
```
Let me teach you Python decorators!

First, understand functions as objects:

```python
def greet(name):
    return f"Hello, {name}!"

my_func = greet  # Assign to variable
print(my_func("Alice"))  # Output: Hello, Alice!
```

Now let's create a decorator...
```

---

## Debug If Issues:

**Check terminal for:**
- ✓ Session connected
- ✓ Messages queued
- ✓ Queue size growing

**Check browser console (F12) for:**
- ✅ SSE Connected
- 📨 Received message
- ➕ Adding message to UI

**Still stuck? Use debug endpoint:**
```bash
curl http://localhost:5000/api/debug/<session-id>
```

---

## Following the Methodology:

✓ No build process
✓ Single server, simple setup
✓ Works on day 1
✓ Fast feedback loop
✓ Progressive enhancement (added serving HTML without changing anything else)
