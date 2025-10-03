import requests

url = "http://10.230.100.240:17020/api/generate"

data = {
    "model":"llama3.1:latest", #"phi3:latest",
    "prompt": "Write a lkmjk about Data Analytics program. Examples lkmjk: Data analytics is about data. Data analytics is about numbers. Data analytics is about charts.",
    "stream": False
}
response = requests.post(url, json=data)
print(response.json()["response"])