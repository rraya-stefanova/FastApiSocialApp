from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from app.schemas import PostCreate, PostResponse
from app.db import Post, create_db_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield

app = FastAPI(lifespan=lifespan)

text_posts = {
    1: {"title": "First post", "content": "First post's content, not really much"},
    2: {"title": "Second post", "content": "Second post, just a trial post"},
    3: {"title": "Third post", "content": "Third post, now clear"}

}

@app.get("/posts/{id}")
def get_post(id: int) -> PostResponse:
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Not found")
    return text_posts.get(id)

@app.post("/create")
def create_post(post: PostCreate) -> PostResponse :
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys()) + 1] = new_post
    return new_post

@app.delete("/delete")
def delete_post(id: int):
    if id >= len(text_posts.keys()):
        raise HTTPException(status_code=404, detail="Not found")
    pass

@app.upload("/upload")
async def upload_post(
        file: UploadFile = File(...),
        caption: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
):
    pass