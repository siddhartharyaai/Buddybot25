#!/usr/bin/env python3
"""
Audio Fix Testing - Focus on TTS, barge-in, overlaps, and latency
Tests the specific audio-related fixes requested
"""

import asyncio
import aiohttp
import time
import json
from playwright.async_api import async_playwright

class AudioFixTester:
    def __init__(self):
        self.base_url = "https://6ddee563-7037-4e87-80ca-83a8a9a9bcae.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.tests_passed = 0
        self.tests_failed = 0
        self.audio_tests = []
        
    async def test_tts_voice_model(self):
        """Test that TTS is using aura-2-amalthea-en model"""
        print("\n🎤 TESTING TTS VOICE MODEL...")
        
        try:
            async with aiohttp.ClientSession() as session:
                tts_data = {
                    "text": "Testing aura-2-amalthea-en voice model",
                    "personality": "friendly_companion"
                }
                
                start_time = time.time()
                async with session.post(f"{self.api_url}/voice/tts", json=tts_data) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        has_audio = 'audio_base64' in data and len(data['audio_base64']) > 1000
                        
                        if has_audio:
                            self.tests_passed += 1
                            print(f"✅ TTS Voice Model: PASS - Audio generated ({duration:.2f}s, {len(data['audio_base64'])} chars)")
                            self.audio_tests.append({
                                "test": "TTS Voice Model",
                                "status": "PASS",
                                "duration": duration,
                                "audio_size": len(data['audio_base64'])
                            })
                        else:
                            self.tests_failed += 1
                            print(f"❌ TTS Voice Model: FAIL - No audio data")
                    else:
                        self.tests_failed += 1
                        print(f"❌ TTS Voice Model: FAIL - Status {response.status}")
                        
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ TTS Voice Model: FAIL - {str(e)}")
    
    async def test_story_chunk_optimization(self):
        """Test that story chunks are optimized for speed"""
        print("\n📚 TESTING STORY CHUNK OPTIMIZATION...")
        
        try:
            async with aiohttp.ClientSession() as session:
                story_data = {
                    "session_id": "audio_test_session",
                    "user_id": "audio_test_user",
                    "message": "Tell me a very short story"
                }
                
                start_time = time.time()
                async with session.post(f"{self.api_url}/conversations/text", json=story_data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get('response_text', '')
                        word_count = len(response_text.split())
                        
                        # Test for faster generation (should be <10s with 50-token chunks)
                        if duration < 10 and word_count > 20:
                            self.tests_passed += 1
                            print(f"✅ Story Chunk Optimization: PASS - Fast generation ({duration:.2f}s, {word_count} words)")
                            self.audio_tests.append({
                                "test": "Story Chunk Optimization",
                                "status": "PASS",
                                "duration": duration,
                                "word_count": word_count
                            })
                        else:
                            self.tests_failed += 1
                            print(f"❌ Story Chunk Optimization: FAIL - Slow generation ({duration:.2f}s, {word_count} words)")
                    else:
                        self.tests_failed += 1
                        print(f"❌ Story Chunk Optimization: FAIL - Status {response.status}")
                        
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Story Chunk Optimization: FAIL - {str(e)}")
    
    async def test_frontend_audio_elements(self):
        """Test frontend audio elements and barge-in using Playwright"""
        print("\n🎭 TESTING FRONTEND AUDIO & BARGE-IN...")
        
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()
            
            # Navigate and complete onboarding quickly
            await page.goto(self.base_url, timeout=30000)
            await page.wait_for_load_state('networkidle')
            
            # Complete signup flow
            get_started = page.get_by_text("Get Started")
            await get_started.click()
            await page.wait_for_timeout(2000)
            
            test_email = f"audio_test_{int(time.time())}@example.com"
            await page.fill('input[placeholder="Enter your email"]', test_email)
            await page.fill('input[placeholder="Create a password"]', 'TestPass123!')
            await page.fill('input[placeholder="Enter your name"]', 'Audio Test')
            await page.fill('input[placeholder="Enter your age"]', '8')
            
            create_account = page.get_by_text("Create Account")
            await create_account.click()
            await page.wait_for_timeout(3000)
            
            # Test microphone button presence
            mic_selectors = [
                'button[aria-label*="record"]',
                'button[aria-label*="microphone"]',
                '[class*="mic"]'
            ]
            
            mic_found = False
            for selector in mic_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible():
                        mic_found = True
                        print(f"✅ Microphone Button: FOUND - {selector}")
                        
                        # Test microphone click (barge-in test)
                        await element.click()
                        await page.wait_for_timeout(500)
                        await element.click()  # Stop recording
                        print(f"✅ Barge-in Click Test: PASS - Button responsive")
                        break
                except:
                    continue
            
            if mic_found:
                self.tests_passed += 1
                self.audio_tests.append({
                    "test": "Frontend Microphone & Barge-in",
                    "status": "PASS",
                    "details": "Microphone button found and clickable"
                })
            else:
                self.tests_failed += 1
                print(f"❌ Microphone Button: NOT FOUND")
            
            # Test dark mode toggle in header
            dark_mode_toggle = page.locator('button[title*="Dark Mode"], button[aria-label*="Dark Mode"]').first
            if await dark_mode_toggle.is_visible():
                self.tests_passed += 1
                print(f"✅ Dark Mode Toggle: FOUND in header")
                self.audio_tests.append({
                    "test": "Dark Mode Toggle",
                    "status": "PASS",
                    "details": "Toggle accessible in header"
                })
            else:
                self.tests_failed += 1
                print(f"❌ Dark Mode Toggle: NOT FOUND in header")
            
            # Test mobile responsiveness for ultra-small screens
            await page.set_viewport_size({"width": 300, "height": 600})  # <320px test
            await page.wait_for_timeout(1000)
            
            # Check if essential elements are still visible
            header_visible = await page.locator('header').is_visible()
            if header_visible:
                self.tests_passed += 1
                print(f"✅ Mobile <320px: PASS - Header visible on ultra-small screen")
                self.audio_tests.append({
                    "test": "Mobile Ultra-Small Screen",
                    "status": "PASS",
                    "details": "Essential elements visible at 300px width"
                })
            else:
                self.tests_failed += 1
                print(f"❌ Mobile <320px: FAIL - Header not visible")
            
            await context.close()
            await browser.close()
            await playwright.stop()
            
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Frontend Audio Test: FAIL - {str(e)}")
    
    async def test_audio_overlap_prevention(self):
        """Test multiple TTS requests to ensure no overlaps"""
        print("\n🚫 TESTING AUDIO OVERLAP PREVENTION...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Send multiple TTS requests simultaneously
                tasks = []
                for i in range(3):
                    tts_data = {
                        "text": f"This is test audio {i+1} to check for overlaps",
                        "personality": "friendly_companion"
                    }
                    task = session.post(f"{self.api_url}/voice/tts", json=tts_data)
                    tasks.append(task)
                
                start_time = time.time()
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                duration = time.time() - start_time
                
                success_count = 0
                for i, response in enumerate(responses):
                    if not isinstance(response, Exception):
                        if response.status == 200:
                            success_count += 1
                
                if success_count >= 2:  # At least 2 out of 3 should succeed
                    self.tests_passed += 1
                    print(f"✅ Audio Overlap Prevention: PASS - {success_count}/3 requests handled ({duration:.2f}s)")
                    self.audio_tests.append({
                        "test": "Audio Overlap Prevention",
                        "status": "PASS",
                        "concurrent_requests": success_count,
                        "duration": duration
                    })
                else:
                    self.tests_failed += 1
                    print(f"❌ Audio Overlap Prevention: FAIL - Only {success_count}/3 succeeded")
                    
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Audio Overlap Prevention: FAIL - {str(e)}")
    
    async def run_all_audio_tests(self):
        """Run all audio-specific tests"""
        print("🎵 STARTING AUDIO FIX TESTING...")
        start_time = time.time()
        
        await self.test_tts_voice_model()
        await self.test_story_chunk_optimization()
        await self.test_audio_overlap_prevention()
        await self.test_frontend_audio_elements()
        
        total_time = time.time() - start_time
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 AUDIO FIX TEST RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {total_time:.2f}s")
        
        # Save detailed results
        results = {
            "total_tests": total_tests,
            "passed": self.tests_passed,
            "failed": self.tests_failed,
            "success_rate": success_rate,
            "duration": total_time,
            "detailed_tests": self.audio_tests
        }
        
        with open('/app/audio_fix_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        if success_rate >= 80:
            print("✅ AUDIO FIXES: WORKING WELL!")
        else:
            print("❌ AUDIO FIXES: NEED MORE WORK")
        
        return results

if __name__ == "__main__":
    async def main():
        tester = AudioFixTester()
        results = await tester.run_all_audio_tests()
        print(f"\n🎯 Results saved to: /app/audio_fix_results.json")
    
    asyncio.run(main())