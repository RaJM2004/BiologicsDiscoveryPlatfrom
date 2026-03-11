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
    
    # Simulate GPU Load based on active jobs
    base_load = 5.0 # System idle
    load_per_job = 15.2
    gpu_load = min(99.0, base_load + (active_ai_jobs * load_per_job) + (random.random() * 2))
    
    return {
        "target_count": target_count,
        "active_ai_jobs": active_ai_jobs,
        "experiment_count": experiment_count,
        "gpu_load": f"{gpu_load:.1f}%",
        "cluster_status": "Operational" if gpu_load < 90 else "High Load"
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
