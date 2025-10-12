#!/usr/bin/env python3
"""Unified Learning Server - Cognitive Teaching System"""

import asyncio
import json
import queue
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import uuid
import traceback
import logging
import os

# Import concept tracking system
from concept_tracker import ConceptBasedPermissionSystem

# Import student knowledge tracker
from student_knowledge import StudentKnowledgeTracker

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
    create_sdk_mcp_server,
)
from claude_agent_sdk.types import (
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
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
from tools.video_tools import (
    generate_educational_video,
    generate_code_animation,
    generate_concept_demo_video,
)
from tools.image_tools import (
    generate_image,
    generate_educational_illustration,
    edit_educational_image,
    fix_code_screenshot,
    update_diagram_labels,
    enhance_example_image,
)

# Import agent configuration (dynamic, SDK-native)
from agent_config import create_agent_definitions, get_enhanced_prompt, get_all_tools

# Import agent router
from agent_router import AgentRouter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Setup FAL AI for image generation
if 'FAL_KEY' not in os.environ:
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

video_tools = create_sdk_mcp_server(
    name="video_tools",
    version="1.0.0",
    tools=[
        generate_educational_video,
        generate_code_animation,
        generate_concept_demo_video,
    ],
)

image_tools = create_sdk_mcp_server(
    name="image_tools",
    version="1.0.0",
    tools=[
        generate_image,
        generate_educational_illustration,
        edit_educational_image,
        fix_code_screenshot,
        update_diagram_labels,
        enhance_example_image,
    ],
)


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-' + os.urandom(24).hex())
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Session storage
sessions = {}
message_queues = {}


class UnifiedSession:
    """Master session with compositional multi-modal teaching"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.concept_permission = ConceptBasedPermissionSystem(session_id)
        self.client = None  # Persistent client for conversation memory
        self.current_agent_message = ""  # Store agent text for concept parsing
        self.router = AgentRouter()  # Intelligent agent routing
        self.knowledge = StudentKnowledgeTracker(session_id=session_id)  # Session-scoped student knowledge

        # Concept-based permission system
        async def limit_tools(
            tool_name: str,
            input_data: dict[str, any],
            context: ToolPermissionContext
        ) -> PermissionResultAllow | PermissionResultDeny:
            # Check concept limit and sequencing
            can_use, reason = self.concept_permission.can_use_tool(
                tool_name,
                input_data,
                self.current_agent_message
            )

            if can_use:
                logger.info(f"[{self.session_id[:8]}] ✓ Tool allowed: {tool_name} - {reason}")
                return PermissionResultAllow(behavior="allow")
            else:
                logger.warning(f"[{self.session_id[:8]}] ✗ Tool denied: {tool_name} - {reason}")
                return PermissionResultDeny(
                    behavior="deny",
                    message=reason,
                    interrupt=False
                )

        # Single adaptive agent with role-switching (SDK doesn't support multi-agent routing)
        master_agent = AgentDefinition(
            description="Adaptive programming teacher that switches roles based on student needs",
            prompt="""You are an adaptive programming teacher. Switch roles based on the request:

**EXPLAINER MODE**: Explain concepts clearly with examples and visuals
**REVIEWER MODE**: Analyze code and provide constructive feedback
**CHALLENGER MODE**: Create practice problems matching skill level
**ASSESSOR MODE**: Test understanding and identify knowledge gaps

Tools available: visual diagrams, educational videos, code animations, image generation, image editing, code examples, simulations, challenges, code review.

IMPORTANT: When asked to generate images (like "generate image of a cat"), use the generate_image tool directly. Do not refuse or suggest programming alternatives unless the request is specifically about learning to code images.

Max 2 tools per response. Max 3 concepts per response.""",
            tools=get_all_tools(),
            model="sonnet"
        )

        self.options = ClaudeAgentOptions(
            agents={"master": master_agent},  # Single adaptive agent
            mcp_servers={
                "scrimba": scrimba_tools,
                "live_coding": live_coding_tools,
                "visual": visual_tools,
                "video": video_tools,
                "image": image_tools,
            },
            allowed_tools=get_all_tools(),
            can_use_tool=limit_tools,
            setting_sources=["project"]
        )
        self.messages = []

    async def connect(self):
        """Establish persistent connection for conversation memory"""
        if not self.client:
            self.client = ClaudeSDKClient(options=self.options)
            await self.client.connect()
            logger.info(f"[{self.session_id[:8]}] Connected - conversation memory active")

    async def disconnect(self):
        """Close connection and cleanup"""
        if self.client:
            await self.client.disconnect()
            logger.info(f"[{self.session_id[:8]}] Disconnected")
            self.client = None

    async def teach(self, instruction):
        """Teach using persistent client with intelligent agent routing and concept-based limits"""
        logger.info(f"[{self.session_id[:8]}] Teaching: {instruction}")

        try:
            # Ensure client is connected
            await self.connect()

            # Reset concept permission system for this request
            self.concept_permission.reset()
            self.current_agent_message = ""

            # Route to appropriate role
            selected_role, confidence = self.router.route(instruction, self.messages)

            role_map = {
                "explainer": "EXPLAINER MODE",
                "reviewer": "REVIEWER MODE",
                "challenger": "CHALLENGER MODE",
                "assessor": "ASSESSOR MODE"
            }

            role_instruction = role_map.get(selected_role, "EXPLAINER MODE")
            routing_msg = f"🎯 Using {role_instruction} (confidence: {confidence:.0%})"

            logger.info(f"[{self.session_id[:8]}] {routing_msg}")

            # Send routing notification to frontend
            if self.session_id in message_queues:
                message_queues[self.session_id].put({
                    "type": "routing",
                    "agent": selected_role,
                    "confidence": confidence,
                    "content": routing_msg,
                    "timestamp": datetime.now().isoformat()
                })

            # Get student knowledge context
            knowledge_context = self.knowledge.get_context_summary()
            logger.info(f"[{self.session_id[:8]}] Knowledge: {knowledge_context}")

            # Build role-specific instruction
            contextual_instruction = f"""ACTIVATE {role_instruction}

Student Context:
{knowledge_context if knowledge_context else "New student - no prior knowledge"}

Request: {instruction}

Remember:
- Max 2 tools per response (quality over quantity)
- Max 3 concepts per response (cognitive load)
- Sequential tool usage (each builds on previous)"""

            # Query with role-based instruction
            await self.client.query(contextual_instruction)

            message_count = 0
            async for msg in self.client.receive_response():
                message_count += 1

                # Capture agent text for concept parsing
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock) and block.text:
                            self.current_agent_message += block.text + " "

                formatted_list = self._format_message(msg)
                if formatted_list:
                    for formatted in formatted_list:
                        self.messages.append(formatted)
                        if self.session_id in message_queues:
                            message_queues[self.session_id].put(formatted)

            status = self.concept_permission.tracker.get_status()
            logger.info(f"[{self.session_id[:8]}] ✓ Complete! {message_count} messages, {status['concept_count']} concepts, {status['tools_used']} tools")

            # Record session in knowledge tracker
            concepts_taught = self.concept_permission.tracker.declared_concepts
            if concepts_taught:
                self.knowledge.record_session(
                    agent_used=selected_role,
                    concepts_taught=concepts_taught,
                    success=True  # TODO: Determine success based on assessment
                )
                self.knowledge.save()
                logger.info(f"[{self.session_id[:8]}] 💾 Knowledge saved: {len(concepts_taught)} concepts")

            # Signal completion
            complete_msg = {"type": "complete", "timestamp": datetime.now().isoformat()}
            self.messages.append(complete_msg)
            if self.session_id in message_queues:
                message_queues[self.session_id].put(complete_msg)

            # Disconnect client to ensure clean state for next message
            # (Each asyncio.run() creates new loop, client must be recreated)
            await self.disconnect()

        except Exception as e:
            logger.error(f"[{self.session_id[:8]}] ❌ Error: {e}")
            logger.error(traceback.format_exc())
            error_msg = {
                "type": "error",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            if self.session_id in message_queues:
                message_queues[self.session_id].put(error_msg)

            # Disconnect on error too
            await self.disconnect()

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


# ===== FRONTEND ROUTES =====

@app.route('/')
def index():
    """Serve the main frontend"""
    from flask import send_file
    return send_file('learn.html')


@app.route('/learn.html')
def learn():
    """Serve the learn.html frontend"""
    from flask import send_file
    return send_file('learn.html')


@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    from flask import send_file
    return send_file('manifest.json', mimetype='application/json')


@app.route('/service-worker.js')
def service_worker():
    """Serve service worker"""
    from flask import send_file
    return send_file('service-worker.js', mimetype='application/javascript')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (icons, etc.)"""
    from flask import send_from_directory
    return send_from_directory('static', filename)


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Create new teaching session"""
    session_id = str(uuid.uuid4())
    session = UnifiedSession(session_id)
    sessions[session_id] = session
    message_queues[session_id] = queue.Queue()  # Thread-safe queue

    logger.info(f"Session created: {session_id}")
    return jsonify({
        "session_id": session_id,
        "status": "ready"
    })


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
            # Use asyncio.run() - SDK-compliant loop management
            asyncio.run(session.teach(message))
        except Exception as e:
            logger.error(f"❌ Error in teach thread: {e}")
            import traceback
            traceback.print_exc()  # Full stack trace to terminal
            # Send error to frontend
            if session_id in message_queues:
                message_queues[session_id].put({
                    "type": "error",
                    "content": f"Error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "processing"})


@app.route('/api/session/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """Get message history for a session"""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    session = sessions[session_id]
    return jsonify({"messages": session.messages})


@app.route('/api/stream/<session_id>')
def stream(session_id):
    """Unified SSE stream with pacing delays for cognitive absorption - THREAD-SAFE"""
    if session_id not in message_queues:
        return jsonify({"error": "Session not found"}), 404

    def generate():
        import time
        msg_queue = message_queues[session_id]
        last_msg_type = None

        while True:  # Keep stream alive indefinitely
            try:
                # Non-blocking atomic dequeue
                msg = msg_queue.get_nowait()
                current_msg_type = msg.get('type')

                # Add pacing delay between tool outputs for cognitive absorption
                if last_msg_type == 'output' and current_msg_type in ['action', 'teacher']:
                    time.sleep(2.0)  # 2-second absorption delay after tool output

                yield f"data: {json.dumps(msg)}\n\n"
                last_msg_type = current_msg_type

            except queue.Empty:
                # No messages available - send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    # Get dynamic agent info
    from agent_config import AGENT_CONFIGS
    agent_count = len(AGENT_CONFIGS)
    tool_count = len(get_all_tools())

    print("=" * 80)
    print("🎓 COGNITIVE TEACHING SYSTEM - SDK-NATIVE ARCHITECTURE")
    print("=" * 80)
    print("\n📱 Server: http://localhost:5000")
    print("🌐 Open to all - No signup/login required")

    print(f"\n🤖 DYNAMIC AGENTS ({agent_count} loaded):")
    for name, config in AGENT_CONFIGS.items():
        print(f"  • {name.upper():12} - {config['description'][:50]}...")

    print(f"\n🔧 TEACHING TOOLS ({tool_count} total):")
    print("  • Visual Tools    - Diagrams & visualizations")
    print("  • Video Tools     - Educational videos & animations")
    print("  • Image Tools     - AI image generation & editing")
    print("  • Concept Tools   - Examples & simulations")
    print("  • Project Tools   - Live coding & review")

    print("\n🧠 COGNITIVE FEATURES:")
    print("  • Flexible concept limits    (soft 3-concept guideline)")
    print("  • Sequential tool chains     (each builds on previous)")
    print("  • Pacing delays              (2s absorption time)")
    print("  • Session-scoped memory      (.claude/sessions/)")
    print("  • Context-aware prompts      (adapts to student knowledge)")

    print("\n🎯 INTELLIGENT ROUTING:")
    print("  'Explain X'        → Auto-routes to best agent")
    print("  'Check my code'    → Detects code → Reviewer")
    print("  'Challenge me'     → Detects intent → Challenger")
    print("  'Test me'          → Detects assessment → Assessor")

    print(f"\n✨ {agent_count} Dynamic Agents, {tool_count} Tools, Zero Hardcoding")
    print("💡 Ctrl+C to stop\n")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
