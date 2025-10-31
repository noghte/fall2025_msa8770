# import asyncio
# from fastmcp import Client

# SERVER_PATH = "http://127.0.0.1:8000/mcp"

# async def mcp_avg(brand_name: str) -> float:
#     async with Client(SERVER_PATH) as client:
#         try:
#             result = await client.call_tool("avg_score_for_brand", {"brand_name": brand_name})
#             print("MCP result:", result)
#             return float(result.data)  # returns float
#         except Exception as e:
#             print("Error:", e)
#             return 0.0

# async def planner_agent(inbox:asyncio.Queue, avg_outbox: asyncio.Queue, ex_outbox: asyncio.Queue):
#     brands = ["Kingston", "Samsung", "SanDisk"]
#     print("Brands:", brands)
#     await avg_outbox.put(("AVG_THESE", brands))

#     results = {}
#     while len(results) < len(brands):
#         mtype, payload = await inbox.get()
#         if mtype == "AVG_RESULT":
#             b, a = payload # b: brand, a: the average score
#             results[b] = a 
#             print(f"[Planner] {b}: {a:.2f} ")

# # async def avg_agent(avg_agent)

# async def main():
#     planner_in = asyncio.Queue()
#     avg_in = asyncio.Queue()
#     ex_in = asyncio.Queue()

#     tasks = [
#         asyncio.create_task(planner_agent(planner_in, avg_in, ex_in)),
#         asyncio.create_task(avg_agent(avg_in, planner_in)),

#     ]
    

# if __name__ == "__main__":
#     asyncio.run(main())