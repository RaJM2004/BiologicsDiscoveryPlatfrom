# Biologics Discovery Platform: Standard Operating Procedure (SOP)

This document defines the **scientifically valid workflow** for using this platform. This pipeline ensures cost-efficiency by prioritizing computational methods (finding/polishing leads) *before* physical expenditure (wet-lab validation).

## ✅ The Correct Pipeline

**Target Explorer** &rarr; **Hit Screening** &rarr; **Lead Optimization** &rarr; **Wet-Lab Validation** &rarr; **Blinded Analysis**

---

## Step-by-Step Breakdown

### 1. Target Explorer (Identify the "Lock")
*   **Goal**: Identify a biological target (protein/gene) implicated in a disease.
*   **Action**: Select a target from the database (e.g., `TRG-8821`).
*   **Output**: A validated Target ID and PDB Structure.
*   **Why First?**: You cannot find a drug if you don't know what it needs to stick to.

### 2. Hit Screening (Find Rough "Keys")
*   **Goal**: Rapidly filter millions of molecules to find those that bind *somewhat* well.
*   **Action**: Upload a library file (`.smi`) containing thousands of compounds. The AI (XGBoost) predicts binding affinity for all of them.
*   **Output**: A list of "Hits" (Top 100 molecules).
*   **Why Second?**: It's a funnel. You start with 1,000,000 compounds and narrow it down to 100 interesting ones.

### 3. Lead Optimization (Polish the "Key")
*   **Goal**: Take a promising "Hit" and use AI to evolve it into a better drug (better affinity, lower toxicity).
*   **Action**: Input the SMILES of your best hit. The Genetic Algorithm mutates the structure (adding atoms, changing bonds) to improve its score.
*   **Output**: An "Optimized Lead Candidate" (e.g., Affinity -12.5 kcal/mol).
*   **CRITICAL NOTE**: **This happens BEFORE Wet-Lab.**
    *   *Computer Interaction*: $0.0001 per run.
    *   *Wet-Lab Experiment*: $500+ per run.
    *   *Rule*: Never send a raw "Hit" to the lab if you can optimize it first.

### 4. Wet-Lab Validation (The "Real" Test)
*   **Goal**: Physically synthesis and test the optimized molecule to prove the AI was right.
*   **Action**: Use the **"Send to Wet Lab"** button. This sends protocols to liquid handling robots (Opentrons) or generates a LIMS work order.
*   **Output**: Experimental Data (Raw Readouts).
*   **Why Fourth?**: This is the most expensive step. We only validate the "Best of the Best".

### 5. Blinded Results (Unbiased Verification)
*   **Goal**: Analyze the wet-lab results without bias.
*   **Action**: The system hides the molecule names (replacing them with IDs like `BLIND-XYZ`) so scientists analyze the data purely on merit, not "hoping" their favorite molecule worked.
*   **Output**: Final "GO / NO-GO" decision for Clinical Trials.

---

## Summary of the "Brain" Upgrade
Your platform now powers this entire flow with real logic:
*   **Screening**: Parses real files and predicts scores.
*   **Optimization**: Evolves structure strings (SMILES) really.
*   **Validation**: Automates the transfer of data + Webhook integration for robots.
