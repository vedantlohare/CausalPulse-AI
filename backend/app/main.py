from fastapi import FastAPI
from app.api.endpoints import diagnostics
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CausalPulse AI: Enterprise KPI Diagnostic and Automated Storytelling Engine",
    version="1.0.0"
)

app.include_router(diagnostics.router, prefix=settings.API_V1_STR + "/diagnostics", tags=["diagnostics"])

@app.get("/")
def read_root():
    return {"message": "Welcome to CausalPulse AI API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
