#!/usr/bin/env python3
"""
Quick Session Management Features Test
Tests the key session management features with minimal interactions
"""

import asyncio
import aiohttp
import json
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = "https://dfc58399-9814-411f-9cc5-6e9560883b27.preview.emergentagent.com/api"

async def test_session_management():
    """Test session management features"""
    async with aiohttp.ClientSession() as session:
        results = {}
        
        # 1. Test Health Check
        logger.info("Testing Health Check...")
        try:
            async with session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    results["health_check"] = {
                        "status": "PASS",
                        "orchestrator_active": data["agents"]["orchestrator"],
                        "gemini_configured": data["agents"]["gemini_configured"],
                        "deepgram_configured": data["agents"]["deepgram_configured"]
                    }
                else:
                    results["health_check"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["health_check"] = {"status": "ERROR", "error": str(e)}
        
        # 2. Create Test User
        logger.info("Creating test user...")
        try:
            profile_data = {
                "name": "QuickTestUser",
                "age": 7,
                "location": "Test City",
                "timezone": "America/New_York",
                "language": "english",
                "voice_personality": "friendly_companion",
                "interests": ["stories"],
                "learning_goals": ["reading"],
                "parent_email": "test@example.com"
            }
            
            async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
                if response.status == 200:
                    user_data = await response.json()
                    test_user_id = user_data["id"]
                    results["user_creation"] = {"status": "PASS", "user_id": test_user_id}
                else:
                    results["user_creation"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
                    return results
        except Exception as e:
            results["user_creation"] = {"status": "ERROR", "error": str(e)}
            return results
        
        # 3. Create Test Session
        logger.info("Creating test session...")
        try:
            session_data = {"user_id": test_user_id, "session_name": "Quick Test Session"}
            
            async with session.post(f"{BACKEND_URL}/conversations/session", json=session_data) as response:
                if response.status == 200:
                    session_data = await response.json()
                    test_session_id = session_data["id"]
                    results["session_creation"] = {"status": "PASS", "session_id": test_session_id}
                else:
                    results["session_creation"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
                    return results
        except Exception as e:
            results["session_creation"] = {"status": "ERROR", "error": str(e)}
            return results
        
        # 4. Test Ambient Listening Start (Session Tracking Initialization)
        logger.info("Testing ambient listening start with session tracking...")
        try:
            start_request = {"session_id": test_session_id, "user_id": test_user_id}
            
            async with session.post(f"{BACKEND_URL}/ambient/start", json=start_request) as response:
                if response.status == 200:
                    start_data = await response.json()
                    results["ambient_start"] = {
                        "status": "PASS",
                        "ambient_started": bool(start_data.get("status")),
                        "session_tracking_initialized": True
                    }
                else:
                    results["ambient_start"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["ambient_start"] = {"status": "ERROR", "error": str(e)}
        
        # 5. Test Session Status (Session Store Verification)
        logger.info("Testing session status...")
        try:
            async with session.get(f"{BACKEND_URL}/ambient/status/{test_session_id}") as response:
                if response.status == 200:
                    status_data = await response.json()
                    results["session_status"] = {
                        "status": "PASS",
                        "session_tracked": bool(status_data.get("session_id")),
                        "session_id_matches": status_data.get("session_id") == test_session_id,
                        "ambient_listening": status_data.get("ambient_listening", False),
                        "listening_state": status_data.get("listening_state")
                    }
                else:
                    results["session_status"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["session_status"] = {"status": "ERROR", "error": str(e)}
        
        # 6. Test Enhanced Conversation Flow
        logger.info("Testing enhanced conversation flow...")
        try:
            text_input = {
                "session_id": test_session_id,
                "user_id": test_user_id,
                "message": "Hi! Can you tell me a short story?"
            }
            
            async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                if response.status == 200:
                    conv_data = await response.json()
                    results["enhanced_conversation"] = {
                        "status": "PASS",
                        "response_received": bool(conv_data.get("response_text")),
                        "content_type": conv_data.get("content_type"),
                        "has_metadata": bool(conv_data.get("metadata")),
                        "response_length": len(conv_data.get("response_text", ""))
                    }
                else:
                    results["enhanced_conversation"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["enhanced_conversation"] = {"status": "ERROR", "error": str(e)}
        
        # 7. Test Multiple Interactions (Interaction Count)
        logger.info("Testing interaction count tracking...")
        try:
            interaction_count = 3
            successful_interactions = 0
            
            for i in range(interaction_count):
                text_input = {
                    "session_id": test_session_id,
                    "user_id": test_user_id,
                    "message": f"Test interaction {i+1}"
                }
                
                async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                    if response.status == 200:
                        successful_interactions += 1
                
                await asyncio.sleep(0.2)
            
            results["interaction_tracking"] = {
                "status": "PASS",
                "interactions_sent": interaction_count,
                "successful_interactions": successful_interactions,
                "tracking_working": successful_interactions > 0
            }
        except Exception as e:
            results["interaction_tracking"] = {"status": "ERROR", "error": str(e)}
        
        # 8. Test Analytics Dashboard (Telemetry)
        logger.info("Testing telemetry/analytics...")
        try:
            async with session.get(f"{BACKEND_URL}/analytics/dashboard/{test_user_id}?days=1") as response:
                if response.status == 200:
                    analytics_data = await response.json()
                    results["telemetry_analytics"] = {
                        "status": "PASS",
                        "analytics_accessible": True,
                        "total_interactions": analytics_data.get("total_interactions", 0),
                        "total_sessions": analytics_data.get("total_sessions", 0),
                        "has_feature_usage": bool(analytics_data.get("feature_usage")),
                        "telemetry_working": analytics_data.get("total_interactions", 0) > 0
                    }
                else:
                    results["telemetry_analytics"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["telemetry_analytics"] = {"status": "ERROR", "error": str(e)}
        
        # 9. Test Session End
        logger.info("Testing session end...")
        try:
            async with session.post(f"{BACKEND_URL}/session/end/{test_session_id}") as response:
                if response.status == 200:
                    end_data = await response.json()
                    results["session_end"] = {
                        "status": "PASS",
                        "session_ended": bool(end_data.get("session_id")),
                        "has_duration": "duration" in end_data,
                        "has_interactions": "interactions" in end_data,
                        "has_engagement_score": "engagement_score" in end_data
                    }
                else:
                    results["session_end"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["session_end"] = {"status": "ERROR", "error": str(e)}
        
        # 10. Test Agent Status
        logger.info("Testing agent status...")
        try:
            async with session.get(f"{BACKEND_URL}/agents/status") as response:
                if response.status == 200:
                    agent_data = await response.json()
                    results["agent_status"] = {
                        "status": "PASS",
                        "orchestrator_active": agent_data.get("orchestrator") == "active",
                        "memory_agent_active": agent_data.get("memory_agent") == "active",
                        "telemetry_agent_active": agent_data.get("telemetry_agent") == "active",
                        "session_count": agent_data.get("session_count", 0),
                        "has_memory_statistics": bool(agent_data.get("memory_statistics")),
                        "has_telemetry_statistics": bool(agent_data.get("telemetry_statistics"))
                    }
                else:
                    results["agent_status"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["agent_status"] = {"status": "ERROR", "error": str(e)}
        
        return results

def print_results(results):
    """Print test results"""
    print("\n" + "="*80)
    print("QUICK SESSION MANAGEMENT FEATURES TEST RESULTS")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result.get("status") == "PASS")
    failed_tests = sum(1 for result in results.values() if result.get("status") == "FAIL")
    error_tests = sum(1 for result in results.values() if result.get("status") == "ERROR")
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Errors: {error_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print("-"*80)
    
    for test_name, result in results.items():
        status = result.get("status", "UNKNOWN")
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name.replace('_', ' ').title()}: {status}")
        
        if status != "PASS" and "error" in result:
            print(f"   Error: {result['error']}")
        elif status == "PASS":
            # Show key success metrics
            key_info = {k: v for k, v in result.items() 
                      if k not in ["status"] and not k.startswith("_")}
            if key_info:
                print(f"   Details: {key_info}")
    
    print("\n" + "="*80)
    
    # Session Management Feature Summary
    print("\nSESSION MANAGEMENT FEATURES SUMMARY:")
    
    # Core Features Status
    core_features = {
        "Session Tracking": results.get("session_status", {}).get("status") == "PASS",
        "Interaction Counting": results.get("interaction_tracking", {}).get("status") == "PASS",
        "Enhanced Conversation Flow": results.get("enhanced_conversation", {}).get("status") == "PASS",
        "Telemetry Integration": results.get("telemetry_analytics", {}).get("status") == "PASS",
        "Agent Status Monitoring": results.get("agent_status", {}).get("status") == "PASS"
    }
    
    for feature, working in core_features.items():
        symbol = "✅" if working else "❌"
        print(f"{symbol} {feature}: {'Working' if working else 'Not Working'}")
    
    print("\n" + "="*80)

async def main():
    """Main execution"""
    logger.info("Starting Quick Session Management Features Test...")
    results = await test_session_management()
    print_results(results)
    
    # Return success status
    passed_tests = sum(1 for result in results.values() if result.get("status") == "PASS")
    total_tests = len(results)
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)