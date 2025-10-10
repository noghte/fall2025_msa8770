
import os
from qdrant_client import QdrantClient
import pandas as pd
# from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
load_dotenv()

QDRANT_URL ="https://b0424e7c-5285-4dff-b396-1da7163372e7.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "msa8770"

df = pd.read_csv("kinase.csv")

@tool
def search_kinase(query_text, limit=3, max_chars=1000):
    """
    Search kinase functions in Qdrant by semantic similarity and return text context.
    Always call this tool before answering any question related to biology.
    """
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    query_vec = embeddings.embed_query(query_text)
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        limit=limit,
        with_payload=True
    )
    points = response.points
    rows = []
    for h in points:
        uniprot = h.payload["uniprot"]
        fn = df[df["uniprot"]==uniprot]["function"].values[0]
        if len(fn)>max_chars:
            fn=fn[:max_chars]
        rows.append(fn)
    return "\n".join(rows) if rows else "No Context"

if __name__ == "__main__":
    # embeddings = OllamaEmbeddings(
    #     model="embeddinggemma:300m",
    #     base_url="http://127.0.0.1:11434"
    # )
    # system_message = SystemMessage(
    #     "",
    #     ""
    #     ""
    #     ""

    # )
    system_message=(
        "You are a concise analyst. Always follow this sequence:\n"
        "1) Call search_kinase(query) to get context.\n2) Do whatenver you want \nAnswer ONLY from tools outputs. If insufficient, say 'Insufficient context'"
    )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    TOOLS = [search_kinase]
    graph = create_react_agent(
        model=chat_model, # "gpt-4o-mini",#
        tools=TOOLS,
        prompt=system_message
    )

    query_text = "Which pubmed article states that G protein- coupled receptor that initiates the phototransduction cascade? Give me just the pubmed id and nothing else."
    state = graph.invoke({"messages": [HumanMessage(content=query_text)]})
    print(state["messages"][-1].content)
