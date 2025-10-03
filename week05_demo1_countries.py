import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_countries_from_wikipedia():
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-G991W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"
    }
    url = "https://en.wikipedia.org/wiki/List_of_sovereign_states"
    r = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(r.text, "html.parser")
    countries = []
    for table in soup.select("table.wikitable"):
        for link in table.select("td b a"):
            name = link.get_text(strip=True)
            if name and name not in countries:
                countries.append(name)

    return countries

if __name__ == "__main__":
    countries = get_countries_from_wikipedia()
    df = pd.DataFrame(countries, columns=["Country"])
    print("Countries:", len(countries))
    df.to_csv("countries.csv", index=None)