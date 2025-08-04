#!/usr/bin/env python3
"""
Quick Performance Test - Verify we restored the 2-3 second performance
"""

import asyncio
import aiohttp
import time
import json

async def test_performance():
    print("🚀 TESTING RESTORED PERFORMANCE...")
    
    base_url = "https://4b9bb89e-ec65-42a8-a718-549834e70943.preview.emergentagent.com/api"
    
    tests = [
        ("Simple Conversation", {"session_id": "perf1", "user_id": "perf1", "message": "Hello, tell me a joke"}),
        ("Story Request", {"session_id": "perf2", "user_id": "perf2", "message": "Tell me a short story about a brave mouse"}),
        ("TTS Test", {"text": "Hello there, this is a test of text to speech", "personality": "friendly_companion"})
    ]
    
    async with aiohttp.ClientSession() as session:
        # Test conversation endpoints
        for test_name, data in tests[:2]:
            try:
                start_time = time.time()
                async with session.post(f"{base_url}/conversations/text", json=data, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response_text", "")
                        word_count = len(response_text.split())
                        
                        status = "✅ EXCELLENT" if duration < 3 else "⚠️ SLOW" if duration < 10 else "❌ VERY SLOW"
                        print(f"{status} {test_name}: {duration:.2f}s ({word_count} words)")
                    else:
                        print(f"❌ {test_name}: HTTP {response.status}")
                        
            except Exception as e:
                print(f"❌ {test_name}: Error - {str(e)}")
        
        # Test TTS endpoint
        try:
            start_time = time.time()
            async with session.post(f"{base_url}/voice/tts", json=tests[2][1], timeout=aiohttp.ClientTimeout(total=10)) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    audio_size = len(result.get("audio_base64", ""))
                    
                    status = "✅ EXCELLENT" if duration < 2 else "⚠️ SLOW" if duration < 5 else "❌ VERY SLOW"
                    print(f"{status} TTS Test: {duration:.2f}s ({audio_size} chars audio)")
                else:
                    print(f"❌ TTS Test: HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ TTS Test: Error - {str(e)}")
    
    print("\n🎯 PERFORMANCE TARGET: <3s for conversations, <2s for TTS")

if __name__ == "__main__":
    asyncio.run(test_performance())