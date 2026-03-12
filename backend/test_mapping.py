from app.utils.file_parsers import _resolve_sids_to_cids, _lookup_cids_to_smiles

sids = ["14727734"]
sid_map = _resolve_sids_to_cids(sids)
print("SID Map:", sid_map)
cids = []
for k, v in sid_map.items():
    cids.extend(v)

print("CIDs:", cids)
smiles_map = _lookup_cids_to_smiles(cids)
print("SMILES Map:", smiles_map)

from rdkit import Chem
for cid in cids:
    if cid in smiles_map:
        smiles = smiles_map[cid]
        mol = Chem.MolFromSmiles(smiles)
        print(f"CID {cid} -> SMILES {smiles} -> Mol: {mol}")
    else:
        print(f"CID {cid} not in smiles_map")
