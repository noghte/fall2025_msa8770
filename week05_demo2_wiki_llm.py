
from helpers import LLM_URL
import requests
import pandas as pd

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

def summarize_text(text):
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

# An example logic to find whether data that user is looking for exists in our database
def find_country_in_query(query, countries):
    q = query.lower()
    for country in countries:
        if country.lower() in q:
            return country
    return None

def first_words(text, n):
    # use re or:
    words = text.split(" ")[:n]
    return " ".join(words)

if __name__ == "__main__":
    query = "Give a brief overview of India focusing on economy and politics"
    df = pd.read_csv("countries.csv")
    
    country = find_country_in_query(query, df["Country"])
    if not country:
        print("No country found in query")
    else:
        print("Country:", country)
        raw_text = fetch_wiki_plaintext(country)
        text = first_words(raw_text, 500)
        summary = summarize_text(text)
        print(summary)