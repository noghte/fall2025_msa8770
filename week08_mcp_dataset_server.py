from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pathlib import Path

mcp = FastMCP("DatasetServer")

@mcp.tool
def list_datasets() -> list[str]:
    data_dir = Path("./data")
    datasets = [p.stem for p in data_dir.glob("*.csv")]
    return datasets

@mcp.resource("dataset://{name}")
def get_dataset(name: str) -> str:
    csv_path = Path(f"./data/{name}.csv")
    if not csv_path.exists():
       raise ToolError(f"Dataset Not Found: {name}") 
    return csv_path.read_text()

@mcp.prompt()
def summarization_prompt() -> str:
    return (
        "You are a senior business analyst. "
        "Summarize the CSV: highlight the trends, "
        "month-over-month growth, and outliers in 2-3 bullet points"
    )

if __name__ == "__main__":
    # mcp.run()
    mcp.run(transport="http", port=8000)