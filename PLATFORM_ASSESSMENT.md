# Platform Assessment: Scientific Utility & Real-Time Capability

## 📊 Executive Summary
**Current Status**: **Functional Demo / MVP**
**Scientific Utility**: **Low** (Simulation-heavy, limited data)
**Real-Time Capability**: **Basic** (Polling-based)

The platform currently demonstrates the *workflow* of a biotech platform but lacks the *computational engine* required for actual discovery. To make this helpful for scientists, we must replace "Simulated Logic" with "Real Computational Workflows".

---

## 🔬 Gap Analysis: Scientific Utility

| Module | Current State | Gap for Scientists | Required Upgrade |
| :--- | :--- | :--- | :--- |
| **Hit Screening** | Uses a hardcoded list of ~12 common drugs (Aspirin, etc.). Runs a light XGBoost model. | Scientists screen **Millions** of compounds. They need to upload their own libraries (SDF/SMILES files). | 1. **File Upload**: Support `.smi` / `.sdf` uploads.<br>2. **Docking Engine**: Integrate **AutoDock Vina** or **DiffDock** for structural analysis (not just features). |
| **Lead Optimization** | **Mocked**. Picks random pre-defined pairs (e.g. Caffeine -> Theobromine). | Scientists need to generate **Novel** molecules based on the specific target pocket. | Integrate a real Generative Model (e.g., **REINVENT**, **LSTM-HC**, or **DiffDock-Generative**). |
| **Wet-Lab** | "Fire and Forget" webhook. Auto-completes after 5s. | Experiments take hours/days. Robots need to report status back asynchronously. | Implement **Async Callbacks**. The robot should POST to `/api/experiments/callback` when done. |
| **Target Discovery** | Fetches PDB metadata? (Assumed) | Needs sequences, variation data, and known binders. | Connect to **Uniprot API** and **ChEMBL API** live. |

---

## ⚡ Gap Analysis: Real-Time Architecture

Currently, the frontend "Polls" (asks the server "Am I done yet?") every 5 seconds.
**Problem**: Slow updates, network chattiness, poor experience for long jobs (docking takes hours).

### Recommended Architecture: WebSocket + Task Queue
1.  **WebSockets (FastAPI)**: Push updates to the UI immediately when a log line is generated or a step completes.
2.  **Celery + Redis**: Move heavy compute (Docking/AI) out of the web server.

---

## 🚀 Roadmap to "Scientist-Grade"

### Phase 1: Real Logic (The "Brain")
1.  **Upgrade `screening.py`**: Allow uploading a `.smi` file. Parse it with RDKit. Run the model on *those* molecules.
2.  **Upgrade `optimization.py`**: Connect to a real generative script (even a simple genetic algorithm using RDKit mutations is better than hardcoded strings).

### Phase 2: Real-Time (The "Nervous System")
1.  **Implement WebSockets**:
    *   Backend: `/ws/experiments/{id}`
    *   Frontend: Replace `setInterval` with `new WebSocket()`.
2.  **Live Logs**: Stream stdout from the AI process directly to the frontend terminal.

### Phase 3: Hardware Integration (The "Hands")
1.  **Robot Listener**: Create a standardized JSON schema for the Robot Webhook.
2.  **Callback Endpoint**: Secure endpoint for the robot to upload results (CSV/Excel).

---

## 📝 Immediate Action Items (Refining the Current Code)

If you want to make it **Scientist-Grade** *right now* with minimal changes, I recommend:

1.  **Enable Custom Screening**: Add a file upload to Hit Screening so they can test *their own* molecules.
2.  **Real Mutations**: In `optimization.py`, write a function that *actually* modifies the SMILES string (adds a group, changes an atom) using RDKit, instead of returning a hardcoded "Theobromine".
