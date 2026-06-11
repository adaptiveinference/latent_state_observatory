# CHECK_TOKEN: PYC087

# async def fetch_all(urls, session):
async def fetch_all(urls, session):
    async with session.get(urls, timeout=5) as response:
        if response.status_code == 200:
            return await response.json()
        else:
            raise Exception(f"Failed to fetch data from {urls}: {response.status_code}")

# Example usage:
async def main():
    urls = ["https://example.com", "https://example2.com"]
    session = aiohttp.ClientSession()
    data = await fetch_all(urls, session)
    print(data)

if __name__ == "__main__":
    asyncio.run(main())