# https://platform.openai.com/docs/pricing
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


df = pd.read_csv("amazon_reviews.csv", nrows=5)
df = df[["reviewText"]]
texts = df["reviewText"].to_list()

client = OpenAI(api_key=api_key)

for text in texts:
    prompt = f"Classify the sentiment of the following review as positive, neutral, or negative: \n\n {text}\n\n Your answer should be ONLY one word (positive, neutral, or negative)"
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that classify sentiments."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
       
    print("=======")
    print("Text", text[:100])
    print(resp.choices[0].message.content)
