# fastapi_app/main.py
from fastapi import FastAPI
from fastapi_app.routers import users

app = FastAPI(title="FastAPI using Django DB")

app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "FastAPI connected to Django PostgreSQL DB!"}
