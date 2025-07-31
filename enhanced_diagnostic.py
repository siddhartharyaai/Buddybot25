#!/usr/bin/env python3
"""
Enhanced diagnostic script to get detailed error information
and test STT functionality specifically.
"""

import asyncio
import aiohttp
import base64
import json
import os

async def test_voice_processing_detailed():
    """Test the voice processing endpoint with detailed error capture"""
    
    # Create a simple test audio (silence for testing)
    test_audio_bytes = b'\x00' * 1000  # 1000 bytes of silence for testing
    test_audio_base64 = base64.b64encode(test_audio_bytes).decode('utf-8')
    
    # Prepare form data
    form_data = aiohttp.FormData()
    form_data.add_field('session_id', 'test_session_123')
    form_data.add_field('user_id', 'test_user_456')
    form_data.add_field('audio_base64', test_audio_base64)
    
    print(f"🧪 DETAILED DIAGNOSTIC: Testing voice processing endpoint")
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Making request to voice processing endpoint...")
            
            async with session.post(
                'http://localhost:8001/api/voice/process_audio',
                data=form_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"📨 Response status: {response.status}")
                
                # Get the full response text to see error details
                response_text = await response.text()
                print(f"📨 Full response text: {response_text}")
                
                try:
                    response_data = json.loads(response_text)
                    print("🔍 Parsed response data:")
                    for key, value in response_data.items():
                        if key == 'response_audio' and value:
                            print(f"  {key}: [audio data {len(value)} chars]")
                        else:
                            print(f"  {key}: {value}")
                            
                    # Check for error details
                    if response_data.get('status') == 'error':
                        error_msg = response_data.get('error', 'Unknown error')
                        message = response_data.get('message', 'No message')
                        print(f"❌ ERROR DETECTED: {error_msg}")
                        print(f"❌ ERROR MESSAGE: {message}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

async def test_direct_stt():
    """Test STT directly to see if it's the problem"""
    print("\n" + "="*50)
    print("🧪 DIRECT STT TEST")
    print("="*50)
    
    try:
        # Import the voice agent directly
        import sys
        sys.path.append('/app/backend')
        
        from agents.voice_agent import VoiceAgent
        
        # Get API key from environment
        deepgram_key = os.getenv('DEEPGRAM_API_KEY', '1069931ea453615c2ce58ad85dc06ccab4ae86b3')
        
        # Create voice agent
        voice_agent = VoiceAgent(deepgram_key)
        
        # Test STT with silence (this should fail gracefully)
        test_audio_bytes = b'\x00' * 1000  # 1000 bytes of silence
        print(f"🎤 Testing STT with {len(test_audio_bytes)} bytes of silence")
        
        transcript = await voice_agent.speech_to_text(test_audio_bytes)
        
        if transcript:
            print(f"✅ STT SUCCESS: Transcript: '{transcript}'")
        else:
            print("⚠️ STT returned None/empty (expected for silent audio)")
            
        # Now test with a minimal WAV file structure
        print("\n🎤 Testing STT with minimal WAV structure...")
        
        # Create a minimal WAV file header + silence
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        wav_data = b'\x00' * 2048  # 2KB of audio data
        wav_file = wav_header + wav_data
        
        print(f"🎤 Testing STT with {len(wav_file)} bytes of WAV data")
        
        transcript2 = await voice_agent.speech_to_text(wav_file)
        
        if transcript2:
            print(f"✅ WAV STT SUCCESS: Transcript: '{transcript2}'")
        else:
            print("⚠️ WAV STT returned None/empty")
            
    except Exception as e:
        print(f"❌ Direct STT test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_orchestrator_directly():
    """Test the orchestrator methods directly"""
    print("\n" + "="*50)
    print("🧪 DIRECT ORCHESTRATOR TEST")
    print("="*50)
    
    try:
        import sys
        sys.path.append('/app/backend')
        
        # Import orchestrator from server
        from server import orchestrator
        
        # Test with simple user profile
        user_profile = {
            "id": "test_user_456",
            "name": "Test User",
            "age": 7,
            "voice_personality": "friendly_companion"
        }
        
        # Test audio data
        test_audio_bytes = b'\x00' * 1000
        
        print("🤖 Testing orchestrator.process_voice_input_fast()...")
        
        result = await orchestrator.process_voice_input_fast(
            "test_session_123", 
            test_audio_bytes, 
            user_profile
        )
        
        print("🔍 Orchestrator result:")
        for key, value in result.items():
            if key == 'response_audio' and value:
                print(f"  {key}: [audio data {len(value)} chars]")
            else:
                print(f"  {key}: {value}")
                
        if 'error' in result:
            print(f"❌ ORCHESTRATOR ERROR: {result['error']}")
        else:
            print("✅ Orchestrator completed without error")
            
    except Exception as e:
        print(f"❌ Direct orchestrator test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting enhanced diagnostic...")
    
    # Run the diagnostic tests
    asyncio.run(test_voice_processing_detailed())
    asyncio.run(test_direct_stt())
    asyncio.run(test_orchestrator_directly())
    
    print("\n🏁 Enhanced diagnostic complete!")