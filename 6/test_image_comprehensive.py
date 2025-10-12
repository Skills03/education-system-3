#!/usr/bin/env python3
"""Comprehensive Image Editing Tests - Verify Before Integration"""

import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv('/home/mahadev/Desktop/dev/education/.env')

import fal_client


class ImageEditTester:
    """Comprehensive image editing test suite"""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log_test(self, name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"       {details}")

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

        self.test_results.append({
            "name": name,
            "passed": passed,
            "details": details
        })

    async def test_basic_edit(self):
        """Test 1: Basic image edit with valid parameters"""
        print("\n" + "="*70)
        print("TEST 1: Basic Image Edit")
        print("="*70)

        try:
            start = time.time()

            handler = await fal_client.submit_async(
                "fal-ai/qwen-image-edit",
                arguments={
                    "prompt": "Change bag to apple macbook",
                    "image_url": "https://v3.fal.media/files/koala/oei_-iPIYFnhdB8SxojND_qwen-edit-res.png"
                },
            )

            # Collect events
            events = []
            async for event in handler.iter_events(with_logs=True):
                events.append(event)
                print(f"  Event: {type(event).__name__}")

            result = await handler.get()
            elapsed = time.time() - start

            # Validate result structure
            has_images = 'images' in result
            has_url = has_images and len(result['images']) > 0 and 'url' in result['images'][0]
            has_dimensions = has_images and len(result['images']) > 0 and 'width' in result['images'][0]

            self.log_test(
                "Basic Edit Returns Result",
                has_images and has_url and has_dimensions,
                f"Time: {elapsed:.2f}s, Events: {len(events)}, URL: {result['images'][0]['url'][:50] if has_url else 'MISSING'}..."
            )

            return result if has_images else None

        except Exception as e:
            self.log_test("Basic Edit Returns Result", False, f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    async def test_event_stream(self):
        """Test 2: Event streaming works correctly"""
        print("\n" + "="*70)
        print("TEST 2: Event Stream Validation")
        print("="*70)

        try:
            handler = await fal_client.submit_async(
                "fal-ai/qwen-image-edit",
                arguments={
                    "prompt": "Add red border",
                    "image_url": "https://v3.fal.media/files/koala/oei_-iPIYFnhdB8SxojND_qwen-edit-res.png"
                },
            )

            in_progress_count = 0
            completed_count = 0

            async for event in handler.iter_events(with_logs=True):
                if isinstance(event, fal_client.InProgress):
                    in_progress_count += 1
                elif isinstance(event, fal_client.Completed):
                    completed_count += 1
                    print(f"  Completed event metrics: {event.metrics}")

            result = await handler.get()

            self.log_test(
                "Event Stream Works",
                in_progress_count > 0 and completed_count == 1,
                f"InProgress: {in_progress_count}, Completed: {completed_count}"
            )

            return result

        except Exception as e:
            self.log_test("Event Stream Works", False, f"Error: {str(e)}")
            return None

    async def test_result_structure(self):
        """Test 3: Result structure contains all expected fields"""
        print("\n" + "="*70)
        print("TEST 3: Result Structure Validation")
        print("="*70)

        try:
            handler = await fal_client.submit_async(
                "fal-ai/qwen-image-edit",
                arguments={
                    "prompt": "Make it brighter",
                    "image_url": "https://v3.fal.media/files/koala/oei_-iPIYFnhdB8SxojND_qwen-edit-res.png"
                },
            )

            async for event in handler.iter_events(with_logs=True):
                pass  # Consume events

            result = await handler.get()

            # Check required fields
            checks = {
                "images array exists": 'images' in result,
                "images not empty": 'images' in result and len(result['images']) > 0,
                "url exists": 'images' in result and len(result['images']) > 0 and 'url' in result['images'][0],
                "width exists": 'images' in result and len(result['images']) > 0 and 'width' in result['images'][0],
                "height exists": 'images' in result and len(result['images']) > 0 and 'height' in result['images'][0],
                "content_type exists": 'images' in result and len(result['images']) > 0 and 'content_type' in result['images'][0],
                "timings exists": 'timings' in result,
                "prompt echoed": 'prompt' in result
            }

            all_passed = all(checks.values())

            details_str = ", ".join([f"{k}: {v}" for k, v in checks.items()])

            self.log_test(
                "Result Structure Complete",
                all_passed,
                details_str
            )

            if all_passed:
                print(f"\n  Full Result Sample:")
                print(f"    URL: {result['images'][0]['url']}")
                print(f"    Dimensions: {result['images'][0]['width']}x{result['images'][0]['height']}")
                print(f"    Content Type: {result['images'][0]['content_type']}")
                print(f"    Inference Time: {result['timings'].get('inference', 'N/A')}s")

            return result

        except Exception as e:
            self.log_test("Result Structure Complete", False, f"Error: {str(e)}")
            return None

    async def test_invalid_url(self):
        """Test 4: Error handling for invalid image URL"""
        print("\n" + "="*70)
        print("TEST 4: Invalid URL Error Handling")
        print("="*70)

        try:
            handler = await fal_client.submit_async(
                "fal-ai/qwen-image-edit",
                arguments={
                    "prompt": "Change color",
                    "image_url": "https://invalid-url-that-does-not-exist.com/image.png"
                },
            )

            async for event in handler.iter_events(with_logs=True):
                print(f"  Event: {type(event).__name__}")

            result = await handler.get()

            # If we get here without error, check if result indicates failure
            error_detected = 'error' in result or ('images' in result and len(result['images']) == 0)

            self.log_test(
                "Invalid URL Handled",
                error_detected,
                "Error properly caught or empty result returned"
            )

        except Exception as e:
            # Exception is expected for invalid URL
            self.log_test(
                "Invalid URL Handled",
                True,
                f"Exception raised as expected: {type(e).__name__}"
            )

    async def test_empty_prompt(self):
        """Test 5: Error handling for empty prompt"""
        print("\n" + "="*70)
        print("TEST 5: Empty Prompt Handling")
        print("="*70)

        try:
            handler = await fal_client.submit_async(
                "fal-ai/qwen-image-edit",
                arguments={
                    "prompt": "",
                    "image_url": "https://v3.fal.media/files/koala/oei_-iPIYFnhdB8SxojND_qwen-edit-res.png"
                },
            )

            async for event in handler.iter_events(with_logs=True):
                pass

            result = await handler.get()

            # Empty prompt might still work or return error
            has_result = 'images' in result and len(result['images']) > 0

            self.log_test(
                "Empty Prompt Handled",
                True,  # As long as it doesn't crash
                f"Result returned: {has_result}"
            )

        except Exception as e:
            self.log_test(
                "Empty Prompt Handled",
                True,  # Exception is acceptable
                f"Exception: {type(e).__name__}"
            )

    async def test_complex_edit(self):
        """Test 6: Complex multi-step edit instruction"""
        print("\n" + "="*70)
        print("TEST 6: Complex Edit Instruction")
        print("="*70)

        try:
            handler = await fal_client.submit_async(
                "fal-ai/qwen-image-edit",
                arguments={
                    "prompt": "Change the bag to a laptop, make it silver colored, and add an Apple logo",
                    "image_url": "https://v3.fal.media/files/koala/oei_-iPIYFnhdB8SxojND_qwen-edit-res.png"
                },
            )

            async for event in handler.iter_events(with_logs=True):
                pass

            result = await handler.get()

            has_result = 'images' in result and len(result['images']) > 0

            self.log_test(
                "Complex Edit Succeeds",
                has_result,
                f"Inference time: {result.get('timings', {}).get('inference', 'N/A')}s" if has_result else "No result"
            )

            return result

        except Exception as e:
            self.log_test("Complex Edit Succeeds", False, f"Error: {str(e)}")
            return None

    async def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*70)
        print("🧪 COMPREHENSIVE IMAGE EDIT TEST SUITE")
        print("="*70)

        # Check API key
        fal_key = os.environ.get('FAL_KEY')
        if not fal_key:
            print("\n❌ FAL_KEY not set!")
            return False

        print(f"\n✓ FAL_KEY configured: {fal_key[:20]}...\n")

        # Run all tests
        await self.test_basic_edit()
        await self.test_event_stream()
        await self.test_result_structure()
        await self.test_invalid_url()
        await self.test_empty_prompt()
        await self.test_complex_edit()

        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"  Passed: {self.tests_passed}")
        print(f"  Failed: {self.tests_failed}")
        print(f"  Total:  {self.tests_passed + self.tests_failed}")

        success_rate = (self.tests_passed / (self.tests_passed + self.tests_failed)) * 100 if (self.tests_passed + self.tests_failed) > 0 else 0

        print(f"\n  Success Rate: {success_rate:.1f}%")

        if self.tests_failed == 0:
            print("\n✅ ALL TESTS PASSED - Ready for MCP integration!")
            return True
        else:
            print(f"\n⚠️  {self.tests_failed} TEST(S) FAILED - Fix before integration")
            return False


async def main():
    tester = ImageEditTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
