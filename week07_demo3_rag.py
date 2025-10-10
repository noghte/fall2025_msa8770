
import os
from qdrant_client import QdrantClient
import pandas as pd
# from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
load_dotenv()

QDRANT_URL ="https://b0424e7c-5285-4dff-b396-1da7163372e7.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "msa8770"

df = pd.read_csv("kinase.csv")

def get_points(query_text, limit=3):
    query_vec = embeddings.embed_query(query_text)
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        limit=limit,
        with_payload=True
    )
    return response.points

def build_context(points, max_chars=1000):
    rows = []
    for h in points:
        uniprot = h.payload["uniprot"]
        fn = df[df["uniprot"]==uniprot]["function"].values[0]
        if len(fn)>max_chars:
            fn=fn[:max_chars]
        rows.append(fn)
    return "\n".join(rows) if rows else "No Context"

def answer_with_llm(question, points):
    context = build_context(points)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    RAG_SYSTEM=(
        "Answer using ONLY the provided context. "
        "If the context is insufficient, say 'Insufficient context'"
    )
    messages = [
        SystemMessage(content=RAG_SYSTEM),
        HumanMessage(content=f"Question: {question}\n\nContext:\n{context}")
    ]
    resp = llm.invoke(messages)
    return resp.content

if __name__ == "__main__":
    # embeddings = OllamaEmbeddings(
    #     model="embeddinggemma:300m",
    #     base_url="http://127.0.0.1:11434"
    # )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    query_text = "Which pubmed article states that G protein- coupled receptor that initiates the phototransduction cascade? Give me just the pubmed id and nothing else."
    points = get_points(query_text)
    answer = answer_with_llm(query_text, points)
    print(answer)
