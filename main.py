#this is a full crud with auth api with a fake db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import users
import todos


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(todos.router)
@app.get("/")
async def index():
    return {"msg":"home page here"}


