# Interactive Demo & Walkthrough Script

This script walks through presenting and demonstrating the AI Customer Support Ticket Classifier.

---

## 1. Setup & Launch
1. Ensure the virtual environment is activated and requirements are installed:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
2. Open the Web Dashboard in your browser:
   [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)

---

## 2. Live Demo Steps

### Step 1: Single Ticket Submission & Auto-Classification
1. In the **New Ticket** panel:
   - Enter Customer Email: `alex@example.com`
   - Enter Ticket Description:
     > *"I was double charged on my invoice #98231 for the monthly subscription and need an immediate refund."*
2. Click **Submit Ticket**.
3. **Observe**:
   - Classification: `Billing` or `Refund`
   - Priority: `High` / `Critical`
   - Method: Fast ML classification with high confidence score.
   - Recommended Knowledge Base article suggestions automatically displayed.

### Step 2: Fallback Handling for Ambiguous / Complex Query
1. Enter an ambiguous or novel ticket description:
   > *"The widget is malfunctioning in a strange manner, can you help?"*
2. Submit and observe the engine evaluate confidence.
3. If below threshold, notice fallback routing via Google Gemini to provide appropriate triage.

### Step 3: Batch Ticket Processing
1. Navigate to the **Bulk Import** tab.
2. Select `data/sample/tickets.csv` or upload a custom CSV.
3. Observe real-time batch processing, category distribution chart updates, and queue population.

### Step 4: Status Updates & Ticket Resolution
1. Click on any ticket in the Triage Queue.
2. Change the status from `Open` to `In Progress` or `Resolved`.
3. View the Similar Tickets recommendation panel to verify historical resolution links.

### Step 5: Analytics Dashboard
1. Review the Analytics section showing:
   - Total tickets processed
   - Distribution by Category (Billing, Technical, Delivery, etc.)
   - Distribution by Priority (Low, Medium, High, Critical)
   - Classification method distribution (`ml` vs `gemini`)
