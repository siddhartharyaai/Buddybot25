#!/usr/bin/env python3
"""
Quick test for voice personalities endpoint
"""

import asyncio
import aiohttp
import json
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://f719749a-b6dd-413e-b001-49d6ffb51041.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_voice_personalities():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/voice/personalities") as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Voice personalities: {json.dumps(data, indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"Error: {error_text}")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_voice_personalities())