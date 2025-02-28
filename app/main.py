from fastapi import FastAPI

from app.api import group, user

app = FastAPI()

app.include_router(user.router)
app.include_router(group.router)
