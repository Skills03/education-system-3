#!/usr/bin/env python3
"""Unified Learning Server - All 3 teaching modes on ONE port"""

import asyncio
import json
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import uuid
import traceback
import logging
import os

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
    ToolResultBlock,
    create_sdk_mcp_server,
)

# Import tools
from tools.concept_tools import (
    show_code_example,
    run_code_simulation,
    show_concept_progression,
    create_interactive_challenge,
)
from tools.project_tools import (
    project_kickoff,
    code_live_increment,
    demonstrate_code,
    student_challenge,
    review_student_work,
)
from tools.visual_tools import (
    generate_concept_diagram,
    generate_data_structure_viz,
    generate_algorithm_flowchart,
    generate_architecture_diagram,
)

# Import agents
from agents.concept_agent import CONCEPT_AGENT
from agents.project_agent import PROJECT_AGENT
from agents.visual_agent import VISUAL_AGENT

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Setup FAL AI for image generation
os.environ['FAL_KEY'] = '7cc98720-6ee8-45da-bf97-97a66d2ecdb3:f54b62a31f19f2f55f0bba871b273ee4'


# ===== CREATE MCP SERVERS =====

scrimba_tools = create_sdk_mcp_server(
    name="scrimba_tools",
    version="1.0.0",
    tools=[
        show_code_example,
        run_code_simulation,
        show_concept_progression,
        create_interactive_challenge,
    ],
)

live_coding_tools = create_sdk_mcp_server(
    name="live_coding",
    version="1.0.0",
    tools=[
        project_kickoff,
        code_live_increment,
        demonstrate_code,
        student_challenge,
        review_student_work,
    ],
)

visual_tools = create_sdk_mcp_server(
    name="visual_tools",
    version="1.0.0",
    tools=[
        generate_concept_diagram,
        generate_data_structure_viz,
        generate_algorithm_flowchart,
        generate_architecture_diagram,
    ],
)


app = Flask(__name__)
CORS(app)

sessions = {}
message_queues = {}


class UnifiedSession:
    """Unified session supporting all 3 teaching modes"""

    def __init__(self, session_id, mode="concept"):
        self.session_id = session_id
        self.mode = mode

        # Single ClaudeAgentOptions with ALL agents and tools
        self.options = ClaudeAgentOptions(
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
                # Concept tools
                "mcp__scrimba__show_code_example",
                "mcp__scrimba__run_code_simulation",
                "mcp__scrimba__show_concept_progression",
                "mcp__scrimba__create_interactive_challenge",
                # Project tools
                "mcp__live_coding__project_kickoff",
                "mcp__live_coding__code_live_increment",
                "mcp__live_coding__demonstrate_code",
                "mcp__live_coding__student_challenge",
                "mcp__live_coding__review_student_work",
                # Visual tools
                "mcp__visual__generate_concept_diagram",
                "mcp__visual__generate_data_structure_viz",
                "mcp__visual__generate_algorithm_flowchart",
                "mcp__visual__generate_architecture_diagram",
            ],
        )
        self.messages = []

    async def teach(self, instruction):
        """Teach using the specified agent mode"""
        logger.info(f"[{self.session_id[:8]}] Mode: {self.mode}, Teaching: {instruction}")

        try:
            async with ClaudeSDKClient(options=self.options) as client:
                # Use the agent based on mode
                await client.query(f"Use the {self.mode} agent: {instruction}")

                message_count = 0
                async for msg in client.receive_response():
                    message_count += 1
                    formatted_list = self._format_message(msg)
                    if formatted_list:
                        for formatted in formatted_list:
                            self.messages.append(formatted)
                            if self.session_id in message_queues:
                                message_queues[self.session_id].append(formatted)

                logger.info(f"[{self.session_id[:8]}] ✓ Complete! {message_count} messages")

            # Signal completion
            complete_msg = {"type": "complete", "timestamp": datetime.now().isoformat()}
            self.messages.append(complete_msg)
            if self.session_id in message_queues:
                message_queues[self.session_id].append(complete_msg)

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
        """Format message for frontend"""
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
                        "content": f"🔧 {block.name}",
                        "timestamp": datetime.now().isoformat()
                    })

        elif isinstance(msg, UserMessage):
            for block in msg.content:
                if isinstance(block, ToolResultBlock):
                    if block.content:
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


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Create new session with specified mode"""
    data = request.json or {}
    mode = data.get('mode', 'concept')  # Default to concept mode

    session_id = str(uuid.uuid4())
    session = UnifiedSession(session_id, mode)
    sessions[session_id] = session
    message_queues[session_id] = []

    logger.info(f"Session created: {session_id}, mode: {mode}")
    return jsonify({"session_id": session_id, "mode": mode, "status": "ready"})


@app.route('/api/teach', methods=['POST'])
def teach():
    """Unified teaching endpoint for all modes"""
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message')

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

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "processing"})


@app.route('/api/stream/<session_id>')
def stream(session_id):
    """Unified SSE stream for all modes"""
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
                        return
                heartbeat_count = 0
            else:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                heartbeat_count += 1
            import time
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    print("=" * 70)
    print("🎓 UNIFIED LEARNING SERVER")
    print("=" * 70)
    print("\n📱 Server: http://localhost:5000")
    print("\n🎯 Three Teaching Modes:")
    print("  1. Concept Teaching  - Interactive code examples & simulations")
    print("  2. Project Building  - Live coding Scrimba-style")
    print("  3. Visual Learning   - AI-generated diagrams")
    print("\n📊 Total: 13 tools, 3 agents, 1 server")
    print("💡 Ctrl+C to stop\n")
    app.run(debug=True, port=5000, threaded=True)
