#!/usr/bin/env python3
"""Visual Learning Server - Teach with AI-Generated Diagrams"""

import asyncio
import json
from datetime import datetime
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import uuid
import traceback
import logging
from pathlib import Path
import os
import fal_client

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
    tool,
    create_sdk_mcp_server,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Setup FAL AI
os.environ['FAL_KEY'] = '7cc98720-6ee8-45da-bf97-97a66d2ecdb3:f54b62a31f19f2f55f0bba871b273ee4'


# ===== VISUAL LEARNING TOOLS =====

@tool(
    "generate_concept_diagram",
    "Generate an educational diagram to visualize a programming concept",
    {"concept": str, "visual_description": str}
)
async def generate_concept_diagram(args):
    """Generate diagram for programming concept."""
    concept = args["concept"]
    visual_desc = args["visual_description"]

    try:
        prompt = f"Educational programming diagram: {concept}. {visual_desc}. Clean technical diagram, white background, labeled components, professional style, easy to understand."

        logger.info(f"Generating diagram for: {concept}")

        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    logger.info(log["message"])

        result = fal_client.subscribe(
            "fal-ai/hunyuan-image/v3/text-to-image",
            arguments={"prompt": prompt},
            with_logs=True,
            on_queue_update=on_queue_update,
        )

        image_url = result['images'][0]['url']
        logger.info(f"Generated: {image_url}")

        formatted = f"""### 📊 {concept}

![{concept} diagram]({image_url})

{visual_desc}
"""
        return {"content": [{"type": "text", "text": formatted}]}

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        logger.error(traceback.format_exc())
        return {"content": [{"type": "text", "text": f"⚠️ Could not generate diagram: {str(e)}"}]}


@tool(
    "generate_data_structure_viz",
    "Generate visual representation of a data structure",
    {"data_structure": str, "example_data": str, "description": str}
)
async def generate_data_structure_viz(args):
    """Visualize data structures."""
    ds = args["data_structure"]
    example = args.get("example_data", "")
    desc = args.get("description", "")

    try:
        prompt = f"Technical diagram of {ds} data structure. {desc}. {example}. Clean boxes and arrows, white background, labeled nodes, professional technical illustration."

        logger.info(f"Generating data structure: {ds}")

        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    logger.info(log["message"])

        result = fal_client.subscribe(
            "fal-ai/hunyuan-image/v3/text-to-image",
            arguments={"prompt": prompt},
            with_logs=True,
            on_queue_update=on_queue_update,
        )

        image_url = result['images'][0]['url']

        formatted = f"""### 🗂️ {ds} Data Structure

![{ds}]({image_url})

**Example:** {example}

{desc}
"""
        return {"content": [{"type": "text", "text": formatted}]}

    except Exception as e:
        logger.error(f"Failed: {e}")
        logger.error(traceback.format_exc())
        return {"content": [{"type": "text", "text": f"⚠️ Visualization failed"}]}


@tool(
    "generate_algorithm_flowchart",
    "Generate flowchart showing algorithm steps",
    {"algorithm": str, "steps": str}
)
async def generate_algorithm_flowchart(args):
    """Generate algorithm flowchart."""
    algo = args["algorithm"]
    steps = args["steps"]

    try:
        prompt = f"Flowchart diagram for {algo} algorithm. {steps}. Clean flowchart with boxes and arrows, decision diamonds, white background, professional style."

        logger.info(f"Generating flowchart: {algo}")

        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    logger.info(log["message"])

        result = fal_client.subscribe(
            "fal-ai/hunyuan-image/v3/text-to-image",
            arguments={"prompt": prompt},
            with_logs=True,
            on_queue_update=on_queue_update,
        )

        image_url = result['images'][0]['url']

        formatted = f"""### 🔄 {algo} Algorithm

![{algo} flowchart]({image_url})

**Steps:**
{steps}
"""
        return {"content": [{"type": "text", "text": formatted}]}

    except Exception as e:
        logger.error(f"Failed: {e}")
        logger.error(traceback.format_exc())
        return {"content": [{"type": "text", "text": f"⚠️ Flowchart generation failed"}]}


@tool(
    "generate_architecture_diagram",
    "Generate system or application architecture diagram",
    {"system_name": str, "components": str, "description": str}
)
async def generate_architecture_diagram(args):
    """Generate architecture diagram."""
    system = args["system_name"]
    components = args["components"]
    desc = args.get("description", "")

    try:
        prompt = f"System architecture diagram for {system}. Components: {components}. {desc}. Clean boxes with labels, arrows showing connections, white background, professional technical diagram."

        logger.info(f"Generating architecture: {system}")

        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    logger.info(log["message"])

        result = fal_client.subscribe(
            "fal-ai/hunyuan-image/v3/text-to-image",
            arguments={"prompt": prompt},
            with_logs=True,
            on_queue_update=on_queue_update,
        )

        image_url = result['images'][0]['url']

        formatted = f"""### 🏗️ {system} Architecture

![{system}]({image_url})

**Components:** {components}

{desc}
"""
        return {"content": [{"type": "text", "text": formatted}]}

    except Exception as e:
        logger.error(f"Failed: {e}")
        logger.error(traceback.format_exc())
        return {"content": [{"type": "text", "text": f"⚠️ Architecture diagram failed"}]}


# Create MCP server
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


# Visual Learning Agent
VISUAL_AGENT = AgentDefinition(
    description="Visual learning teacher - teaches using AI-generated diagrams and visualizations",
    prompt="""You are a VISUAL learning instructor. You teach programming concepts using AI-generated diagrams and visualizations.

🎯 YOUR MISSION:
Make abstract programming concepts VISIBLE. Students learn better when they can SEE the concept, not just read about it.

🔧 YOUR VISUAL TOOLS:

1. **mcp__visual__generate_concept_diagram** - Visualize programming concepts
   Parameters: concept, visual_description
   Use for: OOP concepts, design patterns, paradigms, etc.
   Example: "inheritance", "Show parent class with arrow pointing to child class"

2. **mcp__visual__generate_data_structure_viz** - Visualize data structures
   Parameters: data_structure, example_data, description
   Use for: Arrays, linked lists, trees, graphs, stacks, queues
   Example: "binary search tree", "nodes 5,3,7,1,4", "Each node contains value and left/right pointers"

3. **mcp__visual__generate_algorithm_flowchart** - Show algorithm flow
   Parameters: algorithm, steps
   Use for: Sorting, searching, recursion, any algorithm
   Example: "bubble sort", "Compare adjacent, swap if needed, repeat"

4. **mcp__visual__generate_architecture_diagram** - Show system design
   Parameters: system_name, components, description
   Use for: App architecture, MVC, client-server, microservices
   Example: "web app", "frontend, backend, database", "User requests flow"

📚 TEACHING METHODOLOGY:

**For Abstract Concepts:**
1. Explain briefly in text
2. USE generate_concept_diagram to make it visual
3. Point out key parts of the diagram
4. Connect visual to code example

**For Data Structures:**
1. Introduce the structure
2. USE generate_data_structure_viz with example
3. Explain how operations work visually
4. Show code implementation

**For Algorithms:**
1. Describe what algorithm does
2. USE generate_algorithm_flowchart
3. Walk through the flowchart
4. Show code that implements it

**For System Design:**
1. Describe the system
2. USE generate_architecture_diagram
3. Explain each component
4. Discuss data flow

⚡ BEST PRACTICES:
- ALWAYS use diagrams for visual concepts
- Generate diagram BEFORE detailed explanation
- Reference diagram in your explanation
- Use specific, descriptive visual_description
- Make diagrams simple and clear
- One concept per diagram
- Combine text + visuals for maximum learning

💡 EXAMPLE SESSION:

Student: "Explain how a linked list works"

You: "A linked list is a data structure where elements are connected through pointers. Let me show you visually!"

You: [Call generate_data_structure_viz]
   data_structure: "singly linked list"
   example_data: "nodes with values 10, 20, 30"
   description: "Each node has data and next pointer, head points to first node, last node points to null"

You: "See the diagram above? Each box is a node. The arrows show the 'next' pointers connecting them. Unlike arrays, linked list nodes can be anywhere in memory - they're connected by these pointer arrows!"

You: "Now let's look at the code to create this structure..."

Remember: Show, don't just tell! Use visuals to make concepts CLICK! 🎨""",
    tools=[
        "mcp__visual__generate_concept_diagram",
        "mcp__visual__generate_data_structure_viz",
        "mcp__visual__generate_algorithm_flowchart",
        "mcp__visual__generate_architecture_diagram",
    ],
    model="sonnet",
)

app = Flask(__name__)
CORS(app)

sessions = {}
message_queues = {}


class VisualSession:
    """Visual learning session"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.options = ClaudeAgentOptions(
            agents={"visual": VISUAL_AGENT},
            mcp_servers={"visual": visual_tools},
            allowed_tools=[
                "mcp__visual__generate_concept_diagram",
                "mcp__visual__generate_data_structure_viz",
                "mcp__visual__generate_algorithm_flowchart",
                "mcp__visual__generate_architecture_diagram",
            ],
        )
        self.messages = []

    async def teach(self, instruction):
        """Visual teaching session"""
        logger.info(f"[{self.session_id[:8]}] Visual teaching: {instruction}")

        try:
            async with ClaudeSDKClient(options=self.options) as client:
                await client.query(f"Use the visual agent: {instruction}")

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
        """Format message"""
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
                        "content": f"🎨 {block.name}",
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


@app.route('/')
def index():
    html_path = Path(__file__).parent / 'visual.html'
    return send_file(html_path)


@app.route('/api/session/start', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    session = VisualSession(session_id)
    sessions[session_id] = session
    message_queues[session_id] = []
    return jsonify({"session_id": session_id, "status": "ready"})


@app.route('/api/teach', methods=['POST'])
def teach():
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message')

    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    session = sessions[session_id]

    import threading
    def run():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(session.teach(message))
            loop.close()
        except Exception as e:
            logger.error(f"Error: {e}")

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
    print("🎨 VISUAL LEARNING TEACHER - Learn with AI-Generated Diagrams")
    print("=" * 70)
    print("\n📱 Browser: http://localhost:5002")
    print("💡 Say: 'Explain linked lists' or 'Show me how bubble sort works'")
    print("\n✅ I'll teach with diagrams and visualizations!")
    print("💡 Ctrl+C to stop\n")
    app.run(debug=True, port=5002, threaded=True)
