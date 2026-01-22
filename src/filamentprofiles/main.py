"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from filamentprofiles import __version__
from filamentprofiles.api import export, filaments, machines, plates, profiles

app = FastAPI(
    title="FilamentProfiles",
    description="Print settings management companion for Spoolman",
    version=__version__,
)

# CORS middleware for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(machines.router, prefix="/api/machines", tags=["machines"])
app.include_router(plates.router, prefix="/api/plates", tags=["plates"])
app.include_router(filaments.router, prefix="/api/filaments", tags=["filaments"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint returning API info."""
    return {"name": "FilamentProfiles", "version": __version__}


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
