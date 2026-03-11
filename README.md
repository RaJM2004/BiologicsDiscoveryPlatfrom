# 🧬 Biologics Discovery Platform

An advanced, production-grade AI drug discovery platform designed for pharmaceutical scientists. This platform accelerates the drug discovery pipeline from identifying protein targets to screening millions of compounds using cheminformatics and machine learning.

![Platform Banner](https://upload.wikimedia.org/wikipedia/commons/2/23/DNA_Orbit_Animated.gif) <!-- Placeholder for actual UI screenshot -->

## 🚀 Key Features

*   **Target Discovery (Neural-Bio Interface):** Instantly resolve gene symbols (e.g., EGFR, TP53) to UniProt primary accessions. Automatically fetches genomic sequences, verified 3D structures from **RCSB PDB**, and seamlessly falls back to **AlphaFold** `.cif` predictions when crystal structures are unavailable.
*   **Virtual Hit Screening (Multi-Format):** Accepts diverse scientific data formats (`.smi`, `.sdf`, `.mol2`, `.csv`, `.json` BioAssay, `.mzml` LCMS) and screens them seamlessly. Converts compounds into 2400+ dimensional mathematical features to predict binding affinities (pIC50) using an optimized **XGBoost Regressor**.
*   **Molecular Visualization:** Fully interactive embedded 3D molecule viewing (via `3Dmol.js`), rendering PDB structures and AlphaFold Confidence Arrays directly within the UI.
*   **Lead Optimization:** Evolutionary Generative AI strategies (mutations like heteroatom swaps, additions) for bio-realistic SAR analysis.
*   *(Coming Soon)* **Molecular Docking:** AutoDock Vina containerized execution.

---

## 🏗️ High-Level Architecture

The platform follows a decoupled microservice architecture, allowing the high-compute AI backend to scale independently of the client interface.

```mermaid
graph TD
    %% Users
    Scientist([🧑‍🔬 Pharma Scientist])
    
    %% Frontend
    subgraph Frontend [Vanilla Client UI]
        UI[HTML / CSS / JS UI]
        3DMol[3DMol.js Viewer]
    end

    %% API Gateway
    subgraph Backend [FastAPI Microservices]
        API[FastAPI Gateway]
        TargetService[Target Discovery Service]
        ScreeningService[Virtual Screening Engine]
        AI_Models[(XGBoost / PyTorch Models)]
    end

    %% External Data Sources
    subgraph External [Global Bio-Databases]
        UniProt[(UniProt API)]
        PDB[(RCSB PDB)]
        AlphaFold[(AlphaFold DB)]
        ChEMBL[(ChEMBL API)]
    end

    %% Connections
    Scientist -->|Interact| UI
    UI <-->|REST API| API
    UI -->|Render 3D| 3DMol
    
    API --> TargetService
    API --> ScreeningService
    
    TargetService <--> UniProt
    TargetService <--> PDB
    TargetService <--> AlphaFold
    TargetService <--> ChEMBL
    
    ScreeningService <--> |Extract Features: RDKit| AI_Models
```

---

## ⚙️ High-Level Workflow

The sequence of operations a scientist takes to go from a disease mechanism to a list of potential drug candidates.

```mermaid
sequenceDiagram
    actor Scientist
    participant UI as Platform Interface
    participant TD as Target Discovery
    participant Ext as Public DBs (UniProt/PDB)
    participant VS as Virtual Screening (Multi-Format)
    participant Parser as File Parsers Utility

    Scientist->>UI: Enter Gene Symbol (e.g., "GPR35")
    UI->>TD: POST /api/targets/discover/GPR35
    TD->>Ext: Resolve Gene to Accession (P00533)
    Ext-->>TD: Genomic Seq, PDB IDs, AlphaFold URLs
    TD->>Ext: Fetch known ChEMBL Ligands
    Ext-->>TD: Bioactivity Dataset
    TD-->>UI: Target Profile Complete
    UI-->>Scientist: Render 3D Protein Structure

    Scientist->>UI: Upload Library (.sdf, .csv, .mzml, .json, etc)
    UI->>VS: POST /api/screening/run
    VS->>Parser: parse_molecules(file_path)
    Note right of Parser: Detects extension<br/>Extracts 3D/JSON/XML<br/>Resolves PubChem CIDs to SMILES
    Parser-->>VS: Unified List[{smiles, mol_id}]
    
    loop Feature Extraction
        VS->>VS: RDKit: Convert SMILES -> 2400+ Features
        VS->>VS: XGBoost: Predict Binding Affinity (pIC50)
    end
    VS-->>UI: Top N Candidates Sorted by Affinity
    UI-->>Scientist: Display Viable Hit Compounds
```

### Supported Data Formats (Hit Screening)
The `app/utils/file_parsers.py` utility normalizes various scientific data formats into a unified SMILES pipeline:
- **`2D/1D Text`**: `.smi`, `.txt`, `.csv` (Auto-detects canonical smiles and activity columns)
- **`3D Structures`**: `.sdf`, `.sd`, `.mol2` (Extracts structures using RDKit libraries)
- **`BioAssay Data`**: `.json` (Parses PubChem concise JSON and flat arrays, performs batch API lookups for CID → SMILES resolution)
- **`LCMS Data`**: `.mzml`, `.mzxml` (Lightweight MS parsing, maps formulas to drug databases)

---

## 💻 Tech Stack

*   **Frontend:** Vanilla HTML5, CSS3 (Glassmorphism UI), JavaScript, `3Dmol.js`
*   **Backend:** Python 3.11, FastAPI, Uvicorn (Asynchronous REST API)
*   **Machine Learning / Cheminformatics:** RDKit, XGBoost, Scikit-learn, Pandas, NumPy
*   **Database Integration:** MongoDB / Beanie (Document Storage)

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.9+
*   MongoDB (Local instance or Atlas URI)

### 1. Backend Setup
Navigate to the backend directory and install the scientific dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Train the Core AI Model
Before running the server, build the production XGBoost model locally using the provided script (this generates the `binding_affinity_model.pkl`):
```bash
python train_ai_model.py
```

### 3. Start the API Server
Launch the FastAPI instance on `localhost:8000`:
```bash
uvicorn app.main:app --reload
```

### 4. Run the Client
Since the frontend operates purely on Vanilla HTML/JS/CSS, no build step is required! 
Simply open `frontend/templates/dashboard.html` in your favorite modern web browser or serve it using a lightweight local server:
```bash
cd frontend
python -m http.server 5500
```
Then navigate to `http://localhost:5500/templates/dashboard.html`.

---

## 🧪 Testing

The platform includes a set of pre-generated test datasets in `backend/test_datasets/` covering every supported format:
- `sample_library.smi` (SMILES)
- `sample_library.csv` (CSV with activity columns)
- `sample_library.sdf` (3D Structures)
- `sample_library.mol2` (3D Structures)
- `sample_bioassay.json` (PubChem BioAssay JSON)
- `sample_lcms.mzml` (LCMS mzML)

You can upload any of these files directly into the Hit Screening UI to validate the parsing and inference pipelines.
