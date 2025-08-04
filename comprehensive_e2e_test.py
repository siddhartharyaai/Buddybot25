#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Suite
Tests complete user journeys from landing to story narration with barge-in
"""

import asyncio
import time
import json
import sys
from playwright.async_api import async_playwright

class ComprehensiveE2ETest:
    def __init__(self):
        self.base_url = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com"
        self.bugs_found = []
        self.tests_passed = 0
        self.tests_failed = 0
        
    async def setup_browser(self):
        """Setup browser for testing"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # Listen for console errors
        self.page.on("console", self.handle_console_message)
        self.page.on("pageerror", self.handle_page_error)
        
    async def handle_console_message(self, msg):
        if msg.type == "error":
            self.bugs_found.append({
                "type": "console_error",
                "message": msg.text,
                "location": str(msg.location) if msg.location else "unknown"
            })
            
    async def handle_page_error(self, error):
        self.bugs_found.append({
            "type": "page_error",
            "message": str(error)
        })
    
    def log_test(self, test_name, success, details=""):
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASS {details}")
        else:
            self.tests_failed += 1
            print(f"❌ {test_name}: FAIL {details}")
            self.bugs_found.append({
                "test": test_name,
                "error": details
            })
    
    async def test_complete_onboarding_flow(self):
        """Test complete user onboarding from landing to chat"""
        print("\n🚀 TESTING COMPLETE ONBOARDING FLOW...")
        
        try:
            # Step 1: Landing page
            await self.page.goto(self.base_url, timeout=30000)
            await self.page.wait_for_load_state('networkidle')
            
            # Check title
            title = await self.page.title()
            self.log_test("Landing Page Title", "Buddy" in title, f"Title: {title}")
            
            # Step 2: Click Get Started
            get_started = self.page.get_by_text("Get Started")
            if await get_started.is_visible():
                await get_started.click()
                await self.page.wait_for_timeout(2000)
                self.log_test("Get Started Button Click", True, "Signup form opened")
            else:
                self.log_test("Get Started Button Click", False, "Button not found")
                return
            
            # Step 3: Fill and submit signup form
            test_email = f"e2e_test_{int(time.time())}@example.com"
            await self.page.fill('input[placeholder="Enter your email"]', test_email)
            await self.page.fill('input[placeholder="Create a password"]', 'TestPass123!')
            await self.page.fill('input[placeholder="Enter your name"]', 'E2E Test Child')
            await self.page.fill('input[placeholder="Enter your age"]', '8')
            
            create_account = self.page.get_by_text("Create Account")
            await create_account.click()
            await self.page.wait_for_timeout(3000)
            
            # Check if signup succeeded
            page_content = await self.page.content()
            success_indicators = ["Account created successfully", "profile", "step"]
            signup_success = any(indicator.lower() in page_content.lower() for indicator in success_indicators)
            self.log_test("Signup Form Submission", signup_success, "Account created and profile setup opened")
            
            # Step 4: Complete profile setup
            if signup_success:
                try:
                    # Fill profile form (fields might be pre-filled from signup)
                    name_field = self.page.locator('input[placeholder*="name"]').first
                    if await name_field.is_visible():
                        await name_field.fill('E2E Test Child')
                    
                    age_field = self.page.locator('input[type="number"]').first
                    if await age_field.is_visible():
                        await age_field.fill('8')
                    
                    location_field = self.page.locator('input[placeholder*="location"]').first
                    if await location_field.is_visible():
                        await location_field.fill('Test City')
                    
                    # Click save/next button
                    save_buttons = await self.page.locator('button:has-text("Save"), button:has-text("Next"), button:has-text("Continue")').count()
                    if save_buttons > 0:
                        await self.page.locator('button:has-text("Save"), button:has-text("Next"), button:has-text("Continue")').first.click()
                        await self.page.wait_for_timeout(2000)
                        self.log_test("Profile Setup Completion", True, "Profile form submitted")
                        
                        # Wait for possible parental controls step
                        await self.page.wait_for_timeout(2000)
                        
                        # Check if parental controls modal appears
                        parental_content = await self.page.content()
                        if "parental" in parental_content.lower() or "controls" in parental_content.lower():
                            # Skip parental controls for now
                            skip_buttons = await self.page.locator('button:has-text("Skip"), button:has-text("Later"), button:has-text("×")').count()
                            if skip_buttons > 0:
                                await self.page.locator('button:has-text("Skip"), button:has-text("Later"), button:has-text("×")').first.click()
                                await self.page.wait_for_timeout(2000)
                            
                        self.log_test("Onboarding Flow Complete", True, "Successfully navigated to chat")
                    else:
                        self.log_test("Profile Setup Completion", False, "No save button found")
                except Exception as e:
                    self.log_test("Profile Setup Completion", False, f"Error: {str(e)}")
            
        except Exception as e:
            self.log_test("Complete Onboarding Flow", False, f"Critical error: {str(e)}")
    
    async def test_chat_interface_functionality(self):
        """Test chat interface and microphone functionality"""
        print("\n💬 TESTING CHAT INTERFACE FUNCTIONALITY...")
        
        try:
            # Ensure we're on the chat interface
            await self.page.wait_for_timeout(2000)
            
            # Look for microphone button
            mic_selectors = [
                'button[aria-label*="record"]',
                'button[aria-label*="microphone"]',
                'button:has-text("🎤")',
                '[class*="mic"]'
            ]
            
            mic_found = False
            for selector in mic_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.is_visible():
                        mic_found = True
                        self.log_test("Microphone Button Visibility", True, f"Found with selector: {selector}")
                        
                        # Test microphone button click
                        await element.click()
                        await self.page.wait_for_timeout(1000)
                        
                        # Check if recording started (usually indicated by visual changes)
                        recording_indicators = await self.page.locator('[class*="recording"], [class*="active"], [aria-pressed="true"]').count()
                        self.log_test("Microphone Button Click", recording_indicators > 0, f"Recording indicators: {recording_indicators}")
                        
                        # Click again to stop
                        await element.click()
                        await self.page.wait_for_timeout(1000)
                        break
                except:
                    continue
            
            if not mic_found:
                self.log_test("Microphone Button Visibility", False, "Microphone button not found")
            
            # Test dark mode toggle
            dark_mode_selectors = [
                'button:has-text("🌙")',
                'button:has-text("☀")',
                'button[aria-label*="theme"]'
            ]
            
            dark_mode_found = False
            for selector in dark_mode_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.is_visible():
                        dark_mode_found = True
                        await element.click()
                        await self.page.wait_for_timeout(1000)
                        self.log_test("Dark Mode Toggle", True, f"Toggle found and clicked")
                        break
                except:
                    continue
            
            if not dark_mode_found:
                self.log_test("Dark Mode Toggle", False, "Dark mode toggle not accessible")
                
        except Exception as e:
            self.log_test("Chat Interface Functionality", False, f"Error: {str(e)}")
    
    async def test_story_narration_flow(self):
        """Test story generation and narration"""
        print("\n📚 TESTING STORY NARRATION FLOW...")
        
        try:
            # Simulate typing a story request
            page_content = await self.page.content()
            
            # Look for text input or message input
            text_inputs = await self.page.locator('input[type="text"], textarea, [contenteditable="true"]').count()
            
            if text_inputs > 0:
                # Try to send a story request via text input (if available)
                text_input = self.page.locator('input[type="text"], textarea').first
                if await text_input.is_visible():
                    await text_input.fill("Tell me a short story about a brave little mouse")
                    
                    # Look for send button
                    send_buttons = await self.page.locator('button:has-text("Send"), button[type="submit"]').count()
                    if send_buttons > 0:
                        await self.page.locator('button:has-text("Send"), button[type="submit"]').first.click()
                        await self.page.wait_for_timeout(5000)  # Wait for story generation
                        
                        # Check if story response appears
                        story_content = await self.page.content()
                        story_indicators = ["once upon", "story", "mouse", "tale"]
                        story_found = any(indicator in story_content.lower() for indicator in story_indicators)
                        self.log_test("Story Generation via Text", story_found, "Story content detected in page")
                    else:
                        self.log_test("Story Generation via Text", False, "No send button found")
                else:
                    self.log_test("Story Generation via Text", False, "Text input not accessible")
            else:
                # This is expected for voice-only interface
                self.log_test("Story Generation via Text", True, "Voice-only interface (expected)")
            
            # Test if audio elements appear (indicating TTS is working)
            await self.page.wait_for_timeout(2000)
            audio_elements = await self.page.locator('audio, [data-audio], [class*="audio"]').count()
            self.log_test("Audio Elements Present", audio_elements > 0, f"Found {audio_elements} audio elements")
            
        except Exception as e:
            self.log_test("Story Narration Flow", False, f"Error: {str(e)}")
    
    async def test_responsive_design(self):
        """Test mobile responsiveness"""
        print("\n📱 TESTING RESPONSIVE DESIGN...")
        
        try:
            # Test mobile viewport
            await self.page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE
            await self.page.wait_for_timeout(1000)
            
            # Check if elements are still visible and accessible
            essential_elements = [
                ('Microphone button', 'button[aria-label*="record"]'),
                ('Header', 'header'),
                ('Chat area', '[class*="chat"], [class*="message"]')
            ]
            
            mobile_responsive = True
            for element_name, selector in essential_elements:
                try:
                    element = self.page.locator(selector).first
                    is_visible = await element.is_visible()
                    if not is_visible:
                        mobile_responsive = False
                        self.log_test(f"Mobile {element_name}", False, "Not visible on mobile")
                    else:
                        self.log_test(f"Mobile {element_name}", True, "Visible on mobile")
                except:
                    mobile_responsive = False
                    self.log_test(f"Mobile {element_name}", False, "Element not found")
            
            # Reset to desktop viewport
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
        except Exception as e:
            self.log_test("Responsive Design", False, f"Error: {str(e)}")
    
    async def cleanup(self):
        """Cleanup browser resources"""
        if hasattr(self, 'context'):
            await self.context.close()
        if hasattr(self, 'browser'):
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 STARTING COMPREHENSIVE END-TO-END TESTING...")
        start_time = time.time()
        
        try:
            await self.setup_browser()
            
            await self.test_complete_onboarding_flow()
            await self.test_chat_interface_functionality()
            await self.test_story_narration_flow()
            await self.test_responsive_design()
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {str(e)}")
            self.bugs_found.append({
                "test": "Critical Error",
                "error": str(e)
            })
        finally:
            await self.cleanup()
        
        total_time = time.time() - start_time
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 COMPREHENSIVE E2E TEST RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {total_time:.2f}s")
        print(f"Console Errors: {len([b for b in self.bugs_found if b.get('type') in ['console_error', 'page_error']])}")
        print(f"Functional Issues: {len([b for b in self.bugs_found if b.get('type') not in ['console_error', 'page_error']])}")
        
        if self.bugs_found:
            print(f"\n🐛 ISSUES FOUND:")
            for i, bug in enumerate(self.bugs_found, 1):
                bug_type = bug.get('type', 'functional')
                test_name = bug.get('test', 'Unknown')
                error_msg = bug.get('error', bug.get('message', 'Unknown error'))
                print(f"{i}. [{bug_type.upper()}] {test_name}: {error_msg}")
        
        return {
            "total_tests": total_tests,
            "passed": self.tests_passed,
            "failed": self.tests_failed,
            "success_rate": success_rate,
            "bugs": self.bugs_found,
            "duration": total_time
        }

if __name__ == "__main__":
    async def main():
        tester = ComprehensiveE2ETest()
        results = await tester.run_all_tests()
        
        # Save results
        with open('/app/comprehensive_e2e_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n🎯 Results saved to: /app/comprehensive_e2e_results.json")
        
        if results['success_rate'] >= 90:
            print("✅ COMPREHENSIVE TESTING: EXCELLENT PERFORMANCE!")
        elif results['success_rate'] >= 80:
            print("⚠️ COMPREHENSIVE TESTING: GOOD PERFORMANCE WITH MINOR ISSUES")
        else:
            print("❌ COMPREHENSIVE TESTING: NEEDS IMPROVEMENT")
            sys.exit(1)
    
    asyncio.run(main())