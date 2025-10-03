#!/usr/bin/env python3
"""Backend API server for Scrimba Teacher Agent - FIXED VERSION"""

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

Always use inline format - NO file creation!""",
    tools=[],
    model="sonnet",
)

app = Flask(__name__)
CORS(app)

# Store active sessions
sessions = {}
message_queues = {}


class TeacherSession:
    """Fixed session - creates client in same event loop where it's used"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.options = ClaudeAgentOptions(
            agents={"teacher": TEACHER_AGENT},
        )
        self.messages = []

    async def teach(self, instruction):
        """Create client and teach in SAME async context - proper pattern from docs"""
        logger.info(f"[{self.session_id[:8]}] Teaching: {instruction}")

        try:
            # Following official examples: create client in same async context
            async with ClaudeSDKClient(options=self.options) as client:
                logger.info(f"[{self.session_id[:8]}] ✓ Client connected")

                await client.query(f"Use the teacher agent: {instruction}")
                logger.info(f"[{self.session_id[:8]}] Query sent, receiving...")

                message_count = 0
                async for msg in client.receive_response():
                    message_count += 1
                    msg_type = type(msg).__name__
                    logger.info(f"[{self.session_id[:8]}] Message #{message_count}: {msg_type}")

                    # Format message - returns LIST
                    formatted_list = self._format_message(msg)
                    if formatted_list:
                        for formatted in formatted_list:
                            content_preview = formatted['content'][:60] if len(formatted['content']) > 60 else formatted['content']
                            logger.info(f"[{self.session_id[:8]}] ✓ {formatted['type']}: {content_preview}...")

                            self.messages.append(formatted)
                            if self.session_id in message_queues:
                                message_queues[self.session_id].append(formatted)

                        logger.info(f"[{self.session_id[:8]}] Queue: {len(message_queues[self.session_id])}")

                logger.info(f"[{self.session_id[:8]}] ✓ Complete! {message_count} messages")

            # Signal completion (outside context manager)
            complete_msg = {"type": "complete", "timestamp": datetime.now().isoformat()}
            self.messages.append(complete_msg)
            if self.session_id in message_queues:
                message_queues[self.session_id].append(complete_msg)
                logger.info(f"[{self.session_id[:8]}] Final queue size: {len(message_queues[self.session_id])}")

        except Exception as e:
            logger.error(f"[{self.session_id[:8]}] ❌ Error: {e}")
            logger.error(traceback.format_exc())
            error_msg = {
                "type": "error",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            if self.session_id in message_queues:
                message_queues[self.session_id].append(error_msg)

    def _format_message(self, msg):
        """Format message - returns LIST of formatted messages"""
        result = []

        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
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


@app.route('/')
def index():
    """Serve the main HTML page"""
    html_path = Path(__file__).parent / 'teacher.html'
    return send_file(html_path)


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Create session (no client yet - created on demand)"""
    session_id = str(uuid.uuid4())
    session = TeacherSession(session_id)
    sessions[session_id] = session
    message_queues[session_id] = []

    logger.info(f"Session created: {session_id}")
    return jsonify({"session_id": session_id, "status": "ready"})


@app.route('/api/teach', methods=['POST'])
def teach():
    """Send teaching request"""
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message')

    logger.info(f"Teach request: {session_id[:8]}")

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
    """Stream SSE messages"""
    if session_id not in message_queues:
        return jsonify({"error": "Session not found"}), 404

    def generate():
        queue = message_queues[session_id]
        sent_count = 0
        heartbeat_count = 0

        while heartbeat_count < 60:
            if len(queue) > sent_count:
                for msg in queue[sent_count:]:
                    yield f"data: {json.dumps(msg)}\n\n"
                    sent_count += 1

                    if msg.get('type') in ['complete', 'error']:
                        logger.info(f"Stream ending: {msg.get('type')}")
                        return

                heartbeat_count = 0
            else:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                heartbeat_count += 1

            import time
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/lessons', methods=['GET'])
def get_lessons():
    return jsonify([
        {
            "id": "list-comp",
            "title": "Python List Comprehensions",
            "prompt": "Teach me Python list comprehensions. Show 3 examples: basic, with filter, nested. Explain each."
        },
        {
            "id": "decorators",
            "title": "Python Decorators",
            "prompt": "Teach me Python decorators. Show functions as first-class objects, simple decorators, and decorators with arguments."
        },
        {
            "id": "async",
            "title": "Async/Await",
            "prompt": "Teach me async/await in Python. Cover basics, syntax, and a practical asyncio example."
        },
        {
            "id": "flask-api",
            "title": "Flask REST API",
            "prompt": "Teach me building REST APIs with Flask. Show setup, GET/POST endpoints, and JSON handling."
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
    print("🎓 SCRIMBA TEACHER - Server Starting (FIXED VERSION)")
    print("=" * 70)
    print("\n📱 Open your browser to: http://localhost:5000")
    print("📊 Debug endpoint: http://localhost:5000/api/debug/<session_id>")
    print("\n✅ Client created on-demand in same event loop")
    print("💡 Ctrl+C to stop\n")
    app.run(debug=True, port=5000, threaded=True)
