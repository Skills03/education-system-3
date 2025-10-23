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
    ToolPermissionContext,
    PermissionResultAllow,
    PermissionResultDeny,
)

# Import story teaching tools
from tools.story_teaching_tools import (
    explain_with_analogy,
    walk_through_concept,
    generate_teaching_scene,
)

# Import app building tools
from tools.app_building_tools import (
    list_app_templates,
    customize_app_template,
    generate_client_proposal,
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

story_teaching = create_sdk_mcp_server(
    name="story_teaching",
    version="1.0.0",
    tools=[
        explain_with_analogy,
        walk_through_concept,
        generate_teaching_scene,
    ],
)

app_builder = create_sdk_mcp_server(
    name="app_builder",
    version="1.0.0",
    tools=[
        list_app_templates,
        customize_app_template,
        generate_client_proposal,
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
        self.current_instruction = ""  # Store current instruction for tool limit detection
        self.router = AgentRouter()  # Intelligent agent routing
        self.knowledge = StudentKnowledgeTracker(session_id=session_id)  # Session-scoped student knowledge

        # Concept-based permission system (dynamic limits)
        async def limit_tools(
            tool_name: str,
            input_data: dict[str, any],
            context: ToolPermissionContext
        ):
            # Block all Claude Code interactive tools - only allow MCP tools
            ALLOWED_MCP_TOOLS = [
                "mcp__story__explain_with_analogy",
                "mcp__story__walk_through_concept",
                "mcp__story__generate_teaching_scene",
                "mcp__app_builder__list_app_templates",
                "mcp__app_builder__customize_app_template",
                "mcp__app_builder__generate_client_proposal",
            ]
            
            if tool_name not in ALLOWED_MCP_TOOLS:
                logger.warning(f"[{self.session_id[:8]}] ✗ BLOCKED interactive tool: {tool_name}")
                return PermissionResultDeny(behavior="deny", message=f"Only custom MCP tools allowed. Use app_builder or story tools.")
            
            # Dynamic limit: 10 for building, 3 for teaching
            is_building = any(word in self.current_instruction.lower() for word in ['build', 'create', 'portfolio', 'website', 'app', 'menu', 'booking', 'invoice'])
            HARD_TOOL_LIMIT = 10 if is_building else 3
            tool_count = len(self.concept_permission.tracker.tools_used)

            if tool_count >= HARD_TOOL_LIMIT:
                mode = "BUILD" if is_building else "TEACH"
                logger.warning(f"[{self.session_id[:8]}] ✗ DENIED - {HARD_TOOL_LIMIT} tools used ({mode} mode)")
                return PermissionResultDeny(behavior="deny", message=f"Maximum {HARD_TOOL_LIMIT} tools per response.")

            # Check concept limit and sequencing
            can_use, reason = self.concept_permission.can_use_tool(
                tool_name,
                input_data,
                self.current_agent_message
            )

            if can_use:
                mode = "BUILD" if is_building else "TEACH"
                logger.info(f"[{self.session_id[:8]}] ✓ Tool allowed ({tool_count+1}/{HARD_TOOL_LIMIT} {mode}): {tool_name}")
                return PermissionResultAllow(behavior="allow", updated_input=input_data)
            else:
                logger.warning(f"[{self.session_id[:8]}] ✗ Tool denied: {tool_name} - {reason}")
                return PermissionResultDeny(behavior="deny", message=reason)

        # Single master agent - handles both teaching AND building
        # NOTE: Empty tools=[] blocks Claude Code interactive tools, agent only gets MCP tools from allowed_tools
        master_agent = AgentDefinition(
            description="Teaching and app building agent",
            tools=[],  # CRITICAL: Empty list blocks all Claude Code interactive tools
            prompt="""You are a dual-mode agent with 6 MCP tools.

DETECT user intent from query:

**If query contains "build", "create", "portfolio", "menu", "booking", "client", "website":**
→ APP BUILDING MODE - Use ONLY these MCP tools:
1. mcp__app_builder__list_app_templates
2. mcp__app_builder__customize_app_template
3. mcp__app_builder__generate_client_proposal

**Otherwise (teach, explain, how does, what is):**
→ TEACHING MODE - Use ONLY these MCP tools:
1. mcp__story__explain_with_analogy
2. mcp__story__walk_through_concept
3. mcp__story__generate_teaching_scene

Use EXACTLY 3 tools for chosen mode, then STOP. No commentary after tools complete.

---

## TEACHING MODE DETAILS:

# TOOL 1: mcp__story__explain_with_analogy
Start with real-world metaphor:
- Arrays = egg cartons
- Variables = labeled boxes
- Loops = running laps

Parameters:
- concept: the programming concept name
- analogy: the real-world comparison (2-3 sentences)
- connection: why the comparison works (1-2 sentences)

# TOOL 2: mcp__story__walk_through_concept
Show 4 progressive steps using the analogy:

Parameters:
- concept: same concept from tool 1
- step1: first action using analogy
- step2: second action
- step3: third action
- step4: fourth action
- key_insight: main takeaway (1 sentence)

# TOOL 3: mcp__story__generate_teaching_scene
Create PERSON + OBJECT + ACTION visual:

Parameters:
- concept: same concept
- person_description: "Developer [doing action]" (1 sentence)
- object_description: "Real-world object [details]" (1 sentence)
- action_description: "Person [specific action]" (1 sentence)
- labels: "Technical labels to show: array[0], array[1]..." (1 sentence)

# EXAMPLE for "teach arrays":

Tool 1:
concept: "arrays"
analogy: "Arrays are like egg cartons. Each slot holds one egg. Slots are numbered 0, 1, 2, 3. You grab any egg instantly by its number."
connection: "Array indices are like slot numbers. eggs[2] means 'get the egg in slot 2'."

Tool 2:
concept: "array access"
step1: "Look at the carton (the array)"
step2: "Find slot number 2 (the index)"
step3: "Grab the egg at slot 2 (array access)"
step4: "You got the egg! (retrieved the value)"
key_insight: "Arrays let you access any element instantly by position number."

Tool 3:
concept: "arrays"
person_description: "Developer with index finger extended, pointing downward"
object_description: "Egg carton with 6 eggs in clear numbered slots 0, 1, 2, 3, 4, 5"
action_description: "Developer pointing at slot 2, finger touching the egg"
labels: "Labels showing: array[0], array[1], array[2] (highlighted), array[3], array[4], array[5]"

# RULES:
✅ Use all 3 MCP tools in exact order
✅ Stop immediately after tool 3
✅ Keep parameters concise (1-3 sentences each)
✅ Always use the analogy from tool 1 in tool 2

❌ Do NOT use Claude Code interactive tools (Write, Bash, Edit, Read, etc.)
❌ Do NOT respond to student after tools complete
❌ Do NOT add extra commentary or explanations
❌ Do NOT skip any tool

The 3 teaching tools teach everything.

---

## APP BUILDING MODE DETAILS:

Tool 1: mcp__app_builder__list_app_templates - Show available templates with pricing
Tool 2: mcp__app_builder__customize_app_template - Generate client-ready HTML code
Tool 3: mcp__app_builder__generate_client_proposal - Create professional proposal

PRICING: Portfolio $50-150, Menu $200-500, Booking $300-800

The 3 building MCP tools create sellable apps.""",
            model="sonnet"
        )

        # NO agents parameter - calculator example shows this blocks Claude Code tools
        self.options = ClaudeAgentOptions(
            mcp_servers={
                "story": story_teaching,
                "app_builder": app_builder,
            },
            allowed_tools=[
                "mcp__story__explain_with_analogy",
                "mcp__story__walk_through_concept",
                "mcp__story__generate_teaching_scene",
                "mcp__app_builder__list_app_templates",
                "mcp__app_builder__customize_app_template",
                "mcp__app_builder__generate_client_proposal",
            ],
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
            self.current_instruction = instruction  # Store for tool limit detection

            # Inject mode-specific instructions into query
            is_building = any(word in instruction.lower() for word in ['build', 'create', 'portfolio', 'website', 'app', 'menu', 'booking', 'invoice'])
            
            if is_building:
                full_query = f"""User request: {instruction}

IMPORTANT: You have ONLY these 3 MCP tools available:
1. mcp__app_builder__list_app_templates
2. mcp__app_builder__customize_app_template  
3. mcp__app_builder__generate_client_proposal

Use all 3 tools in order. Do NOT use any other tools (Write, Bash, Edit, etc.). Stop after tool 3 completes."""
            else:
                full_query = f"""User request: {instruction}

IMPORTANT: You have ONLY these 3 MCP tools available:
1. mcp__story__explain_with_analogy
2. mcp__story__walk_through_concept
3. mcp__story__generate_teaching_scene

Use all 3 tools in order. Do NOT use any other tools. Stop after tool 3 completes."""
            
            logger.info(f"[{self.session_id[:8]}] Query: {instruction}")
            logger.info(f"[{self.session_id[:8]}] Mode: {'BUILD' if is_building else 'TEACH'}")
            
            # Get student knowledge context
            knowledge_context = self.knowledge.get_context_summary()
            logger.info(f"[{self.session_id[:8]}] Knowledge: {knowledge_context}")

            await self.client.query(full_query)

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
                    agent_used="auto",  # SDK auto-routes
                    concepts_taught=concepts_taught,
                    success=True
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
