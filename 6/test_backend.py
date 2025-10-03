#!/usr/bin/env python3
"""End-to-end backend test for Master Teacher"""

import requests
import json
import time
import sseclient

API_URL = "http://localhost:5000"

def test_session_creation():
    """Test 1: Session creation without mode parameter"""
    print("\n" + "="*70)
    print("TEST 1: Session Creation (No Mode Parameter)")
    print("="*70)
    
    response = requests.post(f"{API_URL}/api/session/start", json={})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "status" in data
    assert data["status"] == "ready"
    assert "mode" not in data  # Should NOT have mode!
    
    print(f"✅ Session created: {data['session_id'][:8]}...")
    print(f"✅ No mode parameter (unified master agent)")
    return data["session_id"]

def test_compositional_teaching(session_id, request):
    """Test 2: Compositional multi-tool usage"""
    print("\n" + "="*70)
    print(f"TEST 2: Compositional Teaching - '{request}'")
    print("="*70)
    
    # Send teach request
    response = requests.post(f"{API_URL}/api/teach", json={
        "session_id": session_id,
        "message": request
    })
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    print(f"✅ Request sent and processing")
    
    # Monitor SSE stream
    time.sleep(2)
    url = f"{API_URL}/api/stream/{session_id}"
    response = requests.get(url, stream=True, timeout=90)
    client = sseclient.SSEClient(response)
    
    tools_used = []
    message_count = 0
    has_teacher = False
    has_output = False
    has_cost = False
    
    for event in client.events():
        try:
            data = json.loads(event.data)
            message_count += 1
            
            if data["type"] == "action":
                tool_name = data["content"].replace("🔧 ", "")
                tools_used.append(tool_name)
                print(f"  🔧 Tool {len(tools_used)}: {tool_name}")
            elif data["type"] == "teacher":
                has_teacher = True
            elif data["type"] == "output":
                has_output = True
            elif data["type"] == "cost":
                has_cost = True
                print(f"  💰 Cost: {data['content']}")
            elif data["type"] == "complete":
                print(f"\n✅ Lesson complete!")
                print(f"✅ Tools used: {len(tools_used)}")
                print(f"✅ Total messages: {message_count}")
                break
        except json.JSONDecodeError:
            continue
    
    # Verify compositional teaching
    assert len(tools_used) >= 3, f"Expected 3+ tools, got {len(tools_used)}"
    assert has_teacher, "Missing teacher response"
    assert has_output, "Missing tool output"
    
    # Check for multi-modal usage
    visual_tools = [t for t in tools_used if "visual" in t]
    concept_tools = [t for t in tools_used if "scrimba" in t]
    project_tools = [t for t in tools_used if "live_coding" in t]
    
    modalities = sum([len(visual_tools) > 0, len(concept_tools) > 0, len(project_tools) > 0])
    
    print(f"\n📊 Multi-Modal Analysis:")
    print(f"  • Visual tools: {len(visual_tools)}")
    print(f"  • Concept tools: {len(concept_tools)}")
    print(f"  • Project tools: {len(project_tools)}")
    print(f"  • Modalities used: {modalities}/3")
    
    assert modalities >= 2, f"Expected 2+ modalities, got {modalities}"
    print(f"✅ Compositional teaching verified! ({modalities} modalities)")
    
    return {
        "tools_used": len(tools_used),
        "modalities": modalities,
        "messages": message_count
    }

if __name__ == "__main__":
    print("\n🎓 MASTER TEACHER - END-TO-END BACKEND TEST")
    print("="*70)
    
    try:
        # Test 1: Create session
        session_id = test_session_creation()
        
        # Test 2: Compositional teaching
        result = test_compositional_teaching(session_id, "Teach me binary search")
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print(f"\n📈 Summary:")
        print(f"  • Session creation: ✅ (no mode parameter)")
        print(f"  • Compositional teaching: ✅ ({result['tools_used']} tools)")
        print(f"  • Multi-modal learning: ✅ ({result['modalities']} modalities)")
        print(f"  • Real-time streaming: ✅ ({result['messages']} messages)")
        print(f"\n🎉 Master Teacher backend working perfectly!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
