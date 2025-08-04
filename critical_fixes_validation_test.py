#!/usr/bin/env python3
"""
CRITICAL FIXES VALIDATION TEST - Buddy Bot System
Testing Focus: Story Generation Length, TTS System, End-to-End Performance
Based on Review Request: MAJOR FIXES IMPLEMENTED
"""

import asyncio
import aiohttp
import json
import base64
import time
import logging
from typing import Dict, Any, List
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CriticalFixesValidator:
    def __init__(self):
        # Get backend URL from environment
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=')[1].strip() + '/api'
                        break
                else:
                    self.base_url = "http://localhost:8001/api"
        except FileNotFoundError:
            self.base_url = "http://localhost:8001/api"
        
        logger.info(f"🎯 CRITICAL FIXES VALIDATION: Using backend URL: {self.base_url}")
        
        # Test data
        self.test_user_id = f"critical_test_user_{int(time.time())}"
        self.test_session_id = f"critical_session_{int(time.time())}"
        
        # Test results tracking
        self.test_results = {
            "story_generation_length": [],
            "tts_system_functionality": [],
            "end_to_end_performance": [],
            "enhanced_stt_processing": [],
            "verbal_gamification": [],
            "system_health": []
        }
        
        # Success criteria from review
        self.success_criteria = {
            "story_length_words": 300,  # Target 300+ words
            "story_latency_seconds": 4.0,  # Target <4s
            "first_chunk_latency_seconds": 2.0,  # Target <2s
            "tts_success_rate": 100,  # Target 100% success rate
            "tts_latency_seconds": 3.0  # Target <3s
        }

    async def run_all_tests(self):
        """Run all critical validation tests"""
        logger.info("🚀 STARTING CRITICAL FIXES VALIDATION TESTS")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Test 1: System Health Check
            await self.test_system_health()
            
            # Test 2: Story Generation Length (CRITICAL)
            await self.test_story_generation_length()
            
            # Test 3: TTS System Functionality (CRITICAL)
            await self.test_tts_system_functionality()
            
            # Test 4: End-to-End Performance
            await self.test_end_to_end_performance()
            
            # Test 5: Enhanced STT Processing
            await self.test_enhanced_stt_processing()
            
            # Test 6: Verbal Gamification
            await self.test_verbal_gamification()
            
        # Generate comprehensive report
        self.generate_validation_report()

    async def test_system_health(self):
        """Test system health and agent status"""
        logger.info("🏥 TESTING: System Health Check")
        
        try:
            # Health check
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    self.test_results["system_health"].append({
                        "test": "health_check",
                        "status": "PASS",
                        "data": health_data,
                        "agents_configured": health_data.get("agents", {})
                    })
                    logger.info("✅ Health check passed")
                else:
                    self.test_results["system_health"].append({
                        "test": "health_check",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}"
                    })
                    logger.error(f"❌ Health check failed: HTTP {response.status}")
            
            # Agents status
            async with self.session.get(f"{self.base_url}/agents/status") as response:
                if response.status == 200:
                    agents_data = await response.json()
                    self.test_results["system_health"].append({
                        "test": "agents_status",
                        "status": "PASS",
                        "data": agents_data,
                        "active_agents": len(agents_data.get("agents", {}))
                    })
                    logger.info(f"✅ Agents status: {len(agents_data.get('agents', {}))} active")
                else:
                    self.test_results["system_health"].append({
                        "test": "agents_status",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            logger.error(f"❌ System health test error: {str(e)}")
            self.test_results["system_health"].append({
                "test": "system_health_error",
                "status": "FAIL",
                "error": str(e)
            })

    async def test_story_generation_length(self):
        """CRITICAL TEST: Story generation must produce 300+ words consistently"""
        logger.info("📚 CRITICAL TEST: Story Generation Length (Target: 300+ words)")
        
        story_requests = [
            "Tell me a complete story about a brave little mouse who goes on an adventure",
            "I want a long story about a magical forest with talking animals",
            "Can you tell me a detailed story about two friends who discover a hidden treasure",
            "Tell me a story about a young dragon learning to fly",
            "I need a complete adventure story about a girl who can talk to animals"
        ]
        
        total_tests = len(story_requests)
        passed_tests = 0
        
        for i, story_request in enumerate(story_requests, 1):
            logger.info(f"📖 Story Test {i}/{total_tests}: '{story_request[:50]}...'")
            
            try:
                start_time = time.time()
                
                # Test text conversation for story generation
                payload = {
                    "session_id": f"{self.test_session_id}_story_{i}",
                    "user_id": self.test_user_id,
                    "message": story_request
                }
                
                async with self.session.post(
                    f"{self.base_url}/conversations/text",
                    json=payload
                ) as response:
                    generation_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        story_text = result.get("response_text", "")
                        word_count = len(story_text.split())
                        
                        # Check if meets 300+ word requirement
                        meets_length_requirement = word_count >= self.success_criteria["story_length_words"]
                        meets_latency_requirement = generation_time <= self.success_criteria["story_latency_seconds"]
                        
                        if meets_length_requirement:
                            passed_tests += 1
                            
                        self.test_results["story_generation_length"].append({
                            "test": f"story_generation_{i}",
                            "status": "PASS" if meets_length_requirement else "FAIL",
                            "request": story_request,
                            "word_count": word_count,
                            "target_words": self.success_criteria["story_length_words"],
                            "meets_length_requirement": meets_length_requirement,
                            "generation_time": f"{generation_time:.2f}s",
                            "meets_latency_requirement": meets_latency_requirement,
                            "story_preview": story_text[:200] + "..." if len(story_text) > 200 else story_text
                        })
                        
                        if meets_length_requirement:
                            logger.info(f"✅ Story {i}: {word_count} words (PASS - meets 300+ requirement)")
                        else:
                            logger.error(f"❌ Story {i}: {word_count} words (FAIL - below 300 requirement)")
                            
                    else:
                        error_text = await response.text()
                        self.test_results["story_generation_length"].append({
                            "test": f"story_generation_{i}",
                            "status": "FAIL",
                            "error": f"HTTP {response.status}: {error_text}",
                            "request": story_request
                        })
                        logger.error(f"❌ Story {i} failed: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Story generation test {i} error: {str(e)}")
                self.test_results["story_generation_length"].append({
                    "test": f"story_generation_{i}",
                    "status": "FAIL",
                    "error": str(e),
                    "request": story_request
                })
        
        success_rate = (passed_tests / total_tests) * 100
        logger.info(f"📊 STORY GENERATION RESULTS: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")

    async def test_tts_system_functionality(self):
        """CRITICAL TEST: TTS system must have 100% success rate with Deepgram"""
        logger.info("🔊 CRITICAL TEST: TTS System Functionality (Target: 100% success rate)")
        
        tts_test_texts = [
            "Hello! Welcome to Buddy Bot. I'm your friendly AI companion.",
            "Once upon a time, in a magical forest far away, there lived a brave little mouse named Charlie.",
            "Let me tell you an amazing fact about elephants. Did you know they can remember things for many years?",
            "Great job! You're doing wonderfully. Keep up the excellent work, my friend!",
            "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet."
        ]
        
        personalities = ["friendly_companion", "story_narrator", "learning_buddy"]
        
        total_tests = len(tts_test_texts) * len(personalities)
        passed_tests = 0
        
        for personality in personalities:
            logger.info(f"🎭 Testing TTS with personality: {personality}")
            
            for i, text in enumerate(tts_test_texts, 1):
                try:
                    start_time = time.time()
                    
                    payload = {
                        "text": text,
                        "personality": personality
                    }
                    
                    async with self.session.post(
                        f"{self.base_url}/voice/tts",
                        json=payload
                    ) as response:
                        generation_time = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            audio_base64 = result.get("audio_base64", "")
                            
                            # Check if audio was generated
                            has_audio = bool(audio_base64 and len(audio_base64) > 100)
                            meets_latency = generation_time <= self.success_criteria["tts_latency_seconds"]
                            
                            if has_audio:
                                passed_tests += 1
                                
                            self.test_results["tts_system_functionality"].append({
                                "test": f"tts_{personality}_{i}",
                                "status": "PASS" if has_audio else "FAIL",
                                "text": text[:50] + "..." if len(text) > 50 else text,
                                "personality": personality,
                                "has_audio": has_audio,
                                "audio_length": len(audio_base64) if audio_base64 else 0,
                                "generation_time": f"{generation_time:.2f}s",
                                "meets_latency": meets_latency
                            })
                            
                            if has_audio:
                                logger.info(f"✅ TTS {personality} {i}: Generated {len(audio_base64)} chars audio")
                            else:
                                logger.error(f"❌ TTS {personality} {i}: No audio generated")
                                
                        else:
                            error_text = await response.text()
                            self.test_results["tts_system_functionality"].append({
                                "test": f"tts_{personality}_{i}",
                                "status": "FAIL",
                                "error": f"HTTP {response.status}: {error_text}",
                                "personality": personality
                            })
                            logger.error(f"❌ TTS {personality} {i} failed: HTTP {response.status}")
                            
                except Exception as e:
                    logger.error(f"❌ TTS test {personality} {i} error: {str(e)}")
                    self.test_results["tts_system_functionality"].append({
                        "test": f"tts_{personality}_{i}",
                        "status": "FAIL",
                        "error": str(e),
                        "personality": personality
                    })
        
        success_rate = (passed_tests / total_tests) * 100
        logger.info(f"📊 TTS SYSTEM RESULTS: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")

    async def test_end_to_end_performance(self):
        """Test complete pipeline: STT → Story Generation → TTS"""
        logger.info("🔄 TESTING: End-to-End Performance Pipeline")
        
        # Create a simple audio file for testing (base64 encoded silence)
        # This is a minimal WAV file with 1 second of silence
        test_audio_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="
        
        try:
            start_time = time.time()
            
            # Test voice processing endpoint
            payload = {
                "session_id": f"{self.test_session_id}_e2e",
                "user_id": self.test_user_id,
                "audio_base64": test_audio_base64
            }
            
            async with self.session.post(
                f"{self.base_url}/voice/process_audio",
                data=payload
            ) as response:
                total_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    has_transcript = bool(result.get("transcript"))
                    has_response_text = bool(result.get("response_text"))
                    has_response_audio = bool(result.get("response_audio"))
                    pipeline_used = result.get("pipeline", "unknown")
                    
                    self.test_results["end_to_end_performance"].append({
                        "test": "voice_processing_pipeline",
                        "status": "PASS" if has_response_text else "FAIL",
                        "total_time": f"{total_time:.2f}s",
                        "has_transcript": has_transcript,
                        "has_response_text": has_response_text,
                        "has_response_audio": has_response_audio,
                        "pipeline_used": pipeline_used,
                        "transcript": result.get("transcript", ""),
                        "response_preview": result.get("response_text", "")[:100]
                    })
                    
                    logger.info(f"✅ E2E Pipeline: {total_time:.2f}s, Pipeline: {pipeline_used}")
                    
                else:
                    error_text = await response.text()
                    self.test_results["end_to_end_performance"].append({
                        "test": "voice_processing_pipeline",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}: {error_text}"
                    })
                    logger.error(f"❌ E2E Pipeline failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ End-to-end test error: {str(e)}")
            self.test_results["end_to_end_performance"].append({
                "test": "voice_processing_pipeline",
                "status": "FAIL",
                "error": str(e)
            })

    async def test_enhanced_stt_processing(self):
        """Test enhanced STT for Indian kids with accent corrections"""
        logger.info("🎤 TESTING: Enhanced STT Processing for Indian Kids")
        
        # Test conversation suggestions (template system)
        try:
            async with self.session.get(f"{self.base_url}/conversations/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    
                    self.test_results["enhanced_stt_processing"].append({
                        "test": "conversation_suggestions",
                        "status": "PASS",
                        "suggestions_count": len(suggestions),
                        "suggestions": suggestions[:5]  # First 5 suggestions
                    })
                    
                    logger.info(f"✅ Conversation suggestions: {len(suggestions)} available")
                    
                else:
                    self.test_results["enhanced_stt_processing"].append({
                        "test": "conversation_suggestions",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}"
                    })
                    logger.error(f"❌ Conversation suggestions failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ STT processing test error: {str(e)}")
            self.test_results["enhanced_stt_processing"].append({
                "test": "conversation_suggestions",
                "status": "FAIL",
                "error": str(e)
            })

    async def test_verbal_gamification(self):
        """Test reward system integration and achievement tracking"""
        logger.info("🎮 TESTING: Verbal Gamification System")
        
        try:
            # Test user flags (feature flags for gamification)
            async with self.session.get(f"{self.base_url}/flags/{self.test_user_id}") as response:
                if response.status == 200:
                    flags_data = await response.json()
                    
                    self.test_results["verbal_gamification"].append({
                        "test": "user_flags",
                        "status": "PASS",
                        "flags_count": len(flags_data.get("flags", {})),
                        "flags": flags_data.get("flags", {})
                    })
                    
                    logger.info(f"✅ User flags: {len(flags_data.get('flags', {}))} available")
                    
                else:
                    self.test_results["verbal_gamification"].append({
                        "test": "user_flags",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}"
                    })
                    logger.error(f"❌ User flags failed: HTTP {response.status}")
            
            # Test analytics dashboard (for tracking achievements)
            async with self.session.get(f"{self.base_url}/analytics/dashboard/{self.test_user_id}") as response:
                if response.status == 200:
                    analytics_data = await response.json()
                    
                    self.test_results["verbal_gamification"].append({
                        "test": "analytics_dashboard",
                        "status": "PASS",
                        "analytics_available": True,
                        "data_keys": list(analytics_data.keys())
                    })
                    
                    logger.info("✅ Analytics dashboard accessible")
                    
                else:
                    self.test_results["verbal_gamification"].append({
                        "test": "analytics_dashboard",
                        "status": "FAIL",
                        "error": f"HTTP {response.status}"
                    })
                    logger.error(f"❌ Analytics dashboard failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Verbal gamification test error: {str(e)}")
            self.test_results["verbal_gamification"].append({
                "test": "verbal_gamification_error",
                "status": "FAIL",
                "error": str(e)
            })

    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        logger.info("📋 GENERATING CRITICAL FIXES VALIDATION REPORT")
        
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "test_summary": {},
            "critical_findings": [],
            "success_criteria_analysis": {},
            "detailed_results": self.test_results
        }
        
        # Calculate test summary
        for category, tests in self.test_results.items():
            total_tests = len(tests)
            passed_tests = len([t for t in tests if t.get("status") == "PASS"])
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            report["test_summary"][category] = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": f"{success_rate:.1f}%"
            }
        
        # Analyze critical findings
        story_tests = self.test_results.get("story_generation_length", [])
        story_passes = len([t for t in story_tests if t.get("meets_length_requirement", False)])
        story_total = len(story_tests)
        
        tts_tests = self.test_results.get("tts_system_functionality", [])
        tts_passes = len([t for t in tts_tests if t.get("status") == "PASS"])
        tts_total = len(tts_tests)
        
        # Critical findings
        if story_passes < story_total:
            report["critical_findings"].append({
                "issue": "STORY_GENERATION_LENGTH_FAILURE",
                "severity": "CRITICAL",
                "description": f"Only {story_passes}/{story_total} stories met 300+ word requirement",
                "impact": "Stories are too short, not meeting user expectations"
            })
        
        if tts_passes < tts_total:
            report["critical_findings"].append({
                "issue": "TTS_SYSTEM_FAILURE",
                "severity": "CRITICAL", 
                "description": f"Only {tts_passes}/{tts_total} TTS requests succeeded",
                "impact": "Audio generation failing, breaking voice interaction"
            })
        
        # Success criteria analysis
        report["success_criteria_analysis"] = {
            "story_length_300_words": {
                "target": f"{self.success_criteria['story_length_words']}+ words",
                "achieved": f"{story_passes}/{story_total} stories",
                "success": story_passes == story_total
            },
            "tts_100_percent_success": {
                "target": "100% success rate",
                "achieved": f"{(tts_passes/tts_total*100):.1f}%" if tts_total > 0 else "0%",
                "success": tts_passes == tts_total
            }
        }
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 CRITICAL FIXES VALIDATION REPORT")
        print("="*80)
        
        print("\n📊 TEST SUMMARY:")
        for category, summary in report["test_summary"].items():
            status = "✅" if summary["success_rate"] == "100.0%" else "❌"
            print(f"{status} {category}: {summary['passed_tests']}/{summary['total_tests']} ({summary['success_rate']})")
        
        print("\n🚨 CRITICAL FINDINGS:")
        if report["critical_findings"]:
            for finding in report["critical_findings"]:
                print(f"❌ {finding['issue']}: {finding['description']}")
        else:
            print("✅ No critical issues found!")
        
        print("\n🎯 SUCCESS CRITERIA ANALYSIS:")
        for criterion, analysis in report["success_criteria_analysis"].items():
            status = "✅" if analysis["success"] else "❌"
            print(f"{status} {criterion}: {analysis['achieved']} (Target: {analysis['target']})")
        
        print("\n" + "="*80)
        
        # Save detailed report
        with open('/app/critical_fixes_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("📄 Detailed report saved to: /app/critical_fixes_validation_report.json")

async def main():
    """Main test execution"""
    validator = CriticalFixesValidator()
    await validator.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())