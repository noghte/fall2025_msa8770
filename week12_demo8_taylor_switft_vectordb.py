import uuid
import os
import math
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "taylor_swift_lyrics"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)

df = pd.read_csv("data/TaylorSwift.csv")
texts = []
for _, row in df.iterrows():
    text = f"Title: {row['Title']}, Album: {row['Album']}, Year: {row['Year']}, Lyrics: {row['Lyric']}"
    texts.append(text)

print(f"Processing {len(texts)} songs...")
vectors = embeddings.embed_documents(texts)
dim = len(vectors[0])
print(f"Dimension: {dim}")

# For demo purposes - delete collection if it exists
# existing = [c.name for c in client.get_collections().collections]
# if COLLECTION_NAME in existing:
#     print(f"Deleting existing collection: {COLLECTION_NAME}")
#     client.delete_collection(COLLECTION_NAME)


client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
)

points = []
for i, row in df.iterrows():
    points.append(
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vectors[i],
            payload={
                "artist": row["Artist"],
                "title": row["Title"],
                "album": row["Album"],
                "year": row["Year"],
                "date": row["Date"],
                # "lyric": row["Lyric"]
            }
        )
    )


client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"Successfully created vector database with {len(points)} songs!")
