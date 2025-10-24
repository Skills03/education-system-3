#!/usr/bin/env python3
"""Test actual running server via HTTP API"""

import requests
import json
import time

BASE_URL = "http://localhost:5002"

def test_velocity_mode():
    """Test velocity mode: Build portfolio fast"""
    print("=" * 80)
    print("TEST 1: VELOCITY MODE (via HTTP API)")
    print("=" * 80)

    # Start session
    resp = requests.post(f"{BASE_URL}/api/session/start")
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}\n")

    # Send build request
    requests.post(f"{BASE_URL}/api/teach", json={
        "session_id": session_id,
        "message": "Build me a portfolio for Alex the designer"
    })

    # Stream results
    print("Streaming response...\n")
    time.sleep(2)  # Let it start

    resp = requests.get(f"{BASE_URL}/api/session/{session_id}/history")
    messages = resp.json()["messages"]

    tool_calls = [m for m in messages if m.get("type") == "action"]
    print(f"Tools called: {len(tool_calls)}")
    for msg in tool_calls:
        print(f"  - {msg['content']}")

    print(f"\n✓ Velocity mode: {len(tool_calls)} tool calls\n")
    return len(tool_calls)


def test_tutorial_mode():
    """Test tutorial mode: Teach step by step"""
    print("=" * 80)
    print("TEST 2: TUTORIAL MODE (via HTTP API)")
    print("=" * 80)

    # Start session
    resp = requests.post(f"{BASE_URL}/api/session/start")
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}\n")

    # Send tutorial request
    requests.post(f"{BASE_URL}/api/teach", json={
        "session_id": session_id,
        "message": "Teach me how to build a portfolio step by step"
    })

    # Stream results and count steps
    print("Streaming response (this takes 2-3 min for 15 steps)...\n")

    steps_found = 0
    for i in range(60):  # Check for 60 seconds
        time.sleep(1)
        resp = requests.get(f"{BASE_URL}/api/session/{session_id}/history")
        messages = resp.json()["messages"]

        # Count add_code_step tool calls
        tool_calls = [m for m in messages if m.get("type") == "action"]
        add_code_steps = [t for t in tool_calls if "add_code_step" in t.get("content", "")]

        if len(add_code_steps) > steps_found:
            steps_found = len(add_code_steps)
            print(f"  🏗️  Step {steps_found} completed")

        # Check if complete
        if any(m.get("type") == "complete" for m in messages):
            break

    print(f"\n✓ Tutorial mode: {steps_found} incremental steps\n")
    return steps_found


if __name__ == "__main__":
    print("\n🧪 TESTING ACTUAL SERVER (HTTP API)\n")
    print("Server: http://localhost:5002")
    print("Expected: Velocity=3 tools, Tutorial=12-15 steps\n")

    velocity_tools = test_velocity_mode()
    time.sleep(5)  # Gap between tests
    tutorial_steps = test_tutorial_mode()

    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Velocity mode: {velocity_tools} tool calls (expected 3)")
    print(f"Tutorial mode: {tutorial_steps} steps (expected 12-15)")

    if velocity_tools >= 2 and tutorial_steps >= 10:
        print("\n✅ BOTH MODES WORKING!")
    elif velocity_tools >= 2:
        print("\n⚠️  Velocity works, tutorial needs debugging")
    else:
        print("\n❌ Both modes need debugging")
