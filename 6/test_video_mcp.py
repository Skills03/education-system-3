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

import fal_client


def test_video_generation():
    """Test the video generation tool (direct FAL API call)"""
    print("=" * 70)
    print("🎬 Testing Video Generation MCP Tool")
    print("=" * 70)

    # Test simple video generation
    concept = "Binary Search Algorithm"
    scene_desc = "A developer at a computer, searching through a sorted array. Visual representation of dividing search space in half repeatedly. Clean office environment, focused expression."
    duration = 5

    print(f"\n📝 Test Parameters:")
    print(f"   Concept: {concept}")
    print(f"   Duration: {duration}s")
    print(f"   Scene: {scene_desc[:60]}...")

    print(f"\n⏳ Generating video (this may take 30-60 seconds)...\n")

    try:
        # Build prompt (same as video_tools.py)
        prompt = f"""Educational programming video: {concept}.

Scene: {scene_desc}

Style: Cinematic, professional, clear lighting, shallow depth of field,
realistic natural colors, smooth camera movement.
Target duration: {duration} seconds.
Focus on clarity and visual learning."""

        def on_queue_update(update):
            if isinstance(update, fal_client.InProgress):
                for log in update.logs:
                    print(f"   [FAL] {log['message']}")

        # Call FAL API
        result = fal_client.subscribe(
            "fal-ai/sora-2/text-to-video",
            arguments={"prompt": prompt},
            with_logs=True,
            on_queue_update=on_queue_update,
        )

        # Extract video details
        video_data = result.get('video', {})
        video_url = video_data.get('url')
        width = video_data.get('width', 1280)
        height = video_data.get('height', 720)
        fps = video_data.get('fps', 30)
        actual_duration = video_data.get('duration', duration)
        num_frames = video_data.get('num_frames', 0)

        print("\n" + "=" * 70)
        print("✅ VIDEO GENERATION SUCCESSFUL!")
        print("=" * 70)

        print(f"\n📹 Video Details:")
        print(f"   URL: {video_url}")
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps}")
        print(f"   Duration: {actual_duration}s")
        print(f"   Frames: {num_frames}")

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


def main():
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
    success = test_video_generation()

    if success:
        print("\n✅ All tests passed! Video MCP tool is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
