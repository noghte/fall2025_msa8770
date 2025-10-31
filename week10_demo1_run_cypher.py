#pip install neo4j
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

chat_model = ChatOllama(
    base_url="http://10.230.100.240:17020/", #http://localhost:11434", #"http://10.230.100.240:17020/"
    model="gpt-oss:20b",#"llama3.1:latest",
    temperature=0
)

def run_cypher(cypher):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        results = session.run(cypher)
        return [dict(r) for r in results]

def run_cypher_example():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    cypher = """
    MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
    RETURN p.name AS actor, m.title as movie
    LIMIT 10
    """
    results = []
    with driver.session() as session:
        results = session.run(cypher)
        for record in results:
            print(f"{record['actor']} -> {record['movie']} ")
    driver.close()
    return results

def clean_cypher(cypher):
    c = cypher.replace("`","")
    return c

def question_to_cypher(question):
    NODE_INFORMATION = """
    [
  {
    identity: -100,
    labels: ["Movie"],
    properties: {
      name: "Movie",
      indexes: [],
      constraints: ["Constraint( id=3, name='movie_title', type='NODE PROPERTY UNIQUENESS', schema=(:Movie {title}), ownedIndex=2 )"]
    },
    elementId: "-100"
  },
  {
    identity: -101,
    labels: ["Person"],
    properties: {
      name: "Person",
      indexes: [],
      constraints: ["Constraint( id=5, name='person_name', type='NODE PROPERTY UNIQUENESS', schema=(:Person {name}), ownedIndex=4 )"]
    },
    elementId: "-101"
  }
]
    """

    prompt =f"""
    Convert the user question into a valid Cypher query.
    Rules:
    1. Return ONLY the Cypher query, nothing else.
    2. Do not include any markdown or explanations.
    3. Include LIMIT 10 by default.
   
    Node types: {NODE_INFORMATION}

    Question: {question}

    Cypher:
    """

    result = chat_model.invoke([HumanMessage(content=prompt)])
    cypher = result.content.strip()
    cypher = clean_cypher(cypher)
    return cypher

# in-class assignment: make the code work
if __name__ == "__main__":
    question = "Which movies Tom Hanks acted in that was released before 2000 and after 1990?"
    cypher = question_to_cypher(question)
    results = run_cypher(cypher)
    print(results)
