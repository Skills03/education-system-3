#!/usr/bin/env python3
"""Test Image Generation - Generate a cat image"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("🐱 IMAGE GENERATION TEST - CAT IMAGE")
print("=" * 70)

# Create session
response = requests.post(f"{BASE_URL}/api/session/start")
session_id = response.json().get('session_id')
print(f"✅ Session: {session_id[:16]}...")

# Request cat image
teach_request = {
    "session_id": session_id,
    "message": "generate image of a cat"
}

print("\n📤 Sending request: 'generate image of a cat'")
response = requests.post(f"{BASE_URL}/api/teach", json=teach_request)
print(f"✅ Request sent: {response.json()}")

# Monitor stream
print("\n📡 Monitoring stream...")
stream_url = f"{BASE_URL}/api/stream/{session_id}"

tool_called = False
image_url = None
started = False

with requests.get(stream_url, stream=True, timeout=60) as response:
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    msg_type = data.get('type')
                    content = data.get('content', '')

                    if msg_type == 'routing':
                        print(f"\n🎯 {content}")
                        started = True

                    elif msg_type == 'action':
                        print(f"\n🔧 {content}")
                        if 'generate_image' in content.lower():
                            tool_called = True
                            print("   ✅ Image generation tool invoked!")

                    elif msg_type == 'output':
                        # Look for image URL
                        if 'https://' in content and ('.png' in content or '.jpg' in content or 'fal.media' in content):
                            # Extract URL from markdown
                            import re
                            urls = re.findall(r'https://[^\s\)]+\.(?:png|jpg|jpeg)', content)
                            if urls:
                                image_url = urls[0]
                                print(f"\n🖼️  IMAGE GENERATED!")
                                print(f"   URL: {image_url}")

                        # Print first 200 chars of output
                        preview = content[:200].replace('\n', ' ')
                        print(f"   Output preview: {preview}...")

                    elif msg_type == 'complete':
                        print(f"\n✅ Complete!")
                        break

                except Exception as e:
                    pass

# Results
print("\n" + "=" * 70)
print("📊 TEST RESULTS")
print("=" * 70)
print(f"  Tool Invoked: {'✅ generate_image' if tool_called else '❌ Not called'}")
print(f"  Image URL:    {'✅ ' + (image_url if image_url else 'Generated') if image_url else '❌ Not found'}")

if tool_called and image_url:
    print("\n🎉 SUCCESS! Image generation is working!")
    print(f"\n🔗 View your cat image:")
    print(f"   {image_url}")
else:
    print("\n⚠️  Issue detected - check logs above")
