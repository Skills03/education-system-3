#!/usr/bin/env python3
"""
Status line script for Claude Code - shows student learning metrics.
"""
import sys
import json
import os

# Read input from stdin
try:
    input_data = json.load(sys.stdin)
except:
    input_data = {}

# Extract Claude Code metrics
model = input_data.get("model", {}).get("display_name", "Claude")
context = input_data.get("context_window", {}).get("used_percentage", 0)
cost = input_data.get("cost", {}).get("total_cost_usd", 0)

# Try to get student progress
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.database import get_progress_summary, get_profile

    progress = get_progress_summary()
    profile = get_profile()

    mastered = progress.get("mastered", 0)
    practicing = progress.get("practicing", 0)
    success_rate = int(progress.get("success_rate", 0) * 100)
    interest = profile.get("interests", [""])[0] if profile.get("interests") else ""

    # Build status line
    status = f"🎓 {mastered} mastered | 📚 {practicing} practicing | ✅ {success_rate}%"
    if interest:
        status += f" | 🎮 {interest}"
except:
    status = f"📚 {model} | Context: {context:.0f}%"

print(status)
