"""FastAPI application entry point."""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve static frontend files if available
STATIC_DIR = Path("/app/static")
if STATIC_DIR.exists():
    # Mount static assets (JS, CSS, etc.)
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str) -> FileResponse:
        """Serve the SPA for all non-API routes."""
        # Check if file exists in static dir
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        # Fall back to index.html for SPA routing
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    def root() -> dict[str, str]:
        """Root endpoint returning API info (when no frontend is built)."""
        return {"name": "FilamentProfiles", "version": __version__}
