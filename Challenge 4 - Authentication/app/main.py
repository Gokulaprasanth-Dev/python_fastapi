from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import database

from app.api.v1.auth_routes import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await database.connect()
    
    yield
    
    await database.disconnect()
    
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

@app.get("/")
async def  root():
    print("CALLED1")
    return {"message": "FastAPI Modular Auth Service Running"}


app.include_router(auth_router)
