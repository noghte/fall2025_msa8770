import json
import requests
import pandas as pd

df = pd.read_csv("amazon_reviews.csv", nrows=5)
df = df[["reviewText"]]
text = df["reviewText"].to_list()[2]

url = "http://10.230.100.240:17020/api/generate"

schema = """
Return ONLY valid JSON with this schema:
{
 "review": string,
 "sentiment": "positive|neutral|negative",
 "cofidence": number (0..1)
}
"""

data = {
    "model":"llama3.1:latest", #llama3.1:latest",
    "prompt": f"{schema}: Review:\n\n {text}\n\n",
    "stream": False,
    "temperature": 0
}
response = requests.post(url, json=data)
json_text = response.json()["response"]
print(json_text)

def clean_data(text):
    text = text.strip().replace("\n","")
    if text.startswith("```json"):
        text = text[len("```json"):]
    if text.endswith("```"):
        text = text[:-len("```")]
    return text

print("======\nParsed:\n")
try:
    parsed = json.loads(clean_data(json_text))
    print(parsed["sentiment"])
except Exception as e:
    print("\nFailed to parse JSON.")