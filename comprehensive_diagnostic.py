#!/usr/bin/env python3
"""
Test with actual text input to isolate whether the issue is 
with empty transcripts or with the TTS generation in the pipeline.
"""

import asyncio
import aiohttp
import json

async def test_text_processing():
    """Test the text processing endpoint to see if TTS works there"""
    
    print("🧪 TESTING TEXT PROCESSING ENDPOINT")
    print("="*50)
    
    # Test with text input instead of voice
    payload = {
        "session_id": "test_session_123",
        "user_id": "test_user_456",
        "text": "Hello, can you tell me a short story?"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Making request to text processing endpoint...")
            
            async with session.post(
                'http://localhost:8001/api/conversations/text',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"📨 Response status: {response.status}")
                
                response_text = await response.text()
                print(f"📨 Response length: {len(response_text)} characters")
                
                try:
                    response_data = json.loads(response_text)
                    print("🔍 Parsed response data:")
                    for key, value in response_data.items():
                        if key == 'response_audio' and value:
                            print(f"  {key}: [audio data {len(value)} chars]")
                        else:
                            print(f"  {key}: {value}")
                            
                    # Check audio specifically
                    response_audio = response_data.get('response_audio')
                    if response_audio:
                        print(f"✅ AUDIO SUCCESS: Text endpoint generated {len(response_audio)} characters of audio")
                        return True
                    else:
                        print("❌ AUDIO MISSING: Text endpoint also returned null audio")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Raw response: {response_text[:500]}...")
                    return False
                    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

async def test_text_fast_processing():
    """Test the fast text processing endpoint"""
    
    print("\n🧪 TESTING FAST TEXT PROCESSING ENDPOINT")
    print("="*50)
    
    payload = {
        "session_id": "test_session_123", 
        "user_id": "test_user_456",
        "text": "Hello!"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8001/api/conversations/text_fast',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                print(f"📨 Response status: {response.status}")
                
                if response.status == 200:
                    response_data = await response.json()
                    print("🔍 Fast text response:")
                    for key, value in response_data.items():
                        if key == 'response_audio' and value:
                            print(f"  {key}: [audio data {len(value)} chars]")
                        else:
                            print(f"  {key}: {value}")
                            
                    response_audio = response_data.get('response_audio')
                    if response_audio:
                        print(f"✅ FAST AUDIO SUCCESS: Generated {len(response_audio)} characters")
                        return True
                    else:
                        print("❌ FAST AUDIO MISSING: Fast endpoint also returned null audio")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Fast endpoint error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Fast endpoint request failed: {str(e)}")
        return False

async def test_voice_with_text_override():
    """Test voice endpoint but with non-empty transcript simulation"""
    
    print("\n🧪 TESTING VOICE PROCESSING WITH TEXT SIMULATION")
    print("="*50)
    
    # Try to trigger a response by testing what happens when we send audio
    # but mock it to simulate having a transcript
    
    import base64
    
    # Create slightly more realistic test audio (still silence but larger)
    test_audio_bytes = b'\x00' * 4096  # 4KB of silence
    test_audio_base64 = base64.b64encode(test_audio_bytes).decode('utf-8')
    
    form_data = aiohttp.FormData()
    form_data.add_field('session_id', 'test_session_123')
    form_data.add_field('user_id', 'test_user_456')
    form_data.add_field('audio_base64', test_audio_base64)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8001/api/voice/process_audio',
                data=form_data,
                timeout=aiohttp.ClientTimeout(total=30) 
            ) as response:
                
                print(f"📨 Voice response status: {response.status}")
                
                if response.status == 200:
                    response_data = await response.json()
                    print("🔍 Voice processing response:")
                    for key, value in response_data.items():
                        if key == 'response_audio' and value:
                            print(f"  {key}: [audio data {len(value)} chars]")
                        else:
                            print(f"  {key}: {value}")
                            
                    response_audio = response_data.get('response_audio')
                    transcript = response_data.get('transcript', '')
                    response_text = response_data.get('response_text', '')
                    
                    print(f"📝 Transcript: '{transcript}'")
                    print(f"📝 Response text: '{response_text}'")
                    
                    if response_audio:
                        print(f"✅ VOICE AUDIO SUCCESS: Generated {len(response_audio)} characters")
                        return True
                    else:
                        print("❌ VOICE AUDIO MISSING: Still null even with larger audio")
                        
                        # If we have response text but no audio, that's the exact problem
                        if response_text and response_text != "I heard you!":
                            print("🔍 DIAGNOSIS: Response text exists but no audio generated!")
                            print("🔍 This suggests TTS is not being called in the voice pipeline")
                        
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Voice endpoint error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Voice endpoint request failed: {str(e)}")
        return False

async def main():
    print("🚀 Starting comprehensive audio diagnostic...")
    
    text_works = await test_text_processing()
    fast_works = await test_text_fast_processing() 
    voice_works = await test_voice_with_text_override()
    
    print("\n" + "="*50)
    print("🏁 DIAGNOSTIC SUMMARY")
    print("="*50)
    print(f"Text endpoint audio: {'✅ WORKS' if text_works else '❌ BROKEN'}")
    print(f"Fast text endpoint audio: {'✅ WORKS' if fast_works else '❌ BROKEN'}")  
    print(f"Voice endpoint audio: {'✅ WORKS' if voice_works else '❌ BROKEN'}")
    
    if not any([text_works, fast_works, voice_works]):
        print("\n🚨 ALL ENDPOINTS MISSING AUDIO - TTS pipeline issue")
    elif text_works and not voice_works:
        print("\n🔍 TEXT WORKS, VOICE BROKEN - Voice pipeline TTS issue")
    elif voice_works:
        print("\n✅ VOICE WORKS - Issue may be with empty transcripts only")
    
    print("\n🏁 Comprehensive diagnostic complete!")

if __name__ == "__main__":
    asyncio.run(main())