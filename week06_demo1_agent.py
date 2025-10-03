from helpers import LLM_URL
import requests
import pandas as pd
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
# import os
# from dotenv import load_dotenv

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

@tool
def extract_review(person_name):
    """
    This tool fetches reviews posted by a person.
    Use this tool whenever a query asks about a specif person's review.
    """
    print(f"Tool called: extract_review for {person_name}")

    df = pd.read_csv("amazon_reviews.csv")
    reviews = df[df["reviewerName"].str.lower() == person_name.lower()]["reviewText"].tolist()
    print("Length of reviews: ", len(reviews))
    return "\n".join(reviews[:3])


if __name__ == "__main__":
    system_message=(
        "You are a concise analyst. When asked about a product, call relevant tools to provide reviews written by a person for that product.\n"
        "Do not answer directly, always use the tool."
    )
    TOOLS = [extract_review]

    chat_model = ChatOllama(
        base_url="http://10.230.100.240:17020/", #http://localhost:11434", #"http://10.230.100.240:17020/"
        model="gpt-oss:20b",#"llama3.1:latest",
        temperature=0
    )
    # from langchain.chat_models import init_chat_model
    # chat_model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    graph = create_react_agent(
        model=chat_model, # "gpt-4o-mini",#
        tools=TOOLS,
        prompt=system_message
    )

    
    query = "What's the opinion of BuffaloPhil about Kingston cards?"

    init_messages = {
        "messages": [
            HumanMessage(content=query),
            SystemMessage(content="Was it a positive or negative review? First, answer explicitly 'Positive' or 'Negative', then explain why you think so.")
        ]
    }

    state = graph.invoke(init_messages)
    ans = state["messages"][-1].content
    print(ans)

# TODO: Add another tool that gets overall rate of a brand among all reviews 