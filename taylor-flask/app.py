import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings

load_dotenv()

app = Flask(__name__, static_folder='static')

# Config
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "taylor_swift_lyrics"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, check_compatibility=False )

@app.route("/")
def home():
    """Serve frontend HTML."""
    return send_from_directory('static', 'index.html')

@app.route("/api/health", methods=["GET"])
def health():
    """Simple health check."""
    try:
        collections = [c.name for c in qdrant.get_collections().collections]
        return jsonify({
            "status": "healthy",
            "collection_exists": COLLECTION_NAME in collections,
            "songs": qdrant.count(collection_name=COLLECTION_NAME).count,
            "collection": COLLECTION_NAME
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/api/search", methods=["POST"])
def search():
    """Semantic search in Qdrant index."""
    try:
        data = request.json or {}
        query = data.get("query")
        if not query:
            return jsonify({"error": "The 'query' field is required"}), 400

        limit = data.get("limit", 5)

        # Embed the query
        vec = embeddings.embed_query(query)

        # Search
        results_raw = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=vec,
            limit=limit,
            with_payload=True
        )

        # Format output
        results = []
        for p in results_raw.points:
            lyric = p.payload.get("lyric", "")
            preview = lyric[:200] + "..." if len(lyric) > 200 else lyric
            results.append({
                "title": p.payload.get("title"),
                "album": p.payload.get("album"),
                "year": p.payload.get("year"),
                "lyric_preview": preview,
                "score": p.score,
                "relevance_percent": round(p.score * 100, 2)
            })

        return jsonify({
            "query": query,
            "count": len(results),
            "results": results
        })

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)