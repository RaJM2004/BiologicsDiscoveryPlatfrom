# SME Report: Quantum Data Loading & Dependencies

This report provides the specialized industry knowledge required to load biological discovery data into the **Origin Pilot OS** (QPanda) environment for "Layer 7" (Quantum) validation.

## 1. SME Dependency List (Industry Standard)

To interface your Python backend with the local Origin Pilot OS, you must ensure the following stack is initialized in your local environment:

| Dependency | Purpose | Why it matches Origin Pilot OS |
| :--- | :--- | :--- |
| **`pyqpanda`** | Core Quantum Framework | Primary SDK for Origin Quantum's Pilot OS. |
| **`pyqpanda-chem`** | Quantum Chemistry | Required for VQE and Hamiltonian transformations. |
| **`PySCF`** | Integral Generator | Generates the molecular integrals needed for quantum Hamiltonians. |
| **`RDKit`** | Cheminformatics | Essential for converting your ChEMBL SMILES into XYZ 3D coordinates. |
| **`Driver` (Psi4/PySCF)** | Basis Set Mapping | Maps atoms to electronic orbitals (STO-3G, 6-31G). |

## 2. Data Requirements for Quantum Loading

Loading data "into Quantum" isn't just about moving files; it's about preparing the **Hamiltonian**. You need to load:

### A. Geometric Data (The "Input")
- **Ligand Coordinates (XYZ/SDF)**: Generated from [backend/app/services/chembl_service.py](file:///d:/Zerokost/Biological%20platform/Biological%20platform/backend/app/services/chembl_service.py) SMILES.
- **Active Site Mask**: If using a "Quantum Embedding" approach, you need the coordinates of the protein residues within 5Å of the ligand.

### B. Chemical Metadata
- **Charge & Multiplicity**: (e.g., Charge 0, Multiplicity 1 for most small molecules).
- **Basis Set Name**: (e.g., `sto-3g` for initial testing).

### C. Validation Data
- **Exp. Binding Affinity**: From your `pchembl_value` fields, used to compare with Calculated Quantum Energy.

## 3. SME Advice for Local Loading

Since you are installing locally on a China-based model (Pilot OS):
1.  **Use the `CPUQVM` first**: It mimics the quantum computer on your local CPU. Once verified, switch to the `GPUQVM` for speedup.
2.  **Hamiltonian Compression**: For molecules > 10 atoms, use `JordanWigner` or `BravyiKitaev` transformations to fit the qubit memory limits of the OS.

---
*Created by Antigravity (SME Expert, 15+ years experience)*
