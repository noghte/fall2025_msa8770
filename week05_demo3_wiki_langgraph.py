from helpers import LLM_URL
import requests
import pandas as pd
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def fetch_wiki_plaintext(title):
    # https://en.wikipedia.org/w/api.php?action=query&origin=*&prop=extracts&explaintext&titles=India&format=json
    url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-G991W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"
    }
    params = {
        "action": "query",
        "origin": "*",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
        "format": "json"
    }
    r = requests.get(url, params=params, headers=headers).json()
    pages = r["query"]["pages"]
    first_page = next(iter(pages.values()))
    extract = first_page.get("extract","")
    return extract.strip()

def first_words(text, n):
    # use re or:
    words = text.split(" ")[:n]
    return " ".join(words)

@tool
def summarize_text(text):
    """
    Summarize information of country.
    Use this tool whenever a query asks about a specific country.
    """
    print("=====> summarize_text Tool called!")
    prompt = (
        "You are a concise analyst. Summarize in EXACTLY 4 short bullets, covering:\n"
        "1) location 2) population or demographics 3) government or politics 4) economy \n"
        f"Text: {text}"
    )
    payload = {
    "model":"command-r:latest", #llama3.1:latest",
    "prompt": prompt,
    "stream": False,
    "temperature": 0,
    }
    resp = requests.post(LLM_URL, json=payload).json()
    res = resp["response"].strip()
    return res

def find_country_in_query(query, countries):
    q = query.lower()
    for country in countries:
        if country.lower() in q:
            return country
    return None

if __name__ == "__main__":
    system_message=(
        "You are a concise analyst. When asked about a country call relevant tools to provide summarized information.\n"
        "Do not answer directly. Keep it to 3 bullets covering "
        "location and demographics, government/politics, and economy/industries.."
    )
    TOOLS = [summarize_text]

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

    
    df = pd.read_csv("countries.csv")
    
    query = "Give a brief overview of India focusing on economy and politics"
    country = find_country_in_query(query, df["Country"])
    if not country:
        print("No country found in query")
    else:
        print("Country:", country)
        raw_text = fetch_wiki_plaintext(country)
        text = first_words(raw_text, 1000)

        # state = {
        #     "messages": [AIMessage("You are a helpful assistant", tool_calls=TOOLS)],
        #     "country": country,
        #     "query": query,
        # }
        state = {
            "messages": [
                HumanMessage(content=f"{query}\n\nContext text (trimmed):\n{text}")
            ]
        }

        state = graph.invoke(state)
        ans = state["messages"][-1].content
        print(ans)