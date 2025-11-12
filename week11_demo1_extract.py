import os
import json
import pandas as pd
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

load_dotenv()

class Entity(BaseModel):
    """Base entity with common properties."""
    name: str = Field(..., description="Name or identifier of the entity") # ... means  “this field is required”. It’s a special shorthand to say no default value.
    type: str = Field(..., description="Entity type (Person, Location, Attribute)")
    properties: Dict[str, str] = Field(
        default_factory=dict, # means when not provided, default to an empty dict ({}) 
        description="Additional properties specific to this entity"
    )
class Relationship(BaseModel):
    """Generic relationship between entities."""
    source: str = Field(..., description="Source entity name")
    source_type: str = Field(..., description="Source entity type")
    target: str = Field(..., description="Target entity name")
    target_type: str = Field(..., description="Target entity type")
    relationship_type: str = Field(..., description="Type of relationship")
    properties: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional relationship properties"
    )

class SongGraph(BaseModel):
    """
    Complete graph structure for a song including entities and relationships.
    This format is ready for Neo4j import.
    """
    song_title: str = Field(..., description="The title of the song")
    song_properties: Dict[str, str] = Field(
        default_factory=dict,
        description="Song metadata (artist, album, year, etc.)"
    )
    entities: List[Entity] = Field(
        default_factory=list,
        description="All entities extracted from the song"
    )
    relationships: List[Relationship] = Field(
        default_factory=list,
        description="All relationships between entities"
    )

# ====== LLM Setup ======

def setup_llm():
    """Initialize the LLM model for entity extraction."""
    llm = init_chat_model("openai:gpt-4o-mini", temperature=0)
    return llm


# ====== Entity Extraction Prompt ======

def create_extraction_prompt():
    """Create the prompt template for entity extraction."""
    
    system_prompt = """You are an expert at extracting structured information from song lyrics for knowledge graph construction.

Extract the following from the lyrics:

1. PERSONS: People mentioned by name OR pronouns (I, you, he, she, they, we)
   - Keep pronouns as-is, extract actual names when present
   - Add context in properties if available

2. LOCATIONS: Physical places (cities, buildings, parks, streets, venues)
   - Classify location type in properties (city, venue, landmark, etc.)

3. ATTRIBUTES: Descriptive adjectives or qualities
   - These become separate nodes that can be shared across entities

4. RELATIONSHIPS: Connect entities with meaningful verbs
   - Person → MENTIONED_IN → Song
   - Location → APPEARS_IN → Song  
   - Person → [ACTION_VERB] → Location (e.g., WALKED_THROUGH, LIVED_IN)
   - Person → [ACTION_VERB] → Person (e.g., LOVED, KNOWS, FORGETS)
   - Person → HAS_ATTRIBUTE → Attribute
   - Location → HAS_ATTRIBUTE → Attribute

IMPORTANT:
- Extract only what's clearly present
- Use exact wording from lyrics when possible
- For verbs, use UPPER_SNAKE_CASE (e.g., WALKED_THROUGH)
- For values, use lowercase (e.g., i, you, atlanta)
- Be thorough but accurate


{format_instructions}"""

    human_prompt = """Extract the complete graph structure from these lyrics:

SONG TITLE: {song_title}

LYRICS:
{lyrics}

Extract all entities and relationships to create a knowledge graph for this song."""

    return system_prompt, human_prompt


# ====== Main Processing Functions ======

def extract_graph_from_lyrics(
    song_title: str, 
    lyrics: str, 
    song_metadata: dict,
    llm, 
    parser
) -> SongGraph:
    """Extract complete graph structure from a single song's lyrics."""
    
    system_prompt, human_prompt = create_extraction_prompt()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    # Create the chain
    chain = prompt | llm | parser
    
    try:
        # Invoke the chain with the song data
        result = chain.invoke({
            "song_title": song_title,
            "lyrics": lyrics[:3000],  # Limit lyrics length to avoid token limits
            "format_instructions": parser.get_format_instructions()
        })
        
        # Add song metadata
        result.song_properties = song_metadata
        
        return result
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        # Return empty graph on error
        return SongGraph(
            song_title=song_title,
            song_properties=song_metadata,
            entities=[],
            relationships=[]
        )

def append_to_json_file(data: dict, filepath: str):
    """Append a graph entry to the JSON file."""
    
    # Read existing data if file exists
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {"graphs": []}
    else:
        existing_data = {"graphs": []}
    
    # Append new data
    existing_data["graphs"].append(data)
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

def process_lyrics_csv(csv_path: str, output_path: str, num_songs: int = 10):
    """Process the CSV and extract entities, streaming results to JSON."""
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    df_subset = df.head(num_songs)
    
    # Setup LLM and parser
    llm = setup_llm()
    parser = PydanticOutputParser(pydantic_object=SongGraph)
    
    # Clear output file if it exists
    if os.path.exists(output_path):
        os.remove(output_path)
    
    print(f"Processing {num_songs} songs from the dataset...\n")
    
    for idx, row in df_subset.iterrows():
        song_title = row['Title']
        lyrics = row['Lyric']
        
        print(f"[{idx + 1}/{num_songs}] Processing: {song_title}")
        
        # Prepare metadata
        song_metadata = {
            "artist": str(row['Artist']),
            "album": str(row['Album']),
            "year": str(row['Year']),
            "song_index": str(idx)
        }
        
        # Extract graph structure
        graph = extract_graph_from_lyrics(song_title, lyrics, song_metadata, llm, parser)
        
        # Convert to dict and append to file immediately
        graph_dict = graph.model_dump()
        append_to_json_file(graph_dict, output_path)
        
        print(f"  ✓ Extracted {len(graph.entities)} entities, "
              f"{len(graph.relationships)} relationships")
        print(f"  ✓ Appended to {output_path}\n")
    
    print(f"\n{'='*60}")
    print("Processing complete!")
    print(f"{'='*60}")

def generate_neo4j_import_summary(json_path: str):
    """Generate summary statistics from the JSON file."""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    graphs = data.get("graphs", [])
    
    # Collect statistics
    total_songs = len(graphs)
    total_entities = sum(len(g["entities"]) for g in graphs)
    total_relationships = sum(len(g["relationships"]) for g in graphs)
    
    # Count entity types
    entity_types = {}
    for graph in graphs:
        for entity in graph["entities"]:
            etype = entity["type"]
            entity_types[etype] = entity_types.get(etype, 0) + 1
    
    # Count relationship types
    rel_types = {}
    for graph in graphs:
        for rel in graph["relationships"]:
            rtype = rel["relationship_type"]
            rel_types[rtype] = rel_types.get(rtype, 0) + 1
    
    print(f"\nSUMMARY STATISTICS")
    print(f"{'='*60}")
    print(f"Total songs processed: {total_songs}")
    print(f"Total entities extracted: {total_entities}")
    print(f"Total relationships: {total_relationships}")
    print(f"\nEntity Types:")
    for etype, count in sorted(entity_types.items()):
        print(f"  - {etype}: {count}")
    print(f"\nRelationship Types:")
    for rtype, count in sorted(rel_types.items()):
        print(f"  - {rtype}: {count}")
    print(f"{'='*60}")

# ====== Main Execution ======

if __name__ == "__main__":
    # Configuration
    CSV_PATH = "data/TaylorSwift.csv"
    NUM_SONGS = 10
    OUTPUT_JSON = "data/outputs/taylor_swift_graph.json"
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    
    print("=" * 60)
    print("Song Lyrics → Neo4j Knowledge Graph Extraction")
    print("=" * 60)
    
    # Process the CSV with streaming output
    process_lyrics_csv(CSV_PATH, OUTPUT_JSON, NUM_SONGS)
    
    # Generate summary
    generate_neo4j_import_summary(OUTPUT_JSON)
    
    print(f"\nOutput file ready for Neo4j import: {OUTPUT_JSON}")