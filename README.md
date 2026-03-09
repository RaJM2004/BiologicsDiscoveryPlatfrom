# 🧬 Biologics Discovery Platform

An advanced, production-grade AI drug discovery platform designed for pharmaceutical scientists. This platform accelerates the drug discovery pipeline from identifying protein targets to screening millions of compounds using cheminformatics and machine learning.

![Platform Banner](https://upload.wikimedia.org/wikipedia/commons/2/23/DNA_Orbit_Animated.gif) <!-- Placeholder for actual UI screenshot -->

## 🚀 Key Features

*   **Target Discovery (Neural-Bio Interface):** Instantly resolve gene symbols (e.g., EGFR, TP53) to UniProt primary accessions. Automatically fetches genomic sequences, fetches verified 3D structures from **RCSB PDB**, and seamlessly falls back to **AlphaFold** `.cif` predictions when crystal structures are unavailable.
*   **Virtual Hit Screening:** Replaces synthetic assumptions with real scientific models. Converts `.smi` libraries into 2400+ dimensional mathematical features (2048-bit ECFP4 Morgan Fingerprints, 166 MACCS Keys, 200+ RDKit 2D Descriptors) to predict binding affinities (pIC50) using an optimized **XGBoost Regressor** trained on ChEMBL data.
*   **Molecular Visualization:** Fully interactive embedded 3D molecule viewing (via `3Dmol.js`), rendering PDB structures and AlphaFold Confidence Arrays directly within the UI.
*   *(Coming Soon)* **Lead Optimization:** Generative AI for bio-realistic structural mutations.
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
    participant VS as Virtual Screening (RDKit+XGBoost)

    Scientist->>UI: Enter Gene Symbol (e.g., "GPR35")
    UI->>TD: POST /api/targets/discover/GPR35
    TD->>Ext: Resolve Gene to Accession (P00533)
    Ext-->>TD: Genomic Seq, PDB IDs, AlphaFold URLs
    TD->>Ext: Fetch known ChEMBL Ligands
    Ext-->>TD: Bioactivity Dataset
    TD-->>UI: Target Profile Complete
    UI-->>Scientist: Render 3D Protein Structure

    Scientist->>UI: Upload Library (e.g., library.smi)
    UI->>VS: POST /api/screening/run
    loop Feature Extraction
        VS->>VS: RDKit: Convert SMILES -> 2400+ Features
        VS->>VS: XGBoost: Predict Binding Affinity (pIC50)
    end
    VS-->>UI: Top N Candidates Sorted by Affinity
    UI-->>Scientist: Display Viable Hit Compounds
```

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

To test the **Hit Screening** module natively, a test library (`GPR35_test_library.smi`) is provided in the root directory. It contains a mix of real high-affinity agonists and low-affinity decoys to validate the XGBoost model's accuracy.
