from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from fastapi_users import fastapi_users
from sqlalchemy.sql.functions import user

from app.schemas import PostCreate, PostResponse, UserUpdate, UserRead, UserCreate
from app.db import Post, create_db_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import os
import shutil
import uuid
import tempfile
from app.users import auth_backend, current_active_user, fastapi_users

from app.users import auth_backend


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead),prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])


text_posts = {
    1: {"title": "First post", "content": "First post's content, not really much"},
    2: {"title": "Second post", "content": "Second post, just a trial post"},
    3: {"title": "Third post", "content": "Third post, now clear"}

}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...),
                      caption: str = Form(""),
                      user: User = Depends(current_active_user),
                      session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        with open(temp_file_path, "rb") as upload_stream:
            upload_response = imagekit.files.with_raw_response.upload(
                file=upload_stream,
                file_name=file.filename,
                use_unique_file_name=True,
                tags=["backend_upload"],
            )
        if upload_response.status_code == 200:
            upload_result = upload_response.parse()
            post = Post(
                caption=caption,
                url=upload_result.url,
                user_id=user.id,
                file_type="video" if upload_result.file_type.startswith("video") else "image",
                file_name=upload_result.name,
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
        raise HTTPException(status_code=502, detail="Image upload failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.get("/feed")
async def get_feed(
        session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_name": post.file_name,
                "file_type": post.file_type,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "unknown"),
            }
        )
    return {"posts": posts_data}

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str,
                      user: User = Depends(current_active_user),
                      session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to delete this post")
        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))