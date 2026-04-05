import asyncio
import httpx

async def test():
    api_key = "oPmkukxhFP5fOp3FnXeOvpQ0lelsPASj"
    
    print(f"Testing API key: {api_key[:8]}...")
    print(f"Endpoint: https://api.mistral.ai/v1/chat/completions")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            'https://api.mistral.ai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'mistral-small-latest',
                'messages': [{'role': 'user', 'content': 'Say hello'}]
            }
        )
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text[:500]}")
        
        if r.status_code == 200:
            print("\n✅ SUCCESS! API key works!")
        else:
            print(f"\n❌ FAILED! Status: {r.status_code}")

asyncio.run(test())
