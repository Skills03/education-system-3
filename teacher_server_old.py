#!/usr/bin/env python3
"""Backend API server for Scrimba Teacher Agent."""

import asyncio
import json
from datetime import datetime
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import uuid
import traceback
import logging
from pathlib import Path

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
    ToolResultBlock,
)

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Teacher Agent
TEACHER_AGENT = AgentDefinition(
    description="Interactive coding teacher",
    prompt="""You are an expert programming instructor like Scrimba.

CRITICAL RULES:
- DO NOT create files or run bash commands
- Show all code examples INLINE in your response
- Use markdown code blocks with syntax highlighting
- Explain concepts directly without file operations

TEACHING STYLE:
1. Show code examples inline with ```python blocks
2. Build incrementally - start simple, add complexity
3. Explain the why - connect to real-world use cases
4. Be enthusiastic and encouraging

PROCESS:
1. Introduce concept clearly
2. Show clean, commented code in markdown
3. Explain output and behavior
4. Point out gotchas and best practices

EXAMPLE FORMAT:
"Let me teach you about Python decorators!

First, understand functions as first-class objects:

```python
def greet(name):
    return f"Hello, {name}!"

# Assign to variable
my_func = greet
print(my_func("Alice"))  # Output: Hello, Alice!
```

Now let's create a simple decorator..."

Always use this inline format - NO file creation!""",
    tools=[],  # No tools needed - just text responses
    model="sonnet",
)

app = Flask(__name__)
CORS(app)

# Store active sessions
sessions = {}
message_queues = {}


class TeacherSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.client = None
        self.messages = []

    async def start(self):
        logger.info(f"Starting session {self.session_id}")
        try:
            options = ClaudeAgentOptions(
                agents={"teacher": TEACHER_AGENT},
                # No tools needed - teacher explains inline
            )
            self.client = ClaudeSDKClient(options=options)
            await self.client.connect()
            logger.info(f"✓ Session {self.session_id} connected successfully")
        except Exception as e:
            logger.error(f"❌ Error starting session: {e}")
            logger.error(traceback.format_exc())
            raise

    async def teach(self, instruction):
        logger.info(f"Teaching: {instruction}")
        try:
            await self.client.query(f"Use the teacher agent: {instruction}")
            logger.info("Query sent, receiving response...")

            message_count = 0
            async for msg in self.client.receive_response():
                message_count += 1
                logger.info(f"Received message #{message_count}, type: {type(msg).__name__}")

                # Format message - now returns a LIST of formatted messages
                formatted_list = self._format_message(msg)
                if formatted_list:
                    for formatted in formatted_list:
                        logger.info(f"✓ Formatted: {formatted['type']} - {formatted['content'][:50]}...")
                        self.messages.append(formatted)
                        if self.session_id in message_queues:
                            message_queues[self.session_id].append(formatted)
                    logger.info(f"✓ Queue size: {len(message_queues[self.session_id])}")
                else:
                    logger.debug(f"Message not formatted (empty/skipped)")

            # Signal completion
            complete_msg = {"type": "complete", "timestamp": datetime.now().isoformat()}
            self.messages.append(complete_msg)
            if self.session_id in message_queues:
                message_queues[self.session_id].append(complete_msg)
            logger.info(f"✓ Teaching complete. Total messages: {message_count}, Queue size: {len(message_queues[self.session_id])}")

        except Exception as e:
            logger.error(f"❌ Error during teaching: {e}")
            logger.error(traceback.format_exc())
            # Send error to frontend
            error_msg = {
                "type": "error",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            if self.session_id in message_queues:
                message_queues[self.session_id].append(error_msg)

    def _format_message(self, msg):
        """Format message - returns LIST of formatted messages (can be empty)"""
        result = []

        if isinstance(msg, AssistantMessage):
            # Collect ALL non-empty text blocks from this message
            for block in msg.content:
                if isinstance(block, TextBlock):
                    # Only send non-empty text
                    if block.text and block.text.strip():
                        result.append({
                            "type": "teacher",
                            "content": block.text,
                            "timestamp": datetime.now().isoformat()
                        })
                elif isinstance(block, ToolUseBlock):
                    result.append({
                        "type": "action",
                        "content": self._format_tool(block),
                        "timestamp": datetime.now().isoformat()
                    })

        elif isinstance(msg, UserMessage):
            for block in msg.content:
                if isinstance(block, ToolResultBlock):
                    if block.content and len(block.content) < 1000:
                        result.append({
                            "type": "output",
                            "content": block.content,
                            "timestamp": datetime.now().isoformat()
                        })

        elif isinstance(msg, ResultMessage):
            if msg.total_cost_usd:
                result.append({
                    "type": "cost",
                    "content": f"${msg.total_cost_usd:.4f}",
                    "timestamp": datetime.now().isoformat()
                })

        return result if result else None

    def _format_tool(self, block):
        tool = block.name
        if tool == "Write":
            return f"📝 Creating: {block.input.get('file_path', '?')}"
        elif tool == "Edit":
            return f"✏️ Editing: {block.input.get('file_path', '?')}"
        elif tool == "Bash":
            return f"▶️ Running: {block.input.get('command', '?')}"
        elif tool == "Read":
            return f"📖 Reading: {block.input.get('file_path', '?')}"
        return f"🔧 {tool}"

    async def stop(self):
        if self.client:
            await self.client.disconnect()


@app.route('/api/session/start', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    session = TeacherSession(session_id)
    sessions[session_id] = session
    message_queues[session_id] = []

    logger.info(f"Creating session {session_id}")

    # Start session synchronously
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(session.start())
        loop.close()
        logger.info(f"Session {session_id} ready")
        return jsonify({"session_id": session_id, "status": "ready"})
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/teach', methods=['POST'])
def teach():
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message')

    logger.info(f"Teach request for session {session_id}: {message}")

    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    session = sessions[session_id]

    # Run in background thread
    import threading
    def run():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(session.teach(message))
            loop.close()
        except Exception as e:
            logger.error(f"Error in teach thread: {e}")
            logger.error(traceback.format_exc())

    threading.Thread(target=run, daemon=True).start()

    return jsonify({"status": "processing"})


@app.route('/api/stream/<session_id>')
def stream(session_id):
    if session_id not in message_queues:
        return jsonify({"error": "Session not found"}), 404

    def generate():
        queue = message_queues[session_id]
        sent_count = 0
        heartbeat_count = 0

        while heartbeat_count < 60:  # Max 30 seconds of heartbeats
            if len(queue) > sent_count:
                for msg in queue[sent_count:]:
                    yield f"data: {json.dumps(msg)}\n\n"
                    sent_count += 1

                    if msg.get('type') in ['complete', 'error']:
                        logger.info(f"Stream ending with {msg.get('type')}")
                        return

                heartbeat_count = 0  # Reset heartbeat counter
            else:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                heartbeat_count += 1

            import time
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/')
def index():
    """Serve the main HTML page"""
    html_path = Path(__file__).parent / 'teacher.html'
    return send_file(html_path)


@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    return jsonify([
        {
            "id": "list-comp",
            "title": "Python List Comprehensions",
            "prompt": "Teach me Python list comprehensions. Create a file with 3 examples: basic, with filter, nested. Run and explain each."
        },
        {
            "id": "decorators",
            "title": "Python Decorators",
            "prompt": "Teach me Python decorators. Show functions as first-class objects, simple decorators, and decorators with arguments. Create files and run examples."
        },
        {
            "id": "async",
            "title": "Async/Await",
            "prompt": "Teach me async/await in Python. Cover basics, syntax, and a practical asyncio example. Write and run code."
        },
        {
            "id": "flask-api",
            "title": "Flask REST API",
            "prompt": "Teach me building REST APIs with Flask. Show setup, GET/POST endpoints, and JSON handling. Write complete code."
        },
    ])


@app.route('/api/debug/<session_id>')
def debug_session(session_id):
    """Debug endpoint to check session state"""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    queue = message_queues.get(session_id, [])
    return jsonify({
        "session_exists": session_id in sessions,
        "queue_length": len(queue),
        "messages": queue
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🎓 SCRIMBA TEACHER - Server Starting")
    print("=" * 70)
    print("\n📱 Open your browser to: http://localhost:5000")
    print("📊 Debug endpoint: http://localhost:5000/api/debug/<session_id>")
    print("\n✅ No CORS issues - HTML served from same origin")
    print("💡 Ctrl+C to stop\n")
    app.run(debug=True, port=5000, threaded=True)
