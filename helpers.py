import requests

LLM_URL="http://10.230.100.240:17020/api/generate"

def clean_text(text):
    text = text.strip().replace("\n","")
    if text.startswith("```json"):
        text = text[len("```json"):]
    if text.endswith("```"):
        text = text[:-len("```")]
    return text

def simple_llm_response(prompt):
    payload = {
        "model":"command-r:latest", #llama3.1:latest",
        "prompt": prompt,
        "stream": False,
        "temperature": 0,
    }
    resp = requests.post(LLM_URL, json=payload)
    return resp.json()["response"]

if __name__ == "__main__":
    print("hello!")