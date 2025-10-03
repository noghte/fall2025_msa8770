from langgraph.store.memory import InMemoryStore
import uuid

def build_memory(user_id):
    in_memory_store = InMemoryStore()

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
        filter={"topic": "GSU"}
    )
    print(memories[-1])