# StudySprint

**PYQ Intelligence first. Evidence before predictions.**

StudySprint V1 focuses only on previous-year question paper intelligence. Syllabus Intelligence is deliberately removed from the active interface and retained as a future research document.

## Repository structure

- `index.html` — application shell
- `assets/css/app.css` — glassmorphism interface styles
- `assets/js/app.js` — browser UI, PDF text extraction and API client
- `backend/` — FastAPI service and Gemini reasoning integration
- `docs/engines/PYQ_INTELLIGENCE.md` — active engine specification and algorithm roadmap
- `docs/engines/SYLLABUS_INTELLIGENCE.md` — deferred future research only

## V1 analysis flow

1. User selects PDF, TXT or MD papers.
2. Browser extracts selectable PDF text using PDF.js.
3. Browser sends paper names and extracted text to the configured StudySprint API.
4. FastAPI segments numbered question candidates.
5. Gemini classifies the concepts, topics, question types and difficulty estimates.
6. Python computes topic frequency and paper coverage from valid question IDs and original source records.
7. UI displays each finding with the supporting source questions and paper names.

Gemini is an interpretation layer. It does not generate counts. Frequencies are deterministic calculations from the extracted source-question records.

## Run the backend locally

See [backend setup](backend/README.md) for the complete local setup and testing instructions. Quick start:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Add your private GEMINI_API_KEY to backend/.env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the static frontend using VS Code Live Server (commonly `http://127.0.0.1:5500`). In PYQ Intelligence, set the API base URL to `http://127.0.0.1:8000`.

## Security and truth constraints

- Never put a Gemini API key in frontend code, GitHub Pages or a public commit.
- The backend does not persist uploaded paper text. The browser stores the generated report (including source question excerpts) in localStorage on the current device.
- Extracted text is sent to the configured backend and Google Gemini for analysis. Review Google's current Gemini API data-handling terms before sending sensitive material; do not upload confidential documents.
- The backend is a development foundation, not yet ready for unrestricted public traffic. Authentication, rate limits, quotas, request abuse controls and a production privacy/retention policy are required before launch.
- Scanned PDFs need OCR; current browser extraction handles selectable text only.
- Question segmentation and Gemini topic labels require testing on real papers.
- Historical frequency is not a prediction or guarantee about future exams.

## GitHub Pages

GitHub Pages can host the frontend only. The FastAPI backend must be deployed separately (for example, to Render) and its public HTTPS URL entered in the frontend API URL field. Check GitHub Actions for the static deployment status.
