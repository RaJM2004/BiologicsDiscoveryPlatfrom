from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.preformulation import PreformulationReport
from app.utils.drug_development import calculate_preformulation_properties
from pydantic import BaseModel

router = APIRouter()

class PreformulationRequest(BaseModel):
    compound_id: str
    smiles: str

@router.post("/analyze", response_model=PreformulationReport)
async def analyze_preformulation(request: PreformulationRequest):
    properties = calculate_preformulation_properties(request.smiles)
    if not properties:
        raise HTTPException(status_code=400, detail="Invalid SMILES string")
    
    report = PreformulationReport(
        compound_id=request.compound_id,
        smiles=request.smiles,
        **properties
    )
    await report.insert()
    return report

@router.get("/reports", response_model=List[PreformulationReport])
async def get_all_reports():
    return await PreformulationReport.find_all().to_list()

@router.get("/report/{compound_id}", response_model=PreformulationReport)
async def get_report(compound_id: str):
    report = await PreformulationReport.find_one(PreformulationReport.compound_id == compound_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
