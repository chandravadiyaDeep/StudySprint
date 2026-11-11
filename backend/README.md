# StudySprint API — Local setup

## 1. Requirements
- Python 3.11+
- A Gemini API key from Google AI Studio
- Internet access for the backend to call Gemini

## 2. Install

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add your private `GEMINI_API_KEY`. Never paste the real key into frontend files, GitHub commits, screenshots or chat messages.

## 3. Run

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: http://127.0.0.1:8000/api/v1/health
- OpenAPI docs: http://127.0.0.1:8000/docs
- Analyze endpoint: `POST /api/v1/pyq/analyze`

## 4. Request shape

```json
{
  "subject": "Data Structures",
  "papers": [
    {
      "name": "DS_2024.pdf",
      "text": "Q1. Explain linked lists...\\nQ2. Compare stack and queue..."
    }
  ]
}
```

The browser currently extracts selectable PDF text with PDF.js. The backend segments question candidates, asks Gemini to classify the supplied records, then calculates topic counts from returned question IDs and original source records. It does not store uploaded paper text.

## 5. Current limitations (honest V1 baseline)
- Scanned PDFs need OCR and are not supported by the current browser extraction flow.
- Numbered-question segmentation is conservative and will need testing against real university paper formats.
- Gemini topic labels and explanations are AI interpretations and require review.
- The API has a basic per-IP request limit (5 analyses/minute) but is still an early development service. Authentication, user quotas, durable abuse protection, monitoring, audit history and a production privacy/retention policy are required before unrestricted public launch.
- Configure exact CORS origins before deployment. Do not use wildcard CORS with a secret-bearing API.
