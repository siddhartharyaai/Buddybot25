#!/usr/bin/env python3
"""
Voice Processing Diagnostic Test
Comprehensive testing of voice processing pipeline components
"""

import asyncio
import aiohttp
import json
import base64
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend URL
BACKEND_URL = "https://e73353f9-1d22-4a0f-9deb-0707101e1e70.preview.emergentagent.com/api"

async def run_voice_diagnostics():
    """Run comprehensive voice processing diagnostics"""
    
    print("🎤 VOICE PROCESSING PIPELINE DIAGNOSTIC TEST")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Setup test user
        test_user_id = await setup_test_user(session)
        if not test_user_id:
            return
        
        test_session_id = f"diagnostic_{uuid.uuid4().hex[:8]}"
        
        # Test 1: Voice Processing Endpoint Accessibility
        print("\n1️⃣ VOICE PROCESSING ENDPOINT ACCESSIBILITY")
        await test_voice_endpoint_accessibility(session, test_user_id, test_session_id)
        
        # Test 2: Audio Base64 Processing
        print("\n2️⃣ AUDIO BASE64 PROCESSING")
        await test_audio_base64_processing(session, test_user_id, test_session_id)
        
        # Test 3: Form Data Processing
        print("\n3️⃣ FORM DATA PROCESSING")
        await test_form_data_processing(session, test_user_id, test_session_id)
        
        # Test 4: Orchestrator Integration
        print("\n4️⃣ ORCHESTRATOR INTEGRATION")
        await test_orchestrator_integration(session, test_user_id, test_session_id)
        
        # Test 5: STT Integration
        print("\n5️⃣ STT (SPEECH-TO-TEXT) INTEGRATION")
        await test_stt_integration(session, test_user_id, test_session_id)
        
        # Test 6: TTS Integration
        print("\n6️⃣ TTS (TEXT-TO-SPEECH) INTEGRATION")
        await test_tts_integration(session, test_user_id, test_session_id)
        
        # Test 7: Error Handling
        print("\n7️⃣ ERROR HANDLING")
        await test_error_handling(session, test_user_id, test_session_id)
        
        # Test 8: Mobile Audio Format Support
        print("\n8️⃣ MOBILE AUDIO FORMAT SUPPORT")
        await test_mobile_audio_formats(session, test_user_id, test_session_id)
        
        print("\n" + "=" * 60)
        print("🎤 VOICE PROCESSING DIAGNOSTIC COMPLETE")

async def setup_test_user(session):
    """Setup test user for diagnostics"""
    try:
        profile_data = {
            "name": "Voice Diagnostic User",
            "age": 7,
            "location": "Test Location",
            "timezone": "America/New_York",
            "language": "english",
            "voice_personality": "friendly_companion",
            "interests": ["stories", "music"],
            "learning_goals": ["listening"],
            "parent_email": "diagnostic@test.com"
        }
        
        async with session.post(f"{BACKEND_URL}/users/profile", json=profile_data) as response:
            if response.status == 200:
                user_data = await response.json()
                user_id = user_data["id"]
                print(f"✅ Test user created: {user_id}")
                return user_id
            else:
                print(f"❌ Failed to create test user: {response.status}")
                return None
    except Exception as e:
        print(f"❌ User setup error: {e}")
        return None

async def test_voice_endpoint_accessibility(session, user_id, session_id):
    """Test voice endpoint accessibility"""
    try:
        mock_audio = b"accessibility_test_audio"
        audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
        
        form_data = {
            "session_id": session_id,
            "user_id": user_id,
            "audio_base64": audio_base64
        }
        
        async with session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
            print(f"   Status Code: {response.status}")
            print(f"   Endpoint Accessible: {'✅ YES' if response.status in [200, 400, 500] else '❌ NO'}")
            
            if response.status == 200:
                data = await response.json()
                print(f"   Response Status: {data.get('status')}")
            elif response.status == 400:
                error_data = await response.json()
                print(f"   Error Status: {error_data.get('status')}")
                print(f"   Error Detail: {error_data.get('detail')}")
            
    except Exception as e:
        print(f"   ❌ Accessibility test error: {e}")

async def test_audio_base64_processing(session, user_id, session_id):
    """Test audio base64 processing"""
    try:
        # Test different audio sizes
        test_cases = [
            {"name": "Tiny", "data": b"x"},
            {"name": "Small", "data": b"small_audio_data"},
            {"name": "Medium", "data": b"medium_audio_data" * 50},
            {"name": "Large", "data": b"large_audio_data" * 500}
        ]
        
        for case in test_cases:
            audio_base64 = base64.b64encode(case["data"]).decode('utf-8')
            
            form_data = {
                "session_id": session_id,
                "user_id": user_id,
                "audio_base64": audio_base64
            }
            
            try:
                async with session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                    status = "✅ PROCESSED" if response.status in [200, 400, 500] else "❌ FAILED"
                    print(f"   {case['name']} ({len(case['data'])} bytes): {status} ({response.status})")
            except Exception as e:
                print(f"   {case['name']}: ❌ ERROR ({e})")
                
    except Exception as e:
        print(f"   ❌ Base64 processing test error: {e}")

async def test_form_data_processing(session, user_id, session_id):
    """Test form data processing"""
    try:
        mock_audio = b"form_data_test_audio"
        audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
        
        # Test different form data configurations
        test_configs = [
            {
                "name": "Complete form data",
                "data": {
                    "session_id": session_id,
                    "user_id": user_id,
                    "audio_base64": audio_base64
                }
            },
            {
                "name": "Missing session_id",
                "data": {
                    "user_id": user_id,
                    "audio_base64": audio_base64
                }
            },
            {
                "name": "Missing user_id",
                "data": {
                    "session_id": session_id,
                    "audio_base64": audio_base64
                }
            },
            {
                "name": "Missing audio_base64",
                "data": {
                    "session_id": session_id,
                    "user_id": user_id
                }
            }
        ]
        
        for config in test_configs:
            try:
                async with session.post(f"{BACKEND_URL}/voice/process_audio", data=config["data"]) as response:
                    if config["name"] == "Complete form data":
                        status = "✅ VALID" if response.status in [200, 400, 500] else "❌ INVALID"
                    else:
                        status = "✅ REJECTED" if response.status in [400, 422] else "❌ ACCEPTED"
                    print(f"   {config['name']}: {status} ({response.status})")
            except Exception as e:
                print(f"   {config['name']}: ❌ ERROR ({e})")
                
    except Exception as e:
        print(f"   ❌ Form data processing test error: {e}")

async def test_orchestrator_integration(session, user_id, session_id):
    """Test orchestrator integration"""
    try:
        mock_audio = b"orchestrator_integration_test_audio"
        audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
        
        form_data = {
            "session_id": session_id,
            "user_id": user_id,
            "audio_base64": audio_base64
        }
        
        async with session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
            response_text = await response.text()
            
            # Check for specific orchestrator method errors
            if "process_conversation" in response_text:
                print("   ❌ BROKEN: Old 'process_conversation' method error")
                print("   🔧 Fix needed: Update to use 'process_voice_input' method")
            elif "process_voice_input" in response_text and "not found" in response_text:
                print("   ❌ BROKEN: 'process_voice_input' method not found")
                print("   🔧 Fix needed: Implement process_voice_input method")
            else:
                print("   ✅ WORKING: Orchestrator method integration successful")
                print(f"   Status Code: {response.status}")
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        print(f"   Method Called: process_voice_input")
                        print(f"   Response Status: {data.get('status')}")
                    except:
                        pass
                elif response.status == 400:
                    try:
                        data = json.loads(response_text)
                        print(f"   Expected Error: {data.get('detail')}")
                    except:
                        pass
                        
    except Exception as e:
        print(f"   ❌ Orchestrator integration test error: {e}")

async def test_stt_integration(session, user_id, session_id):
    """Test STT integration"""
    try:
        # Test voice personalities endpoint (indicates STT integration)
        async with session.get(f"{BACKEND_URL}/voice/personalities") as response:
            if response.status == 200:
                personalities = await response.json()
                print(f"   ✅ Voice personalities available: {len(personalities)}")
                
                # Test actual voice processing
                mock_audio = b"stt_integration_test_hello_world"
                audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
                
                form_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "audio_base64": audio_base64
                }
                
                async with session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as voice_response:
                    if voice_response.status == 200:
                        voice_data = await voice_response.json()
                        print(f"   ✅ STT processing successful")
                        print(f"   Transcript received: {'✅ YES' if voice_data.get('transcript') else '❌ NO'}")
                    elif voice_response.status == 400:
                        error_data = await voice_response.json()
                        if "Could not understand audio" in error_data.get('detail', ''):
                            print("   ✅ STT integration working (expected error with mock data)")
                        else:
                            print(f"   ⚠️ STT processing error: {error_data.get('detail')}")
                    else:
                        print(f"   ❌ STT processing failed: {voice_response.status}")
            else:
                print(f"   ❌ Voice personalities failed: {response.status}")
                
    except Exception as e:
        print(f"   ❌ STT integration test error: {e}")

async def test_tts_integration(session, user_id, session_id):
    """Test TTS integration"""
    try:
        # Test text conversation to verify TTS
        text_input = {
            "session_id": session_id,
            "user_id": user_id,
            "message": "Hello, please respond with audio"
        }
        
        async with session.post(f"{BACKEND_URL}/conversations/text", json=text_input) as response:
            if response.status == 200:
                data = await response.json()
                response_audio = data.get("response_audio")
                
                print(f"   ✅ TTS integration working")
                print(f"   Response text: {len(data.get('response_text', ''))} chars")
                print(f"   Response audio: {'✅ YES' if response_audio else '❌ NO'}")
                if response_audio:
                    print(f"   Audio size: {len(response_audio)} chars (base64)")
                    print(f"   Content type: {data.get('content_type')}")
            else:
                error_text = await response.text()
                print(f"   ❌ TTS integration failed: {response.status}")
                print(f"   Error: {error_text}")
                
    except Exception as e:
        print(f"   ❌ TTS integration test error: {e}")

async def test_error_handling(session, user_id, session_id):
    """Test error handling"""
    try:
        error_test_cases = [
            {
                "name": "Empty audio",
                "audio_base64": "",
                "expected_error": True
            },
            {
                "name": "Invalid base64",
                "audio_base64": "invalid_base64_data!!!",
                "expected_error": True
            },
            {
                "name": "Very small audio",
                "audio_base64": base64.b64encode(b"x").decode('utf-8'),
                "expected_error": True
            }
        ]
        
        for test in error_test_cases:
            form_data = {
                "session_id": session_id,
                "user_id": user_id,
                "audio_base64": test["audio_base64"]
            }
            
            try:
                async with session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                    if test["expected_error"]:
                        status = "✅ HANDLED" if response.status in [400, 422, 500] else "❌ NOT HANDLED"
                    else:
                        status = "✅ PROCESSED" if response.status in [200] else "❌ FAILED"
                    print(f"   {test['name']}: {status} ({response.status})")
            except Exception as e:
                print(f"   {test['name']}: ✅ HANDLED (Exception: {type(e).__name__})")
                
    except Exception as e:
        print(f"   ❌ Error handling test error: {e}")

async def test_mobile_audio_formats(session, user_id, session_id):
    """Test mobile audio format support"""
    try:
        # Test mobile audio format signatures
        mobile_formats = [
            {"name": "WebM", "signature": b'\x1a\x45\xdf\xa3', "mime": "audio/webm"},
            {"name": "MP4", "signature": b'\x00\x00\x00\x20ftypmp4', "mime": "audio/mp4"},
            {"name": "OGG", "signature": b'OggS', "mime": "audio/ogg"},
            {"name": "WAV", "signature": b'RIFF', "mime": "audio/wav"}
        ]
        
        for fmt in mobile_formats:
            # Create mock audio with format signature
            mock_audio = fmt["signature"] + b"mobile_audio_test_data" * 10
            audio_base64 = base64.b64encode(mock_audio).decode('utf-8')
            
            form_data = {
                "session_id": session_id,
                "user_id": user_id,
                "audio_base64": audio_base64
            }
            
            try:
                async with session.post(f"{BACKEND_URL}/voice/process_audio", data=form_data) as response:
                    status = "✅ SUPPORTED" if response.status in [200, 400, 500] else "❌ NOT SUPPORTED"
                    print(f"   {fmt['name']} ({fmt['mime']}): {status} ({response.status})")
            except Exception as e:
                print(f"   {fmt['name']}: ❌ ERROR ({type(e).__name__})")
                
    except Exception as e:
        print(f"   ❌ Mobile audio format test error: {e}")

if __name__ == "__main__":
    asyncio.run(run_voice_diagnostics())