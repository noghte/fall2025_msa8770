import io
import asyncio
import pandas as pd
from openai import OpenAI
from fastmcp import Client

# SERVER_PATH = "week08_mcp_dataset_server.py"
SERVER_PATH = "http://127.0.0.1:8000/mcp" 
DATASET_URI = "dataset://sales"
MODEL_NAME = "gpt-4o"

async def fetch_csv() -> str:
    print("EVENT: fetch_csv has been called!")
    client = Client(SERVER_PATH)
    async with client:
        try:
            content = await client.read_resource(DATASET_URI)
            print(content[0].text)
            return content[0].text
        except Exception:
            return "No Data"


async def fetch_prompt_text() -> str:
    print("EVENT: fetch_prompt_text has been called!")
    client = Client(SERVER_PATH)
    async with client:
        try:
            content = await client.get_prompt("summarization_prompt")
            print(content[0].text)
            return content[0].text
        except Exception:
            return ("Show summary")


def summarize_with_openai(csv_text: str, prompt_text: str) -> str:
    print("EVENT: summarize_with_openai has been called!")
    llm = OpenAI() # reads OPEN_AI_KEY from env
    sample = "\n".join(csv_text.splitlines()[:60])
    prompt = f"{prompt_text}\n\n Here is the contents of the CSV:\n{sample}"
    resp = llm.responses.create(
        model=MODEL_NAME,
        input = [{"role": "user", "content": prompt}]
    )
    return resp.output_text

async def main():
    csv_text = await fetch_csv()
    prompt_text = await fetch_prompt_text()
    summary = summarize_with_openai(csv_text, prompt_text)
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())