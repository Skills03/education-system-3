#!/usr/bin/env python3
"""Test image editing with FAL AI"""

import asyncio
import os
import sys

# Load environment
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv('/home/mahadev/Desktop/dev/education/.env')

import fal_client


async def test_image_edit():
    """Test image editing functionality"""
    print("=" * 70)
    print("🎨 Testing Image Editing with FAL AI")
    print("=" * 70)

    print("\n📝 Test Parameters:")
    print("   Prompt: 'Change bag to apple macbook'")
    print("   Source Image: Qwen example image")

    print("\n⏳ Submitting image edit request...\n")

    try:
        handler = await fal_client.submit_async(
            "fal-ai/qwen-image-edit",
            arguments={
                "prompt": "Change bag to apple macbook",
                "image_url": "https://v3.fal.media/files/koala/oei_-iPIYFnhdB8SxojND_qwen-edit-res.png"
            },
        )

        print("✅ Request submitted, waiting for events...\n")

        async for event in handler.iter_events(with_logs=True):
            print(f"📡 Event: {event}")

        result = await handler.get()

        print("\n" + "=" * 70)
        print("✅ IMAGE EDIT SUCCESSFUL!")
        print("=" * 70)

        if 'image' in result:
            image_data = result['image']
            print(f"\n🖼️ Edited Image:")
            print(f"   URL: {image_data.get('url')}")
            print(f"   Content Type: {image_data.get('content_type')}")
            print(f"   Width: {image_data.get('width')}")
            print(f"   Height: {image_data.get('height')}")
        else:
            print(f"\nFull Result: {result}")

        print("\n" + "=" * 70)
        print("🎉 Image Edit Test: PASSED")
        print("=" * 70)

        return True

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ IMAGE EDIT FAILED!")
        print("=" * 70)
        print(f"\nError: {e}")

        import traceback
        print("\nTraceback:")
        traceback.print_exc()

        return False


async def main():
    """Run test"""
    print("\n🧪 Starting Image Edit Integration Test\n")

    # Check FAL_KEY
    fal_key = os.environ.get('FAL_KEY')
    if not fal_key:
        print("❌ FAL_KEY environment variable not set!")
        sys.exit(1)

    print(f"✓ FAL_KEY configured: {fal_key[:20]}...")

    # Run test
    success = await test_image_edit()

    if success:
        print("\n✅ Image editing works! Ready to integrate as MCP tool.")
        sys.exit(0)
    else:
        print("\n❌ Image editing test failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
