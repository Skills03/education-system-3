#!/usr/bin/env python3
"""Debug: What happens with invalid URL?"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv('/home/mahadev/Desktop/dev/education/.env')

import fal_client


async def test_invalid_url():
    print("Testing invalid URL behavior...\n")

    try:
        handler = await fal_client.submit_async(
            "fal-ai/qwen-image-edit",
            arguments={
                "prompt": "Change color to red",
                "image_url": "https://invalid-url-that-does-not-exist.com/image.png"
            },
        )

        print("Request submitted. Waiting for events...")

        async for event in handler.iter_events(with_logs=True):
            print(f"Event: {event}")

        result = await handler.get()

        print("\n" + "="*70)
        print("Result received:")
        print("="*70)
        print(result)

        if 'images' in result and len(result['images']) > 0:
            print(f"\n✅ FAL returned valid result even with invalid URL!")
            print(f"   URL: {result['images'][0]['url']}")
            print(f"   This means FAL is VERY robust - it handles bad URLs gracefully")
        else:
            print(f"\n⚠️ No images in result (expected for invalid URL)")

    except Exception as e:
        print(f"\n❌ Exception raised: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


asyncio.run(test_invalid_url())
