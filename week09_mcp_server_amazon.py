from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pathlib import Path
import pandas as pd
import networkx as nx
import json
from networkx.readwrite import json_graph
mcp = FastMCP("AmazonReviewMCP")

DF = pd.read_csv("amazon_reviews.csv", nrows=400) 
DF = DF[["asin","reviewText","overall","summary"]]
DF = DF.fillna("")
DF["_text"] = (DF["summary"].astype(str) + ", " + DF["reviewText"].astype(str)).str.strip()

BRANDS = ["samsung","sandisk","adata","apple","kingston","sony","toshiba"]

def find_brand(txt):
    for b in BRANDS:
        if b in txt.lower():
            return b.capitalize()
    return None

DF["_brand"] = DF["_text"].apply(find_brand)

G = nx.DiGraph()

def nid(kind, val):
    return f"{kind}:{val}"

for i, r in DF.iterrows():
    if not r["_brand"]:
        continue
    rnode = nid("Review", i)
    G.add_node(rnode, kind="review", overall=float(r.get("overall")))
    if r["asin"]:
        anode = nid("ASIN", r["asin"]) #ASIN = Amazon Standard Identification Number
        G.add_node(anode, kind="asin")
        G.add_edge(rnode, anode, relation="about_asin", weight=0.7)
    bnode = nid("Brand", r["_brand"])
    G.add_node(bnode, kind="brand")
    G.add_edge(rnode, bnode, relation="mentions_brand", weight=1.0)

with open("kg.json", "w") as f:
    json.dump(nx.json_graph.node_link_data(G), f)

@mcp.tool
def list_datasets() -> list[str]:
    data_dir = Path("./data")
    datasets = [p.stem for p in data_dir.glob("*.csv")]
    return datasets


if __name__ == "__main__":
    # mcp.run()
    mcp.run(transport="http", port=8000)