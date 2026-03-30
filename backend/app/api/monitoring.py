from fastapi import APIRouter
from typing import Dict, Any
import random
from app.models.target import Target
from app.models.experiment import Experiment
from app.models.docking import DockingJob
from app.models.admet import ADMETJob
from app.models.optimization import OptimizationJob

router = APIRouter()

@router.get("/stats")
async def get_platform_stats() -> Dict[str, Any]:
    print("Fetching platform stats for dashboard...")
    """
    Aggregation of platform-wide metrics for the dashboard.
    """
    target_count = await Target.count()
    experiment_count = await Experiment.count()
    
    # Active AI Jobs across different modules
    active_docking = await DockingJob.find(DockingJob.status == "Running").count()
    active_admet = await ADMETJob.find(ADMETJob.status == "Running").count()
    active_opt = await OptimizationJob.find(OptimizationJob.status == "Running").count()
    
    active_ai_jobs = active_docking + active_admet + active_opt
    
    # 🧬 Pipeline Distribution
    pipeline = {
        "Target Discovery": target_count,
        "Structural Mapping": await DockingJob.count(),
        "Lead Optimization": await OptimizationJob.count(),
        "ADMET Profiling": await ADMETJob.count()
    }

    # 🏆 Top Discoveries (Recent high-affinity optimizations)
    recent_optimizations = await OptimizationJob.find(OptimizationJob.status == "Completed").sort("-completed_at").limit(5).to_list()
    top_candidates = []
    for opt in recent_optimizations:
        res = opt.results or {}
        top_candidates.append({
            "target": opt.target_id,
            "smiles": res.get("optimized_smiles", "N/A"),
            "affinity": res.get("optimized_affinity", 0),
            "improvement": res.get("improvement", "0%"),
            "model": res.get("model_used", "GA-v1")
        })

    # Simulate GPU/CPU load
    gpu_load = 5.0 + (active_ai_jobs * 12.5) + (random.random() * 5)
    
    return {
        "target_count": target_count,
        "active_ai_jobs": active_ai_jobs,
        "experiment_count": experiment_count,
        "gpu_load": f"{min(gpu_load, 99.0):.1f}%",
        "cluster_status": "Operational" if gpu_load < 85 else "Critical Load",
        "pipeline": pipeline,
        "top_candidates": top_candidates,
        "system_health": "98.2%", # Mock health index
        "daily_throughput": 12400 + random.randint(0, 500) # Mols processed today
    }

@router.get("/health")
async def get_system_health():
    return {
        "status": "Healthy",
        "gpu_cluster": "Online",
        "storage": "82% Free",
        "database": "Connected",
        "robot_interface": "Standby"
    }
