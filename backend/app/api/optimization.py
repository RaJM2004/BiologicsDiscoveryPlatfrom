from fastapi import APIRouter, BackgroundTasks
from app.models.optimization import OptimizationJob
from typing import List
import asyncio
import random
import numpy as np
import pickle
import os
from datetime import datetime
from rdkit import Chem
from rdkit.Chem import AllChem

router = APIRouter()

# Load Model for Scoring
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_models", "binding_affinity_model.pkl")
AI_MODEL = None
try:
    with open(MODEL_PATH, "rb") as f:
        AI_MODEL = pickle.load(f)
except:
    pass

from app.utils.cheminformatics import calculate_molecular_properties

# --- EVOLUTIONARY STRATEGIES ---

def mutate_molecule(mol):
    """
    Applies a random structural mutation to an RDKit Mol object.
    Mutations include adding atoms (C, H, O), removing atoms, changing bonds,
    and swapping atom types to generate diverse SAR insights.
    Returns (new_mol, mutation_description) or (None, None) if failed.
    """
    if mol is None: return None, None

    # Map of atom types used in mutations: atomic_number -> symbol
    ATOM_CHOICES = [
        (6, "Carbon"),
        (1, "Hydrogen"),
        (8, "Oxygen"),
    ]

    try:
        rw_mol = Chem.RWMol(mol)
        
        mutation_type = random.choice([
            "add_atom", "add_atom",       # weighted: additions are common
            "remove_atom",
            "change_bond",
            "swap_atom",                   # heteroatom substitution
        ])
        desc = "Unknown mutation"
        
        if mutation_type == "add_atom":
            if rw_mol.GetNumAtoms() > 0:
                idx = random.choice(range(rw_mol.GetNumAtoms()))
                atom_sym = rw_mol.GetAtomWithIdx(idx).GetSymbol()
                # Randomly pick from Carbon, Hydrogen, or Oxygen
                new_atomic_num, new_name = random.choice(ATOM_CHOICES)
                new_idx = rw_mol.AddAtom(Chem.Atom(new_atomic_num))
                rw_mol.AddBond(idx, new_idx, Chem.BondType.SINGLE)
                desc = f"Added {new_name} to {atom_sym}{idx}"
            else:
                return None, None
            
        elif mutation_type == "remove_atom":
            if rw_mol.GetNumAtoms() > 5:
                # Find atoms with degree 1 (terminal atoms)
                tips = [a.GetIdx() for a in rw_mol.GetAtoms() if a.GetDegree() == 1]
                if tips:
                    idx_to_remove = random.choice(tips)
                    atom_sym = rw_mol.GetAtomWithIdx(idx_to_remove).GetSymbol()
                    rw_mol.RemoveAtom(idx_to_remove)
                    desc = f"Removed terminal {atom_sym} atom"
                else:
                    return None, None
            else:
                return None, None

        elif mutation_type == "swap_atom":
            # Swap an existing atom's element to explore heteroatom effects
            if rw_mol.GetNumAtoms() > 2:
                eligible = [a for a in rw_mol.GetAtoms() if a.GetSymbol() in ("C", "O", "N")]
                if eligible:
                    atom = random.choice(eligible)
                    old_sym = atom.GetSymbol()
                    # Pick a different element from C/H/O
                    swap_choices = [(n, name) for n, name in ATOM_CHOICES if n != atom.GetAtomicNum()]
                    new_atomic_num, new_name = random.choice(swap_choices)
                    atom.SetAtomicNum(new_atomic_num)
                    desc = f"Swapped {old_sym}{atom.GetIdx()} → {new_name}"
                else:
                    return None, None
            else:
                return None, None
                    
        elif mutation_type == "change_bond":
             if rw_mol.GetNumBonds() > 0:
                 b = random.choice(list(rw_mol.GetBonds()))
                 a1 = b.GetBeginAtom().GetSymbol() + str(b.GetBeginAtomIdx())
                 a2 = b.GetEndAtom().GetSymbol() + str(b.GetEndAtomIdx())
                 if b.GetBondType() == Chem.BondType.SINGLE:
                     b.SetBondType(Chem.BondType.DOUBLE)
                     desc = f"Changed bond {a1}-{a2} to DOUBLE"
                 else:
                     b.SetBondType(Chem.BondType.SINGLE)
                     desc = f"Changed bond {a1}={a2} to SINGLE"
             else:
                 return None, None
                     
        Chem.SanitizeMol(rw_mol)
        return rw_mol, desc
        
    except:
        return None, None

from app.utils.cheminformatics import calculate_molecular_properties, extract_features

def score_molecule(smiles):
    """
    Scores a molecule using the XGBoost model and penalizes for synthetic difficulty.
    """
    props = calculate_molecular_properties(smiles)
    if not props: return -10.0
    
    # Generate 2400+ scientific features (Morgan FP + MACCS + Descriptors)
    features = extract_features(smiles).reshape(1, -1)
    
    score = -5.0 # Baseline
    if AI_MODEL:
        try:
            # Predict pIC50
            score = float(AI_MODEL.predict(features)[0])
        except Exception as e:
            print(f"Scoring Error: {e}")
            pass
    
    # 🧪 SCIENTIFIC RIGOR: Synthetic Accessibility Penalty
    # SA Score: 1-10 (1=Easy, 10=Impossible)
    # Penalize anything above 5.0 to steer the GA away from 'impossible' molecules
    sa = props.get("SA_Score", 5.0)
    if sa > 5.0:
        penalty = (sa - 5.0) * 0.4
        score -= penalty
        
    return round(score, 2)

from app.utils.websockets import manager

async def run_generative_optimization(job_id: str):
    """
    Runs a Genetic Algorithm to evolve the molecule.
    """
    # Start with a Seed based on target or default
    current_smiles = "CN1C=NC2=C1C(=O)N(C(=O)N2C)C" # Caffeine default
    current_mol = Chem.MolFromSmiles(current_smiles)
    
    best_smiles = current_smiles
    best_score = score_molecule(current_smiles)
    original_score = best_score
    
    await manager.broadcast(f"🧬 [BitGA] Starting Evolution. Baseline Score: {best_score:.2f}", job_id)
    
    generations = 15
    population_size = 8
    
    modifications_log = []
    sar_insights = [] # Track structural mutations and their effect on affinity
    
    for gen in range(generations):
        # 1. Mutate
        candidates = []
        for _ in range(population_size):
            mutated, desc = mutate_molecule(current_mol)
            if mutated:
                try:
                    candidates.append((Chem.MolToSmiles(mutated), desc))
                except: pass
        
        # 2. Score
        scored_candidates = []
        parent_score = score_molecule(Chem.MolToSmiles(current_mol))
        
        for smi, desc in candidates:
             s = score_molecule(smi)
             scored_candidates.append((s, smi, desc))
             
             # Log SAR
             delta = s - parent_score
             impact = "Positive" if delta > 0.1 else ("Negative" if delta < -0.1 else "Neutral")
             sar_insights.append({
                 "mutation": desc,
                 "affinity_change": round(delta, 2),
                 "impact": impact
             })
             
        # 3. Select Best
        if not scored_candidates: continue
        
        scored_candidates.sort(reverse=True, key=lambda x: x[0])
        gen_best_score, gen_best_smiles, gen_best_desc = scored_candidates[0]
        
        if gen_best_score > best_score:
            await manager.broadcast(f"  > Gen {gen}: New Best {gen_best_score:.2f} ({gen_best_desc})", job_id)
            best_score = gen_best_score
            best_smiles = gen_best_smiles
            current_mol = Chem.MolFromSmiles(best_smiles)
            modifications_log.append(gen_best_desc)
        else:
             if gen % 5 == 0:
                 await manager.broadcast(f"  > Gen {gen}: Exploring...", job_id)
            
        await asyncio.sleep(0.2) # Yield to event loop + simulate work
    
    # Process SAR Analysis
    sar_insights.sort(key=lambda x: x["affinity_change"], reverse=True)
    seen_muts = set()
    unique_sar = []
    for insight in sar_insights:
        if insight["mutation"] not in seen_muts:
            seen_muts.add(insight["mutation"])
            unique_sar.append(insight)
            
    top_positive = [s for s in unique_sar if s["affinity_change"] > 0][:5]
    top_negative = [s for s in unique_sar if s["affinity_change"] < 0][-5:]
    overall_sar = top_positive + top_negative
    
    # Final Result
    improvement_pct = int(((best_score - original_score) / abs(original_score)) * 100) if original_score != 0 else 0
    await manager.broadcast(f"✅ Optimization Complete. Improvement: {improvement_pct}%", job_id)
    
    results = {
        "original_affinity": round(original_score, 2),
        "optimized_affinity": round(best_score, 2),
        "improvement": f"{improvement_pct}%",
        "modifications": modifications_log[:5] or ["Structural Refinement"],
        "sar_analysis": overall_sar,
        "optimized_smiles": best_smiles,
        "model_used": "GeneticAlgorithm-XGBoost",
        "generated_at": datetime.now().isoformat(),
    }
    
    # Update DB
    job = await OptimizationJob.get(job_id)
    if job:
        job.status = "Completed"
        job.results = results
        job.completed_at = datetime.now()
        await job.save()

@router.post("/run", response_model=OptimizationJob)
async def run_optimization(target_id: str, constraints: dict, background_tasks: BackgroundTasks):
    job = OptimizationJob(target_id=target_id, constraints=constraints, status="Running", results=None)
    await job.insert()
    
    # Dispatch GenAI Task
    background_tasks.add_task(run_generative_optimization, job.id)
    
    return job

@router.get("/{job_id}", response_model=OptimizationJob)
async def get_optimization_job(job_id: str):
    job = await OptimizationJob.get(job_id)
    return job

@router.get("/", response_model=List[OptimizationJob])
async def get_optimizations():
    return await OptimizationJob.find_all().sort("-created_at").to_list()
