# Comprehensive End-to-End Testing Guide

This guide provides a complete manual testing workflow for the Biologics Discovery Platform. It covers the entire lifecycle of a drug discovery project, from authentication to wet-lab validation.

## 📋 Prerequisites

Before starting, ensure your environment is ready:

1.  **Backend**: Open a terminal in `backend/` and run:
    ```bash
    uvicorn app.main:app --reload
    ```
    *Verify*: Server should be running on `http://127.0.0.1:8000`.

2.  **Database**: Ensure your MongoDB instance is running (if local) or your connection string is valid.

3.  **Frontend**: Open the `frontend/` folder. You will be opening HTML files directly in your browser.

---

## 🧪 End-to-End Test Scenario

We will simulate a scientist's workflow:
**"Login -> Find a Protein Target -> Screen for Drug Hits -> Optimize a Lead Compound -> Send for Wet-Lab Testing -> Review Blinded Results"**

---

### Step 1: Authentication
**Goal**: Verify access control.

1.  **Open**: `frontend/login.html` in your browser.
2.  **Action**:
    -   Enter any username/password (currently using mock auth) or standard credentials if configured.
    -   Click **LOGIN**.
3.  **Verify**:
    -   You are redirected to the **Dashboard** (`dashboard.html`).
    -   Navigation sidebar is visible.

---

### Step 2: Target Discovery
**Goal**: Select a biological target for the project.

1.  **Navigate**: Click **Target Explorer** in the sidebar.
2.  **Action**:
    -   Search for a target (e.g., type `EGFR` or `TRG-`).
    -   Select a target from the list.
3.  **Verify**:
    -   Target details panel appears (Name, Type, PDB ID).
    -   3D Structure viewer loads the protein structure (if configured) or placeholder.
    -   **Pass Criteria**: You can successfully "Select" a target ID (note this ID, e.g., `TRG-8821`).

---

### Step 3: Hit Screening
**Goal**: Identify initial drug candidates.

1.  **Navigate**: Click **Hit Screening**.
2.  **Action**:
    -   **Target PDB ID**: Enter `4INS` (or any valid PDB code).
    -   **Small Molecule Library**: Keep default `ChemDiv-2024-Ultra` or enter another name.
    -   Click **EXECUTE SCREENING**.
3.  **Verify**:
    -   Status updates below the button (e.g., "Initializing...").
    -   A new job appears in the **Real-Time Queue Monitor** on the right.
    -   **Pass Criteria**: Once completed (green status), "Hits Found" and a table of molecules should appear. Note the top molecule ID (e.g., `Compound-A1`).

---

### Step 4: Lead Optimization (Generative AI)
**Goal**: Improve the selected candidate using AI.

1.  **Navigate**: Click **Lead Optimization**.
2.  **Setup**:
    -   **Target ID**: Enter the ID from Step 2 (e.g., `TRG-8821`).
    -   **Optimization Goal**: Select `Maximize Affinity`.
    -   *(Note: The input molecule is currently inferred from the target context or latest screening hit).*
3.  **Action**:
    -   Click **✨ GENERATE & OPTIMIZE**.
4.  **Verify**:
    -   Status changes to "RUNNING INFERENCE".
    -   Logs show AI model steps (DiffDock/ProteinMPNN simulation).
    -   After ~5-10 seconds, results appear.
    -   **Pass Criteria**: "Optimization Complete" message and a new "Optimized Score" (e.g., +30% improvement).

---

### Step 5: Wet-Lab Validation
**Goal**: Order a physical experiment for the optimized lead.

1.  **Navigate**: Click **Wet-Lab Validation**.
2.  **Action**:
    -   **Name**: Enter `Validation-Exp-001`.
    -   **Assay Type**: `Binding Affinity (SPR)`.
    -   **Target ID**: `TRG-8821`.
    -   **Webhook URL (Optional)**: Leave empty for **Simulation Mode**.
        -   *Note*: This field allows connecting to real lab automation hardware (e.g., Opentrons). If provided, the system sends instructions to that URL. If empty, the system simulates the robot's actions.
    -   **Description**: "Validating AI optimized lead".
    -   Click **INITIATE PROTOCOL**.
3.  **Verify**:
    -   Success message: "✅ Protocol Initiated".
    -   Experiment appears in the **Active Lab Bench** table.
    -   Status: `Planned` -> `Running` (if simulated) -> `Completed`.

---

### Step 6: Blinded Results View
**Goal**: Ensure scientific rigor by blinding data.

1.  **Navigate**: Click **Blinded Results**.
2.  **Verify Blinding**:
    -   Locate `Validation-Exp-001`.
    -   **Check**: The "True Identity" column should be **BLURRED/HASHED** (e.g., `XJ9#...`).
    -   **Check**: The "Blinded ID" is unique (e.g., `BLIND-7721`).
3.  **Action**:
    -   Click **DECRYPT DATA** (top right).
4.  **Verify**:
    -   Animation reveals the true identity: `Validation-Exp-001`.
    -   Button changes to "ACCESS GRANTED".

---

## 🛑 Troubleshooting

| Issue | Possible Cause | Fix |
| :--- | :--- | :--- |
| **"Network Error" / API Fail** | Backend not running | Check terminal for `uvicorn` errors. Restart server. |
| **3D Viewer Blank** | WebGL or File Path | Ensure `.pdb` files exist or ignore for mock testing. |
| **Blinding not working** | CSS/JS Error | Hard refresh (Ctrl+F5) to reload scripts. |
| **No Results in Screening** | Database Empty | Ensure database is seeded or connected. |

---

## ✅ Checklist for Release

- [ ] All pages load without console errors (F12 > Console).
- [ ] Navigation flows seamlessly between modules.
- [ ] Data persists (refreshing Wet-Lab page shows saved experiments).
- [ ] AI simulation runs to completion without timeout.
