import requests

url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1736381/property/CanonicalSMILES,IsomericSMILES/JSON"
resp = requests.get(url, timeout=30)
props = resp.json().get("PropertyTable", {}).get("Properties", [])
for p in props:
    print(list(p.keys()))
