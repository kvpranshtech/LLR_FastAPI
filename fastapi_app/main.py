# fastapi_app/main.py
from fastapi import FastAPI
from fastapi_app.routers import auth, users

app = FastAPI(title="FastAPI using Django DB")

app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "FastAPI connected to Django PostgreSQL DB!"}


app = FastAPI(title="LLR FastAPI", version="1.0.0")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "LLR FastAPI is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}