import asyncio
from fastmcp import Client

SERVER_PATH = "http://127.0.0.1:8000/mcp"

async def count_brand(brand_name: str) -> int:
    async with Client(SERVER_PATH) as client:
        try:
            result = await client.call_tool("count_brands", {"brand_name": brand_name})
            print("Raw MCP result:", result)
            return result.data  # returns integer
        except Exception as e:
            print("Error:", e)
            return -1

async def main():
    c = await count_brand("Kingston")
    print("Count:", c)

if __name__ == "__main__":
    asyncio.run(main())