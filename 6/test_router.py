#!/usr/bin/env python3
"""Test Intelligent Agent Router"""

import os
from pathlib import Path
from agent_router import AgentRouter

# Load .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)
    print(f"✓ Loaded environment from {env_path}")

def test_routing():

    router = AgentRouter()

    test_cases = [
        # Explainer tests
        ("What is a variable?", "explainer"),
        ("Explain how loops work", "explainer"),
        ("Teach me about functions", "explainer"),
        ("How does recursion work?", "explainer"),
        ("I don't understand async/await", "explainer"),

        # Reviewer tests
        ("Check my code: def foo(): pass", "reviewer"),
        ("Here's my solution: print('hello')", "reviewer"),
        ("Is my code correct?", "reviewer"),
        ("My code has a bug, can you help?", "reviewer"),
        ("```python\ndef calc(x): return x * 2\n```", "reviewer"),

        # Challenger tests
        ("Challenge me on arrays", "challenger"),
        ("Give me a practice problem", "challenger"),
        ("I want to practice loops", "challenger"),
        ("Can I try some exercises?", "challenger"),

        # Assessor tests
        ("Test me on variables", "assessor"),
        ("Quiz me about functions", "assessor"),
        ("Am I ready for advanced topics?", "assessor"),
        ("Do I understand loops correctly?", "assessor"),
    ]

    print("=" * 80)
    print("🧪 TESTING INTELLIGENT LLM-BASED AGENT ROUTER")
    print("=" * 80)
    print("Using Claude Haiku for intelligent classification\n")

    passed = 0
    failed = 0

    for query, expected_agent in test_cases:
        try:
            agent, confidence = router.route(query)
            status = "✓" if agent == expected_agent else "✗"

            if agent == expected_agent:
                passed += 1
                print(f"{status} '{query[:60]:60}' → {agent.upper():10} ({confidence:.0%})")
            else:
                failed += 1
                print(f"{status} '{query[:60]:60}' → {agent.upper():10} (expected: {expected_agent.upper()}, {confidence:.0%})")

        except Exception as e:
            print(f"✗ '{query[:60]:60}' → ERROR: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    accuracy = (passed / len(test_cases)) * 100 if test_cases else 0
    print(f"Accuracy: {accuracy:.1f}%")

    if failed == 0:
        print("✅ All routing tests passed!")
    else:
        print(f"⚠️ {failed} test(s) failed")

    # Test caching
    print("\n" + "=" * 80)
    print("🧪 TESTING CACHE")
    print("=" * 80)
    query = "What is a variable?"
    print(f"First call: {query}")
    agent1, _ = router.route(query)
    print(f"Second call (should be cached): {query}")
    agent2, _ = router.route(query)
    if agent1 == agent2:
        print("✅ Cache working correctly")
    else:
        print("✗ Cache failed - different results")

    return failed == 0

if __name__ == "__main__":
    success = test_routing()
    exit(0 if success else 1)
