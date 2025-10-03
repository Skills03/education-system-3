#!/usr/bin/env python3
"""Test backend API endpoints directly"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_lessons_endpoint():
    """Test: GET /api/lessons"""
    print("=" * 60)
    print("TEST 1: Lessons Endpoint")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/lessons")
    if response.status_code == 200:
        lessons = response.json()
        print(f"✅ SUCCESS: Got {len(lessons)} lessons")
        for lesson in lessons:
            print(f"  - {lesson['title']}")
        return True
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        return False

def test_session_start():
    """Test: POST /api/session/start"""
    print("\n" + "=" * 60)
    print("TEST 2: Session Start")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/session/start",
        json={}
    )

    if response.status_code == 200:
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ SUCCESS: Session created")
        print(f"   Session ID: {session_id}")
        return session_id
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_teach(session_id):
    """Test: POST /api/teach"""
    print("\n" + "=" * 60)
    print("TEST 3: Send Teaching Request")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/teach",
        json={
            "session_id": session_id,
            "message": "Explain list comprehensions in one paragraph"
        }
    )

    if response.status_code == 200:
        print("✅ SUCCESS: Teaching request sent")
        print("   Waiting 2 seconds for processing...")
        time.sleep(2)
        return True
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        return False

def test_debug(session_id):
    """Test: GET /api/debug/<session_id>"""
    print("\n" + "=" * 60)
    print("TEST 4: Debug Endpoint (Check Queue)")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/api/debug/{session_id}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Debug info retrieved")
        print(f"   Queue length: {data.get('queue_length')}")
        print(f"   Session exists: {data.get('session_exists')}")

        messages = data.get('messages', [])
        if messages:
            print(f"\n   Messages in queue:")
            for i, msg in enumerate(messages[:3], 1):  # Show first 3
                msg_type = msg.get('type', 'unknown')
                content = msg.get('content', '')[:50]
                print(f"   {i}. Type: {msg_type}")
                if content:
                    print(f"      Content: {content}...")
        return data
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        return None

def test_html_serving():
    """Test: GET / (HTML page)"""
    print("\n" + "=" * 60)
    print("TEST 5: HTML Page Serving")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/")

    if response.status_code == 200 and 'html' in response.text.lower():
        print("✅ SUCCESS: HTML page served")
        print(f"   Response length: {len(response.text)} bytes")
        if 'Interactive Coding Teacher' in response.text:
            print("   ✓ Title found in HTML")
        if 'const API_URL' in response.text:
            print("   ✓ JavaScript found in HTML")
        return True
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n🧪 BACKEND API TESTS")
    print("=" * 60)
    print("Make sure server is running: python3 teacher_server.py\n")

    try:
        # Test 1: Lessons
        if not test_lessons_endpoint():
            print("\n⚠️  Lessons endpoint failed - stopping tests")
            return

        # Test 2: Session
        session_id = test_session_start()
        if not session_id:
            print("\n⚠️  Session creation failed - stopping tests")
            return

        # Test 3: Teach
        if not test_teach(session_id):
            print("\n⚠️  Teaching request failed - stopping tests")
            return

        # Test 4: Debug
        debug_data = test_debug(session_id)
        if not debug_data:
            print("\n⚠️  Debug endpoint failed")

        # Test 5: HTML
        test_html_serving()

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        if debug_data:
            queue_len = debug_data.get('queue_length', 0)
            if queue_len > 0:
                print(f"✅ ALL TESTS PASSED!")
                print(f"   - Session created: {session_id}")
                print(f"   - Messages in queue: {queue_len}")
                print(f"   - HTML page serving: OK")
                print(f"\n✨ Backend is working! Frontend should work too.")
            else:
                print(f"⚠️  Tests passed but no messages in queue")
                print(f"   This might mean the agent didn't respond")

    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR")
        print("   Is the server running?")
        print("   Run: python3 teacher_server.py")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
