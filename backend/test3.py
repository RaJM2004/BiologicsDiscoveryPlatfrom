from app.utils.file_parsers import _lookup_cids_to_smiles
import requests
url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1736381/property/CanonicalSMILES,IsomericSMILES/JSON"
resp = requests.get(url, timeout=30)
props = resp.json().get("PropertyTable", {}).get("Properties", [])
print('Props list:', props)
smiles_map = {}
for prop in props:
    cid = str(prop.get("CID", ""))
    smiles = prop.get("CanonicalSMILES", "") or prop.get("IsomericSMILES", "")
    if cid and smiles:
        smiles_map[cid] = smiles
print("from script obj:", smiles_map)
