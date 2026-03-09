from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, rdMolDescriptors

def calculate_molecular_properties(smiles: str):
    """
    Parses a SMILES string and returns calculated physicochemical properties.
    Returns None if the SMILES is invalid.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return None
        
        props = {
            "MolWt": round(Descriptors.MolWt(mol), 2),
            "LogP": round(Descriptors.MolLogP(mol), 2),
            "NumHDonors": Lipinski.NumHDonors(mol),
            "NumHAcceptors": Lipinski.NumHAcceptors(mol),
            "RotatableBonds":Descriptors.NumRotatableBonds(mol),
            "TPSA": round(Descriptors.TPSA(mol), 2),
            "IsLipinskiCompliant": False
        }

        # Check Lipinski's Rule of 5
        # MW <= 500, LogP <= 5, H-Donors <= 5, H-Acceptors <= 10
        if (props["MolWt"] <= 500 and props["LogP"] <= 5 and 
            props["NumHDonors"] <= 5 and props["NumHAcceptors"] <= 10):
            props["IsLipinskiCompliant"] = True
            
        return props
    except Exception as e:
        print(f"Error calculating properties for {smiles}: {e}")
        return None
