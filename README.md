# FastApiSocial

A backend project for a social app similar to Instagram, where users upload a photo or video together with a caption.

## What This Project Does

This API provides the backend for a simple social feed:

- Users can register/login with JWT authentication.
- Authenticated users can upload an image/video with a caption.
- Uploaded media is stored in ImageKit.io, while post metadata is stored in the database.
- The feed endpoint returns stored posts ordered by newest first.
- Users can delete only their own posts.

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

## Wiring Overview

### ImageKit.io Integration

- `app/images.py` creates a shared `ImageKit` client using environment variables.
- In `POST /upload` (`app/app.py`), incoming `UploadFile` content is copied to a temporary file.
- That file stream is uploaded through the ImageKit SDK.
- On successful upload, the API stores the returned URL, file name, and inferred media type (`image` or `video`) in the `posts` table.

Expected environment variables:

- `IMAGEKIT_PRIVATE_KEY`
- `IMAGEKIT_PUBLIC_KEY`
- `IMAGEKIT_URL_ENDPOINT`

### Database Connection and Models

- `app/db.py` configures an async SQLAlchemy engine with `sqlite+aiosqlite:///./test.db`.
- `async_sessionmaker` provides `AsyncSession` instances through `get_async_session()`.
- `create_db_tables()` runs at startup and creates tables from SQLAlchemy metadata.
- Main models:
  - `User` (from `fastapi-users` SQLAlchemy base table)
  - `Post` (caption, media URL, media type, file name, timestamp, and `user_id` FK)
- Auth and user persistence are connected through `SQLAlchemyUserDatabase` and `get_user_db()`.

### FastAPI Techniques Used

- Lifespan startup hook initializes database tables before serving requests.
- Dependency injection (`Depends`) is used for:
  - authenticated user context
  - database session management
  - user manager/database bindings
- Router composition from `fastapi-users` wires auth/user endpoints (`/auth/*`, `/users/*`).
- Async endpoint handlers use SQLAlchemy async queries and commits.
- Request parsing combines multipart file uploads (`UploadFile`) and form fields (`Form`) in the same endpoint.
