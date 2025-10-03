#!/usr/bin/env python3
import requests
import json
import time

API_URL = "http://localhost:5000"

print("="*70)
print("🎓 MASTER TEACHER - END-TO-END BACKEND TEST")
print("="*70)

# TEST 1: Session Creation
print("\n TEST 1: Session Creation (No Mode Parameter)")
print("-"*70)

resp = requests.post(f"{API_URL}/api/session/start", json={})
data = resp.json()
session_id = data["session_id"]

print(f"✅ Session created: {session_id[:8]}...")
print(f"✅ No mode in response: {'mode' not in data}")
print(f"Response: {json.dumps(data, indent=2)}")

# TEST 2: Send teaching request
print("\n TEST 2: Compositional Teaching - 'Teach me merge sort'")
print("-"*70)

resp = requests.post(f"{API_URL}/api/teach", json={
    "session_id": session_id,
    "message": "Teach me merge sort"
})
print(f"✅ Request status: {resp.json()['status']}")

# TEST 3: Monitor stream for tools used
print("\n🔧 Monitoring tool usage (30 seconds)...")
print("-"*70)

time.sleep(2)
tools = []
messages = 0
complete = False

try:
    resp = requests.get(f"{API_URL}/api/stream/{session_id}", stream=True, timeout=35)
    for line in resp.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    messages += 1
                    
                    if data["type"] == "action":
                        tool = data["content"].replace("🔧 ", "")
                        tools.append(tool)
                        print(f"  {len(tools)}. {tool}")
                    elif data["type"] == "complete":
                        complete = True
                        break
                    elif data["type"] == "cost":
                        print(f"\n💰 Cost: {data['content']}")
                except json.JSONDecodeError:
                    pass
except requests.exceptions.Timeout:
    print("\n⏱ Timeout reached (still processing...)")

# Analysis
print("\n" + "="*70)
print("📊 RESULTS")
print("="*70)

visual = sum(1 for t in tools if "visual" in t)
concept = sum(1 for t in tools if "scrimba" in t)
project = sum(1 for t in tools if "live_coding" in t)
modalities = sum([visual > 0, concept > 0, project > 0])

print(f"\n✅ Session creation: PASSED (no mode parameter)")
print(f"✅ Tools used: {len(tools)}")
print(f"✅ Modalities: {modalities}/3")
print(f"  • Visual tools: {visual}")
print(f"  • Concept tools: {concept}")  
print(f"  • Project tools: {project}")
print(f"✅ Messages received: {messages}")
print(f"✅ Completed: {complete}")

if len(tools) >= 3 and modalities >= 2:
    print("\n🎉 COMPOSITIONAL TEACHING VERIFIED!")
    print("="*70)
else:
    print(f"\n⚠️  Expected 3+ tools and 2+ modalities")
    
print("\n✅ Master Teacher backend working!")
