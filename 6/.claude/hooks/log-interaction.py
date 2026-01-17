#!/usr/bin/env python3
"""
Hook: Logs interactions for learning analytics.
Used with PostToolUse to track what's happening.
"""

import sys
import json
import os
from datetime import datetime

# Read input from stdin
try:
    input_data = json.load(sys.stdin)
except:
    input_data = {}

tool_name = input_data.get("tool_name", "unknown")
tool_input = input_data.get("tool_input", {})

# Log to file
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
os.makedirs(log_dir, exist_ok=True)

log_entry = {
    "timestamp": datetime.now().isoformat(),
    "tool": tool_name,
    "input_summary": str(tool_input)[:200]
}

log_file = os.path.join(log_dir, "interactions.jsonl")
with open(log_file, "a") as f:
    f.write(json.dumps(log_entry) + "\n")

# Don't block
sys.exit(0)
