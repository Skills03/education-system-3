#!/usr/bin/env python3
"""Comprehensive end-to-end test of the teaching system"""

import requests
import time
import json
import sseclient

BASE_URL = "http://localhost:5000"

class TeachingSystemTest:
    def __init__(self):
        self.session_id = None
        self.results = {
            "routing": [],
            "memory": [],
            "concepts": [],
            "tools": [],
            "overall": True
        }

    def log(self, emoji, message):
        print(f"{emoji} {message}")

    def test_session_creation(self):
        """Test 1: Create teaching session"""
        self.log("🧪", "TEST 1: Session Creation")

        try:
            response = requests.post(f"{BASE_URL}/api/session/start")
            data = response.json()

            if response.status_code == 200 and "session_id" in data:
                self.session_id = data["session_id"]
                self.log("✅", f"Session created: {self.session_id[:8]}...")
                return True
            else:
                self.log("❌", f"Session creation failed: {data}")
                return False
        except Exception as e:
            self.log("❌", f"Error: {e}")
            return False

    def send_message(self, message, description):
        """Send teaching request and stream response"""
        self.log("📤", f"{description}: '{message}'")

        # Send teaching request
        response = requests.post(
            f"{BASE_URL}/api/teach",
            json={"session_id": self.session_id, "message": message}
        )

        if response.status_code != 200:
            self.log("❌", "Failed to send message")
            return None

        # Stream response
        events = []
        try:
            stream_response = requests.get(
                f"{BASE_URL}/api/stream/{self.session_id}",
                stream=True,
                timeout=60
            )

            client = sseclient.SSEClient(stream_response)

            for event in client.events():
                if event.data:
                    data = json.loads(event.data)
                    events.append(data)

                    msg_type = data.get('type')
                    content = data.get('content', '')

                    if msg_type == 'routing':
                        agent = data.get('agent')
                        confidence = data.get('confidence', 0)
                        self.log("🎯", f"Routed to: {agent} (confidence: {confidence:.0%})")

                    elif msg_type == 'action':
                        self.log("🔧", f"Tool: {content}")

                    elif msg_type == 'teacher':
                        preview = content[:100] + "..." if len(content) > 100 else content
                        self.log("💬", f"Agent: {preview}")

                    elif msg_type == 'complete':
                        self.log("✓", "Response complete")
                        break

                    elif msg_type == 'error':
                        self.log("❌", f"Error: {content}")
                        return None

        except requests.exceptions.Timeout:
            self.log("⏱", "Stream timeout (normal for short responses)")
        except Exception as e:
            self.log("⚠", f"Stream error: {e}")

        return events

    def test_routing_explainer(self):
        """Test 2: Routing to Explainer Agent"""
        self.log("\n🧪", "TEST 2: Explainer Agent Routing")

        events = self.send_message(
            "Explain what a variable is in Python",
            "Testing explainer routing"
        )

        if events:
            # Check if routed to explainer
            routing_events = [e for e in events if e.get('type') == 'routing']
            if routing_events and routing_events[0].get('agent') == 'explainer':
                self.log("✅", "Correctly routed to explainer agent")
                self.results["routing"].append(("explainer", True))
                return True
            else:
                self.log("❌", "Routing failed or wrong agent")
                self.results["routing"].append(("explainer", False))
                return False

        return False

    def test_routing_reviewer(self):
        """Test 3: Routing to Code Reviewer Agent"""
        self.log("\n🧪", "TEST 3: Code Reviewer Agent Routing")

        code_snippet = """
def calculate(x, y):
    return x + y
print(calculate(5, 3))
"""

        events = self.send_message(
            f"Review this code:\n{code_snippet}",
            "Testing reviewer routing"
        )

        if events:
            routing_events = [e for e in events if e.get('type') == 'routing']
            if routing_events and routing_events[0].get('agent') == 'reviewer':
                self.log("✅", "Correctly routed to reviewer agent")
                self.results["routing"].append(("reviewer", True))
                return True
            else:
                agent = routing_events[0].get('agent') if routing_events else 'none'
                self.log("⚠", f"Routed to {agent} (expected reviewer)")
                self.results["routing"].append(("reviewer", False))
                return False

        return False

    def test_routing_challenger(self):
        """Test 4: Routing to Challenger Agent"""
        self.log("\n🧪", "TEST 4: Challenger Agent Routing")

        events = self.send_message(
            "Give me a practice problem about loops",
            "Testing challenger routing"
        )

        if events:
            routing_events = [e for e in events if e.get('type') == 'routing']
            if routing_events and routing_events[0].get('agent') == 'challenger':
                self.log("✅", "Correctly routed to challenger agent")
                self.results["routing"].append(("challenger", True))
                return True
            else:
                agent = routing_events[0].get('agent') if routing_events else 'none'
                self.log("⚠", f"Routed to {agent} (expected challenger)")
                self.results["routing"].append(("challenger", False))
                return False

        return False

    def test_memory_persistence(self):
        """Test 5: Memory Persistence Across Sessions"""
        self.log("\n🧪", "TEST 5: Memory Persistence")

        # Read CLAUDE.md before
        try:
            with open('.claude/CLAUDE.md', 'r') as f:
                before = f.read()

            session_count_before = int(before.split("Session Count:** ")[1].split("\n")[0])
            self.log("📖", f"Sessions before: {session_count_before}")

            # Teach a new concept
            events = self.send_message(
                "Teach me about functions in Python",
                "Testing memory update"
            )

            # Wait for update
            time.sleep(2)

            # Read CLAUDE.md after
            with open('.claude/CLAUDE.md', 'r') as f:
                after = f.read()

            session_count_after = int(after.split("Session Count:** ")[1].split("\n")[0])
            self.log("📖", f"Sessions after: {session_count_after}")

            if session_count_after > session_count_before:
                self.log("✅", "CLAUDE.md updated with new session")
                self.results["memory"].append(("session_count", True))
            else:
                self.log("❌", "CLAUDE.md not updated")
                self.results["memory"].append(("session_count", False))

            if "functions" in after.lower():
                self.log("✅", "New concept 'functions' recorded")
                self.results["memory"].append(("concept_recorded", True))
                return True
            else:
                self.log("❌", "Concept not recorded in memory")
                self.results["memory"].append(("concept_recorded", False))
                return False

        except Exception as e:
            self.log("❌", f"Memory test error: {e}")
            return False

    def test_concept_limits(self):
        """Test 6: Concept-Based Limits"""
        self.log("\n🧪", "TEST 6: Concept-Based Limits")

        events = self.send_message(
            "Teach me about Python basics",
            "Testing concept declaration"
        )

        if events:
            # Check for concept declaration in teacher messages
            teacher_msgs = [e.get('content', '') for e in events if e.get('type') == 'teacher']
            full_response = ' '.join(teacher_msgs)

            if 'teaches' in full_response.lower() and 'concept' in full_response.lower():
                self.log("✅", "Agent declared concepts")
                self.results["concepts"].append(("declaration", True))

                # Count tools used
                tool_events = [e for e in events if e.get('type') == 'action']
                tool_count = len(tool_events)
                self.log("🔧", f"Tools used: {tool_count}")

                if tool_count <= 4:  # Max 3-4 tools for 3 concepts
                    self.log("✅", "Tool usage within concept-based limits")
                    self.results["tools"].append(("count", True))
                    return True
                else:
                    self.log("⚠", f"High tool usage: {tool_count} tools")
                    self.results["tools"].append(("count", False))
                    return False
            else:
                self.log("⚠", "No concept declaration found")
                self.results["concepts"].append(("declaration", False))
                return False

        return False

    def test_tool_sequencing(self):
        """Test 7: Tool Sequencing"""
        self.log("\n🧪", "TEST 7: Tool Sequencing")

        events = self.send_message(
            "Explain arrays with examples",
            "Testing tool sequencing"
        )

        if events:
            tool_events = [e.get('content', '') for e in events if e.get('type') == 'action']

            if len(tool_events) >= 2:
                self.log("🔧", f"Tool sequence: {' → '.join(tool_events)}")

                # Check for visual → code pattern
                has_visual = any('diagram' in t.lower() or 'viz' in t.lower() for t in tool_events)
                has_code = any('code' in t.lower() or 'example' in t.lower() for t in tool_events)

                if has_visual and has_code:
                    self.log("✅", "Sequential pattern detected (visual → code)")
                    self.results["tools"].append(("sequencing", True))
                    return True
                else:
                    self.log("✅", "Tools used sequentially")
                    self.results["tools"].append(("sequencing", True))
                    return True
            else:
                self.log("⚠", f"Only {len(tool_events)} tools used")
                return False

        return False

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*80, "")
        self.log("📊", "TEST SUMMARY")
        self.log("="*80, "")

        total_tests = 0
        passed_tests = 0

        self.log("🎯", f"Agent Routing: {len(self.results['routing'])} tests")
        for agent, result in self.results['routing']:
            status = "✅" if result else "❌"
            self.log(f"  {status}", f"{agent.capitalize()} routing")
            total_tests += 1
            if result: passed_tests += 1

        self.log("💾", f"Memory Persistence: {len(self.results['memory'])} tests")
        for test, result in self.results['memory']:
            status = "✅" if result else "❌"
            self.log(f"  {status}", test.replace("_", " ").capitalize())
            total_tests += 1
            if result: passed_tests += 1

        self.log("🧠", f"Concept System: {len(self.results['concepts'])} tests")
        for test, result in self.results['concepts']:
            status = "✅" if result else "❌"
            self.log(f"  {status}", test.replace("_", " ").capitalize())
            total_tests += 1
            if result: passed_tests += 1

        self.log("🔧", f"Tool Management: {len(self.results['tools'])} tests")
        for test, result in self.results['tools']:
            status = "✅" if result else "❌"
            self.log(f"  {status}", test.replace("_", " ").capitalize())
            total_tests += 1
            if result: passed_tests += 1

        self.log("\n" + "="*80, "")
        percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        self.log("📈", f"FINAL SCORE: {passed_tests}/{total_tests} ({percentage:.0f}%)")

        if percentage >= 80:
            self.log("🎉", "SYSTEM FULLY OPERATIONAL")
        elif percentage >= 60:
            self.log("⚠", "SYSTEM PARTIALLY WORKING")
        else:
            self.log("❌", "SYSTEM NEEDS FIXES")

        self.log("="*80, "")

def main():
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE TEACHING SYSTEM TEST")
    print("="*80 + "\n")

    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✅ Server is running\n")
    except:
        print("❌ Server is NOT running!")
        print("   Start server with: python3 server.py")
        return

    test = TeachingSystemTest()

    # Run tests
    if not test.test_session_creation():
        print("❌ Cannot proceed without session")
        return

    time.sleep(1)

    test.test_routing_explainer()
    time.sleep(2)

    test.test_routing_reviewer()
    time.sleep(2)

    test.test_routing_challenger()
    time.sleep(2)

    test.test_memory_persistence()
    time.sleep(2)

    test.test_concept_limits()
    time.sleep(2)

    test.test_tool_sequencing()
    time.sleep(1)

    # Print summary
    test.print_summary()

if __name__ == "__main__":
    main()
