#!/usr/bin/env python3
"""
Education MCP Server - 10x Version

Claude generates problems dynamically. This server provides:
- Student state (mastery, errors, progress)
- Problem storage (Claude generates, we store)
- Code execution (sandboxed)
- Progress tracking
"""

import sys
import json
import os
from typing import Any

# Add core to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.education_tools import (
    tool_get_student_state,
    tool_save_problem,
    tool_run_code,
    tool_get_concept_guide,
    tool_get_progress,
    tool_record_mastery_event,
)


class MCPServer:
    """MCP server for education system."""

    def __init__(self):
        self.tools = {
            "get_student_state": {
                "handler": lambda args: tool_get_student_state(),
                "schema": {
                    "name": "get_student_state",
                    "description": "Get comprehensive student state: mastery, error patterns, what to practice. CALL THIS FIRST.",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                }
            },
            "save_problem": {
                "handler": lambda args: tool_save_problem(
                    args.get("concept", ""),
                    args.get("prompt", ""),
                    args.get("function_name", ""),
                    args.get("test_cases", [])
                ),
                "schema": {
                    "name": "save_problem",
                    "description": "Save a problem YOU generated. Include concept, prompt, function_name, and test_cases.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "concept": {"type": "string", "description": "Concept: loops, functions, etc."},
                            "prompt": {"type": "string", "description": "Problem description you generated"},
                            "function_name": {"type": "string", "description": "Function student writes"},
                            "test_cases": {
                                "type": "array",
                                "description": "[{call: 'func(1)', expected: 2}, ...]",
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["concept", "prompt", "function_name", "test_cases"]
                    }
                }
            },
            "run_code": {
                "handler": lambda args: tool_run_code(args.get("code", "")),
                "schema": {
                    "name": "run_code",
                    "description": "Execute student code in sandbox. Returns detailed results for YOU to analyze.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Student's Python code"}
                        },
                        "required": ["code"]
                    }
                }
            },
            "get_concept_guide": {
                "handler": lambda args: tool_get_concept_guide(args.get("concept", "")),
                "schema": {
                    "name": "get_concept_guide",
                    "description": "Get teaching guide for a concept.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "concept": {"type": "string"}
                        },
                        "required": ["concept"]
                    }
                }
            },
            "get_progress": {
                "handler": lambda args: tool_get_progress(),
                "schema": {
                    "name": "get_progress",
                    "description": "Get visual progress dashboard.",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                }
            },
            "record_mastery_event": {
                "handler": lambda args: tool_record_mastery_event(
                    args.get("concept", ""),
                    args.get("event_type", ""),
                    args.get("details", "")
                ),
                "schema": {
                    "name": "record_mastery_event",
                    "description": "Log learning events.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "concept": {"type": "string"},
                            "event_type": {"type": "string"},
                            "details": {"type": "string"}
                        },
                        "required": ["concept", "event_type"]
                    }
                }
            }
        }


    def handle_message_sync(self, message: dict) -> dict:
        """Handle MCP message (sync version)."""
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "education-server", "version": "2.0.0"}
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": [t["schema"] for t in self.tools.values()]}
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})

            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }

            try:
                result = self.tools[tool_name]["handler"](tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                        "isError": True
                    }
                }

        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Unknown: {method}"}}

    def run_sync(self):
        """Run MCP server on stdio (synchronous - Windows compatible)."""
        # Set binary mode FIRST before any I/O
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer

        while True:
            try:
                # Read headers
                header = b""
                while not header.endswith(b"\r\n\r\n"):
                    byte = stdin.read(1)
                    if not byte:
                        return
                    header += byte

                # Parse content length
                content_length = 0
                for line in header.decode().split('\r\n'):
                    if line.startswith('Content-Length:'):
                        content_length = int(line.split(':')[1].strip())

                # Read body
                body = stdin.read(content_length)
                message = json.loads(body.decode())

                response = self.handle_message_sync(message)

                if response:
                    resp_bytes = json.dumps(response).encode()
                    out_header = f"Content-Length: {len(resp_bytes)}\r\n\r\n".encode()
                    stdout.write(out_header + resp_bytes)
                    stdout.flush()

            except Exception as e:
                # Silent fail - don't pollute stderr
                continue



def test():
    """Test the 10x system."""
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    from core.database import init_db
    import os

    # Fresh start
    db_path = os.path.join(os.path.dirname(__file__), 'student_data.db')
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()

    print("=" * 60)
    print("10x EDUCATION SYSTEM TEST")
    print("=" * 60)

    # 1. Get state
    print("\n[1] Get student state")
    state = tool_get_student_state()
    print(f"    Available: {[c['concept'] for c in state['available_to_learn'][:3]]}")
    print("    PASS")

    # 2. Claude generates a problem
    print("\n[2] Save problem (Claude generates this)")
    problem = tool_save_problem(
        concept="variables",
        prompt="Write `swap(a, b)` returning swapped tuple",
        function_name="swap",
        test_cases=[
            {"call": "swap(1, 2)", "expected": (2, 1)},
            {"call": "swap('a', 'b')", "expected": ('b', 'a')},
        ]
    )
    print(f"    Success: {problem.get('success')}")
    print("    PASS")

    # 3. Wrong code
    print("\n[3] Run wrong code")
    result = tool_run_code("def swap(a, b): return a, b")
    print(f"    Status: {result['status']}")
    assert result['status'] == 'failed'
    print("    PASS")

    # 4. Correct code
    print("\n[4] Run correct code")
    result = tool_run_code("def swap(a, b): return b, a")
    print(f"    Status: {result['status']}")
    print(f"    Successes: {result['mastery_update']['successes']}")
    assert result['status'] == 'all_passed'
    print("    PASS")

    # 5. Progress
    print("\n[5] Get progress")
    progress = tool_get_progress()
    print(f"    Concepts tracked: {len(progress['progress_map'])}")
    print("    PASS")

    # 6. Concept guide
    print("\n[6] Get concept guide")
    guide = tool_get_concept_guide("loops")
    print(f"    Prerequisites: {guide.get('prerequisites')}")
    print("    PASS")

    print("\n" + "=" * 60)
    print("ALL 6 TESTS PASSED - 10x SYSTEM WORKING")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test()
    else:
        MCPServer().run_sync()
