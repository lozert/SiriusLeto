import asyncio
import aiohttp

VECTORIZE_URL = "https://sci-tinder-stage.lab.pish.pstu.ru/fastapi/vectorize"

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(VECTORIZE_URL, json={"queries": ["Привет"]}, allow_redirects=False) as response:
            print("status:", response.status)
            print("location:", response.headers.get("Location"))
            print("content-type:", response.headers.get("Content-Type"))
            print(await response.text())

asyncio.run(main())
