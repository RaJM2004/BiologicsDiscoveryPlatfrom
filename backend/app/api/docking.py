from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.docking import DockingJob
from app.utils.websockets import manager
import asyncio
import random
from datetime import datetime
from typing import List

router = APIRouter()

async def run_docking_simulation(job_id: str):
    """
    Simulates a molecular docking session using AutoDock Vina logic.
    In a real scenario, this would involve:
    1. Converting SMILES to PDBQT (OpenBabel)
    2. Preparing Receptor (Target) PDBQT
    3. Running `vina` subprocess
    4. Parsing Log files for Delta G (kcal/mol)
    """
    job = await DockingJob.get(job_id)
    if not job: return

    job.status = "Running"
    await job.save()

    await manager.broadcast(f"📂 [Docking] Initializing Receptor-Ligand systems for job {job_id[:8]}...", job_id)
    await asyncio.sleep(1.5)

    await manager.broadcast(f"⚙️ [Docking] Generating conformers for ligand: {job.ligand_smiles[:20]}...", job_id)
    await asyncio.sleep(2)

    await manager.broadcast("🧬 [Docking] Running AutoDock Vina Monte Carlo Search...", job_id)
    
    # Simulate iterations
    for i in range(1, 6):
        score = -6.0 - (random.random() * 4) # Random score between -6 and -10
        await manager.broadcast(f"   > Iteration {i}: Lowest Binding Energy = {score:.2f} kcal/mol", job_id)
        await asyncio.sleep(1)

    final_score = -7.5 - (random.random() * 2.5)
    
    results = {
        "binding_energy": round(final_score, 2),
        "unit": "kcal/mol",
        "pose_count": 9,
        "rmsd_lb": 0.0,
        "rmsd_ub": 0.0,
        "efficiency": round(abs(final_score) / 20, 3) # Mock efficiency
    }

    job.status = "Completed"
    job.results = results
    job.completed_at = datetime.now()
    await job.save()

    await manager.broadcast(f"✅ [Docking] Complete! Best Affinity: {final_score:.2f} kcal/mol", job_id)

@router.post("/run", response_model=DockingJob)
async def start_docking(target_id: str, smiles: str, background_tasks: BackgroundTasks):
    job = DockingJob(target_id=target_id, ligand_smiles=smiles, status="Pending")
    await job.insert()
    
    background_tasks.add_task(run_docking_simulation, str(job.id))
    return job

@router.get("/{job_id}", response_model=DockingJob)
async def get_docking_job(job_id: str):
    job = await DockingJob.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/", response_model=List[DockingJob])
async def list_docking_jobs():
    return await DockingJob.find_all().sort("-created_at").to_list()
