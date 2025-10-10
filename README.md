 # Demo Projects

 This repository contains weekly demo scripts showcasing various LLM and data processing techniques for MSA8770 course offered by Institute for Insight at Georgia State University.

 ## Week 03 Demos

- `week03_download_reviews.py`: Download Amazon reviews dataset from Kaggle and save to CSV.
- `week03_json.py`: Generate and parse LLM output as JSON for review sentiment analysis.
- `week03_gsu_ollama.py`: Basic text generation demo using Ollama API.
- `week03_sentiment_ollama.py`: Classify Amazon review sentiments using Ollama API.
- `week03_sentiment_openai.py`: Classify Amazon review sentiments using OpenAI API.

 ## Week 04 Demos

- `week04_demo1_pydantic.py`: Validate sentiment analysis results with Pydantic models.
- `week04_demo2_json.py`: Use LangChain JSON output parser to map LLM responses into Pydantic.
- `week04_demo3_weather_simple.py`: Manual function-calling demonstration for fetching weather data.
- `week04_demo4_weather_openai.py`: Agent-based weather lookup using OpenAI and web search tool.

 ## Week 05 Demos

- `week05_demo1_countries.py`: Scrape a list of sovereign states from Wikipedia.
- `week05_demo2_wiki_llm.py`: Fetch Wikipedia extracts and summarize with an LLM.
- `week05_demo3_wiki_langgraph.py`: Build a React agent with LangGraph to summarize country info.

 ## Week 06 Demos

- `week06_demo1_agent.py`: Integrate LangGraph tools for extracting and analyzing Amazon reviews.
- `week06_demo2_longterm_memory1.py`: Demonstrate storing and retrieving simple long-term memories.
- `week06_demo2_longterm_memory2.py`: Extend long-term memory store and query by metadata filter.
- `week06_demo3_shortterm_memory.py`: Illustrate short-term memory checkpointing across conversation turns.
 - `week06_demo4_longterm_memory_semantic.py`: Show semantic memory retrieval using vector embeddings.

## Week 07 Demos

- `week07_demo1_uniprot.py`: Fetch protein names and function annotations from UniProt for kinases and save to CSV.
- `week07_demo2_create_vectordb.py`: Create a Qdrant collection and populate it with embeddings of kinase functions using OpenAIEmbeddings.
- `week07_demo3_rag.py`: Perform retrieval-augmented generation by querying kinase function vectors in Qdrant and answering biology questions with ChatOpenAI.
- `week07_demo4_agentic_rag.py`: Agentic RAG example: build a REACT agent with LangGraph to search kinase functions and answer biology questions.

 # Helpers and Tests

 Additional utility functions and tests are provided in `helpers.py` and `helpers_test.py`.
