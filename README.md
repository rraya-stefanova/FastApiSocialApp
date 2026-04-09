# FastApiSocial

A backend project for a social app similar to Instagram, where users upload a photo or video together with a caption.

## Project Structure

- `app/` - Core application package.
- `app/app.py` - FastAPI app instance, lifespan setup, and API endpoints.
- `app/db.py` - Async SQLAlchemy setup and `Post` database model.
- `app/schemas.py` - Pydantic request/response schemas.
- `main.py` - Local entry point that starts Uvicorn.
- `pyproject.toml` - Project metadata and Python dependencies.
- `uv.lock` - Locked dependency versions for reproducible installs.
- `test.db` - Local SQLite database file used by the app.
- `README.md` - Project overview and structure notes.
