# Biologics Discovery Platform - Testing Guide

This guide will walk you through testing the end-to-end functionality of your Biologics Discovery Platform. 

**Prerequisite**: Ensure your backend server is running in a terminal window:
```powershell
# In backend/ directory
uvicorn app.main:app --reload
```

---

## 1. Dashboard (`dashboard.html`)
**Goal**: Verify connection to the backend and view real-time statistics.

1.  Open `frontend/templates/dashboard.html` in your web browser.
2.  **Check Status**: Look at the top right corner. You should see a green badge saying **"● System Online"**.
3.  **Check Connection**: If it says "Connecting..." or "Offline", ensure your backend is running.
4.  **Initial State**: The statistics (Experiments, Targets, Jobs) will likely be **0**. This is correct for a fresh database.

---

## 2. Target Explorer (`target_explorer.html`)
**Goal**: Create and Search for biological targets.

1.  Navigate to **Target Explorer** using the sidebar.
2.  **Search**: Type a gene name like `Insulin` or `EGFR` in the search box and click **Search**.
    *   *Result*: Since the database is empty, it will say "No local targets found".
3.  **Create Target**: A button **"+ Create New Target"** will appear. Click it.
    *   *Action*: This sends a `POST` request to the backend to save this target name to MongoDB.
4.  **Verify**: Click **Search** again.
    *   *Result*: You should now see a card displaying "Insulin" (or your name) with status "Candidate".

---

## 3. Hit Screening (`hit_screening.html`)
**Goal**: Launch a virtual screening job for a target.

1.  Navigate to **Hit Screening**.
2.  **Input Data**:
    *   **Target ID**: Enter the name of the target you created (e.g., `Insulin`). *Note: In a full app, this would be a specific ID, but for this test, any text works to trigger the job.*
    *   **Library ID**: Leave as default or type `ChemDiv-TEST`.
3.  **Run**: Click **"Start Screening"**.
    *   *Result*: You should see a green success message: "✓ Job Started!".
4.  **Check Queue**: Look at the "Running Jobs" section below. Your new job should appear with status **"RUNNING"**.

---

## 4. Wet-Lab Validation (`wet_lab.html`)
**Goal**: Log physical experiment results into the system.

1.  Navigate to **Wet-Lab Validation**.
2.  **Log Data**:
    *   **Name**: Enter `Binding Assay 001`.
    *   **Type**: Select `Binding Affinity`.
3.  **Save**: Click **"Log Experiment"**.
    *   *Result*: Message changes to "Saved!".
4.  **Verify**: The "Recent Experiments" list below will update to show your new experiment.

---

## 5. Verification Loop
**Goal**: meaningful integration test.

1.  Go back to **Dashboard**.
2.  **Check Stats**: The numbers should have updated!
    *   **Targets**: Should be `1` (from step 2).
    *   **Screening Jobs**: Should be `1` (from step 3).
    *   **Experiments**: Should be `1` (from step 4).

If you see these numbers update, your **Frontend**, **Backend**, and **Database** are all talking to each other perfectly.
