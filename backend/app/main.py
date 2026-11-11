"""StudySprint PYQ Intelligence API."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analysis import analyze

settings = get_settings()
app = FastAPI(title="StudySprint PYQ Intelligence API", version="0.1.0")

# Restrict browser access to known frontend origins; configure the production origin explicitly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/v1/health")
def health() -> dict:
    # Health checks deliberately do not expose secret values or API-key presence.
    return {"status": "ok", "service": "studysprint-pyq-api", "version": "0.1.0"}


@app.post("/api/v1/pyq/analyze", response_model=AnalyzeResponse)
def analyze_pyq(payload: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return analyze(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        # Missing configuration and empty model responses are actionable server errors.
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        # Do not leak provider details, secrets or stack traces to public clients.
        raise HTTPException(status_code=502, detail="PYQ analysis failed. Check backend logs and try again.") from exc
