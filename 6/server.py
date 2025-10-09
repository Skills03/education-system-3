#!/usr/bin/env python3
"""Unified Learning Server - All 3 teaching modes on ONE port"""

import asyncio
import json
from datetime import datetime
from flask import Flask, request, jsonify, Response, session
from flask_cors import CORS
import uuid
import traceback
import logging
import os
from functools import wraps

# Import auth database and email service
from auth_db import AuthDB
from email_service import EmailService

# Import concept tracking system
from concept_tracker import ConceptBasedPermissionSystem

# Import student knowledge tracker
from student_knowledge import StudentKnowledgeTracker

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

# Import agents
from agents.master_agent import MASTER_TEACHER_AGENT
from agents.specialized_agents import (
    EXPLAINER_AGENT,
    CODE_REVIEWER_AGENT,
    CHALLENGER_AGENT,
    ASSESSOR_AGENT,
)

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


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-' + os.urandom(24).hex())
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Initialize auth database and email service
auth_db = AuthDB()
email_service = EmailService()

# === AUTH TOGGLE === (3-line toggle to enable/disable ALL authentication)
AUTH_ENABLED = os.environ.get('AUTH_ENABLED', 'false').lower() == 'true'
# Set ENV AUTH_ENABLED=true in Dockerfile to enable auth, false to disable
# ==================

sessions = {}
message_queues = {}


# ===== AUTHENTICATION MIDDLEWARE =====

def login_required(f):
    """Decorator to require authentication (bypassed if AUTH_ENABLED=false)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AUTH_ENABLED:  # 3-line toggle: bypass auth entirely
            request.current_user = {'id': 1, 'username': 'anonymous', 'email': 'anonymous@localhost'}
            return f(*args, **kwargs)
        token = request.cookies.get('session_token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        user = auth_db.get_user_by_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired session"}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function


class UnifiedSession:
    """Master session with compositional multi-modal teaching"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.concept_permission = ConceptBasedPermissionSystem(session_id)
        self.client = None  # Persistent client for conversation memory
        self.current_agent_message = ""  # Store agent text for concept parsing
        self.router = AgentRouter()  # Intelligent agent routing
        self.knowledge = StudentKnowledgeTracker(session_id=session_id)  # Session-scoped student knowledge

        # Set Claude CLI path in environment
        os.environ['PATH'] = f"/root/.nvm/versions/node/v22.20.0/bin:{os.environ.get('PATH', '')}"

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

        self.options = ClaudeAgentOptions(
            agents={
                "master": MASTER_TEACHER_AGENT,  # Legacy - kept for compatibility
                "explainer": EXPLAINER_AGENT,
                "reviewer": CODE_REVIEWER_AGENT,
                "challenger": CHALLENGER_AGENT,
                "assessor": ASSESSOR_AGENT,
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
            can_use_tool=limit_tools,  # Concept-based permission system
            setting_sources=["project"]  # Enable memory persistence via .claude/CLAUDE.md
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

            # Route to appropriate specialist agent
            selected_agent, confidence = self.router.route(instruction, self.messages)
            routing_msg = self.router.get_routing_explanation(instruction)

            logger.info(f"[{self.session_id[:8]}] {routing_msg}")

            # Send routing notification to frontend
            if self.session_id in message_queues:
                message_queues[self.session_id].append({
                    "type": "routing",
                    "agent": selected_agent,
                    "confidence": confidence,
                    "content": routing_msg,
                    "timestamp": datetime.now().isoformat()
                })

            # Get student knowledge context
            knowledge_context = self.knowledge.get_context_summary()
            logger.info(f"[{self.session_id[:8]}] Knowledge: {knowledge_context}")

            # Query with selected specialist agent and concept-based constraints
            teaching_prompt = f"""Use the {selected_agent} agent: {instruction}

STUDENT KNOWLEDGE CONTEXT:
{knowledge_context}

CRITICAL: Follow concept-based teaching protocol:
1. DECLARE concepts first: "This response teaches N concepts: ..."
2. Maximum 3 concepts per response (working memory limit)
3. Use sequential tool chaining (each tool builds on previous)
4. Maintain consistent teaching patterns
5. Don't re-teach mastered concepts unless reviewing
6. Address weak areas and prerequisites first

Remember our previous conversation context."""

            await self.client.query(teaching_prompt)

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
                            message_queues[self.session_id].append(formatted)

            status = self.concept_permission.tracker.get_status()
            logger.info(f"[{self.session_id[:8]}] ✓ Complete! {message_count} messages, {status['concept_count']} concepts, {status['tools_used']} tools")

            # Record session in knowledge tracker
            concepts_taught = self.concept_permission.tracker.declared_concepts
            if concepts_taught:
                self.knowledge.record_session(
                    agent_used=selected_agent,
                    concepts_taught=concepts_taught,
                    success=True  # TODO: Determine success based on assessment
                )
                self.knowledge.save()
                logger.info(f"[{self.session_id[:8]}] 💾 Knowledge saved: {len(concepts_taught)} concepts")

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


# ===== AUTHENTICATION ENDPOINTS =====

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Create new user account and send verification email"""
    data = request.json

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # Validation
    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if not email or '@' not in email:
        return jsonify({"error": "Valid email required"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    result = auth_db.create_user(username, email, password)

    if result['success']:
        # Auto-verify and login
        auth_db.verify_email(result['verification_token'])
        auth_result = auth_db.authenticate(username, password)
        token = auth_db.create_session_token(auth_result['user']['id'])
        response = jsonify({"success": True, "message": "Account created successfully", "user": auth_result['user']})
        response.set_cookie('session_token', token, httponly=True, samesite='Lax', max_age=30*24*60*60)
        return response
    else:
        return jsonify({"error": result['error']}), 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    result = auth_db.authenticate(username, password)

    if result['success']:
        token = auth_db.create_session_token(result['user']['id'])

        response = jsonify({
            "success": True,
            "message": "Logged in successfully",
            "user": result['user']
        })
        response.set_cookie('session_token', token, httponly=True, samesite='Lax', max_age=30*24*60*60)
        return response
    else:
        return jsonify({"error": result['error']}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    token = request.cookies.get('session_token')

    if token:
        auth_db.delete_session(token)

    response = jsonify({"success": True, "message": "Logged out successfully"})
    response.set_cookie('session_token', '', expires=0)
    return response


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user"""
    return jsonify({
        "success": True,
        "user": request.current_user
    })


@app.route('/api/auth/verify', methods=['GET'])
def verify_email():
    """Verify email address via token from email link"""
    token = request.args.get('token')

    if not token:
        return jsonify({"error": "Verification token required"}), 400

    result = auth_db.verify_email(token)

    if result['success']:
        return jsonify({
            "success": True,
            "message": "Email verified successfully! You can now log in."
        })
    else:
        return jsonify({"error": result['error']}), 400


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


@app.route('/api/session/start', methods=['POST'])
@login_required
def start_session():
    """Create new session with master agent (requires authentication)"""
    session_id = str(uuid.uuid4())
    session = UnifiedSession(session_id)
    sessions[session_id] = session
    message_queues[session_id] = []

    logger.info(f"Session created: {session_id} for user: {request.current_user['username']}")
    return jsonify({
        "session_id": session_id,
        "status": "ready",
        "user": request.current_user['username']
    })


@app.route('/api/teach', methods=['POST'])
@login_required
def teach():
    """Unified teaching endpoint for all modes (requires authentication)"""
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
    """Unified SSE stream with pacing delays for cognitive absorption"""
    if session_id not in message_queues:
        return jsonify({"error": "Session not found"}), 404

    def generate():
        queue = message_queues[session_id]
        sent_count = 0
        heartbeat_count = 0
        last_msg_type = None

        while True:  # Keep stream alive indefinitely
            if len(queue) > sent_count:
                for msg in queue[sent_count:]:
                    current_msg_type = msg.get('type')

                    # Add pacing delay between tool outputs for cognitive absorption
                    if last_msg_type == 'output' and current_msg_type in ['action', 'teacher']:
                        import time
                        time.sleep(2.0)  # 2-second absorption delay after tool output

                    yield f"data: {json.dumps(msg)}\n\n"
                    sent_count += 1
                    last_msg_type = current_msg_type

                    # Don't close stream on complete - allow multiple teach requests
                heartbeat_count = 0
            else:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                heartbeat_count += 1
            import time
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    print("=" * 80)
    print("🎓 SPECIALIZED TEACHING SYSTEM - INTELLIGENT AGENT ROUTING")
    print("=" * 80)
    print("\n📱 Server: http://localhost:5000")
    print("\n🤖 SPECIALIZED AGENTS (Auto-routed):")
    print("  • 📚 EXPLAINER    - Teaches concepts, builds mental models")
    print("  • 🔍 REVIEWER     - Analyzes code, provides feedback")
    print("  • 🎯 CHALLENGER   - Creates practice problems")
    print("  • 📊 ASSESSOR     - Tests understanding, identifies gaps")
    print("\n🔧 13 TEACHING TOOLS:")
    print("  • 4 Visual Tools     - Diagrams & visualizations")
    print("  • 4 Concept Tools    - Examples & simulations")
    print("  • 5 Project Tools    - Live coding & review")
    print("\n🧠 COGNITIVE FEATURES:")
    print("  • Concept-based limits    (max 3 concepts per response)")
    print("  • Sequential tool chains  (each tool builds on previous)")
    print("  • Pacing delays           (2s absorption time)")
    print("  • Session-scoped memory   (.claude/sessions/{session_id}_knowledge.md)")
    print("\n🎯 INTELLIGENT ROUTING:")
    print("  'Explain X'        → Explainer Agent")
    print("  'Check my code'    → Reviewer Agent")
    print("  'Challenge me'     → Challenger Agent")
    print("  'Test me'          → Assessor Agent")
    print("\n✨ 4 Specialist Agents, 13 Tools, Infinite Learning")
    print("💡 Ctrl+C to stop\n")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
