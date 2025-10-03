# ollama pull embeddinggemma:300m
from langgraph.store.memory import InMemoryStore
import uuid
from langchain.embeddings import init_embeddings
from langchain_ollama import OllamaEmbeddings

def build_memory(user_id):
    # OpenAI embedding example
    # in_memory_store = InMemoryStore(
    #     index = {
    #         "embed":init_embeddings("openai:text-embedding-3-small"),
    #         "dims": 1536,
    #         # "field": ["topic", "hobby"]
    #     }
    # )
    embeddings = OllamaEmbeddings(
        model="embeddinggemma:300m",
        base_url="http://127.0.0.1:11434"
    )

    in_memory_store = InMemoryStore(
        index = {
            "embed":embeddings.embed_documents,
            "dims": 768,
            # "field": ["topic", "hobby"]
        }
    )

    # Memories are namespaced by a tuple:
    namespace_for_memory = (user_id, "memories")

    memory_id = str(uuid.uuid4())
    memory = {"topic": "GSU", "courses": "I like MSA8770 the most!"}
    in_memory_store.put(namespace_for_memory, memory_id, memory)

    memory_id = str(uuid.uuid4())
    memory = {"hobby": "biking"}
    in_memory_store.put(namespace_for_memory, memory_id, memory)

    memory_id = str(uuid.uuid4())
    memory = {"skills": "writing", "languages": "English, French, Arabic"}
    in_memory_store.put(namespace_for_memory, memory_id, memory)

    return in_memory_store

if __name__ == "__main__":
    user_id = "1"
    store = build_memory(user_id)

    memories = store.search(
        (user_id, "memories"),
        query="What languages and skills the user have?",
        limit=1
    )
    print(memories[-1])