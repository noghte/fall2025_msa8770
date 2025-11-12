import json
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()

# ====== Neo4j Configuration ======
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "lyrics992211")


class Neo4jKnowledgeGraphImporter:
    """Import song knowledge graphs into Neo4j with optimized batch operations."""
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"Connected to Neo4j at {uri}")
    
    def close(self):
        self.driver.close()
        print("Neo4j connection closed")
    
    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")

    def create_indexes_and_constraints(self):
        """Create indexes and constraints for optimal performance."""
        with self.driver.session() as session:
            operations = [
                # Constraints for uniqueness
                "CREATE CONSTRAINT song_title IF NOT EXISTS FOR (s:Song) REQUIRE s.title IS UNIQUE",
                "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE (e.name, e.type) IS UNIQUE",
                
                # Indexes for faster lookups
                "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
                "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
                "CREATE INDEX song_artist IF NOT EXISTS FOR (s:Song) ON (s.artist)",
            ]
            
            for operation in operations:
                try:
                    session.run(operation)
                    constraint_name = operation.split("IF NOT EXISTS")[0].strip().split()[-1]
                    print(f"  ✓ Created: {constraint_name}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"  ⚠ Warning: {e}")

    def import_song_graph(self, graph_data: Dict):
        """
        Import a single song's complete graph (song node + entities + relationships).
        This is optimized for the new simplified format.
        """
        with self.driver.session() as session:
            # 1. Create Song node
            song_title = graph_data["song_title"]
            song_props = graph_data.get("song_properties", {})
            
            session.run("""
                MERGE (s:Song {title: $title})
                SET s += $properties
            """, 
                title=song_title,
                properties=song_props
            )
            
            # 2. Create all Entity nodes with labels
            entities = graph_data.get("entities", [])
            for entity in entities:
                # Create entity with both :Entity and specific type label (e.g., :Person)
                entity_type = entity["type"]
                entity_name = entity["name"]
                properties = entity.get("properties", {})
                
                # Use dynamic label creation
                query = f"""
                    MERGE (e:Entity:{entity_type} {{name: $name, type: $type}})
                    SET e += $properties
                """
                
                session.run(query,
                    name=entity_name,
                    type=entity_type,
                    properties=properties
                )
            
            # 3. Create all relationships
            relationships = graph_data.get("relationships", [])
            for rel in relationships:
                source_name = rel["source"]
                source_type = rel["source_type"]
                target_name = rel["target"]
                target_type = rel["target_type"]
                rel_type = rel["relationship_type"]
                rel_props = rel.get("properties", {})
                
                # Build dynamic query based on target type
                # Songs are matched by title, entities by name+type
                if target_type == "Song":
                    query = f"""
                        MATCH (source:Entity {{name: $source_name, type: $source_type}})
                        MATCH (target:Song {{title: $target_name}})
                        MERGE (source)-[r:{rel_type}]->(target)
                        SET r += $properties
                    """
                    session.run(query,
                        source_name=source_name,
                        source_type=source_type,
                        target_name=target_name,
                        properties=rel_props
                    )
                else:
                    query = f"""
                        MATCH (source:Entity {{name: $source_name, type: $source_type}})
                        MATCH (target:Entity {{name: $target_name, type: $target_type}})
                        MERGE (source)-[r:{rel_type}]->(target)
                        SET r += $properties
                    """
                    session.run(query,
                        source_name=source_name,
                        source_type=source_type,
                        target_name=target_name,
                        target_type=target_type,
                        properties=rel_props
                    )
    
    def import_all_graphs(self, graphs: List[Dict], show_progress: bool = True):
        """Import multiple song graphs with progress tracking."""
        total = len(graphs)
        
        for idx, graph in enumerate(graphs, 1):
            song_title = graph["song_title"]
            
            if show_progress:
                print(f"[{idx}/{total}] Importing: {song_title}")
            
            try:
                self.import_song_graph(graph)
                
                if show_progress:
                    entity_count = len(graph.get("entities", []))
                    rel_count = len(graph.get("relationships", []))
                    print(f"  ✓ {entity_count} entities, {rel_count} relationships\n")
                    
            except Exception as e:
                print(f"  ✗ ERROR importing '{song_title}': {str(e)}\n")
    
    def get_statistics(self):
        """Get comprehensive database statistics."""
        with self.driver.session() as session:
            stats = {}
            
            # Total nodes and relationships
            result = session.run("MATCH (n) RETURN count(n) as count")
            stats["Total Nodes"] = result.single()["count"]
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats["Total Relationships"] = result.single()["count"]
            
            # Count Songs
            result = session.run("MATCH (s:Song) RETURN count(s) as count")
            stats["Songs"] = result.single()["count"]
            
            # Count Entities by type
            result = session.run("""
                MATCH (e:Entity)
                RETURN e.type as type, count(e) as count
                ORDER BY count DESC
            """)
            
            entity_counts = {}
            for record in result:
                entity_counts[record["type"]] = record["count"]
            
            stats["Entities by Type"] = entity_counts
            
            # Count Relationships by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """)
            
            rel_counts = {}
            for record in result:
                rel_counts[record["rel_type"]] = record["count"]
            
            stats["Relationships by Type"] = rel_counts
            
            return stats
    
    def print_sample_queries(self):
        """Print useful sample queries for exploring the graph."""
        print("\n" + "=" * 70)
        print("SAMPLE CYPHER QUERIES")
        print("=" * 70)
        
        queries = [
            ("View all entity types", 
             "MATCH (e:Entity) RETURN DISTINCT e.type, count(*) as count ORDER BY count DESC"),
            
            ("Find all persons mentioned in songs",
             "MATCH (p:Person)-[:MENTIONED_IN]->(s:Song) RETURN p.name, s.title LIMIT 10"),
            
            ("Find locations and songs they appear in",
             "MATCH (l:Location)-[:APPEARS_IN]->(s:Song) RETURN l.name, s.title LIMIT 10"),
            
            ("Find person-location connections",
             "MATCH (p:Person)-[r]->(l:Location) WHERE type(r) <> 'MENTIONED_IN' RETURN p.name, type(r) as action, l.name, r.song LIMIT 10"),
            
            ("Find person attributes",
             "MATCH (p:Person)-[:HAS_ATTRIBUTE]->(a:Attribute) RETURN p.name, a.name LIMIT 10"),
            
            ("Find most connected entities",
             "MATCH (e:Entity)-[r]-() RETURN e.name, e.type, count(r) as connections ORDER BY connections DESC LIMIT 10"),
            
            ("Find songs with most entities",
             "MATCH (e:Entity)-[r]->(s:Song) RETURN s.title, count(DISTINCT e) as entity_count ORDER BY entity_count DESC LIMIT 10"),
            
            ("Path between two entities (example)",
             "MATCH path = shortestPath((e1:Entity {name: 'I'})-[*..5]-(e2:Entity {name: 'you'})) RETURN path LIMIT 1"),
        ]
        
        for idx, (description, query) in enumerate(queries, 1):
            print(f"\n{idx}. {description}:")
            print(f"   {query}")
        
        print("\n" + "=" * 70)
def import_from_json(json_path: str, clear_db: bool = False):
    """
    Import song knowledge graphs from JSON file into Neo4j.
    
    Args:
        json_path: Path to the graph JSON file
        clear_db: Whether to clear the database before importing
    """
    
    # Load the JSON data
    print(f"\n{'='*70}")
    print(f"Loading data from: {json_path}")
    print(f"{'='*70}\n")
    
    if not os.path.exists(json_path):
        print(f"ERROR: File not found: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    graphs = data.get("graphs", [])
    
    if not graphs:
        print("ERROR: No graphs found in JSON file")
        return
    
    print(f"Found {len(graphs)} song graphs to import\n")
    
    # Create importer
    importer = Neo4jKnowledgeGraphImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Clear database if requested
        if clear_db:
            print("\n⚠  Clearing existing database...")
            importer.clear_database()
            print()
        
        # Create constraints and indexes
        print("Setting up indexes and constraints...")
        importer.create_indexes_and_constraints()
        print()
        
        # Import all graphs
        print("Importing song graphs...\n")
        importer.import_all_graphs(graphs, show_progress=True)
        
        # Get and print statistics
        print("=" * 70)
        print("IMPORT COMPLETE - DATABASE STATISTICS")
        print("=" * 70)
        
        stats = importer.get_statistics()
        
        print(f"\n📊 Overview:")
        print(f"  Total Nodes: {stats['Total Nodes']}")
        print(f"  Total Relationships: {stats['Total Relationships']}")
        print(f"  Songs: {stats['Songs']}")
        
        print(f"\n📦 Entities by Type:")
        for entity_type, count in stats["Entities by Type"].items():
            print(f"  {entity_type}: {count}")
        
        print(f"\n🔗 Relationships by Type:")
        for rel_type, count in sorted(stats["Relationships by Type"].items(), 
                                    key=lambda x: x[1], reverse=True):
            print(f"  {rel_type}: {count}")
        
        # Print sample queries
        importer.print_sample_queries()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        importer.close()

if __name__ == "__main__":
    # Configuration
    JSON_PATH = "data/outputs/taylor_swift_graph.json"
    CLEAR_DATABASE = True  # Set to False to append to existing data
    
    print("=" * 70)
    print("Neo4j Knowledge Graph Importer")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Neo4j URI: {NEO4J_URI}")
    print(f"  Neo4j User: {NEO4J_USER}")
    print(f"  JSON File: {JSON_PATH}")
    print(f"  Clear database before import: {CLEAR_DATABASE}")
    
    # Import the data
    import_from_json(JSON_PATH, clear_db=CLEAR_DATABASE)