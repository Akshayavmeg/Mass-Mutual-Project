"""Backend entrypoint (docs/36_Development_Guidelines.md Section 4).

Run locally with:

    uvicorn main:app --reload

The actual FastAPI application is assembled in app.main so it stays
importable as a plain module for testing (app.main:app) as well.
"""

from app.main import app

__all__ = ["app"]
