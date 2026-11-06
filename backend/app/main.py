from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="D&D Helper API",
    description=(
        "Backend API for D&D Helper, "
        "including character building, "
        "campaign management, and D&D reference data."
    ),
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "application": "D&D Helper API",
        "version": app.version,
        "status": "running",
    }
