# Strategic Guidance: Quantum-AI PIN1 Platform

Based on the strategic vision and a comprehensive audit of the current codebase in `backend/app`, here is the technical assessment and execution strategy.

## 1. System Requirements & Infrastructure
To transition from the current MVP to a production-grade Quantum-AI platform, the following stack is required:

### A. Compute Infrastructure (AI & Classical)
- **Training Cluster**: NVIDIA A100 or H100 GPU nodes (8x multi-pair) for training Diffusion and GNN models (Layer 5).
- **Inference/Docking**: CPU/GPU hybrid cluster. Classical docking (AutoDock Vina) is CPU-bound but massively parallelizable via **Kubernetes**.
- **Model Registry**: **MLFlow** or **Weights & Biases** for experiment tracking (currently missing).
- **Workflow Orchestration**: **Apache Airflow** or **Prefect** to manage the "collaboration workflow" (1 → 8).

### B. Personal Workstation Recommendations (Local Development)
For designers and developers without existing GPU hardware, the following systems are recommended to support local model orchestration and quantum simulation:

| Tier | Recommended Model | Key Specs | Price Range |
| :--- | :--- | :--- | :--- |
| **Ultimate AI** | **MacBook Pro 16" (M4 Max)**| 128GB Unified Memory, 40-Core GPU | ~$4,500 - $5,500 |
| **CUDA Power** | **ASUS ROG Zephyrus G16** | RTX 5090 (16GB), 64GB RAM, OLED | ~$3,500 - $4,200 |
| **Professional** | **Dell Precision 7680** | RTX 2000 Ada, 32GB RAM, i9-13th Gen | ~$2,400 - $3,000 |
| **Entry AI** | **MacBook Air 15" (M3)** | 24GB RAM, 1TB SSD (Portable) | ~$1,800 - $2,200 |

> [!NOTE]
> High unified memory (Apple) or high VRAM (NVIDIA) is critical for running large structural models (AlphaFold) or quantum simulators locally.

### C. Quantum Infrastructure
- **Frameworks**: Qiskit (Python-based) for circuit design.
- **Runtime**: Hybrid Quantum-Classical architecture using **Qiskit Runtime** for low-latency iterations.
- **Hardware**: Access to **IBM Quantum (Eagle/Osprey)** or **Azure Quantum**.

## 2. Code Readiness Audit
The current implementation is an **Advanced MVP (Level 2-3)**. 

| Layer | Status | Code Reference | Gap Analysis |
| :--- | :--- | :--- | :--- |
| **Layer 4: Structural** | ✅ Ready | `alphafold_service.py` | Basic metadata fetching; needs AlphaFold-Multimer integration. |
| **Layer 5: GenAI** | ⚠️ Alpha | `optimization.py` | Uses GA (Genetic Algorithm). Needs Diffusion/Transformer upgrade. |
| **Layer 6: Screening** | ✅ Ready | `screening.py` | Functional XGBoost screening. Needs physical docking post-inference. |
| **Layer 7: Quantum** | ❌ **Missing** | N/A | No Qiskit or VQE implementation found. |
| **Layer 8: ADMET** | ⚠️ Alpha | `admet.py` | Heuristic-based. Needs ensemble deep learning models. |

> [!IMPORTANT]
> **Can the current code run the platform?**
> Partially. It can perform early-stage hit discovery and lead optimization, but it **cannot** perform quantum validation or systems biology simulation without new module development.

## 3. Quantum Impact Analysis

### A. Speed & Accuracy (VQE vs Classical)
Classical docking uses "Scoring Functions" (Energy Grids). Quantum Molecular Simulation focuses on Electronic Structure.
- **Classical (AutoDock Vina)**: ~1-5 seconds per pose. High false-positives.
- **Quantum (VQE Refinement)**: ~10-30 minutes per molecule (on simulators) or few seconds on hardware + queue time.
- **The Speedup**: Quantum doesn't make discovery "faster" in seconds; it makes it "faster" in **success rate**. High-precision binding energy prevents late-stage clinical failures.

### B. Approximate Cost (Model-Wise)
*Estimates based on IBM Quantum Premium Access.*

| Task | Quantum Model | Estimated Cost | Hardware Need |
| :--- | :--- | :--- | :--- |
| **Binding Refinement** | VQE (Variational Quantum Eigensolver) | ~$150 - $400 / molecule | 20+ Error-Corrected Qubits |
| **Vibrational Analysis** | QPE (Quantum Phase Est.) | ~$1k+ / molecule | High-fidelity depth (Future) |
| **SAR Optimization** | Quantum GNN | ~$50 / optimization step | Noisy Intermediate-Scale (NISQ) |

## 4. Infrastructure Costing & Financial Projections
*Estimated figures for 2026 Cloud-Native discovery workloads.*

### A. Monthly Infrastructure OpEx (Classical/AI)
| Item | Unit | Estimated Cost | Total (Moderate Usage) |
| :--- | :--- | :--- | :--- |
| **GPU Compute (8x H100)** | per Hour | $25 - $35 | ~$18k - $25k / mo |
| **Worker Nodes (CPU)** | per Cluster | $2.5k / mo | $2.5k / mo |
| **K8s Control Plane** | per Month | $75 | $75 |
| **Storage (Bio-Datasets)** | per TB | $25 (Object) | $250 (10TB) |
| **Total Baseline** | | | **~$21k - $28k / mo** |

> [!TIP]
> Use **Spot Instances** for large virtual screening batches to reduce GPU costs by up to 60-70%.

### B. Quantum Validation Costs (Per Discovery Milestone)
*Milestone: High-precision refinement of Top 20 Candidates.*

| Service | Model | Cost per Run | Total Project Cost |
| :--- | :--- | :--- | :--- |
| **IBM Quantum** | Flex Plan (VQE) | $72 / min | ~$14.4k (200 mins) |
| **Azure Quantum** | IonQ Tokens | $97.50 min/exec | ~$2k (Per Batch) |

## 5. Summary: High-Level Investment Required
- **MVP Phase (Current)**: ~$500 - $2k / mo (Low-tier GPUs + Free Tier K8s).
- **Scale Phase (Active Discovery)**: ~$30k - $50k / mo (Full GPU Cluster + Quantum Validation).
- **Enterprise Phase**: $500k+ / Annual reserved capacity with direct Quantum partnership.

## 6. Strategic Implementation Roadmap
1.  **Initialize Layer 7**: Create `backend/app/services/quantum_service.py` using Qiskit.
2.  **Hybrid Workflow**: Modify `optimization.py` to call `quantum_service.refine_pose()` for the top 10 candidates found by the Genetic Algorithm.
3.  **Deploy on Cloud**: Move the local FastAPI server to a Dockerized Kubernetes environment to support asynchronous compute-heavy tasks.
