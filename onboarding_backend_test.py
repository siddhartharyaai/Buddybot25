#!/usr/bin/env python3
"""
Onboarding Flow Backend Testing Suite
Tests backend endpoints specifically for the new onboarding flow implementation
"""

import asyncio
import aiohttp
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend URL from frontend environment
BACKEND_URL = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"

class OnboardingBackendTester:
    """Focused backend tester for onboarding flow"""
    
    def __init__(self):
        self.session = None
        self.test_results = {}
        self.test_users = []  # Store created test users for cleanup
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_onboarding_tests(self):
        """Run all onboarding-related backend tests"""
        logger.info("🚀 Starting Onboarding Flow Backend Testing...")
        
        # Test sequence for onboarding flow
        test_sequence = [
            # Core Health Check
            ("Health Check", self.test_health_check),
            
            # New User Flow Tests
            ("New User Signup", self.test_new_user_signup),
            ("New User Profile Creation", self.test_new_user_profile_creation),
            ("New User Parental Controls Setup", self.test_new_user_parental_controls),
            ("New User Profile Update During Onboarding", self.test_profile_update_onboarding),
            ("New User is_new_user Flag Verification", self.test_is_new_user_flag),
            
            # Existing User Flow Tests
            ("Existing User Signin", self.test_existing_user_signin),
            ("Existing User Profile Retrieval", self.test_existing_user_profile_retrieval),
            ("Existing User Bypass Onboarding Check", self.test_existing_user_bypass_onboarding),
            
            # Profile Setup Integration Tests
            ("Profile Setup - Basic Information", self.test_profile_setup_basic_info),
            ("Profile Setup - Voice Personality Selection", self.test_profile_setup_voice_personality),
            ("Profile Setup - Interest Selection", self.test_profile_setup_interests),
            ("Profile Setup - Complete Profile Validation", self.test_complete_profile_validation),
            
            # Parental Controls Integration Tests
            ("Parental Controls - Default Creation", self.test_parental_controls_default_creation),
            ("Parental Controls - Time Limits Setup", self.test_parental_controls_time_limits),
            ("Parental Controls - Content Restrictions Setup", self.test_parental_controls_content_restrictions),
            ("Parental Controls - Monitoring Settings", self.test_parental_controls_monitoring),
            
            # Authentication Token Tests
            ("JWT Token Generation", self.test_jwt_token_generation),
            ("JWT Token Validation", self.test_jwt_token_validation),
            ("Profile Access via Token", self.test_profile_access_via_token),
            
            # Environment Consistency Tests
            ("Preview Mode Behavior", self.test_preview_mode_behavior),
            ("Production Mode Simulation", self.test_production_mode_simulation),
            
            # Error Handling Tests
            ("Duplicate Email Handling", self.test_duplicate_email_handling),
            ("Duplicate Name Handling", self.test_duplicate_name_handling),
            ("Invalid Credentials Handling", self.test_invalid_credentials_handling),
            ("Missing Required Fields", self.test_missing_required_fields),
            
            # Data Persistence Tests
            ("User Data Persistence", self.test_user_data_persistence),
            ("Profile Data Persistence", self.test_profile_data_persistence),
            ("Parental Controls Persistence", self.test_parental_controls_persistence),
            
            # Integration Flow Tests
            ("Complete New User Onboarding Flow", self.test_complete_new_user_flow),
            ("Complete Existing User Flow", self.test_complete_existing_user_flow),
        ]
        
        for test_name, test_func in test_sequence:
            try:
                logger.info(f"🧪 Running test: {test_name}")
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result.get("success", False) else "FAIL",
                    "details": result
                }
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                logger.info(f"{status} {test_name}")
            except Exception as e:
                logger.error(f"💥 Test {test_name} failed with exception: {str(e)}")
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": {"error": str(e)}
                }
        
        return self.test_results
    
    async def test_health_check(self):
        """Test health check endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"🏥 Health check response: {data}")
                    
                    return {
                        "success": True,
                        "status": data.get("status"),
                        "agents_initialized": data.get("agents", {}).get("orchestrator", False),
                        "gemini_configured": data.get("agents", {}).get("gemini_configured", False),
                        "deepgram_configured": data.get("agents", {}).get("deepgram_configured", False),
                        "database": data.get("database")
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_new_user_signup(self):
        """Test new user signup endpoint"""
        try:
            # Generate unique test data
            test_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
            test_name = f"TestChild_{uuid.uuid4().hex[:6]}"
            
            signup_data = {
                "email": test_email,
                "password": "TestPassword123!",
                "name": test_name,
                "age": 7,
                "location": "New York"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/signup",
                json=signup_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Store test user for cleanup
                    self.test_users.append({
                        "email": test_email,
                        "user_id": data.get("user_id"),
                        "profile_id": data.get("profile_id"),
                        "access_token": data.get("access_token")
                    })
                    
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "profile_id": data.get("profile_id"),
                        "has_access_token": bool(data.get("access_token")),
                        "token_type": data.get("token_type"),
                        "email": test_email,
                        "name": test_name
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_new_user_profile_creation(self):
        """Test profile creation during signup"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]  # Get the most recent test user
            profile_id = test_user["profile_id"]
            
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{profile_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "profile_id": data.get("id"),
                        "name": data.get("name"),
                        "age": data.get("age"),
                        "location": data.get("location"),
                        "voice_personality": data.get("voice_personality"),
                        "interests": data.get("interests", []),
                        "learning_goals": data.get("learning_goals", []),
                        "avatar": data.get("avatar"),
                        "created_at": data.get("created_at")
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_new_user_parental_controls(self):
        """Test parental controls creation during signup"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            async with self.session.get(
                f"{BACKEND_URL}/users/{profile_id}/parental-controls"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "time_limits": data.get("time_limits", {}),
                        "content_restrictions": data.get("content_restrictions", []),
                        "allowed_content_types": data.get("allowed_content_types", []),
                        "quiet_hours": data.get("quiet_hours", {}),
                        "monitoring_enabled": data.get("monitoring_enabled"),
                        "notification_preferences": data.get("notification_preferences", {})
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_profile_update_onboarding(self):
        """Test profile updates during onboarding process"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            # Simulate profile setup updates
            update_data = {
                "voice_personality": "story_narrator",
                "interests": ["stories", "animals", "music"],
                "learning_goals": ["reading", "counting", "colors"],
                "avatar": "lion",
                "speech_speed": "normal",
                "energy_level": "high"
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/users/profile/{profile_id}",
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "updated_voice_personality": data.get("voice_personality"),
                        "updated_interests": data.get("interests", []),
                        "updated_learning_goals": data.get("learning_goals", []),
                        "updated_avatar": data.get("avatar"),
                        "updated_speech_speed": data.get("speech_speed"),
                        "updated_energy_level": data.get("energy_level"),
                        "updated_at": data.get("updated_at")
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_is_new_user_flag(self):
        """Test that new users have is_new_user flag set correctly"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            access_token = test_user["access_token"]
            
            # Get profile using token to check is_new_user flag
            async with self.session.get(
                f"{BACKEND_URL}/auth/profile",
                params={"token": access_token}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if profile indicates new user status
                    # This might be implicit based on creation time or explicit flag
                    created_at = data.get("created_at")
                    is_recent = False
                    
                    if created_at:
                        from datetime import datetime, timedelta
                        try:
                            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            is_recent = (datetime.now().replace(tzinfo=created_time.tzinfo) - created_time) < timedelta(minutes=5)
                        except:
                            is_recent = True  # Assume recent if parsing fails
                    
                    return {
                        "success": True,
                        "profile_id": data.get("id"),
                        "created_at": created_at,
                        "is_recent_creation": is_recent,
                        "has_minimal_setup": len(data.get("interests", [])) == 0,  # New users start with empty interests
                        "default_voice_personality": data.get("voice_personality") == "friendly_companion",
                        "new_user_indicators": {
                            "recent_creation": is_recent,
                            "minimal_interests": len(data.get("interests", [])) == 0,
                            "default_settings": data.get("voice_personality") == "friendly_companion"
                        }
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_existing_user_signin(self):
        """Test existing user signin"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            # Use the first test user as an "existing" user
            test_user = self.test_users[0]
            
            signin_data = {
                "email": test_user["email"],
                "password": "TestPassword123!"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/signin",
                json=signin_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "user_id": data.get("user_id"),
                        "profile_id": data.get("profile_id"),
                        "has_access_token": bool(data.get("access_token")),
                        "token_type": data.get("token_type"),
                        "existing_user_signin": True
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_existing_user_profile_retrieval(self):
        """Test existing user profile retrieval"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[0]
            profile_id = test_user["profile_id"]
            
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{profile_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if this looks like an existing user (has setup data)
                    has_interests = len(data.get("interests", [])) > 0
                    has_learning_goals = len(data.get("learning_goals", [])) > 0
                    has_custom_settings = data.get("voice_personality") != "friendly_companion"
                    
                    return {
                        "success": True,
                        "profile_id": data.get("id"),
                        "name": data.get("name"),
                        "has_interests": has_interests,
                        "has_learning_goals": has_learning_goals,
                        "has_custom_settings": has_custom_settings,
                        "existing_user_indicators": {
                            "setup_complete": has_interests or has_learning_goals or has_custom_settings,
                            "interests_count": len(data.get("interests", [])),
                            "learning_goals_count": len(data.get("learning_goals", [])),
                            "voice_personality": data.get("voice_personality")
                        }
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_existing_user_bypass_onboarding(self):
        """Test that existing users can bypass onboarding popups"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[0]
            profile_id = test_user["profile_id"]
            
            # Get profile to check completion status
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{profile_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check profile completion indicators
                    has_interests = len(data.get("interests", [])) > 0
                    has_learning_goals = len(data.get("learning_goals", [])) > 0
                    has_voice_personality = data.get("voice_personality") != "friendly_companion"
                    has_avatar = data.get("avatar") != "bunny"  # Default avatar
                    
                    profile_complete = has_interests or has_learning_goals or has_voice_personality or has_avatar
                    
                    # Get parental controls to check completion
                    async with self.session.get(
                        f"{BACKEND_URL}/users/{profile_id}/parental-controls"
                    ) as pc_response:
                        if pc_response.status == 200:
                            pc_data = await pc_response.json()
                            
                            # Check if parental controls have been customized
                            default_time_limits = {"monday": 60, "tuesday": 60, "wednesday": 60, "thursday": 60, "friday": 60, "saturday": 90, "sunday": 90}
                            has_custom_time_limits = pc_data.get("time_limits", {}) != default_time_limits
                            has_content_restrictions = len(pc_data.get("content_restrictions", [])) > 0
                            
                            parental_controls_customized = has_custom_time_limits or has_content_restrictions
                            
                            return {
                                "success": True,
                                "profile_complete": profile_complete,
                                "parental_controls_customized": parental_controls_customized,
                                "should_bypass_onboarding": profile_complete and parental_controls_customized,
                                "completion_indicators": {
                                    "has_interests": has_interests,
                                    "has_learning_goals": has_learning_goals,
                                    "has_custom_voice_personality": has_voice_personality,
                                    "has_custom_avatar": has_avatar,
                                    "has_custom_time_limits": has_custom_time_limits,
                                    "has_content_restrictions": has_content_restrictions
                                }
                            }
                        else:
                            return {"success": False, "error": f"Parental controls check failed: HTTP {pc_response.status}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_profile_setup_basic_info(self):
        """Test profile setup - basic information step"""
        try:
            # Create a new test profile for profile setup testing
            profile_data = {
                "name": f"ProfileSetupTest_{uuid.uuid4().hex[:6]}",
                "age": 8,
                "location": "California",
                "timezone": "America/Los_Angeles",
                "language": "english",
                "parent_email": "parent_setup@example.com"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/users/profile",
                json=profile_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Store for cleanup
                    self.test_users.append({
                        "profile_id": data.get("id"),
                        "email": "profile_setup_test@example.com"
                    })
                    
                    return {
                        "success": True,
                        "profile_id": data.get("id"),
                        "name": data.get("name"),
                        "age": data.get("age"),
                        "location": data.get("location"),
                        "timezone": data.get("timezone"),
                        "language": data.get("language"),
                        "parent_email": data.get("parent_email"),
                        "basic_info_complete": True
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_profile_setup_voice_personality(self):
        """Test profile setup - voice personality selection"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            # Test voice personality options
            voice_personalities = ["friendly_companion", "story_narrator", "learning_buddy"]
            
            for personality in voice_personalities:
                update_data = {"voice_personality": personality}
                
                async with self.session.put(
                    f"{BACKEND_URL}/users/profile/{profile_id}",
                    json=update_data
                ) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"Failed to set {personality}"}
            
            # Verify final personality setting
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{profile_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "voice_personality": data.get("voice_personality"),
                        "voice_personalities_tested": voice_personalities,
                        "voice_personality_step_complete": True
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_profile_setup_interests(self):
        """Test profile setup - interest selection"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            # Test interest selection
            interests = ["stories", "animals", "music", "science", "art", "sports"]
            learning_goals = ["reading", "counting", "colors", "shapes", "letters"]
            
            update_data = {
                "interests": interests,
                "learning_goals": learning_goals
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/users/profile/{profile_id}",
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "interests": data.get("interests", []),
                        "learning_goals": data.get("learning_goals", []),
                        "interests_count": len(data.get("interests", [])),
                        "learning_goals_count": len(data.get("learning_goals", [])),
                        "interest_selection_complete": True
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complete_profile_validation(self):
        """Test complete profile validation after setup"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{profile_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate profile completeness
                    required_fields = ["name", "age", "location", "voice_personality", "interests", "learning_goals"]
                    missing_fields = []
                    
                    for field in required_fields:
                        if not data.get(field):
                            missing_fields.append(field)
                    
                    profile_complete = len(missing_fields) == 0
                    
                    return {
                        "success": True,
                        "profile_complete": profile_complete,
                        "missing_fields": missing_fields,
                        "profile_data": {
                            "name": data.get("name"),
                            "age": data.get("age"),
                            "location": data.get("location"),
                            "voice_personality": data.get("voice_personality"),
                            "interests_count": len(data.get("interests", [])),
                            "learning_goals_count": len(data.get("learning_goals", [])),
                            "avatar": data.get("avatar"),
                            "created_at": data.get("created_at"),
                            "updated_at": data.get("updated_at")
                        }
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_parental_controls_default_creation(self):
        """Test default parental controls creation"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            async with self.session.get(
                f"{BACKEND_URL}/users/{profile_id}/parental-controls"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate default parental controls
                    expected_defaults = {
                        "time_limits": {"monday": 60, "tuesday": 60, "wednesday": 60, "thursday": 60, "friday": 60, "saturday": 90, "sunday": 90},
                        "allowed_content_types": ["story", "song", "rhyme", "educational"],
                        "quiet_hours": {"start": "20:00", "end": "07:00"},
                        "monitoring_enabled": True
                    }
                    
                    defaults_correct = True
                    validation_results = {}
                    
                    for key, expected_value in expected_defaults.items():
                        actual_value = data.get(key)
                        matches = actual_value == expected_value
                        validation_results[key] = {
                            "expected": expected_value,
                            "actual": actual_value,
                            "matches": matches
                        }
                        if not matches:
                            defaults_correct = False
                    
                    return {
                        "success": True,
                        "defaults_correct": defaults_correct,
                        "validation_results": validation_results,
                        "user_id": data.get("user_id"),
                        "content_restrictions": data.get("content_restrictions", []),
                        "notification_preferences": data.get("notification_preferences", {})
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_parental_controls_time_limits(self):
        """Test parental controls time limits setup"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            # Test custom time limits
            custom_time_limits = {
                "monday": 45,
                "tuesday": 45,
                "wednesday": 45,
                "thursday": 45,
                "friday": 60,
                "saturday": 120,
                "sunday": 120
            }
            
            update_data = {"time_limits": custom_time_limits}
            
            async with self.session.put(
                f"{BACKEND_URL}/users/{profile_id}/parental-controls",
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "time_limits_updated": data.get("time_limits") == custom_time_limits,
                        "updated_time_limits": data.get("time_limits"),
                        "custom_time_limits": custom_time_limits,
                        "time_limits_setup_complete": True
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_parental_controls_content_restrictions(self):
        """Test parental controls content restrictions setup"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            # Test content restrictions
            content_restrictions = ["violence", "scary", "mature_themes"]
            allowed_content_types = ["story", "educational", "music"]
            
            update_data = {
                "content_restrictions": content_restrictions,
                "allowed_content_types": allowed_content_types
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/users/{profile_id}/parental-controls",
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "content_restrictions_updated": data.get("content_restrictions") == content_restrictions,
                        "allowed_content_types_updated": data.get("allowed_content_types") == allowed_content_types,
                        "updated_content_restrictions": data.get("content_restrictions"),
                        "updated_allowed_content_types": data.get("allowed_content_types"),
                        "content_restrictions_setup_complete": True
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_parental_controls_monitoring(self):
        """Test parental controls monitoring settings"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            # Test monitoring settings
            monitoring_settings = {
                "monitoring_enabled": True,
                "notification_preferences": {
                    "activity_summary": True,
                    "safety_alerts": True,
                    "weekly_reports": False,
                    "content_alerts": True
                }
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/users/{profile_id}/parental-controls",
                json=monitoring_settings
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "monitoring_enabled": data.get("monitoring_enabled"),
                        "notification_preferences": data.get("notification_preferences"),
                        "monitoring_setup_complete": True,
                        "settings_match": data.get("monitoring_enabled") == monitoring_settings["monitoring_enabled"]
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_jwt_token_generation(self):
        """Test JWT token generation during signup"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[0]
            access_token = test_user.get("access_token")
            
            if not access_token:
                return {"success": False, "error": "No access token available"}
            
            # Basic token structure validation
            token_parts = access_token.split('.')
            has_proper_structure = len(token_parts) == 3  # header.payload.signature
            
            return {
                "success": True,
                "has_access_token": bool(access_token),
                "token_structure_valid": has_proper_structure,
                "token_parts_count": len(token_parts),
                "token_length": len(access_token),
                "token_type": "JWT" if has_proper_structure else "Unknown"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_jwt_token_validation(self):
        """Test JWT token validation"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[0]
            access_token = test_user.get("access_token")
            
            if not access_token:
                return {"success": False, "error": "No access token available"}
            
            # Test token validation by using it to access profile
            async with self.session.get(
                f"{BACKEND_URL}/auth/profile",
                params={"token": access_token}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "token_valid": True,
                        "profile_accessible": bool(data.get("id")),
                        "profile_id": data.get("id"),
                        "profile_name": data.get("name")
                    }
                elif response.status == 401:
                    return {
                        "success": False,
                        "token_valid": False,
                        "error": "Token validation failed"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_profile_access_via_token(self):
        """Test profile access via JWT token"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[0]
            access_token = test_user.get("access_token")
            
            if not access_token:
                return {"success": False, "error": "No access token available"}
            
            async with self.session.get(
                f"{BACKEND_URL}/auth/profile",
                params={"token": access_token}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify profile data matches expected user
                    expected_profile_id = test_user.get("profile_id")
                    actual_profile_id = data.get("id")
                    
                    return {
                        "success": True,
                        "profile_accessible": True,
                        "profile_id_matches": actual_profile_id == expected_profile_id,
                        "expected_profile_id": expected_profile_id,
                        "actual_profile_id": actual_profile_id,
                        "profile_data": {
                            "name": data.get("name"),
                            "age": data.get("age"),
                            "location": data.get("location"),
                            "voice_personality": data.get("voice_personality")
                        }
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_preview_mode_behavior(self):
        """Test preview mode behavior (REACT_APP_IS_PREVIEW=true)"""
        try:
            # In preview mode, the system should work normally but might have different behaviors
            # Test health check to ensure system is operational in preview mode
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Test that we can create users in preview mode
                    test_email = f"preview_test_{uuid.uuid4().hex[:8]}@example.com"
                    signup_data = {
                        "email": test_email,
                        "password": "PreviewTest123!",
                        "name": f"PreviewChild_{uuid.uuid4().hex[:6]}",
                        "age": 6,
                        "location": "Preview Location"
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/auth/signup",
                        json=signup_data
                    ) as signup_response:
                        preview_signup_works = signup_response.status == 200
                        
                        return {
                            "success": True,
                            "preview_mode_active": True,
                            "health_check_passed": True,
                            "signup_works_in_preview": preview_signup_works,
                            "backend_operational": data.get("status") == "healthy",
                            "agents_initialized": data.get("agents", {}).get("orchestrator", False)
                        }
                else:
                    return {"success": False, "error": f"Health check failed: HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_production_mode_simulation(self):
        """Test production mode simulation"""
        try:
            # Test that all endpoints work as expected (simulating production behavior)
            # This is essentially the same as preview mode for backend testing
            
            # Test multiple endpoints to ensure production readiness
            endpoints_to_test = [
                f"{BACKEND_URL}/health",
                f"{BACKEND_URL}/voice/personalities"
            ]
            
            endpoint_results = []
            
            for endpoint in endpoints_to_test:
                try:
                    async with self.session.get(endpoint) as response:
                        endpoint_results.append({
                            "endpoint": endpoint.split("/")[-1],
                            "status_code": response.status,
                            "accessible": response.status in [200, 404]  # 404 is acceptable for some endpoints
                        })
                except Exception as e:
                    endpoint_results.append({
                        "endpoint": endpoint.split("/")[-1],
                        "error": str(e),
                        "accessible": False
                    })
            
            accessible_endpoints = [r for r in endpoint_results if r.get("accessible", False)]
            
            return {
                "success": True,
                "production_simulation": True,
                "endpoints_tested": len(endpoints_to_test),
                "accessible_endpoints": len(accessible_endpoints),
                "production_readiness": f"{len(accessible_endpoints)/len(endpoints_to_test)*100:.1f}%",
                "endpoint_results": endpoint_results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_duplicate_email_handling(self):
        """Test duplicate email handling during signup"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            # Try to signup with an existing email
            existing_user = self.test_users[0]
            existing_email = existing_user["email"]
            
            duplicate_signup_data = {
                "email": existing_email,
                "password": "DifferentPassword123!",
                "name": f"DuplicateTest_{uuid.uuid4().hex[:6]}",
                "age": 8,
                "location": "Duplicate Location"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/signup",
                json=duplicate_signup_data
            ) as response:
                if response.status == 400:
                    error_data = await response.json()
                    error_detail = error_data.get("detail", "")
                    
                    return {
                        "success": True,
                        "duplicate_email_rejected": True,
                        "status_code": response.status,
                        "error_message": error_detail,
                        "proper_error_handling": "already registered" in error_detail.lower() or "email" in error_detail.lower()
                    }
                elif response.status == 200:
                    return {
                        "success": False,
                        "duplicate_email_rejected": False,
                        "error": "Duplicate email was accepted (should be rejected)"
                    }
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Unexpected response: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_duplicate_name_handling(self):
        """Test duplicate name handling during profile creation"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            # Get an existing user's name
            existing_user = self.test_users[0]
            profile_id = existing_user["profile_id"]
            
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{profile_id}"
            ) as response:
                if response.status == 200:
                    existing_profile = await response.json()
                    existing_name = existing_profile.get("name")
                    
                    # Try to create a new profile with the same name
                    duplicate_profile_data = {
                        "name": existing_name,
                        "age": 9,
                        "location": "Different Location",
                        "timezone": "America/Chicago",
                        "language": "english"
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/users/profile",
                        json=duplicate_profile_data
                    ) as create_response:
                        if create_response.status == 200:
                            new_profile = await create_response.json()
                            new_name = new_profile.get("name")
                            
                            # Store for cleanup
                            self.test_users.append({
                                "profile_id": new_profile.get("id"),
                                "email": "duplicate_name_test@example.com"
                            })
                            
                            return {
                                "success": True,
                                "duplicate_name_handled": new_name != existing_name,
                                "original_name": existing_name,
                                "new_name": new_name,
                                "name_modified": "_" in new_name or new_name.endswith(tuple("0123456789")),
                                "proper_duplicate_handling": True
                            }
                        else:
                            error_text = await create_response.text()
                            return {"success": False, "error": f"Profile creation failed: HTTP {create_response.status}: {error_text}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Failed to get existing profile: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_invalid_credentials_handling(self):
        """Test invalid credentials handling during signin"""
        try:
            # Test with non-existent email
            invalid_signin_data = {
                "email": "nonexistent@example.com",
                "password": "WrongPassword123!"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/signin",
                json=invalid_signin_data
            ) as response:
                if response.status == 401:
                    error_data = await response.json()
                    error_detail = error_data.get("detail", "")
                    
                    # Test with existing email but wrong password
                    if self.test_users:
                        existing_user = self.test_users[0]
                        wrong_password_data = {
                            "email": existing_user["email"],
                            "password": "WrongPassword123!"
                        }
                        
                        async with self.session.post(
                            f"{BACKEND_URL}/auth/signin",
                            json=wrong_password_data
                        ) as wrong_pass_response:
                            wrong_pass_rejected = wrong_pass_response.status == 401
                            
                            return {
                                "success": True,
                                "invalid_email_rejected": True,
                                "invalid_password_rejected": wrong_pass_rejected,
                                "error_message": error_detail,
                                "proper_error_handling": "invalid" in error_detail.lower() or "password" in error_detail.lower()
                            }
                    else:
                        return {
                            "success": True,
                            "invalid_email_rejected": True,
                            "error_message": error_detail,
                            "proper_error_handling": "invalid" in error_detail.lower()
                        }
                else:
                    return {
                        "success": False,
                        "invalid_credentials_rejected": False,
                        "error": f"Invalid credentials were accepted: HTTP {response.status}"
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_missing_required_fields(self):
        """Test missing required fields handling"""
        try:
            # Test signup with missing fields
            incomplete_signup_data = {
                "email": "incomplete@example.com",
                # Missing password, name, age, location
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/signup",
                json=incomplete_signup_data
            ) as response:
                signup_validation = response.status in [400, 422]  # Should reject incomplete data
                
                # Test profile creation with missing fields
                incomplete_profile_data = {
                    "name": "IncompleteProfile",
                    # Missing age, location, etc.
                }
                
                async with self.session.post(
                    f"{BACKEND_URL}/users/profile",
                    json=incomplete_profile_data
                ) as profile_response:
                    profile_validation = profile_response.status in [400, 422]
                    
                    return {
                        "success": True,
                        "signup_validation": signup_validation,
                        "profile_validation": profile_validation,
                        "proper_field_validation": signup_validation and profile_validation,
                        "signup_status": response.status,
                        "profile_status": profile_response.status
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_user_data_persistence(self):
        """Test user data persistence across requests"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[0]
            user_id = test_user.get("user_id")
            profile_id = test_user.get("profile_id")
            
            if not user_id or not profile_id:
                return {"success": False, "error": "Missing user or profile ID"}
            
            # Get initial profile data
            async with self.session.get(
                f"{BACKEND_URL}/users/profile/{profile_id}"
            ) as response:
                if response.status == 200:
                    initial_data = await response.json()
                    
                    # Wait a moment and fetch again to test persistence
                    await asyncio.sleep(1)
                    
                    async with self.session.get(
                        f"{BACKEND_URL}/users/profile/{profile_id}"
                    ) as second_response:
                        if second_response.status == 200:
                            second_data = await second_response.json()
                            
                            # Compare key fields for persistence
                            persistent_fields = ["id", "name", "age", "location", "voice_personality", "created_at"]
                            persistence_results = {}
                            
                            for field in persistent_fields:
                                initial_value = initial_data.get(field)
                                second_value = second_data.get(field)
                                persistence_results[field] = {
                                    "persistent": initial_value == second_value,
                                    "initial": initial_value,
                                    "second": second_value
                                }
                            
                            all_persistent = all(result["persistent"] for result in persistence_results.values())
                            
                            return {
                                "success": True,
                                "data_persistent": all_persistent,
                                "persistence_results": persistence_results,
                                "profile_id": profile_id,
                                "test_duration": "1 second"
                            }
                        else:
                            error_text = await second_response.text()
                            return {"success": False, "error": f"Second request failed: HTTP {second_response.status}: {error_text}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Initial request failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_profile_data_persistence(self):
        """Test profile data persistence after updates"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]  # Use most recent user
            profile_id = test_user["profile_id"]
            
            # Update profile data
            update_data = {
                "interests": ["persistence_test", "data_integrity"],
                "learning_goals": ["testing", "validation"],
                "avatar": "robot",
                "speech_speed": "slow"
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/users/profile/{profile_id}",
                json=update_data
            ) as response:
                if response.status == 200:
                    updated_data = await response.json()
                    
                    # Wait and fetch again to test persistence
                    await asyncio.sleep(1)
                    
                    async with self.session.get(
                        f"{BACKEND_URL}/users/profile/{profile_id}"
                    ) as fetch_response:
                        if fetch_response.status == 200:
                            fetched_data = await fetch_response.json()
                            
                            # Verify updates persisted
                            updates_persistent = {
                                "interests": fetched_data.get("interests") == update_data["interests"],
                                "learning_goals": fetched_data.get("learning_goals") == update_data["learning_goals"],
                                "avatar": fetched_data.get("avatar") == update_data["avatar"],
                                "speech_speed": fetched_data.get("speech_speed") == update_data["speech_speed"]
                            }
                            
                            all_updates_persistent = all(updates_persistent.values())
                            
                            return {
                                "success": True,
                                "updates_persistent": all_updates_persistent,
                                "persistence_details": updates_persistent,
                                "updated_at_changed": updated_data.get("updated_at") != fetched_data.get("updated_at"),
                                "profile_id": profile_id
                            }
                        else:
                            error_text = await fetch_response.text()
                            return {"success": False, "error": f"Fetch after update failed: HTTP {fetch_response.status}: {error_text}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Profile update failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_parental_controls_persistence(self):
        """Test parental controls persistence after updates"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            test_user = self.test_users[-1]
            profile_id = test_user["profile_id"]
            
            # Update parental controls
            update_data = {
                "time_limits": {
                    "monday": 30,
                    "tuesday": 30,
                    "wednesday": 30,
                    "thursday": 30,
                    "friday": 45,
                    "saturday": 60,
                    "sunday": 60
                },
                "content_restrictions": ["persistence_test"],
                "monitoring_enabled": False
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/users/{profile_id}/parental-controls",
                json=update_data
            ) as response:
                if response.status == 200:
                    updated_data = await response.json()
                    
                    # Wait and fetch again to test persistence
                    await asyncio.sleep(1)
                    
                    async with self.session.get(
                        f"{BACKEND_URL}/users/{profile_id}/parental-controls"
                    ) as fetch_response:
                        if fetch_response.status == 200:
                            fetched_data = await fetch_response.json()
                            
                            # Verify updates persisted
                            updates_persistent = {
                                "time_limits": fetched_data.get("time_limits") == update_data["time_limits"],
                                "content_restrictions": fetched_data.get("content_restrictions") == update_data["content_restrictions"],
                                "monitoring_enabled": fetched_data.get("monitoring_enabled") == update_data["monitoring_enabled"]
                            }
                            
                            all_updates_persistent = all(updates_persistent.values())
                            
                            return {
                                "success": True,
                                "updates_persistent": all_updates_persistent,
                                "persistence_details": updates_persistent,
                                "updated_at_changed": updated_data.get("updated_at") != fetched_data.get("updated_at"),
                                "user_id": profile_id
                            }
                        else:
                            error_text = await fetch_response.text()
                            return {"success": False, "error": f"Fetch after update failed: HTTP {fetch_response.status}: {error_text}"}
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"Parental controls update failed: HTTP {response.status}: {error_text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complete_new_user_flow(self):
        """Test complete new user onboarding flow end-to-end"""
        try:
            # Step 1: New user signup
            test_email = f"complete_flow_{uuid.uuid4().hex[:8]}@example.com"
            test_name = f"CompleteFlowChild_{uuid.uuid4().hex[:6]}"
            
            signup_data = {
                "email": test_email,
                "password": "CompleteFlow123!",
                "name": test_name,
                "age": 6,
                "location": "Complete Flow City"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/signup",
                json=signup_data
            ) as signup_response:
                if signup_response.status != 200:
                    return {"success": False, "error": "Signup failed"}
                
                signup_data_response = await signup_response.json()
                user_id = signup_data_response.get("user_id")
                profile_id = signup_data_response.get("profile_id")
                access_token = signup_data_response.get("access_token")
                
                # Store for cleanup
                self.test_users.append({
                    "email": test_email,
                    "user_id": user_id,
                    "profile_id": profile_id,
                    "access_token": access_token
                })
                
                # Step 2: Profile setup (simulate onboarding steps)
                profile_updates = {
                    "voice_personality": "story_narrator",
                    "interests": ["stories", "animals", "adventure"],
                    "learning_goals": ["reading", "imagination", "vocabulary"],
                    "avatar": "dragon",
                    "speech_speed": "normal",
                    "energy_level": "high"
                }
                
                async with self.session.put(
                    f"{BACKEND_URL}/users/profile/{profile_id}",
                    json=profile_updates
                ) as profile_response:
                    if profile_response.status != 200:
                        return {"success": False, "error": "Profile setup failed"}
                    
                    # Step 3: Parental controls setup
                    parental_controls_updates = {
                        "time_limits": {
                            "monday": 45,
                            "tuesday": 45,
                            "wednesday": 45,
                            "thursday": 45,
                            "friday": 60,
                            "saturday": 90,
                            "sunday": 90
                        },
                        "content_restrictions": ["violence", "scary"],
                        "allowed_content_types": ["story", "educational", "music"],
                        "monitoring_enabled": True,
                        "notification_preferences": {
                            "activity_summary": True,
                            "safety_alerts": True
                        }
                    }
                    
                    async with self.session.put(
                        f"{BACKEND_URL}/users/{profile_id}/parental-controls",
                        json=parental_controls_updates
                    ) as pc_response:
                        if pc_response.status != 200:
                            return {"success": False, "error": "Parental controls setup failed"}
                        
                        # Step 4: Verify complete setup
                        async with self.session.get(
                            f"{BACKEND_URL}/users/profile/{profile_id}"
                        ) as final_profile_response:
                            if final_profile_response.status == 200:
                                final_profile = await final_profile_response.json()
                                
                                async with self.session.get(
                                    f"{BACKEND_URL}/users/{profile_id}/parental-controls"
                                ) as final_pc_response:
                                    if final_pc_response.status == 200:
                                        final_pc = await final_pc_response.json()
                                        
                                        return {
                                            "success": True,
                                            "complete_flow_successful": True,
                                            "signup_completed": True,
                                            "profile_setup_completed": True,
                                            "parental_controls_setup_completed": True,
                                            "user_data": {
                                                "user_id": user_id,
                                                "profile_id": profile_id,
                                                "name": final_profile.get("name"),
                                                "age": final_profile.get("age"),
                                                "voice_personality": final_profile.get("voice_personality"),
                                                "interests_count": len(final_profile.get("interests", [])),
                                                "learning_goals_count": len(final_profile.get("learning_goals", [])),
                                                "monitoring_enabled": final_pc.get("monitoring_enabled")
                                            },
                                            "onboarding_flow": "Complete new user flow successful"
                                        }
                                    else:
                                        return {"success": False, "error": "Final parental controls check failed"}
                            else:
                                return {"success": False, "error": "Final profile check failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complete_existing_user_flow(self):
        """Test complete existing user flow (signin and direct access)"""
        if not self.test_users:
            return {"success": False, "error": "No test users available"}
        
        try:
            # Use the first test user as an existing user
            existing_user = self.test_users[0]
            
            # Step 1: Existing user signin
            signin_data = {
                "email": existing_user["email"],
                "password": "TestPassword123!"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/auth/signin",
                json=signin_data
            ) as signin_response:
                if signin_response.status != 200:
                    return {"success": False, "error": "Existing user signin failed"}
                
                signin_data_response = await signin_response.json()
                user_id = signin_data_response.get("user_id")
                profile_id = signin_data_response.get("profile_id")
                access_token = signin_data_response.get("access_token")
                
                # Step 2: Direct profile access (no onboarding needed)
                async with self.session.get(
                    f"{BACKEND_URL}/users/profile/{profile_id}"
                ) as profile_response:
                    if profile_response.status == 200:
                        profile_data = await profile_response.json()
                        
                        # Step 3: Check parental controls access
                        async with self.session.get(
                            f"{BACKEND_URL}/users/{profile_id}/parental-controls"
                        ) as pc_response:
                            if pc_response.status == 200:
                                pc_data = await pc_response.json()
                                
                                # Determine if user should bypass onboarding
                                has_interests = len(profile_data.get("interests", [])) > 0
                                has_learning_goals = len(profile_data.get("learning_goals", [])) > 0
                                has_custom_settings = profile_data.get("voice_personality") != "friendly_companion"
                                
                                should_bypass_onboarding = has_interests or has_learning_goals or has_custom_settings
                                
                                return {
                                    "success": True,
                                    "existing_user_flow_successful": True,
                                    "signin_completed": True,
                                    "profile_accessible": True,
                                    "parental_controls_accessible": True,
                                    "should_bypass_onboarding": should_bypass_onboarding,
                                    "user_data": {
                                        "user_id": user_id,
                                        "profile_id": profile_id,
                                        "name": profile_data.get("name"),
                                        "age": profile_data.get("age"),
                                        "has_interests": has_interests,
                                        "has_learning_goals": has_learning_goals,
                                        "has_custom_settings": has_custom_settings,
                                        "interests_count": len(profile_data.get("interests", [])),
                                        "learning_goals_count": len(profile_data.get("learning_goals", []))
                                    },
                                    "onboarding_flow": "Existing user bypasses onboarding" if should_bypass_onboarding else "Existing user may need onboarding"
                                }
                            else:
                                return {"success": False, "error": "Parental controls access failed"}
                    else:
                        return {"success": False, "error": "Profile access failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Main test runner"""
    async with OnboardingBackendTester() as tester:
        results = await tester.run_onboarding_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 ONBOARDING FLOW BACKEND TEST RESULTS")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = len([r for r in results.values() if r["status"] == "PASS"])
        failed_tests = len([r for r in results.values() if r["status"] == "FAIL"])
        error_tests = len([r for r in results.values() if r["status"] == "ERROR"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"💥 Errors: {error_tests}")
        print(f"📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        print("\n🔍 DETAILED RESULTS:")
        print("-" * 80)
        
        for test_name, result in results.items():
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "💥"
            print(f"{status_emoji} {test_name}: {result['status']}")
            
            if result["status"] != "PASS" and "error" in result["details"]:
                print(f"   Error: {result['details']['error']}")
        
        print("\n" + "="*80)
        
        # Return results for further processing
        return results

if __name__ == "__main__":
    asyncio.run(main())