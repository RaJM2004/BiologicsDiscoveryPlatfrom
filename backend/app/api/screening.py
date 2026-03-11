from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from app.models.screening import ScreeningJob
from typing import List
import asyncio
import os
import shutil
import pickle
import numpy as np
from datetime import datetime
from app.utils.cheminformatics import calculate_molecular_properties
from app.utils.file_parsers import parse_molecules
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, MACCSkeys, Descriptors

# Disable RDKit C++ backend warnings (hides the MorganGenerator terminal spam)
RDLogger.DisableLog('rdApp.*')

router = APIRouter()

# --- REAL AI INFERENCE ENGINE ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_models", "binding_affinity_model.pkl")
AI_MODEL = None

try:
    with open(MODEL_PATH, "rb") as f:
        AI_MODEL = pickle.load(f)
    print("✅ Logic: XGBoost Model Loaded Successfully")
except Exception as e:
    print(f"⚠️ Warning: perform 'python train_ai_model.py' first. Using mock mode. {e}")

from app.utils.websockets import manager

async def run_ai_screening_task(job_id: str, file_path: str):
    """
    Parses the uploaded file (multi-format) and runs inference on every molecule.
    Supported formats: .smi, .sdf, .mol2, .csv, .mzml, .mzxml
    """
    hits = []
    
    # Parse molecules using the multi-format parser
    try:
        parsed_molecules = parse_molecules(file_path)
    except Exception as e:
        await manager.broadcast(f"❌ Error parsing file: {e}", job_id)
        return

    if not parsed_molecules:
        await manager.broadcast(f"❌ No valid molecules found in uploaded file.", job_id)
        return

    await manager.broadcast(f"🧪 [Job {job_id}] Screening {len(parsed_molecules)} molecules...", job_id)

    processed_count = 0
    for mol_entry in parsed_molecules:
        smiles = mol_entry["smiles"]
        mol_id = mol_entry["mol_id"]
        
        # 1. Calculate Properties (RDKit)
        props = calculate_molecular_properties(smiles)
        if not props:
            # await manager.broadcast(f"⚠️ Invalid SMILES: {smiles[:10]}...", job_id)
            continue # Invalid SMILES
            
        # 2. Prepare Features for the New 2400+ Parameter Model
        try:
            mol = Chem.MolFromSmiles(smiles)
            if not mol:
                continue

            fp_morgan = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
            arr_morgan = np.zeros((0,), dtype=np.int8)
            Chem.DataStructs.ConvertToNumpyArray(fp_morgan, arr_morgan)

            fp_maccs = MACCSkeys.GenMACCSKeys(mol)
            arr_maccs = np.zeros((0,), dtype=np.int8)
            Chem.DataStructs.ConvertToNumpyArray(fp_maccs, arr_maccs)

            desc_keys = [d[0] for d in Descriptors.descList]
            arr_desc = np.zeros(len(desc_keys))
            for i, (name, func) in enumerate(Descriptors.descList):
                try:
                    val = func(mol)
                    arr_desc[i] = val if not np.isnan(val) and not np.isinf(val) else 0.0
                except:
                    arr_desc[i] = 0.0

            features = np.concatenate((arr_morgan, arr_maccs, arr_desc))
            features = features.reshape(1, -1) # XGBoost expects 2D array
        except Exception as e:
            await manager.broadcast(f"Featurization Error: {e}", job_id)
            continue
            
        # 3. Predict Real Binding Affinity
        score = -5.0
        conf = 0.0
        
        if AI_MODEL:
            try:
                raw_score = AI_MODEL.predict(features)[0]
                score = round(float(raw_score), 2)
                conf = min(0.99, abs(score)/12.0)
            except Exception as e:
                print(f"Inference Error: {e}")
        
        hits.append({
            "molecule_id": mol_id,
            "smiles": smiles,
            "properties": props,
            "affinity": score,
            "confidence": round(conf, 2)
        })
        processed_count += 1
        
        if processed_count % 5 == 0:
            await manager.broadcast(f"Processing... {processed_count}/{len(parsed_molecules)}", job_id)
            await asyncio.sleep(0.01)
    
    # Sort by affinity (High to Low for pIC50)
    hits.sort(key=lambda x: x["affinity"], reverse=True)
    top_hits = hits[:100] # Keep top 100 to save DB space

    # Update Job
    job = await ScreeningJob.get(job_id)
    if job:
        job.status = "Completed"
        job.results = {
            "hits_found": len(hits), 
            "top_hits": top_hits, 
            "model_used": "XGBoost-Real-v1" if AI_MODEL else "Fallback"
        }
        job.completed_at = datetime.now()
        await job.save()
        
    await manager.broadcast(f"✅ Screening Complete. Found {len(hits)} hits.", job_id)
        
    # Cleanup temp file
    if os.path.exists(file_path):
        os.remove(file_path)


@router.post("/run", response_model=ScreeningJob)
async def run_screening(
    target_id: str, 
    library_id: str, # Just a name tag now
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # 1. Save file to disk (preserve original extension for format detection)
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    original_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".smi"
    file_path = os.path.join(temp_dir, f"{library_id}_{int(datetime.now().timestamp())}{original_ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Create Job
    job = ScreeningJob(target_id=target_id, library_id=library_id, status="Running")
    await job.insert()
    
    # 3. Dispatch Task
    background_tasks.add_task(run_ai_screening_task, job.id, file_path)
    
    return job

@router.get("/", response_model=List[ScreeningJob])
async def get_screenings():
    return await ScreeningJob.find_all().sort("-created_at").to_list()

