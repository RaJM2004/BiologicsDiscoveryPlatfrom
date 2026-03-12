import requests
import json

url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/sid/14727734/property/CanonicalSMILES/JSON"
try:
    resp = requests.get(url)
    print("Status:", resp.status_code)
    print("Response:", resp.json())
except Exception as e:
    print(e)
