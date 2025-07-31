#!/usr/bin/env python3
"""
Diagnostic script to test the voice processing API endpoint
and identify why response_audio might be missing.
"""

import asyncio
import aiohttp
import base64
import json
import os

async def test_voice_processing():
    """Test the voice processing endpoint to diagnose audio issues"""
    
    # Create a simple test audio (silence for testing)
    # In a real scenario, this would be actual audio data
    test_audio_bytes = b'\x00' * 1000  # 1000 bytes of silence for testing
    test_audio_base64 = base64.b64encode(test_audio_bytes).decode('utf-8')
    
    # Prepare form data
    form_data = aiohttp.FormData()
    form_data.add_field('session_id', 'test_session_123')
    form_data.add_field('user_id', 'test_user_456')
    form_data.add_field('audio_base64', test_audio_base64)
    
    print(f"🧪 DIAGNOSTIC TEST: Sending {len(test_audio_base64)} chars of base64 audio")
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Making request to voice processing endpoint...")
            
            async with session.post(
                'http://localhost:8001/api/voice/process_audio',
                data=form_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"📨 Response status: {response.status}")
                print(f"📨 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    try:
                        response_data = await response.json()
                        print("✅ Response JSON structure:")
                        print(json.dumps({
                            'status': response_data.get('status'),
                            'transcript': response_data.get('transcript', 'N/A'),
                            'response_text': response_data.get('response_text', 'N/A')[:100] + '...',
                            'response_audio_present': bool(response_data.get('response_audio')),
                            'response_audio_length': len(response_data.get('response_audio', '')) if response_data.get('response_audio') else 0,
                            'content_type': response_data.get('content_type'),
                            'metadata': response_data.get('metadata'),
                            'pipeline': response_data.get('pipeline'),
                        }, indent=2))
                        
                        # Check if audio is present and valid
                        response_audio = response_data.get('response_audio')
                        if response_audio:
                            print(f"🎵 AUDIO DIAGNOSTIC: Audio present with {len(response_audio)} characters")
                            print(f"🎵 AUDIO DIAGNOSTIC: First 50 chars: {response_audio[:50]}...")
                            print(f"🎵 AUDIO DIAGNOSTIC: Audio appears to be base64: {response_audio.startswith('UklGR') or response_audio.startswith('AAAA')}")
                        else:
                            print("❌ AUDIO DIAGNOSTIC: NO AUDIO DATA in response!")
                            print("❌ This explains the 'No audio: Missing audio data' error")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        response_text = await response.text()
                        print(f"Raw response: {response_text[:500]}...")
                        
                else:
                    response_text = await response.text()
                    print(f"❌ Error response: {response_text}")
                    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

async def test_direct_tts():
    """Test TTS directly to isolate the issue"""
    print("\n" + "="*50)
    print("🧪 DIRECT TTS TEST")
    print("="*50)
    
    try:
        # Import the voice agent directly
        import sys
        sys.path.append('/app/backend')
        
        from agents.voice_agent import VoiceAgent
        
        # Get API key from environment
        deepgram_key = os.getenv('DEEPGRAM_API_KEY', '1069931ea453615c2ce58ad85dc06ccab4ae86b3')
        print(f"🔑 Using Deepgram API key: {deepgram_key[:10]}...{deepgram_key[-10:]}")
        
        # Create voice agent
        voice_agent = VoiceAgent(deepgram_key)
        
        # Test simple TTS
        test_text = "Hello, this is a test message."
        print(f"🎵 Testing TTS with text: '{test_text}'")
        
        audio_result = await voice_agent.text_to_speech(test_text, "friendly_companion")
        
        if audio_result:
            print(f"✅ TTS SUCCESS: Generated {len(audio_result)} characters of base64 audio")
            print(f"🎵 Audio preview: {audio_result[:50]}...")
        else:
            print("❌ TTS FAILED: Returned None")
            
    except Exception as e:
        print(f"❌ Direct TTS test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting voice processing diagnostic...")
    
    # Run the diagnostic tests
    asyncio.run(test_voice_processing())
    asyncio.run(test_direct_tts())
    
    print("\n🏁 Diagnostic complete!")