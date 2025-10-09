#!/usr/bin/env python3
"""Test session-scoped knowledge isolation"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from student_knowledge import StudentKnowledgeTracker

def test_session_isolation():
    print("=" * 70)
    print("TESTING SESSION-SCOPED KNOWLEDGE ISOLATION")
    print("=" * 70)

    # Session 1: Teach Python basics
    print("\n1. SESSION A - Teaching Python basics...")
    session_a = StudentKnowledgeTracker(session_id="session-aaa-111")
    session_a.record_session("explainer", ["variables", "loops"], True)
    session_a.promote_to_mastered("variables")
    session_a.save()
    print(f"   Session A file: {session_a.file_path}")
    print(f"   Session A mastered: {session_a.mastered}")
    print(f"   Session A learning: {session_a.learning}")

    # Session 2: Teach JavaScript (completely isolated)
    print("\n2. SESSION B - Teaching JavaScript (isolated)...")
    session_b = StudentKnowledgeTracker(session_id="session-bbb-222")
    session_b.record_session("explainer", ["functions", "closures"], True)
    session_b.promote_to_mastered("functions")
    session_b.save()
    print(f"   Session B file: {session_b.file_path}")
    print(f"   Session B mastered: {session_b.mastered}")
    print(f"   Session B learning: {session_b.learning}")

    # Session 3: Continue Session A
    print("\n3. SESSION A (continued) - Loading previous knowledge...")
    session_a_resumed = StudentKnowledgeTracker(session_id="session-aaa-111")
    print(f"   Session A resumed mastered: {session_a_resumed.mastered}")
    print(f"   Session A resumed learning: {session_a_resumed.learning}")

    # Session 4: Continue Session B
    print("\n4. SESSION B (continued) - Loading previous knowledge...")
    session_b_resumed = StudentKnowledgeTracker(session_id="session-bbb-222")
    print(f"   Session B resumed mastered: {session_b_resumed.mastered}")
    print(f"   Session B resumed learning: {session_b_resumed.learning}")

    # Verification
    print("\n5. VERIFICATION...")

    # Check Session A isolation
    assert "variables" in session_a_resumed.mastered, "❌ Session A should have 'variables'"
    assert "loops" in session_a_resumed.learning, "❌ Session A should be learning 'loops'"
    assert "functions" not in session_a_resumed.mastered, "❌ Session A should NOT know 'functions' (from Session B)"
    assert "closures" not in session_a_resumed.learning, "❌ Session A should NOT have 'closures' (from Session B)"
    print("   ✓ Session A isolation: PASS")

    # Check Session B isolation
    assert "functions" in session_b_resumed.mastered, "❌ Session B should have 'functions'"
    assert "closures" in session_b_resumed.learning, "❌ Session B should be learning 'closures'"
    assert "variables" not in session_b_resumed.mastered, "❌ Session B should NOT know 'variables' (from Session A)"
    assert "loops" not in session_b_resumed.learning, "❌ Session B should NOT have 'loops' (from Session A)"
    print("   ✓ Session B isolation: PASS")

    # Check file separation
    assert session_a_resumed.file_path != session_b_resumed.file_path, "❌ Sessions should have different files"
    assert "session-aaa-111" in session_a_resumed.file_path, "❌ Session A file should contain session ID"
    assert "session-bbb-222" in session_b_resumed.file_path, "❌ Session B file should contain session ID"
    print("   ✓ File separation: PASS")

    # Check files exist
    assert os.path.exists(session_a_resumed.file_path), "❌ Session A file should exist"
    assert os.path.exists(session_b_resumed.file_path), "❌ Session B file should exist"
    print("   ✓ File persistence: PASS")

    print("\n" + "=" * 70)
    print("✅ SESSION ISOLATION TEST PASSED")
    print("=" * 70)

    print("\n📁 Created session files:")
    print(f"   - {session_a_resumed.file_path}")
    print(f"   - {session_b_resumed.file_path}")

    # Cleanup test files
    print("\n🧹 Cleaning up test files...")
    os.remove(session_a_resumed.file_path)
    os.remove(session_b_resumed.file_path)
    print("   ✓ Test files removed")

if __name__ == "__main__":
    try:
        test_session_isolation()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
