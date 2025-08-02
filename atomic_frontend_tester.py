#!/usr/bin/env python3
"""
Atomic Frontend Testing - Test every UI component and interaction
Uses Playwright for comprehensive frontend testing
"""

import asyncio
import time
import json
import sys
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

class AtomicFrontendTester:
    def __init__(self):
        self.base_url = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com"
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
        """Handle console messages"""
        if msg.type == "error":
            self.bugs_found.append({
                "type": "console_error",
                "message": msg.text,
                "location": msg.location
            })
            
    async def handle_page_error(self, error):
        """Handle page errors"""
        self.bugs_found.append({
            "type": "page_error", 
            "message": str(error)
        })
    
    async def test_landing_page(self):
        """Test landing page functionality"""
        print("\n🏠 TESTING LANDING PAGE...")
        
        try:
            await self.page.goto(self.base_url, timeout=30000)
            await self.page.wait_for_load_state('networkidle')
            
            # Check if page loaded
            title = await self.page.title()
            if "Buddy" in title or "AI Companion" in title:
                self.tests_passed += 1
                print("✅ Landing Page Load: PASS")
            else:
                self.tests_failed += 1
                print(f"❌ Landing Page Load: FAIL - Title: {title}")
                self.bugs_found.append({
                    "test": "Landing Page Load",
                    "error": f"Unexpected title: {title}"
                })
            
            # Check for basic elements
            elements_to_check = [
                "Get Started",
                "Sign Up", 
                "Sign In",
                "Features"
            ]
            
            for element_text in elements_to_check:
                try:
                    element = self.page.get_by_text(element_text, exact=False).first
                    is_visible = await element.is_visible()
                    if is_visible:
                        self.tests_passed += 1
                        print(f"✅ Element '{element_text}': VISIBLE")
                    else:
                        self.tests_failed += 1
                        print(f"❌ Element '{element_text}': NOT VISIBLE")
                        self.bugs_found.append({
                            "test": f"Element Visibility: {element_text}",
                            "error": "Element not visible on landing page"
                        })
                except Exception as e:
                    self.tests_failed += 1
                    print(f"❌ Element '{element_text}': ERROR - {str(e)}")
                    self.bugs_found.append({
                        "test": f"Element Check: {element_text}",
                        "error": str(e)
                    })
                    
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Landing Page Load: CRITICAL ERROR - {str(e)}")
            self.bugs_found.append({
                "test": "Landing Page Load",
                "error": f"Critical error: {str(e)}"
            })
    
    async def test_signup_flow(self):
        """Test signup flow"""
        print("\n📝 TESTING SIGNUP FLOW...")
        
        try:
            # Navigate to signup
            await self.page.get_by_text("Sign Up", exact=False).first.click()
            await self.page.wait_for_load_state('networkidle')
            
            # Fill signup form
            await self.page.fill('input[type="email"]', f'test_{int(time.time())}@example.com')
            await self.page.fill('input[type="password"]', 'TestPass123!')
            
            # Look for confirm password field
            confirm_fields = await self.page.locator('input[type="password"]').count()
            if confirm_fields > 1:
                await self.page.locator('input[type="password"]').nth(1).fill('TestPass123!')
            
            # Submit form
            await self.page.get_by_text("Sign Up", exact=False).click()
            
            # Check for success or appropriate error
            await self.page.wait_for_timeout(3000)  # Wait for response
            
            # Look for success indicators or error messages
            page_content = await self.page.content()
            
            if "profile" in page_content.lower() or "welcome" in page_content.lower():
                self.tests_passed += 1
                print("✅ Signup Flow: SUCCESS")
            elif "error" in page_content.lower() or "failed" in page_content.lower():
                self.tests_failed += 1
                print("❌ Signup Flow: ERROR DETECTED")
                self.bugs_found.append({
                    "test": "Signup Flow",
                    "error": "Signup failed with error message"
                })
            else:
                self.tests_failed += 1
                print("❌ Signup Flow: UNCLEAR RESULT")
                self.bugs_found.append({
                    "test": "Signup Flow", 
                    "error": "Unclear signup result"
                })
                
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Signup Flow: EXCEPTION - {str(e)}")
            self.bugs_found.append({
                "test": "Signup Flow",
                "error": f"Exception during signup: {str(e)}"
            })
    
    async def test_profile_setup(self):
        """Test profile setup functionality"""
        print("\n👤 TESTING PROFILE SETUP...")
        
        try:
            # Look for profile setup elements
            profile_indicators = [
                "name",
                "age", 
                "profile",
                "setup"
            ]
            
            page_content = await self.page.content()
            found_profile_setup = any(indicator in page_content.lower() for indicator in profile_indicators)
            
            if found_profile_setup:
                # Try to fill profile form
                name_input = self.page.locator('input[placeholder*="name"], input[name*="name"]').first
                if await name_input.is_visible():
                    await name_input.fill("Test Child")
                    
                age_input = self.page.locator('input[placeholder*="age"], input[name*="age"], input[type="number"]').first
                if await age_input.is_visible():
                    await age_input.fill("7")
                
                # Look for save/submit button
                save_buttons = await self.page.locator('button:has-text("Save"), button:has-text("Submit"), button:has-text("Next")').count()
                if save_buttons > 0:
                    await self.page.locator('button:has-text("Save"), button:has-text("Submit"), button:has-text("Next")').first.click()
                    await self.page.wait_for_timeout(2000)
                    
                    self.tests_passed += 1
                    print("✅ Profile Setup: FORM SUBMITTED")
                else:
                    self.tests_failed += 1
                    print("❌ Profile Setup: NO SAVE BUTTON FOUND")
                    self.bugs_found.append({
                        "test": "Profile Setup",
                        "error": "No save button found in profile form"
                    })
            else:
                self.tests_failed += 1
                print("❌ Profile Setup: NO PROFILE FORM FOUND")
                self.bugs_found.append({
                    "test": "Profile Setup",
                    "error": "Profile setup form not found"
                })
                
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Profile Setup: EXCEPTION - {str(e)}")
            self.bugs_found.append({
                "test": "Profile Setup",
                "error": f"Exception during profile setup: {str(e)}"
            })
    
    async def test_chat_interface(self):
        """Test chat interface functionality"""
        print("\n💬 TESTING CHAT INTERFACE...")
        
        try:
            # Look for chat interface elements
            chat_indicators = [
                "chat",
                "message", 
                "microphone",
                "talk",
                "buddy"
            ]
            
            page_content = await self.page.content()
            found_chat = any(indicator in page_content.lower() for indicator in chat_indicators)
            
            if found_chat:
                # Look for microphone button
                mic_button = self.page.locator('button[aria-label*="microphone"], button[aria-label*="record"], .microphone, [class*="mic"]').first
                if await mic_button.is_visible():
                    self.tests_passed += 1
                    print("✅ Chat Interface: MICROPHONE BUTTON VISIBLE")
                    
                    # Test microphone button click
                    try:
                        await mic_button.click()
                        await self.page.wait_for_timeout(1000)
                        self.tests_passed += 1
                        print("✅ Chat Interface: MICROPHONE BUTTON CLICKABLE")
                    except Exception as e:
                        self.tests_failed += 1
                        print(f"❌ Chat Interface: MICROPHONE CLICK FAILED - {str(e)}")
                        self.bugs_found.append({
                            "test": "Microphone Button Click",
                            "error": f"Click failed: {str(e)}"
                        })
                else:
                    self.tests_failed += 1
                    print("❌ Chat Interface: NO MICROPHONE BUTTON FOUND")
                    self.bugs_found.append({
                        "test": "Chat Interface",
                        "error": "Microphone button not found"
                    })
            else:
                self.tests_failed += 1
                print("❌ Chat Interface: CHAT INTERFACE NOT FOUND")
                self.bugs_found.append({
                    "test": "Chat Interface",
                    "error": "Chat interface not found"
                })
                
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Chat Interface: EXCEPTION - {str(e)}")
            self.bugs_found.append({
                "test": "Chat Interface",
                "error": f"Exception during chat test: {str(e)}"
            })
    
    async def test_dark_mode(self):
        """Test dark mode functionality"""
        print("\n🌙 TESTING DARK MODE...")
        
        try:
            # Look for dark mode toggle
            dark_mode_selectors = [
                'button[aria-label*="dark"]',
                'button[aria-label*="theme"]', 
                '.dark-mode',
                '[class*="theme"]',
                'button:has-text("🌙")',
                'button:has-text("☀")'
            ]
            
            dark_mode_button = None
            for selector in dark_mode_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.is_visible():
                        dark_mode_button = element
                        break
                except:
                    continue
            
            if dark_mode_button:
                # Test dark mode toggle
                await dark_mode_button.click()
                await self.page.wait_for_timeout(1000)
                
                # Check if dark mode was applied
                body_class = await self.page.locator('body').get_attribute('class')
                html_class = await self.page.locator('html').get_attribute('class')
                
                if 'dark' in (body_class or '') or 'dark' in (html_class or ''):
                    self.tests_passed += 1
                    print("✅ Dark Mode: TOGGLE WORKING")
                else:
                    self.tests_failed += 1
                    print("❌ Dark Mode: TOGGLE NOT WORKING")
                    self.bugs_found.append({
                        "test": "Dark Mode Toggle",
                        "error": "Dark mode class not applied to body/html"
                    })
            else:
                self.tests_failed += 1
                print("❌ Dark Mode: TOGGLE BUTTON NOT FOUND")
                self.bugs_found.append({
                    "test": "Dark Mode",
                    "error": "Dark mode toggle button not found"
                })
                
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Dark Mode: EXCEPTION - {str(e)}")
            self.bugs_found.append({
                "test": "Dark Mode",
                "error": f"Exception during dark mode test: {str(e)}"
            })
    
    async def cleanup(self):
        """Cleanup browser resources"""
        if hasattr(self, 'context'):
            await self.context.close()
        if hasattr(self, 'browser'):
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def run_all_tests(self):
        """Run all frontend tests"""
        print("🚀 STARTING ATOMIC FRONTEND TESTING...")
        start_time = time.time()
        
        try:
            await self.setup_browser()
            
            await self.test_landing_page()
            await self.test_signup_flow()
            await self.test_profile_setup()
            await self.test_chat_interface()
            await self.test_dark_mode()
            
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
        
        print(f"\n📊 FRONTEND TEST RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {total_time:.2f}s")
        print(f"Bugs Found: {len(self.bugs_found)}")
        
        if self.bugs_found:
            print(f"\n🐛 FRONTEND BUGS FOUND:")
            for i, bug in enumerate(self.bugs_found, 1):
                print(f"{i}. {bug.get('test', 'Unknown')}: {bug.get('error', bug.get('message', 'Unknown error'))}")
        
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
        tester = AtomicFrontendTester()
        results = await tester.run_all_tests()
        
        # Save results
        with open('/app/atomic_frontend_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n🎯 Results saved to: /app/atomic_frontend_results.json")
        
        if results['success_rate'] < 100:
            print(f"❌ {results['failed']} FRONTEND BUGS NEED FIXING!")
            sys.exit(1)
        else:
            print("✅ ALL FRONTEND TESTS PASSED!")
    
    asyncio.run(main())