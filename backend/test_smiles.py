import requests

url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1736381/property/CanonicalSMILES,IsomericSMILES/JSON"
resp = requests.get(url)
print(resp.json())
