import json
import requests
from helpers import clean_text, LLM_URL, simple_llm_response

def get_weather(location,day):
    r = requests.get(f"https://wttr.in/{location}" , params={"format": "j1"}, timeout=20)
    if r.status_code != 200:
        return {"error": "service unavailable"}
    
    if day.strip().lower() == "tomorrow":
        idx = 1
    else:
        idx = 0
   
    data = r.json()
    d = data.get("weather", [])[idx]
    return {
        "location": location,
        "day": day,
        "high": d.get("maxtempF"),
        "low": d.get("mintempF"),
        "avg": d.get("avgtempF"),
    }


function_schema = """
You are a function-calling assistant.
Return ONLY a JSON object like this:
{
    "function": "get_weather",
    "arguments": {
        "location": string, //e.g., Atlanta
        "day": "today" | "tomorrow"
    }
}

Do not add explanations, extra text, or markdown.
"""

user_request = "What's the weather in Atlanta tomorrow?"

payload = {
    "model":"command-r:latest", #llama3.1:latest",
    "prompt": f"{function_schema}\n\nUser request: {user_request}",
    "stream": False,
    "temperature": 0,
}

resp = requests.post(LLM_URL, json=payload)
raw_response = resp.json()["response"]


parsed = json.loads(clean_text(raw_response))

if parsed.get("function") == "get_weather":
    args = parsed.get("arguments", {})
    location = args.get("location", "Atlanta")
    day = args.get("day", "today")

    result = get_weather(location,day)
    print("Result:")
    str_weather_info = json.dumps(result, indent=2)
    print(str_weather_info)
    print(simple_llm_response(f"Write an interesting weather report based on the following data \n{str_weather_info} "))