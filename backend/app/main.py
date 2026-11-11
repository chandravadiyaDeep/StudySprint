"""StudySprint PYQ Intelligence API."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from app.config import get_settings
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analysis import analyze

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app = FastAPI(title="StudySprint PYQ Intelligence API", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Restrict browser access to known frontend origins; CORS is not an authentication system.
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
@limiter.limit("5/minute")
def analyze_pyq(request: Request, payload: AnalyzeRequest) -> AnalyzeResponse:
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
