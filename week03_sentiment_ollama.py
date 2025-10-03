import requests
import pandas as pd

df = pd.read_csv("amazon_reviews.csv", nrows=5)
df = df[["reviewText"]]
texts = df["reviewText"].to_list()

url = "http://10.230.100.240:17020/api/generate"

for text in texts:
    data = {
        "model":"gpt-oss:20b", #llama3.1:latest",
        "prompt": f"Classify the sentiment of the following review as positive, neutral, or negative: \n\n {text}\n\n Your answer should be ONLY one word (positive, neutral, or negative)",
        "stream": False
    }
    response = requests.post(url, json=data)
    print("=======")
    print("Text", text[:100])
    print(response.json()["response"])