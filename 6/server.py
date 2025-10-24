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
    add_code_step,
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
        add_code_step,
    ],
)


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-' + os.urandom(24).hex())
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Session storage
sessions = {}
message_queues = {}


class UnifiedSession:
    """Master session with orchestrator pattern - delegates to specialized agents"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.concept_permission = ConceptBasedPermissionSystem(session_id)
        self.client = None  # Persistent client for conversation memory
        self.current_agent_message = ""  # Store agent text for concept parsing
        self.current_instruction = ""  # Store current instruction for tool limit detection
        self.router = AgentRouter()  # Intelligent agent routing
        self.knowledge = StudentKnowledgeTracker(session_id=session_id)  # Session-scoped student knowledge

        # ===== BUILDER AGENT - Dual-mode: Velocity + Tutorial =====
        builder_dual_mode_prompt = """You help students build apps using TWO modes:

## MODE DETECTION (FIRST THING YOU DO)

**Check the request for these keywords:**

**TUTORIAL MODE keywords:**
- "teach", "show step", "learn", "how to", "explain"
- If ANY of these appear → TUTORIAL MODE

**VELOCITY MODE:**
- Everything else → VELOCITY MODE

## IF TUTORIAL MODE:
You MUST use add_code_step tool 12-15 times.
DO NOT use customize_app_template in tutorial mode.
BUILD THE APP INCREMENTALLY, ONE PIECE AT A TIME.

## IF VELOCITY MODE:
Use customize_app_template + generate_client_proposal.
DO NOT use add_code_step in velocity mode

---

## 🎓 TUTORIAL MODE (Scrimba-style Teaching)

**GOAL:** Student learns HOW to build, not just sees final product.

**Pattern:** Explain → Add → Preview → Repeat

**Use add_code_step tool 12-15 times sequentially:**

**Step 1:** Basic HTML structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio</title>
</head>
<body>
</body>
</html>
```
Explanation: "Every website starts with HTML structure. This is the skeleton."

**Step 2:** Add title tag
Code: `<title>{Client Name} - Portfolio</title>`
Explanation: "Title shows in browser tab. Important for SEO and branding."

**Step 3:** Start style section
Code: `<style>\n* { margin: 0; padding: 0; box-sizing: border-box; }\n</style>`
Explanation: "CSS reset ensures consistent spacing across browsers."

**Step 4:** Add hero div
Code: `<div class="hero">\n  <h1>Client Name</h1>\n</div>`
Explanation: "Hero section is first thing visitors see. Big, bold, impactful."

**Step 5:** Style hero with gradient
Code: `.hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 100px 20px; color: white; text-align: center; }`
Explanation: "Gradient backgrounds look professional. Purple is trust + creativity."

**[Continue 10 more steps...]**

**BETWEEN EACH STEP:**
- Pause (student sees preview)
- Explain WHY this piece matters
- Show live result

**Final step:** Deployment instructions

---

## ⚡ VELOCITY MODE (Fast Income Generation)

**GOAL:** Ship complete app in <5 seconds, student starts earning.

**EXECUTE IMMEDIATELY:**

**Step 1:** Call `customize_app_template`
- template_type: "portfolio" (default) OR "restaurant_menu" OR "booking" OR "invoice"
- client_name: Extract from request
- business_name: Extract from request
- customizations: Extract 3-5 key features

**Step 2:** Call `generate_client_proposal`
- client_name: Same
- project_type: Template name
- price: Portfolio=$150, Menu=$300, Booking=$500, Invoice=$150
- timeline: "3-5 days"
- features: From customizations

**Step 3:** Explain what was built + velocity techniques used

**NO planning. NO asking questions. Use intelligent defaults. SHIP.**

---

## INTELLIGENT DEFAULTS (Velocity Mode Only)

**Portfolio keywords:** portfolio, website, personal site, showcase
→ template_type="portfolio"

**Menu keywords:** menu, restaurant, cafe, food, QR code
→ template_type="restaurant_menu"

**Booking keywords:** booking, appointment, schedule, calendar
→ template_type="booking"

**Invoice keywords:** invoice, billing, receipt, payment
→ template_type="invoice"

**No match?** → Default to "portfolio"

---

## TEACHING MINDSET

**Tutorial mode:** "Let me show you HOW we build this, piece by piece."
**Velocity mode:** "Let me build this for you right now. Ready to ship."

**Key difference:**
- Tutorial = 15 steps, 15 previews, 15 teaching moments
- Velocity = 1 customization call, 1 proposal, done

DETECT the mode from request language and execute accordingly."""

        builder_agent = AgentDefinition(
            description="Dual-mode app builder: Tutorial mode (step-by-step teaching) or Velocity mode (fast income generation)",
            tools=[
                "mcp__app_builder__list_app_templates",
                "mcp__app_builder__customize_app_template",
                "mcp__app_builder__generate_client_proposal",
                "mcp__app_builder__add_code_step"
            ],
            prompt=builder_dual_mode_prompt,
            model="sonnet"
        )

        # ===== TEACHER AGENT - Story-based teaching =====
        teacher_prompt = """You are a story-based teaching agent that explains concepts using analogies, visualizations, and memorable scenes.

Use your tools to:
- explain_with_analogy: Create memorable comparisons
- walk_through_concept: Step-by-step explanations with examples
- generate_teaching_scene: Visual scenes that illustrate concepts

Focus on making concepts stick through narrative and visual memory."""

        teacher_agent = AgentDefinition(
            description="Story-based teaching agent that explains concepts using analogies and visualizations",
            tools=[
                "mcp__story_teaching__explain_with_analogy",
                "mcp__story_teaching__walk_through_concept",
                "mcp__story_teaching__generate_teaching_scene"
            ],
            prompt=teacher_prompt,
            model="sonnet"
        )

        # ===== ORCHESTRATOR - Routes to specialized agents =====
        orchestrator_prompt = """You are an orchestrator agent that routes requests to specialized agents.

**Routing Rules:**
- App building requests (portfolio, website, app, menu, booking, invoice, build) → delegate to 'builder' subagent
- Teaching/explanation requests (explain, teach, help me understand, what is) → delegate to 'teacher' subagent

**How to delegate:**
Use the Task tool with:
- prompt: The user's EXACT request (do not modify)
- subagent_type: Either 'builder' or 'teacher'
- description: Short 3-5 word description like "Build portfolio app" or "Teach loops"

**Example:**
User: "Build me a portfolio website"
→ Task(prompt="Build me a portfolio website", subagent_type='builder', description="Build portfolio app")

User: "Explain loops to me"
→ Task(prompt="Explain loops to me", subagent_type='teacher', description="Teach loops")

CRITICAL: Do NOT try to build or teach yourself. ONLY delegate using Task tool."""

        # ===== OPTIONS - Orchestrator with specialized agents =====
        self.options = ClaudeAgentOptions(
            agents={
                "builder": builder_agent,
                "teacher": teacher_agent
            },
            mcp_servers={
                "app_builder": app_builder,
                "story_teaching": story_teaching
            },
            allowed_tools=[
                "Task",
                # Builder tools
                "mcp__app_builder__list_app_templates",
                "mcp__app_builder__customize_app_template",
                "mcp__app_builder__generate_client_proposal",
                "mcp__app_builder__add_code_step",
                # Teacher tools
                "mcp__story_teaching__explain_with_analogy",
                "mcp__story_teaching__walk_through_concept",
                "mcp__story_teaching__generate_teaching_scene"
            ],
            system_prompt=orchestrator_prompt,
            cwd="/home/mahadev/Desktop/dev/education/6"
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

            # Builder mode only - no mode detection needed
            logger.info(f"[{self.session_id[:8]}] Query: {instruction}")
            logger.info(f"[{self.session_id[:8]}] Mode: BUILD")
            
            # Get student knowledge context
            knowledge_context = self.knowledge.get_context_summary()
            logger.info(f"[{self.session_id[:8]}] Knowledge: {knowledge_context}")

            # Send directly - agent has prompt with instructions
            await self.client.query(instruction)

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
