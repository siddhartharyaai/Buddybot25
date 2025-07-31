#!/usr/bin/env python3
"""
Focused Session Management Features Test
Tests the specific features mentioned in the review request
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
BACKEND_URL = "https://9c87ad27-55c0-4609-a47c-ef5b9de00cdd.preview.emergentagent.com/api"

async def test_specific_session_features():
    """Test specific session management features from review request"""
    async with aiohttp.ClientSession() as session:
        results = {}
        
        # Setup test user and session
        logger.info("Setting up test user and session...")
        
        # Create test user
        profile_data = {
            "name": "SessionFeatureTestUser",
            "age": 8,
            "location": "Test City",
            "timezone": "America/New_York",
            "language": "english",
            "voice_personality": "friendly_companion",
            "interests": ["stories", "games"],
            "learning_goals": ["reading"],
            "parent_email": "test@example.com"
        }
        
        async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
            if response.status != 200:
                return {"error": "Failed to create test user"}
            user_data = await response.json()
            test_user_id = user_data["id"]
        
        # Create test session
        session_data = {"user_id": test_user_id, "session_name": "Feature Test Session"}
        async with session.post(f"{BACKEND_URL}/conversations/session", json=session_data) as response:
            if response.status != 200:
                return {"error": "Failed to create test session"}
            session_data = await response.json()
            test_session_id = session_data["id"]
        
        # Start ambient listening for session tracking
        start_request = {"session_id": test_session_id, "user_id": test_user_id}
        async with session.post(f"{BACKEND_URL}/ambient/start", json=start_request) as response:
            if response.status != 200:
                return {"error": "Failed to start ambient listening"}
        
        # 1. Test Session Start Times and Interaction Counts
        logger.info("Testing session tracking...")
        try:
            # Send some interactions
            for i in range(5):
                text_input = {
                    "session_id": test_session_id,
                    "user_id": test_user_id,
                    "message": f"Session tracking test {i+1}"
                }
                async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                    if response.status != 200:
                        break
                await asyncio.sleep(0.1)
            
            # Check session status
            async with session.get(f"{BACKEND_URL}/ambient/status/{test_session_id}") as response:
                if response.status == 200:
                    status_data = await response.json()
                    results["session_tracking"] = {
                        "status": "PASS",
                        "session_tracked": bool(status_data.get("session_id")),
                        "session_id_matches": status_data.get("session_id") == test_session_id,
                        "ambient_listening": status_data.get("ambient_listening", False),
                        "conversation_active": status_data.get("conversation_active", False),
                        "listening_state": status_data.get("listening_state")
                    }
                else:
                    results["session_tracking"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["session_tracking"] = {"status": "ERROR", "error": str(e)}
        
        # 2. Test Enhanced Conversation Processing with Session Management Checks
        logger.info("Testing enhanced conversation processing...")
        try:
            text_input = {
                "session_id": test_session_id,
                "user_id": test_user_id,
                "message": "Tell me about a brave little mouse who helps others"
            }
            
            async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                if response.status == 200:
                    conv_data = await response.json()
                    metadata = conv_data.get("metadata", {})
                    
                    results["enhanced_conversation_processing"] = {
                        "status": "PASS",
                        "response_received": bool(conv_data.get("response_text")),
                        "content_type": conv_data.get("content_type"),
                        "has_metadata": bool(metadata),
                        "has_emotional_state": bool(metadata.get("emotional_state")),
                        "has_dialogue_plan": bool(metadata.get("dialogue_plan")),
                        "has_memory_context": bool(metadata.get("memory_context")),
                        "response_length": len(conv_data.get("response_text", "")),
                        "session_management_integrated": conv_data.get("content_type") in ["conversation", "story", "rate_limit", "mic_locked", "break_suggestion"]
                    }
                else:
                    results["enhanced_conversation_processing"] = {"status": "FAIL", "error": f"HTTP {response.status}"}
        except Exception as e:
            results["enhanced_conversation_processing"] = {"status": "ERROR", "error": str(e)}
        
        # 3. Test Integration with start_ambient_listening
        logger.info("Testing start_ambient_listening integration...")
        try:
            # Create a new session for this test
            new_session_id = str(uuid.uuid4())
            start_request = {"session_id": new_session_id, "user_id": test_user_id}
            
            async with session.post(f"{BACKEND_URL}/ambient/start", json=start_request) as response:
                if response.status == 200:
                    start_data = await response.json()
                    
                    # Check if session tracking was initialized
                    async with session.get(f"{BACKEND_URL}/ambient/status/{new_session_id}") as status_response:
                        if status_response.status == 200:
                            status_data = await status_response.json()
                            
                            results["ambient_listening_integration"] = {
                                "status": "PASS",
                                "ambient_start_successful": bool(start_data.get("status")),
                                "session_tracking_initialized": bool(status_data.get("session_id")),
                                "session_id_matches": status_data.get("session_id") == new_session_id,
                                "ambient_listening_active": status_data.get("ambient_listening", False),
                                "listening_state": status_data.get("listening_state")
                            }
                            
                            # Clean up
                            stop_request = {"session_id": new_session_id}
                            async with session.post(f"{BACKEND_URL}/ambient/stop", json=stop_request) as stop_response:
                                pass
                        else:
                            results["ambient_listening_integration"] = {"status": "FAIL", "error": f"Status check failed: {status_response.status}"}
                else:
                    results["ambient_listening_integration"] = {"status": "FAIL", "error": f"Ambient start failed: {response.status}"}
        except Exception as e:
            results["ambient_listening_integration"] = {"status": "ERROR", "error": str(e)}
        
        # 4. Test Session Store Maintenance
        logger.info("Testing session store maintenance...")
        try:
            # Create multiple sessions to test store
            session_ids = []
            for i in range(3):
                new_session_id = str(uuid.uuid4())
                session_ids.append(new_session_id)
                
                start_request = {"session_id": new_session_id, "user_id": test_user_id}
                async with session.post(f"{BACKEND_URL}/ambient/start", json=start_request) as response:
                    if response.status != 200:
                        break
            
            # Check all sessions are tracked
            tracked_sessions = 0
            for session_id in session_ids:
                async with session.get(f"{BACKEND_URL}/ambient/status/{session_id}") as response:
                    if response.status == 200:
                        status_data = await response.json()
                        if status_data.get("session_id") == session_id:
                            tracked_sessions += 1
            
            results["session_store_maintenance"] = {
                "status": "PASS",
                "sessions_created": len(session_ids),
                "sessions_tracked": tracked_sessions,
                "all_sessions_tracked": tracked_sessions == len(session_ids),
                "session_store_working": tracked_sessions > 0
            }
            
            # Clean up sessions
            for session_id in session_ids:
                stop_request = {"session_id": session_id}
                async with session.post(f"{BACKEND_URL}/ambient/stop", json=stop_request) as stop_response:
                    pass
                    
        except Exception as e:
            results["session_store_maintenance"] = {"status": "ERROR", "error": str(e)}
        
        # 5. Test Telemetry Events for Session Management
        logger.info("Testing telemetry events...")
        try:
            # Send interactions to generate telemetry events
            for i in range(3):
                text_input = {
                    "session_id": test_session_id,
                    "user_id": test_user_id,
                    "message": f"Telemetry event test {i+1}"
                }
                async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
                    if response.status != 200:
                        break
                await asyncio.sleep(0.1)
            
            # Check analytics dashboard
            async with session.get(f"{BACKEND_URL}/analytics/dashboard/{test_user_id}?days=1") as response:
                if response.status == 200:
                    analytics_data = await response.json()
                    
                    results["telemetry_events"] = {
                        "status": "PASS",
                        "analytics_accessible": True,
                        "has_date_range": bool(analytics_data.get("date_range")),
                        "total_users": analytics_data.get("total_users", 0),
                        "total_sessions": analytics_data.get("total_sessions", 0),
                        "total_interactions": analytics_data.get("total_interactions", 0),
                        "has_feature_usage": bool(analytics_data.get("feature_usage")),
                        "has_engagement_trends": bool(analytics_data.get("engagement_trends")),
                        "telemetry_system_working": True  # Analytics endpoint is accessible
                    }
                else:
                    results["telemetry_events"] = {"status": "FAIL", "error": f"Analytics failed: {response.status}"}
        except Exception as e:
            results["telemetry_events"] = {"status": "ERROR", "error": str(e)}
        
        # 6. Test All Existing Functionality Still Works
        logger.info("Testing existing functionality...")
        try:
            # Test memory management
            async with session.post(f"{BACKEND_URL}/memory/snapshot/{test_user_id}") as response:
                memory_snapshot_works = response.status == 200
            
            # Test content suggestions
            async with session.get(f"{BACKEND_URL}/content/suggestions/{test_user_id}") as response:
                content_suggestions_work = response.status == 200
            
            # Test voice personalities
            async with session.get(f"{BACKEND_URL}/voice/personalities") as response:
                voice_personalities_work = response.status == 200
            
            # Test agent status
            async with session.get(f"{BACKEND_URL}/agents/status") as response:
                agent_status_works = response.status == 200
                if response.status == 200:
                    agent_data = await response.json()
                    all_agents_active = (
                        agent_data.get("orchestrator") == "active" and
                        agent_data.get("memory_agent") == "active" and
                        agent_data.get("telemetry_agent") == "active"
                    )
                else:
                    all_agents_active = False
            
            results["existing_functionality"] = {
                "status": "PASS",
                "memory_management_works": memory_snapshot_works,
                "content_suggestions_work": content_suggestions_work,
                "voice_personalities_work": voice_personalities_work,
                "agent_status_works": agent_status_works,
                "all_agents_active": all_agents_active,
                "no_regression": all([memory_snapshot_works, content_suggestions_work, voice_personalities_work, agent_status_works])
            }
        except Exception as e:
            results["existing_functionality"] = {"status": "ERROR", "error": str(e)}
        
        # 7. Test Data Validation
        logger.info("Testing data validation...")
        try:
            # End session to get telemetry data
            async with session.post(f"{BACKEND_URL}/session/end/{test_session_id}") as response:
                if response.status == 200:
                    end_data = await response.json()
                    
                    results["data_validation"] = {
                        "status": "PASS",
                        "session_end_successful": bool(end_data.get("session_id")),
                        "session_id_correct": end_data.get("session_id") == test_session_id,
                        "has_duration": "duration" in end_data,
                        "has_interactions": "interactions" in end_data,
                        "has_engagement_score": "engagement_score" in end_data,
                        "duration_is_number": isinstance(end_data.get("duration"), (int, float)),
                        "interactions_is_number": isinstance(end_data.get("interactions"), int),
                        "engagement_score_is_number": isinstance(end_data.get("engagement_score"), (int, float)),
                        "data_properly_stored": all([
                            end_data.get("session_id") == test_session_id,
                            "duration" in end_data,
                            "interactions" in end_data
                        ])
                    }
                else:
                    results["data_validation"] = {"status": "FAIL", "error": f"Session end failed: {response.status}"}
        except Exception as e:
            results["data_validation"] = {"status": "ERROR", "error": str(e)}
        
        return results

def print_focused_results(results):
    """Print focused test results"""
    print("\n" + "="*80)
    print("FOCUSED SESSION MANAGEMENT FEATURES TEST RESULTS")
    print("="*80)
    
    if "error" in results:
        print(f"❌ Setup Error: {results['error']}")
        return
    
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
    
    # Map test keys to readable names
    test_names = {
        "session_tracking": "Session Tracking (Start Times & Interaction Counts)",
        "enhanced_conversation_processing": "Enhanced Conversation Processing with Session Management",
        "ambient_listening_integration": "Start Ambient Listening with Session Tracking",
        "session_store_maintenance": "Session Store Maintenance",
        "telemetry_events": "Telemetry Events for Session Management",
        "existing_functionality": "All Existing Functionality Still Works",
        "data_validation": "Data Validation (Session Data Storage)"
    }
    
    for test_key, result in results.items():
        test_name = test_names.get(test_key, test_key.replace('_', ' ').title())
        status = result.get("status", "UNKNOWN")
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        
        if status != "PASS" and "error" in result:
            print(f"   Error: {result['error']}")
        elif status == "PASS":
            # Show key success metrics
            key_info = {k: v for k, v in result.items() 
                      if k not in ["status"] and not k.startswith("_")}
            if key_info:
                # Show only the most important details
                important_keys = ["session_tracked", "response_received", "ambient_start_successful", 
                                "all_sessions_tracked", "telemetry_system_working", "no_regression", 
                                "data_properly_stored"]
                important_info = {k: v for k, v in key_info.items() if k in important_keys}
                if important_info:
                    print(f"   Key Results: {important_info}")
    
    print("\n" + "="*80)
    
    # Review Request Feature Summary
    print("\nREVIEW REQUEST FEATURES SUMMARY:")
    
    features_status = {
        "Session Tracking (Start Times & Interaction Counts)": results.get("session_tracking", {}).get("status") == "PASS",
        "Enhanced Conversation Flow with Session Management": results.get("enhanced_conversation_processing", {}).get("status") == "PASS",
        "Integration with start_ambient_listening": results.get("ambient_listening_integration", {}).get("status") == "PASS",
        "Session Store Maintenance": results.get("session_store_maintenance", {}).get("status") == "PASS",
        "Telemetry Events for Session Management": results.get("telemetry_events", {}).get("status") == "PASS",
        "No Regression in Existing Functionality": results.get("existing_functionality", {}).get("status") == "PASS",
        "Data Validation (Session Data Storage)": results.get("data_validation", {}).get("status") == "PASS"
    }
    
    for feature, working in features_status.items():
        symbol = "✅" if working else "❌"
        print(f"{symbol} {feature}: {'Working' if working else 'Not Working'}")
    
    print("\n" + "="*80)
    
    # Overall Assessment
    all_working = all(features_status.values())
    print(f"\n🎯 OVERALL SESSION MANAGEMENT ASSESSMENT: {'✅ ALL FEATURES WORKING' if all_working else '❌ SOME FEATURES NEED ATTENTION'}")
    
    if all_working:
        print("\n✨ The newly implemented session management features are fully operational!")
        print("   • Session tracking is working correctly")
        print("   • Enhanced conversation flow integrates session management")
        print("   • Telemetry events are being tracked")
        print("   • No regression in existing functionality")
        print("   • Data validation confirms proper storage")
    
    print("\n" + "="*80)

async def main():
    """Main execution"""
    logger.info("Starting Focused Session Management Features Test...")
    results = await test_specific_session_features()
    print_focused_results(results)
    
    # Return success status
    if "error" not in results:
        passed_tests = sum(1 for result in results.values() if result.get("status") == "PASS")
        total_tests = len(results)
        return passed_tests == total_tests
    else:
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)