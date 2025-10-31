#pip install neo4j
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def run_cypher(cypher):
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

def question_to_cypher(question):
    cypher = ""
    return cypher
    
if __name__ == "__main__":
    question = "Which movies Tom Hanks acted in that was released before 2000 and after 1990?"
    cypher = question_to_cypher(question)
    results = run_cypher(cypher)
    print(results)
