from fastapi import FastAPI, HTTPException
from schemas import PostCreate

app = FastAPI()

text_posts = {
    1: {"title": "First post", "content": "First post's content, not really much"},
    2: {"title": "Second post", "content": "A:A;A::A:LALADPAda"},
    3: {"title": "Third post", "content": "LSA:L:DL"}

}
@app.get("/hello")
def hello_world():
    return {"message": "Hello World"}

@app.post("/create")
def create_post(post: PostCreate):
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys()) + 1] = new_post
    return new_post