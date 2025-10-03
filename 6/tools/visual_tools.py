"""Visual Learning Tools - Generate AI diagrams"""

import logging
import traceback
import fal_client
from claude_agent_sdk import tool

logger = logging.getLogger(__name__)


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
