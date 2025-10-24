#!/usr/bin/env python3
"""Standalone MCP server runner for app_builder tools."""

import asyncio
import sys
import json
from tools.app_building_tools import (
    list_app_templates,
    customize_app_template,
    generate_client_proposal,
)

async def main():
    """Run app_builder MCP server in stdio mode."""
    # Read from stdin, write to stdout for MCP protocol
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            request = json.loads(line)

            # Handle list_tools request
            if request.get("method") == "tools/list":
                response = {
                    "tools": [
                        {
                            "name": "list_app_templates",
                            "description": "Show available app templates students can customize and sell",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "customize_app_template",
                            "description": "Customize app template for client",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "template_name": {"type": "string"},
                                    "client_name": {"type": "string"},
                                    "customizations": {"type": "string"}
                                },
                                "required": ["template_name", "client_name", "customizations"]
                            }
                        },
                        {
                            "name": "generate_client_proposal",
                            "description": "Generate professional proposal for client",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "client_name": {"type": "string"},
                                    "app_type": {"type": "string"},
                                    "features": {"type": "string"},
                                    "price": {"type": "number"}
                                },
                                "required": ["client_name", "app_type", "features", "price"]
                            }
                        }
                    ]
                }
                print(json.dumps(response), flush=True)

            # Handle tool call requests
            elif request.get("method") == "tools/call":
                tool_name = request["params"]["name"]
                args = request["params"]["arguments"]

                if tool_name == "list_app_templates":
                    result = await list_app_templates({})
                elif tool_name == "customize_app_template":
                    result = await customize_app_template(args)
                elif tool_name == "generate_client_proposal":
                    result = await generate_client_proposal(args)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                response = {"content": result.get("content", [])}
                print(json.dumps(response), flush=True)

        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
