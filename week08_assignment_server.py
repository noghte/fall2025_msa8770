from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pathlib import Path
import pandas as pd

mcp = FastMCP("DatasetServer")

@mcp.tool
def count_brands(brand_name:str) -> int:
    text = Path("./amazon_reviews.csv").read_text()
    c = text.lower().count(brand_name.lower())
    return c

if __name__ == "__main__":
    # mcp.run()
    mcp.run(transport="http", port=8000)