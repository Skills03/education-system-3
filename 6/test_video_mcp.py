#!/usr/bin/env python3
"""Test video generation MCP tool integration"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment
from dotenv import load_dotenv
load_dotenv('/home/mahadev/Desktop/dev/education/.env')

from tools.video_tools import generate_educational_video


async def test_video_generation():
    """Test the video generation tool"""
    print("=" * 70)
    print("🎬 Testing Video Generation MCP Tool")
    print("=" * 70)

    # Test simple video generation
    test_args = {
        "concept": "Binary Search Algorithm",
        "scene_description": "A developer at a computer, searching through a sorted array. Visual representation of dividing search space in half repeatedly. Clean office environment, focused expression.",
        "duration_seconds": 5
    }

    print(f"\n📝 Test Parameters:")
    print(f"   Concept: {test_args['concept']}")
    print(f"   Duration: {test_args['duration_seconds']}s")
    print(f"   Scene: {test_args['scene_description'][:60]}...")

    print(f"\n⏳ Generating video (this may take 30-60 seconds)...\n")

    try:
        result = await generate_educational_video(test_args)

        print("\n" + "=" * 70)
        print("✅ VIDEO GENERATION SUCCESSFUL!")
        print("=" * 70)

        content = result.get('content', [])
        if content and len(content) > 0:
            text = content[0].get('text', '')
            print(f"\n{text}")
        else:
            print(f"\nResult: {result}")

        print("\n" + "=" * 70)
        print("🎉 MCP Tool Integration Test: PASSED")
        print("=" * 70)

        return True

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ VIDEO GENERATION FAILED!")
        print("=" * 70)
        print(f"\nError: {e}")

        import traceback
        print("\nTraceback:")
        traceback.print_exc()

        return False


async def main():
    """Run all tests"""
    print("\n🧪 Starting MCP Video Tool Integration Tests\n")

    # Check FAL_KEY is set
    fal_key = os.environ.get('FAL_KEY')
    if not fal_key:
        print("❌ FAL_KEY environment variable not set!")
        print("   Please set it in /home/mahadev/Desktop/dev/education/.env")
        sys.exit(1)

    print(f"✓ FAL_KEY configured: {fal_key[:20]}...")

    # Run test
    success = await test_video_generation()

    if success:
        print("\n✅ All tests passed! Video MCP tool is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
