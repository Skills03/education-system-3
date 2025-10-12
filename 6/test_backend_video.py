#!/usr/bin/env python3
"""Comprehensive Backend Test for Video MCP Integration"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log(msg, color=Colors.RESET):
    print(f"{color}{msg}{Colors.RESET}")

def test_backend_video_integration():
    """Test video generation through full backend stack"""

    log("\n" + "="*80, Colors.BOLD)
    log("🎬 COMPREHENSIVE BACKEND VIDEO MCP INTEGRATION TEST", Colors.BOLD)
    log("="*80 + "\n", Colors.BOLD)

    BASE_URL = "http://localhost:5000"

    # Test 1: Server Health Check
    log("📡 Test 1: Server Health Check", Colors.CYAN)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            log("   ✅ Server is running", Colors.GREEN)
        else:
            log(f"   ❌ Server returned {response.status_code}", Colors.RED)
            return False
    except requests.exceptions.ConnectionError:
        log("   ❌ Server not running! Please start with: python3 server.py", Colors.RED)
        return False

    # Test 2: Create Session
    log("\n📡 Test 2: Create Teaching Session", Colors.CYAN)
    try:
        response = requests.post(f"{BASE_URL}/api/session/start")
        data = response.json()
        session_id = data.get('session_id')

        if session_id:
            log(f"   ✅ Session created: {session_id[:16]}...", Colors.GREEN)
        else:
            log("   ❌ Failed to create session", Colors.RED)
            return False
    except Exception as e:
        log(f"   ❌ Error: {e}", Colors.RED)
        return False

    # Test 3: Request Video Generation (Async)
    log("\n📡 Test 3: Request Video Generation via MCP Tool", Colors.CYAN)
    log("   Sending: 'Generate a short video showing how bubble sort works'", Colors.YELLOW)

    try:
        teach_request = {
            "session_id": session_id,
            "message": "Generate a short educational video showing how the bubble sort algorithm works. Make it about 5 seconds long."
        }

        response = requests.post(f"{BASE_URL}/api/teach", json=teach_request)
        data = response.json()

        if data.get('status') == 'processing':
            log("   ✅ Request accepted, processing started", Colors.GREEN)
        else:
            log(f"   ❌ Unexpected response: {data}", Colors.RED)
            return False

    except Exception as e:
        log(f"   ❌ Error: {e}", Colors.RED)
        return False

    # Test 4: Stream Response and Verify Video Generation
    log("\n📡 Test 4: Monitor SSE Stream for Video MCP Tool Execution", Colors.CYAN)
    log("   Connecting to event stream...", Colors.YELLOW)

    video_tool_detected = False
    video_output_detected = False
    video_url = None
    routing_info = None
    teacher_messages = []

    try:
        stream_url = f"{BASE_URL}/api/stream/{session_id}"

        with requests.get(stream_url, stream=True, timeout=120) as response:
            start_time = time.time()
            max_wait = 120  # 2 minutes max

            for line in response.iter_lines():
                if time.time() - start_time > max_wait:
                    log(f"   ⏱️ Timeout after {max_wait}s", Colors.YELLOW)
                    break

                if line:
                    line = line.decode('utf-8')

                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            msg_type = data.get('type')
                            content = data.get('content', '')

                            # Routing detection
                            if msg_type == 'routing':
                                agent = data.get('agent')
                                confidence = data.get('confidence', 0)
                                routing_info = f"{agent} ({confidence:.0%})"
                                log(f"   🎯 Routed to: {routing_info}", Colors.BLUE)

                            # Tool usage detection
                            elif msg_type == 'action':
                                log(f"   🔧 Tool Called: {content}", Colors.BLUE)
                                if 'video' in content.lower():
                                    video_tool_detected = True
                                    log(f"   ✅ VIDEO MCP TOOL DETECTED!", Colors.GREEN)

                            # Output detection (tool results)
                            elif msg_type == 'output':
                                if '<video' in content or '.mp4' in content or 'Video Details' in content:
                                    video_output_detected = True
                                    log(f"   ✅ VIDEO OUTPUT DETECTED!", Colors.GREEN)

                                    # Extract video URL
                                    if 'https://' in content and '.mp4' in content:
                                        start = content.find('https://')
                                        end = content.find('.mp4', start) + 4
                                        video_url = content[start:end]
                                        log(f"   📹 Video URL: {video_url}", Colors.CYAN)

                            # Teacher response
                            elif msg_type == 'teacher':
                                teacher_messages.append(content[:80])
                                log(f"   💬 Teacher: {content[:80]}...", Colors.YELLOW)

                            # Completion
                            elif msg_type == 'complete':
                                log(f"   ✅ Response complete", Colors.GREEN)
                                break

                            # Error
                            elif msg_type == 'error':
                                log(f"   ❌ Error: {content}", Colors.RED)
                                break

                        except json.JSONDecodeError:
                            continue

    except requests.exceptions.Timeout:
        log("   ⏱️ Stream timeout", Colors.YELLOW)
    except Exception as e:
        log(f"   ❌ Stream error: {e}", Colors.RED)
        return False

    # Test 5: Validation
    log("\n📊 Test 5: Validation Results", Colors.CYAN)

    results = {
        "Session Created": True,
        "Request Accepted": True,
        "Agent Routing": routing_info is not None,
        "Video Tool Called": video_tool_detected,
        "Video Generated": video_output_detected,
        "Video URL Retrieved": video_url is not None
    }

    for check, passed in results.items():
        status = "✅" if passed else "❌"
        color = Colors.GREEN if passed else Colors.RED
        log(f"   {status} {check}: {passed}", color)

    if video_url:
        log(f"\n   📹 Generated Video: {video_url}", Colors.CYAN)

    # Final verdict
    log("\n" + "="*80, Colors.BOLD)

    if all(results.values()):
        log("🎉 BACKEND VIDEO MCP INTEGRATION: FULLY OPERATIONAL!", Colors.GREEN + Colors.BOLD)
        log("="*80 + "\n", Colors.BOLD)
        return True
    else:
        failed = [k for k, v in results.items() if not v]
        log(f"❌ INTEGRATION TEST FAILED", Colors.RED + Colors.BOLD)
        log(f"   Failed checks: {', '.join(failed)}", Colors.RED)
        log("="*80 + "\n", Colors.BOLD)
        return False


def check_server_running():
    """Check if server is running, provide instructions if not"""
    try:
        response = requests.get("http://localhost:5000/", timeout=2)
        return True
    except:
        return False


if __name__ == "__main__":
    log("\n🚀 Starting Comprehensive Backend Video MCP Test\n", Colors.BOLD)

    # Check if server is running
    if not check_server_running():
        log("⚠️  Flask server not detected on port 5000", Colors.YELLOW)
        log("\n📝 To start the server:", Colors.CYAN)
        log("   cd /home/mahadev/Desktop/dev/education/6", Colors.CYAN)
        log("   python3 server.py\n", Colors.CYAN)
        log("Then run this test again.\n", Colors.YELLOW)
        sys.exit(1)

    # Run test
    success = test_backend_video_integration()

    sys.exit(0 if success else 1)
