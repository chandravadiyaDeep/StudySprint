# Add your Gemini API key locally

This repository is public, so **never save a real Gemini API key in a GitHub-tracked file**.

## Create your private key file

From the repository root in Windows PowerShell:

```powershell
# Move into the backend folder
cd backend

# Create your private local environment file from the safe template
Copy-Item .env.example .env
```

Open `backend/.env` in VS Code and replace the placeholder:

```env
GEMINI_API_KEY=paste_your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Save the file. The root `.gitignore` excludes `.env` and other local environment files, so Git should not upload your secret.

## Start StudySprint API

```powershell
# Run from the backend folder with your virtual environment activated
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/api/v1/health` to check that the local API is running.

**Important:** `.env.example` is safe to keep in GitHub because it contains only a placeholder. The real `.env` file exists on your computer only. Do not paste your key into `.env.example`, source code, GitHub's website, screenshots or chat.

If you accidentally commit a real key, revoke it in Google AI Studio and generate a new one. Deleting the key from the latest commit is not sufficient.
