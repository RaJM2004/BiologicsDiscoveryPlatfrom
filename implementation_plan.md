# Quantum Integration Plan (Origin Pilot OS / QPanda)

This plan outlines the steps to integrate local quantum simulation capabilities using the **Origin Pilot OS** (QPanda framework) into the existing Biologics Discovery Platform.

## User Review Required

> [!IMPORTANT]
> Since you are using **Origin Pilot OS** (developed by Origin Quantum), we will utilize the **QPanda** framework instead of Qiskit for local compatibility.
> 
> **Action Required**: Please confirm if you have the `pyqpanda` library installed in your local Python environment.

## Proposed Changes

### [Backend] Quantum Service Layer

#### [NEW] [quantum_service.py](file:///d:/Zerokost/Biological%20platform/Biological%20platform/backend/app/services/quantum_service.py)
Create a new service to handle quantum molecular simulations.
- **Goal**: Implement a Variational Quantum Eigensolver (VQE) wrapper using `pyqpanda`.
- **Inputs**: Molecular structure (SMILES/XYZ), Basis set selection.
- **Output**: Refined ground state energy / Binding affinity score.

### [Backend] Integration with Optimization

#### [MODIFY] [optimization.py](file:///d:/Zerokost/Biological%20platform/Biological%20platform/backend/app/services/optimization.py)
- Integrate `quantum_service` to allow "Layer 7" validation for top-tier lead candidates.

## Data SME: Required Data for Quantum Loading

To perform accurate quantum discovery, you must load the following data into the Quantum workspace:

1.  **Structural Data**: 
    - **SMILES**: For small molecule identity.
    - **PDB/SDF**: 3D coordinates of the ligand and protein active site (crucial for Hamiltonians).
2.  **Quantum Chemistry Parameters**:
    - **Basis Sets**: (e.g., STO-3G for speed, 6-31G* for accuracy).
    - **Active Space**: Number of electrons and orbitals to include in the simulation.
3.  **Hamiltonian Data**: Generated from the molecular geometry via `pyqpanda-chem` or similar utilities.

## Local Installation Guide (Origin Pilot OS)

1.  **Environment Setup**:
    ```bash
    pip install pyqpanda
    ```
2.  **Quantum Cluster Connection**:
    - If running on a local Origin Pilot OS cluster, ensure the `QCloud` or local `CPUQVM` / `GPUQVM` is initialized.
3.  **Driver Dependencies**:
    - Ensure `psi4` or `PySCF` is installed if you need to generate molecular integrals for the quantum simulation.

## Verification Plan

### Automated Tests
- Run `pytest backend/tests/test_quantum_service.py` (to be created) using a `CPUQVM` simulator.

### Manual Verification
- Verify that a sample SMILES (e.g., Caffeine/Water) can undergo a basic energy calculation without errors.
