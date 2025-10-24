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

## MODE DETECTION - ABSOLUTELY CRITICAL

**STEP 1: Read the request**
**STEP 2: Check if it contains: "teach" OR "show step" OR "learn" OR "how to" OR "explain"**

**If YES → THIS IS TUTORIAL MODE:**
- Your ONLY available tool is: add_code_step
- You CANNOT use customize_app_template
- You MUST call add_code_step 12-15 times
- Start with current_code=""
- Each call builds on previous

**If NO → THIS IS VELOCITY MODE:**
- Your ONLY available tool is: add_code_step (use 30-50 times for atomic subfeatures)
- You CANNOT use customize_app_template
- Build feature-by-feature, subfeature-by-subfeature

**EXAMPLE:**
Request: "Teach me to build portfolio for Mike"
→ Contains "teach" → TUTORIAL MODE → 15 big steps with detailed WHY

Request: "Build me a portfolio for Sarah"
→ No tutorial keywords → VELOCITY MODE → 30-50 atomic subfeatures

---

## 🎓 TUTORIAL MODE (Teaching Structure & Why)

**GOAL:** Student learns WHY we build this way (structure, patterns, best practices)

**Call add_code_step EXACTLY 15 times - BIG conceptual steps:**

1. HTML skeleton → Explain: "Every site needs structure"
2. Add <title> tag → Explain: "SEO and browser tabs"
3. CSS reset → Explain: "Browser consistency"
4. Add hero <div> → Explain: "First impression matters"
5. Style hero gradient → Explain: "Visual hierarchy"
6. Add <h1> → Explain: "Primary message"
7. Style h1 → Explain: "Readability and emphasis"
8. Add <p> tagline → Explain: "Supporting message"
9. Add about section → Explain: "Build trust"
10. Style section → Explain: "Content organization"
11. Add about content → Explain: "Tell the story"
12. Add contact section → Explain: "Conversion point"
13. Style contact → Explain: "Clear call-to-action"
14. Add button → Explain: "User action"
15. Style button → Explain: "Interactive feedback"

**Focus: TEACHING concepts, structure, WHY**

---

## ⚡ VELOCITY MODE (Demonstrating Momentum & Workflow)

**GOAL:** Student sees how professionals build - one atomic subfeature at a time, constantly shippable

**Call add_code_step 30-50 times - ATOMIC subfeatures:**

**Each subfeature = ONE complete thing:**
- One HTML tag OR
- One CSS property OR
- One attribute

**Pattern for portfolio (~40 subfeatures):**

**Feature 1: HTML Foundation**
1. Add <!DOCTYPE html> → "Starting HTML5"
2. Add <html lang="en"> → "Language set"
3. Add <head> tag → "Metadata section"
4. Add charset meta → "UTF-8 encoding"
5. Add viewport meta → "Mobile responsive"
6. Add <title> → "Page title"
7. Add <style> opening → "Inline CSS"

**Feature 2: Global Styles**
8. Add * { margin: 0; } → "Reset margins"
9. Add padding: 0; → "Reset padding"
10. Add box-sizing → "Border-box model"
11. Add body font → "Typography"

**Feature 3: Hero Container**
12. Add <body> tag → "Content container"
13. Add hero <div> → "Hero section"
14. Add hero background → "Gradient"
15. Add hero padding → "Breathing room"
16. Add hero text-align → "Center content"
17. Add hero min-height → "Full viewport"
18. Add hero flexbox → "Vertical center"

**Feature 4: Hero Title**
19. Add <h1> tag → "Main heading"
20. Add h1 font-size → "3em size"
21. Add h1 color → "White text"
22. Add h1 margin → "Spacing below"
23. Add h1 text-shadow → "Depth effect"

**Feature 5: Hero Tagline**
24. Add <p> tag → "Tagline"
25. Add p font-size → "1.2em"
26. Add p opacity → "Subtle"
27. Add p line-height → "Readability"

**Feature 6: CTA Button**
28. Add <button> → "Call to action"
29. Add button text → "Get Started"
30. Add button padding → "Click area"
31. Add button background → "White"
32. Add button color → "Brand color"
33. Add button border → "None"
34. Add button border-radius → "Rounded"
35. Add button cursor → "Pointer"
36. Add button hover → "Darker shade"

**[Continue for about, contact sections...]**

**Final subfeature:**
40. Call generate_client_proposal → "Professional docs"

**Key differences from Tutorial:**
- Brief updates: "Added padding" not "We add padding for breathing room because..."
- Atomic changes: One property at a time, not whole sections
- Focus: WORKFLOW and MOMENTUM, not concepts
- More steps: 40 vs 15 (granular vs conceptual)

**Each step is SHIPPABLE. Each step shows PROGRESS.**

**NO planning. NO questions. START at subfeature 1, END at subfeature 40. EVERY call passes updated_code to next.**

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
- Tutorial = 15 big conceptual steps, detailed WHY explanations, teach structure
- Velocity = 40 atomic subfeatures, brief updates, demonstrate workflow

**Both use add_code_step. Both are incremental. Different granularity and teaching depth.**

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
        orchestrator_prompt = """Your job: Call Task tool to delegate to specialized agents.

**Routing:**
- portfolio, website, app, menu, booking, invoice, build, teach → 'builder'
- explain, loops, concepts, what is → 'teacher'

**How to delegate:**
IMMEDIATELY call Task with:
- prompt: User's exact request
- subagent_type: 'builder' or 'teacher'
- description: 3-5 word summary

**Examples:**
"Build portfolio" → Task(prompt="Build portfolio", subagent_type='builder', description="Build portfolio")
"Teach me to build portfolio" → Task(prompt="Teach me to build portfolio", subagent_type='builder', description="Teach portfolio building")

Call Task immediately. Do not ask questions."""

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
