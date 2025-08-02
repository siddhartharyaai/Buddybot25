#!/usr/bin/env python3
"""
Story Generation Timeout Fix Validation Test
Focus: Test the story generation timeout fix implementation
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://5989f568-2718-4892-b46b-e42563583d9e.preview.emergentagent.com/api"

class StoryTimeoutFixTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.user_id = "timeout_test_user"
        self.session_id = f"timeout_test_session_{int(time.time())}"
        
    async def setup_session(self):
        """Setup HTTP session"""
        timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout for requests
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details, duration=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        print(f"{status}: {test_name}{duration_str}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        
    async def test_health_check(self):
        """Test system health before story generation tests"""
        print("\n🏥 TESTING SYSTEM HEALTH...")
        
        try:
            start_time = time.time()
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    agents_status = data.get("agents", {})
                    orchestrator_ok = agents_status.get("orchestrator", False)
                    gemini_ok = agents_status.get("gemini_configured", False)
                    
                    if orchestrator_ok and gemini_ok:
                        self.log_result("System Health Check", True, 
                                      f"All systems operational - orchestrator: {orchestrator_ok}, gemini: {gemini_ok}", duration)
                        return True
                    else:
                        self.log_result("System Health Check", False, 
                                      f"System issues - orchestrator: {orchestrator_ok}, gemini: {gemini_ok}", duration)
                        return False
                else:
                    self.log_result("System Health Check", False, 
                                  f"HTTP {response.status}", duration)
                    return False
                    
        except Exception as e:
            self.log_result("System Health Check", False, f"Exception: {str(e)}")
            return False
            
    async def test_story_generation_timeout_fix(self, story_prompt, test_name):
        """Test story generation with timeout monitoring"""
        print(f"\n🎭 TESTING STORY GENERATION: {test_name}")
        
        try:
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "message": story_prompt
            }
            
            start_time = time.time()
            print(f"   📝 Prompt: '{story_prompt}'")
            print(f"   ⏱️  Starting at: {datetime.now().strftime('%H:%M:%S')}")
            
            async with self.session.post(f"{BACKEND_URL}/conversations/text", 
                                       json=payload,
                                       headers={"Content-Type": "application/json"}) as response:
                
                duration = time.time() - start_time
                print(f"   ⏱️  Response received after: {duration:.2f}s")
                
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    word_count = len(response_text.split()) if response_text else 0
                    
                    # Check timeout fix criteria
                    timeout_fixed = duration <= 30.0  # Should complete within 30 seconds
                    has_content = word_count > 0
                    meets_length = word_count >= 50  # At least some substantial content
                    
                    success = timeout_fixed and has_content
                    
                    details = f"Duration: {duration:.2f}s, Words: {word_count}, Content: {'Yes' if has_content else 'No'}"
                    if word_count >= 300:
                        details += " (Meets 300+ word target)"
                    elif word_count >= 100:
                        details += " (Good length)"
                    elif word_count >= 50:
                        details += " (Acceptable length)"
                    else:
                        details += " (Too short)"
                        
                    if not timeout_fixed:
                        details += f" - TIMEOUT ISSUE: {duration:.2f}s > 30s limit"
                        
                    self.log_result(f"Story Generation - {test_name}", success, details, duration)
                    
                    # Log story preview
                    if response_text:
                        preview = response_text[:150] + "..." if len(response_text) > 150 else response_text
                        print(f"   📖 Story preview: {preview}")
                    
                    return success, duration, word_count
                    
                else:
                    error_text = await response.text()
                    self.log_result(f"Story Generation - {test_name}", False, 
                                  f"HTTP {response.status}: {error_text}", duration)
                    return False, duration, 0
                    
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            self.log_result(f"Story Generation - {test_name}", False, 
                          f"Request timeout after {duration:.2f}s - TIMEOUT FIX FAILED", duration)
            return False, duration, 0
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(f"Story Generation - {test_name}", False, 
                          f"Exception after {duration:.2f}s: {str(e)}", duration)
            return False, duration, 0
            
    async def test_multiple_story_requests(self):
        """Test multiple story requests to validate consistent timeout fix"""
        print("\n🎯 TESTING MULTIPLE STORY REQUESTS FOR TIMEOUT FIX...")
        
        story_prompts = [
            ("Tell me a story about a brave little mouse on an adventure", "Brave Mouse Story"),
            ("Can you create a story about a magical forest with talking animals", "Magical Forest Story"),
            ("I want a complete story about friendship and helping others", "Friendship Story")
        ]
        
        results = []
        total_duration = 0
        successful_stories = 0
        
        for prompt, name in story_prompts:
            success, duration, word_count = await self.test_story_generation_timeout_fix(prompt, name)
            results.append((success, duration, word_count))
            total_duration += duration
            
            if success:
                successful_stories += 1
                
            # Small delay between requests
            await asyncio.sleep(1)
            
        # Summary analysis
        avg_duration = total_duration / len(story_prompts)
        success_rate = (successful_stories / len(story_prompts)) * 100
        
        print(f"\n📊 STORY GENERATION TIMEOUT FIX SUMMARY:")
        print(f"   ✅ Successful stories: {successful_stories}/{len(story_prompts)} ({success_rate:.1f}%)")
        print(f"   ⏱️  Average duration: {avg_duration:.2f}s")
        print(f"   🎯 Timeout fix working: {'YES' if avg_duration <= 30 else 'NO'}")
        
        # Overall assessment
        timeout_fix_working = successful_stories >= 2 and avg_duration <= 30
        
        self.log_result("Multiple Story Requests - Timeout Fix", timeout_fix_working,
                       f"Success rate: {success_rate:.1f}%, Avg duration: {avg_duration:.2f}s")
        
        return timeout_fix_working
        
    async def test_quick_integration(self):
        """Quick integration test for basic functionality"""
        print("\n🔗 TESTING QUICK INTEGRATION...")
        
        # Test basic text conversation
        try:
            payload = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "message": "Hello, how are you today?"
            }
            
            start_time = time.time()
            async with self.session.post(f"{BACKEND_URL}/conversations/text", 
                                       json=payload,
                                       headers={"Content-Type": "application/json"}) as response:
                
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response_text", "")
                    has_response = len(response_text) > 0
                    
                    self.log_result("Basic Text Conversation", has_response,
                                  f"Response length: {len(response_text)} chars", duration)
                    return has_response
                else:
                    error_text = await response.text()
                    self.log_result("Basic Text Conversation", False,
                                  f"HTTP {response.status}: {error_text}", duration)
                    return False
                    
        except Exception as e:
            self.log_result("Basic Text Conversation", False, f"Exception: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all timeout fix validation tests"""
        print("🚀 STARTING STORY GENERATION TIMEOUT FIX VALIDATION")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Test 1: System Health
            health_ok = await self.test_health_check()
            if not health_ok:
                print("\n❌ CRITICAL: System health check failed - aborting tests")
                return False
                
            # Test 2: Multiple Story Generation (Main Focus)
            timeout_fix_working = await self.test_multiple_story_requests()
            
            # Test 3: Quick Integration
            integration_ok = await self.test_quick_integration()
            
            # Final Assessment
            print("\n" + "=" * 60)
            print("📋 FINAL ASSESSMENT - STORY GENERATION TIMEOUT FIX")
            print("=" * 60)
            
            passed_tests = sum(1 for result in self.test_results if result["success"])
            total_tests = len(self.test_results)
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
            
            # Key metrics
            story_tests = [r for r in self.test_results if "Story Generation" in r["test"]]
            story_durations = [r["duration"] for r in story_tests if r["duration"] is not None]
            
            if story_durations:
                avg_story_duration = sum(story_durations) / len(story_durations)
                max_story_duration = max(story_durations)
                
                print(f"⏱️  Story Generation Metrics:")
                print(f"   - Average duration: {avg_story_duration:.2f}s")
                print(f"   - Maximum duration: {max_story_duration:.2f}s")
                print(f"   - Timeout fix status: {'✅ WORKING' if max_story_duration <= 30 else '❌ STILL TIMING OUT'}")
                
            # Critical assessment
            critical_success = timeout_fix_working and health_ok
            
            print(f"\n🎯 TIMEOUT FIX VALIDATION: {'✅ SUCCESS' if critical_success else '❌ FAILED'}")
            
            if critical_success:
                print("   The story generation timeout fix is working correctly!")
                print("   Stories are generating within acceptable time limits.")
            else:
                print("   The story generation timeout fix needs further investigation.")
                print("   Stories may still be timing out or system has issues.")
                
            return critical_success
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = StoryTimeoutFixTester()
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())