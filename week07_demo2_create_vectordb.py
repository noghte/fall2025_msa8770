import uuid
import os
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
#from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

QDRANT_URL ="https://b0424e7c-5285-4dff-b396-1da7163372e7.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "msa8770"

# embeddings = OllamaEmbeddings(
#     model="embeddinggemma:300m",
#     base_url="http://127.0.0.1:11434"
# )

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
df = pd.read_csv("kinase.csv")
functions = df["function"].fillna("").tolist()

vectors = embeddings.embed_documents(functions)
dim = len(vectors[0])
print("Dimension: ", dim)

# For demo-purposes
existing = [c.name for c in client.get_collections().collections]
if COLLECTION_NAME in existing:
    print("Deleting collection: ", COLLECTION_NAME)
    client.delete_collection(COLLECTION_NAME)

client.create_collection(collection_name=COLLECTION_NAME, 
vectors_config=VectorParams(size=dim, distance=Distance.COSINE))

points = []

for i, row in df.iterrows():
    points.append(
        PointStruct(
            id=str(uuid.uuid4()),
            vector = vectors[i],
            payload ={
                "uniprot": row["uniprot"],
                "name": row["name"]
            }
        )
    )

client.upsert(collection_name=COLLECTION_NAME, points=points)