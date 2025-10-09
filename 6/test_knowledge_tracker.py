#!/usr/bin/env python3
"""Test script for Student Knowledge Tracker"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from student_knowledge import StudentKnowledgeTracker

def test_knowledge_tracker():
    print("=" * 60)
    print("TESTING STUDENT KNOWLEDGE TRACKER")
    print("=" * 60)

    # Initialize tracker
    print("\n1. Loading existing knowledge...")
    tracker = StudentKnowledgeTracker()

    print(f"   Mastered: {tracker.mastered}")
    print(f"   Learning: {tracker.learning}")
    print(f"   Weak Areas: {tracker.weak_areas}")
    print(f"   Session Count: {tracker.session_count}")

    # Test adding learning concepts
    print("\n2. Adding new learning concepts...")
    tracker.add_learning_concept("variables")
    tracker.add_learning_concept("loops")
    tracker.add_learning_concept("conditionals")
    print(f"   Learning: {tracker.learning}")

    # Test recording a session
    print("\n3. Recording teaching session...")
    tracker.record_session(
        agent_used="explainer",
        concepts_taught=["variables", "data types"],
        success=True
    )
    print(f"   Session count: {tracker.session_count}")
    print(f"   Learning concepts: {tracker.learning}")

    # Test promoting to mastered
    print("\n4. Promoting 'variables' to mastered...")
    tracker.promote_to_mastered("variables")
    print(f"   Mastered: {tracker.mastered}")
    print(f"   Learning: {tracker.learning}")

    # Test adding weak area
    print("\n5. Adding 'loops' as weak area...")
    tracker.add_weak_area("loops")
    print(f"   Weak areas: {tracker.weak_areas}")
    print(f"   Learning: {tracker.learning}")

    # Test context summary
    print("\n6. Getting context summary...")
    summary = tracker.get_context_summary()
    print(f"   {summary}")

    # Test saving
    print("\n7. Saving knowledge to CLAUDE.md...")
    tracker.save()
    print("   ✓ Saved successfully")

    # Test loading again
    print("\n8. Loading knowledge again to verify persistence...")
    tracker2 = StudentKnowledgeTracker()
    print(f"   Mastered: {tracker2.mastered}")
    print(f"   Learning: {tracker2.learning}")
    print(f"   Weak Areas: {tracker2.weak_areas}")
    print(f"   Session Count: {tracker2.session_count}")

    # Verify
    print("\n9. Verification...")
    assert "variables" in tracker2.mastered, "❌ 'variables' should be mastered"
    assert "data types" in tracker2.learning, "❌ 'data types' should be learning"
    assert "loops" in tracker2.weak_areas, "❌ 'loops' should be in weak areas"
    assert tracker2.session_count == tracker.session_count, "❌ Session count mismatch"
    print("   ✓ All assertions passed!")

    print("\n" + "=" * 60)
    print("✅ KNOWLEDGE TRACKER TEST PASSED")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_knowledge_tracker()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
