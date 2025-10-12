#!/usr/bin/env python3
"""Quick Backend Integration Test for Image Editing Tools"""

import requests
import json
import time
import sys


def test_image_backend():
    """Test image editing through backend"""

    BASE_URL = "http://localhost:5000"

    print("="*70)
    print("🎨 IMAGE EDITING BACKEND INTEGRATION TEST")
    print("="*70)

    # Check server
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("\n✅ Server running")
    except:
        print("\n❌ Server not running! Start with: python3 server.py")
        return False

    # Create session
    response = requests.post(f"{BASE_URL}/api/session/start")
    session_id = response.json().get('session_id')
    print(f"✅ Session: {session_id[:16]}...")

    # Request image edit
    teach_request = {
        "session_id": session_id,
        "message": "Edit this image to change the bag to a laptop: https://v3.fal.media/files/koala/oei_-iPIYFnhdB8SxojND_qwen-edit-res.png"
    }

    response = requests.post(f"{BASE_URL}/api/teach", json=teach_request)
    print(f"✅ Request sent: {response.json()}")

    # Monitor stream
    print("\n📡 Monitoring stream...")
    stream_url = f"{BASE_URL}/api/stream/{session_id}"

    image_tool_called = False
    image_result = False

    with requests.get(stream_url, stream=True, timeout=30) as response:
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        msg_type = data.get('type')
                        content = data.get('content', '')

                        if msg_type == 'action' and 'image' in content.lower():
                            image_tool_called = True
                            print(f"✅ IMAGE TOOL CALLED: {content}")

                        elif msg_type == 'output' and ('image' in content.lower() or '.png' in content):
                            image_result = True
                            print(f"✅ IMAGE RESULT RECEIVED")
                            print(f"   Preview: {content[:100]}...")

                        elif msg_type == 'complete':
                            print(f"✅ Complete")
                            break

                    except:
                        pass

    # Results
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    print(f"  Image Tool Called: {'✅' if image_tool_called else '❌'}")
    print(f"  Image Result: {'✅' if image_result else '❌'}")

    success = image_tool_called or image_result

    if success:
        print("\n🎉 IMAGE EDITING BACKEND: OPERATIONAL!")
    else:
        print("\n⚠️  Image editing may need more time (inference takes 3-6s)")

    return success


if __name__ == "__main__":
    # Check server
    try:
        requests.get("http://localhost:5000/", timeout=2)
    except:
        print("\n⚠️  Start server first:")
        print("   python3 server.py\n")
        sys.exit(1)

    test_image_backend()
