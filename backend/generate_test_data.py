"""
Generate sample .sdf and .mol2 test files for hit screening.
Run from: backend/
"""
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rdkit import Chem
from rdkit.Chem import AllChem

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_datasets")

MOLECULES = [
    ("CC1=CC=C(C=C1)NC(=O)C2=CC=CC=C2", "GPR35-001"),
    ("OC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2", "GPR35-002"),
    ("CC(=O)NC1=CC=C(C=C1)O", "Acetaminophen"),
    ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "Caffeine"),
    ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "Ibuprofen"),
    ("CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C", "Testosterone"),
    ("OC(=O)C1=CC=CC=C1O", "SalicylicAcid"),
    ("CC(=O)OC1=CC=CC=C1C(=O)O", "Aspirin"),
    ("NC1=NC=NC2=C1N=CN2", "Adenine"),
    ("OC(=O)C1=CC=CC=C1", "BenzoicAcid"),
]

def generate_sdf():
    """Generate a multi-molecule SDF file with 3D coordinates."""
    path = os.path.join(OUTPUT_DIR, "sample_library.sdf")
    writer = Chem.SDWriter(path)
    
    for smiles, name in MOLECULES:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            try:
                AllChem.MMFFOptimizeMolecule(mol)
            except:
                pass
            mol = Chem.RemoveHs(mol)
            mol.SetProp("_Name", name)
            mol.SetProp("ID", name)
            mol.SetProp("Activity", "Active" if hash(name) % 2 == 0 else "Inactive")
            writer.write(mol)
    
    writer.close()
    print(f"✅ Generated SDF: {path}")

def generate_mol2():
    """Generate a multi-molecule MOL2 file with manual block construction."""
    path = os.path.join(OUTPUT_DIR, "sample_library.mol2")
    
    mol2_blocks = []
    for smiles, name in MOLECULES[:5]:  # Use 5 molecules for MOL2
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            try:
                AllChem.MMFFOptimizeMolecule(mol)
            except:
                pass
            
            conf = mol.GetConformer()
            num_atoms = mol.GetNumAtoms()
            num_bonds = mol.GetNumBonds()
            
            block = f"@<TRIPOS>MOLECULE\n{name}\n{num_atoms} {num_bonds}\nSMALL\nNO_CHARGES\n\n"
            block += "@<TRIPOS>ATOM\n"
            for idx in range(num_atoms):
                atom = mol.GetAtomWithIdx(idx)
                pos = conf.GetAtomPosition(idx)
                sym = atom.GetSymbol()
                label = f"{sym}{idx+1}"
                block += f"{idx+1:>7} {label:<5s} {pos.x:>10.4f} {pos.y:>10.4f} {pos.z:>10.4f} {sym:<8s} 1 LIG 0.0000\n"
            
            block += "@<TRIPOS>BOND\n"
            for idx in range(num_bonds):
                bond = mol.GetBondWithIdx(idx)
                bt = "1" if bond.GetBondType() == Chem.BondType.SINGLE else ("2" if bond.GetBondType() == Chem.BondType.DOUBLE else "ar")
                block += f"{idx+1:>6} {bond.GetBeginAtomIdx()+1:>5} {bond.GetEndAtomIdx()+1:>5} {bt}\n"
            
            mol2_blocks.append(block)
    
    with open(path, "w") as f:
        f.write("\n".join(mol2_blocks))
    
    print(f"✅ Generated MOL2: {path}")

def generate_mzml():
    """Generate a minimal mzML-like XML file for LCMS testing."""
    path = os.path.join(OUTPUT_DIR, "sample_lcms.mzml")
    
    content = """<?xml version="1.0" encoding="utf-8"?>
<indexedmzML xmlns="http://psi.hupo.org/ms/mzml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <mzML>
    <run>
      <spectrumList count="3">
        <spectrum index="0" id="scan=1">
          <cvParam name="ms level" value="2"/>
          <cvParam name="molecular formula" value="C8H10N4O2"/>
          <cvParam name="compound name" value="Caffeine"/>
          <precursorList>
            <precursor>
              <selectedIonList>
                <selectedIon>
                  <cvParam name="selected ion m/z" value="195.09"/>
                </selectedIon>
              </selectedIonList>
            </precursor>
          </precursorList>
        </spectrum>
        <spectrum index="1" id="scan=2">
          <cvParam name="ms level" value="2"/>
          <cvParam name="molecular formula" value="C9H8O4"/>
          <cvParam name="compound name" value="Aspirin"/>
          <precursorList>
            <precursor>
              <selectedIonList>
                <selectedIon>
                  <cvParam name="selected ion m/z" value="180.06"/>
                </selectedIon>
              </selectedIonList>
            </precursor>
          </precursorList>
        </spectrum>
        <spectrum index="2" id="scan=3">
          <cvParam name="ms level" value="2"/>
          <cvParam name="molecular formula" value="C13H18O2"/>
          <cvParam name="compound name" value="Ibuprofen"/>
          <precursorList>
            <precursor>
              <selectedIonList>
                <selectedIon>
                  <cvParam name="selected ion m/z" value="206.12"/>
                </selectedIon>
              </selectedIonList>
            </precursor>
          </precursorList>
        </spectrum>
      </spectrumList>
    </run>
  </mzML>
</indexedmzML>
"""
    with open(path, "w") as f:
        f.write(content)
    
    print(f"✅ Generated mzML: {path}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generate_sdf()
    generate_mol2()
    generate_mzml()
    print("\n🎉 All test datasets generated!")
