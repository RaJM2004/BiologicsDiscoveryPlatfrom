import requests

url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1736381/property/CanonicalSMILES/JSON"
resp = requests.get(url)
print(resp.json())

props = resp.json().get("PropertyTable", {}).get("Properties", [])
print('Props:', props)
smiles_map = {}
for prop in props:
    cid = str(prop.get("CID", ""))
    smiles = prop.get("CanonicalSMILES", "")
    print(f"Prop CID: '{cid}'")
    print(f"Prop SMILES: '{smiles}'")
    if cid and smiles:
        smiles_map[cid] = smiles

print("Resulting Map:", smiles_map)
