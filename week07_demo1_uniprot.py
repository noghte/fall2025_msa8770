import requests
import pandas as pd

def extract_function(data):
    for c in data.get("comments", []):
        if c.get("commentType") == "FUNCTION":
            return "\n".join(t["value"] for t in c.get("texts", []))
    return "No function annotation found"
    
if __name__ == "__main__":
    df = pd.read_csv("kinase_classification.csv")
    uniprot_ids = df["uniprot"].dropna().unique().tolist()[:20]
    names = []
    functions = []
    for ACC in uniprot_ids:
        url= f"https://rest.uniprot.org/uniprotkb/{ACC}.json"
        r = requests.get(url)
        r.raise_for_status()
        if r.status_code == 200:
            data = r.json()
            print(data)
            names.append(data["proteinDescription"]["recommendedName"]["fullName"]["value"])
            functions.append(extract_function(data))
    df_output = pd.DataFrame({"uniprot": uniprot_ids, "name": names, "function": functions})
    df_output.to_csv("kinase.csv", index=False)
