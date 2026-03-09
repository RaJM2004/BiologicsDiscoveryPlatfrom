from typing import List, Optional
from beanie import Document
from pydantic import BaseModel
from datetime import datetime

class TargetProperties(BaseModel):
    molecular_weight: Optional[float] = None
    solubility: Optional[str] = None
    affinity: Optional[float] = None # e.g. Kd value

class Target(Document):
    name: str
    type: str # e.g., "Protein", "Antibody", "Small Molecule"
    uniprot_id: Optional[str] = None
    sequence: Optional[str] = None # Amino acid or nucleotide sequence
    description: Optional[str] = None
    properties: Optional[dict] = None
    pdb_ids: List[str] = []
    alphafold_url: Optional[str] = None
    known_ligands: List[dict] = []
    status: str = "Candidate" # Candidate, Screened, Validated, Rejected
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "targets"
